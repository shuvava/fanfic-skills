#!/usr/bin/env python3
"""Outside readers for a drafted chapter: other models flag sentences, Claude decides.

Standard library only. Run from the project root, after `naturalize` in `write-chapter` §5.

    # the key: OPENROUTER_API_KEY in the shell, or in .env at the project root (gitignored)
    python3 critique.py prompt drafts/book-01/ch05-<slug>.md --dir <out>   # prompt for Claude's own critic
    python3 critique.py add    drafts/book-01/ch05-<slug>.md --dir <out> --reply <out>/claude.reply.json
    python3 critique.py run    drafts/book-01/ch05-<slug>.md --dir <out>   # the OpenRouter critics
    python3 critique.py merge  drafts/book-01/ch05-<slug>.md --dir <out>   # all flags, by sentence

`<out>` is `<book>/naturalness/critics/<chapter stem>/`. The critics are listed in `critics:` in
CANON.md; `claude` there means Claude's own fresh-context critic (a subagent fed `prompt.md`), every
other entry is an OpenRouter model id. `--model` overrides the list for `run`.

What a critic gets
------------------
The draft body (frontmatter and image lines removed) and the project's taste: `plan/HARNESS.md` →
`## Naturalness examples` and `## Overused patterns`, and the whole of `wiki/canon/overview.md`
(comic register, dialogue layout, non-standard orthography — on a pilot two outside models
"corrected" the author's dialogue punctuation when they had not been shown it). It returns a JSON
array of {quote, problem, suggestion}. It never rewrites the chapter.

What comes back
---------------
`<out>/<critic>.json` per critic. A quote that is not an exact substring of the draft is dropped
and counted — a critic that paraphrases cannot be applied by quote. `merge` groups the surviving
flags by the sentence they touch and writes `<out>/merged.md`, one entry per sentence with each
critic's remark under it, for Claude to accept or reject against the user's verdicts.

Exit codes: 0 ok, 1 a critic failed (the others are still written), 3 usage error.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from envfile import load_env  # noqa: E402
from export_chapter import FRONTMATTER_RE, IMAGE_RE  # noqa: E402

API = "https://openrouter.ai/api/v1/chat/completions"
TRANSIENT = {408, 429, 500, 502, 503, 504, 520, 522, 524}
CLAUDE = "claude"

SYSTEM = """You are a strict editor reading a chapter of fiction in its own language, as a native \
reader would. It was drafted by another model imitating an author. Point at the places a native \
reader stumbles on: clumsy or machine-sounding constructions, broken collocations, wrong \
government or agreement, abstractions where an image is needed, sentences whose meaning has to be \
puzzled out, jokes that do not land, and logic that contradicts the page (a claim the next line \
undoes, a premise the reader was never given).

Rules:
- Do NOT rewrite the chapter. Only point at places.
- Deliberately pompous or ceremonious phrasing about trivial things is the narrator's irony — a \
joke. Do not flag it when it is funny. The project notes below hold the author's own verdicts on \
earlier edits: they outrank your taste.
- The author's orthography and dialogue layout, as the notes record them, are correct by \
definition. Never "fix" them.
- A suggestion must keep the facts, the action and the joke. A different verb is a different fact. \
If you cannot fix without changing meaning, leave the suggestion empty.
- A pattern from "Overused patterns" is not a defect by itself. Flag only what you stumble on.
- Ten precise flags beat forty doubtful ones. At most 25.
- Write `problem` and `suggestion` in the chapter's language.

Answer with a JSON array only, nothing before or after:
[{"quote": "<exact quote from the chapter, 3-25 words, punctuation included>",
  "problem": "<what a reader stumbles on, one line>",
  "suggestion": "<a minimal fix, or empty>"}]
The quote must match the chapter text character for character."""


def usage(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(3)


def section(path: Path, heading: str) -> str:
    if not path.is_file():
        return ""
    m = re.search(rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)", path.read_text(encoding="utf-8"),
                  re.M | re.S)
    return m.group(1).strip() if m else ""


def body(draft: Path) -> str:
    text = draft.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if m:
        text = text[m.end():]
    return "\n".join(l for l in text.splitlines() if not IMAGE_RE.match(l.strip())).strip()


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def canon_list(key: str) -> list[str]:
    """`key: [a, b]` or a `- item` block from CANON.md's frontmatter."""
    p = Path("CANON.md")
    m = FRONTMATTER_RE.match(p.read_text(encoding="utf-8")) if p.is_file() else None
    if not m:
        return []
    fm = m.group(1)
    inline = re.search(rf"^{key}:\s*\[(.*?)\]", fm, re.M)
    if inline:
        return [x.strip().strip("'\"") for x in inline.group(1).split(",") if x.strip()]
    block = re.search(rf"^{key}:\s*\n((?:\s+-\s+.*\n?)+)", fm, re.M)
    if block:
        return [re.sub(r"^\s+-\s+", "", l).split("#")[0].strip().strip("'\"")
                for l in block.group(1).splitlines() if l.strip()]
    return []


def user_message(draft: Path) -> str:
    harness = Path("plan/HARNESS.md")
    parts = [("Author's verdicts on earlier edits", section(harness, "Naturalness examples")),
             ("Overused patterns", section(harness, "Overused patterns"))]
    overview = Path("wiki/canon/overview.md")
    if overview.is_file():
        parts.append(("Canon overview: register, dialogue layout, orthography",
                      overview.read_text(encoding="utf-8")))
    notes = "\n\n".join(f"# {h}\n\n{t}" for h, t in parts if t)
    return f"{notes}\n\n# CHAPTER\n\n{body(draft)}"


def stem(critic: str) -> str:
    return critic.replace("/", "_").replace("~", "").replace(":", "_")


def call(model: str, key: str, retries: int, system: str, user: str) -> tuple[str, dict]:
    payload = {"model": model, "temperature": 0.3,
               "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    req = urllib.request.Request(API, data=json.dumps(payload).encode(), method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
        "X-Title": "fanfic-wiki critique"})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=900) as resp:
                data = json.load(resp)
            if "error" in data:
                raise RuntimeError(json.dumps(data["error"], ensure_ascii=False))
            return data["choices"][0]["message"]["content"] or "", data.get("usage", {})
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            if e.code in TRANSIENT and attempt < retries:
                time.sleep(10 * (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {e.code}: {detail[:300]}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < retries:
                time.sleep(10 * (attempt + 1))
                continue
            raise RuntimeError(f"network: {e}") from None
    raise RuntimeError("unreachable")


def parse_flags(reply: str) -> list[dict]:
    m = re.search(r"\[.*\]", reply, re.S)
    if not m:
        raise ValueError("no JSON array in the reply")
    items = json.loads(m.group(0))
    return [i for i in items if isinstance(i, dict) and isinstance(i.get("quote"), str)]


def save(out: Path, critic: str, draft: Path, flags: list[dict], extra: dict) -> str:
    flat = norm(body(draft))
    kept = [f for f in flags if norm(f["quote"]) and norm(f["quote"]) in flat]
    record = {"critic": critic, "target": str(draft), "returned": len(flags),
              "dropped_inexact": len(flags) - len(kept), "flags": kept, **extra}
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{stem(critic)}.json").write_text(json.dumps(record, ensure_ascii=False, indent=1),
                                               encoding="utf-8")
    cost = extra.get("usage", {}).get("cost")
    return (f"{critic}: {len(kept)} flag(s), {len(flags) - len(kept)} dropped as inexact"
            + (f", ${cost:.3f}" if cost else ""))


def cmd_prompt(a) -> int:
    a.dir.mkdir(parents=True, exist_ok=True)
    p = a.dir / "prompt.md"
    p.write_text(f"{SYSTEM}\n\n---\n\n{user_message(a.draft)}\n", encoding="utf-8")
    print(f"wrote {p}: give it to a fresh-context subagent; save its JSON reply as "
          f"{a.dir / 'claude.reply.json'} and run `add`")
    return 0


def cmd_add(a) -> int:
    reply = a.reply.read_text(encoding="utf-8")
    try:
        flags = parse_flags(reply)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"{a.critic}: unreadable reply ({e})", file=sys.stderr)
        return 1
    print(save(a.dir, a.critic, a.draft, flags, {}))
    return 0


def cmd_run(a) -> int:
    models = a.model or [c for c in canon_list("critics") if c != CLAUDE]
    if not models:
        print("no OpenRouter critics: `critics:` in CANON.md lists none (or only claude)")
        return 0
    load_env(Path(".env"))
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        usage("OPENROUTER_API_KEY is not set (shell or .env)")
    user = user_message(a.draft)
    failed = 0

    def one(model: str) -> str:
        t0 = time.time()
        reply, u = call(model, key, a.retries, SYSTEM, user)
        return save(a.dir, model, a.draft, parse_flags(reply),
                    {"usage": u, "seconds": round(time.time() - t0)})

    with cf.ThreadPoolExecutor(len(models)) as ex:
        futs = {ex.submit(one, m): m for m in models}
        for f in cf.as_completed(futs):
            try:
                print(f.result(), flush=True)
            except Exception as e:  # noqa: BLE001 — one critic failing must not lose the others
                failed += 1
                print(f"FAIL {futs[f]}: {e}", flush=True)
    return 1 if failed else 0


def sentences(flat: str) -> list[tuple[int, int]]:
    spans, start = [], 0
    for m in re.finditer(r"(?<=[.!?…])\s+", flat):
        spans.append((start, m.start()))
        start = m.end()
    spans.append((start, len(flat)))
    return spans


def cmd_merge(a) -> int:
    flat = norm(body(a.draft))
    spans = sentences(flat)
    by_sentence: dict[int, list[tuple[str, dict]]] = {}
    critics = []
    for p in sorted(a.dir.glob("*.json")):
        if p.name.endswith(".reply.json"):
            continue
        rec = json.loads(p.read_text(encoding="utf-8"))
        critics.append(f"{rec['critic']} {len(rec['flags'])}")
        for f in rec["flags"]:
            i = flat.find(norm(f["quote"]))
            if i < 0:
                continue
            first = next(n for n, (s, e) in enumerate(spans) if e >= i)
            by_sentence.setdefault(first, []).append((rec["critic"], f))
    out = [f"# Outside readers — {a.draft}\n\n", f"Critics: {', '.join(critics) or 'none'}. "
           f"{len(by_sentence)} sentence(s) flagged. Claude decides each; see `naturalize`.\n"]
    for k, n in enumerate(sorted(by_sentence), 1):
        s, e = spans[n]
        out.append(f"\n## {k}. {flat[s:e]}\n")
        for critic, f in by_sentence[n]:
            fix = f" → {f['suggestion']}" if f.get("suggestion") else ""
            out.append(f"- **{critic}:** «{f['quote']}» — {f.get('problem', '')}{fix}\n")
    (a.dir / "merged.md").write_text("".join(out), encoding="utf-8")
    print(f"wrote {a.dir / 'merged.md'}: {len(by_sentence)} sentence(s) from {len(critics)} critic(s)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("prompt", "run", "add", "merge"):
        p = sub.add_parser(name)
        p.add_argument("draft", type=Path)
        p.add_argument("--dir", type=Path, required=True, help="<book>/naturalness/critics/<stem>/")
        if name == "run":
            p.add_argument("--model", nargs="+", help="OpenRouter ids; default: `critics:` in CANON.md")
            p.add_argument("--retries", type=int, default=3)
        if name == "add":
            p.add_argument("--critic", default=CLAUDE)
            p.add_argument("--reply", type=Path, required=True, help="the subagent's JSON reply")
    a = ap.parse_args()
    if not a.draft.is_file():
        usage(f"no such chapter: {a.draft}")
    return {"prompt": cmd_prompt, "run": cmd_run, "add": cmd_add, "merge": cmd_merge}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
