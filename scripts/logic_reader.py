#!/usr/bin/env python3
"""Logic and canon reader: a fresh-context Claude asks the questions an attentive fan would ask.

Standard library only. Run from the project root, in `write-chapter` at the beat gate (target =
the beat file) and in §5 before `naturalize` (target = the draft).

    python3 logic_reader.py prompt <target> --stage beats|draft --dir <out> [--beats <beat file>]
    python3 logic_reader.py add    <target> --dir <out> --reply <out>/reply.json
    python3 logic_reader.py eval   <cases.json> --runs <dir> [--baseline <dir>]

`<out>` is `<book>/logic/<chapter stem>-<stage>/`.

Why a separate reader
---------------------
`naturalize` and its outside readers judge sentences; they are not given the source and cannot
tell a canon slip from a true fact. Most of what a user corrects in a beat card or a first draft is
of another kind: a fact `raw/` does not support, a detail with no origin, a character who knows
what he could not, a plan with a shorter road the character would obviously take. The drafter
checks these against its own beliefs; a reader with fresh context and `raw/` at hand does not
share them.

What the reader gets
--------------------
`prompt.md`: the task, the target text, and where to look — `raw/`, `wiki/`, `drafts/continuity.md`,
the fic's earlier chapters. The reader is a subagent with file tools; it is given `prompt.md` as its
whole task and nothing of the drafting conversation. It returns a JSON array of
{quote, kind, question, evidence: [{file, quote}], certainty}.

What comes back
---------------
`add` keeps a flag only if its quote is an exact substring of the target, and marks each piece of
evidence verified or not by searching the cited file for the quoted words. A `canon` flag whose
evidence does not verify is kept but marked — the reader may have misremembered, exactly as the
drafter did. Writes `<out>/flags.json` and `<out>/report.md`.

`eval` scores runs against a case file of real user objections (anchor quotes in the same
targets): a flag hits an objection when its quote falls in the same sentence as the anchor.
It prints recall by kind and lists unmatched flags for a human to judge — an unmatched flag is not
necessarily noise.

Exit codes: 0 ok, 1 unreadable reply, 3 usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_chapter import FRONTMATTER_RE, IMAGE_RE  # noqa: E402

KINDS = ("canon", "logic", "knows", "motive", "invented", "unneeded")

TASK = """You are a reader who knows the source canon well — you can look anything up — reading \
{what} of a fan continuation of that source. You are not an editor of style. You ask the questions \
an attentive fan asks when something does not add up, before the author's readers ask them.

Look for six kinds of trouble:
- canon: a fact about the world, a character or past events that the source contradicts or does \
not support. Look it up; quote the line. A hedge in the source ("примерно", "по слухам", \
"кажется") that became a flat fact counts.
- logic: cause and effect do not hold. Someone does what their situation makes impossible or \
pointless (a guard who slept through the theft \
describes the thief's face); an action has no purpose; a conclusion does not \
follow; an object behaves unlike its material.
- knows: someone knows what they could not have learned on the page or in canon; the world knows \
the hero's private discovery; locals use the narrator's words for things.
- motive: a character acts against their recorded character or interest, or takes a long road when \
an obvious short one exists (bribes a clerk for a date posted on \
the public board); a clever character is \
written as naive.
- invented: a specific — a number, a price, a fee, a custom, an institution, a name — that neither \
the source nor the wiki nor the fic's earlier chapters give. Ask where it came from.
- unneeded: a sentence that explains what the story does not need explained.

How to work:
1. Read the target. List to yourself every claim about how the world works and every specific.
2. For each, search before judging: `{raw}` (the source; grep word stems in the source's language, \
several spellings), `wiki/canon/`, `wiki/fanon/`, `drafts/continuity.md`, and the fic's earlier \
chapters under `{drafts}`. The fic's earlier chapters are canon for this fic. A claim that is \
supported is not a flag. A citation in the target ([src: …]) is a claim too: open it and check \
that the line says what the target says it says.
3. For each character's choice, ask what they want and whether a simpler way was open to them.
4. Keep only what you would put to the author as a question.
{extra}
Do NOT flag: word choice, rhythm, clumsy phrasing, punctuation, jokes that fall flat, the \
narrator's ironic pomposity. Another reader handles those.

Ten precise flags beat thirty doubtful ones. At most 20. Write `question` in the target's \
language, the way a reader would ask it aloud: «зачем…, если можно…?», «откуда он знает…?», \
«в каноне иначе: …». Evidence quotes are copied character for character from the file they cite; \
give the file path relative to the project root.

Answer with a JSON array only, nothing before or after:
[{{"quote": "<exact quote from the target, 3-25 words>",
   "kind": "canon|logic|knows|motive|invented|unneeded",
   "question": "<the question, one or two lines>",
   "evidence": [{{"file": "<path>", "quote": "<exact words from that file>"}}],
   "certainty": "high|medium"}}]
`evidence` may be empty for logic, motive and unneeded. The quote must match the target \
character for character."""

EXTRA = {
    "beats": "The target is a beat file: a short retelling, questions for the author with \
recommended answers, and one card per scene with its canon and fanon dependencies. Recommended \
answers and dependencies are claims to check like any other.\n",
    "draft": "The target is a drafted chapter. Its beat file{beats} records what the drafter meant \
and what the author already decided; a decision recorded there is not a flag unless canon \
contradicts it.\n",
}


def usage(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(3)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("ё", "е").replace("Ё", "Е")).strip()


def body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if m:
        text = text[m.end():]
    return "\n".join(l for l in text.splitlines() if not IMAGE_RE.match(l.strip())).strip()


def raw_dir() -> str:
    return "raw/" if Path("raw").is_dir() else "<source directory>"


def cmd_prompt(a) -> int:
    parent = a.target.parent.parent if a.target.parent.name == "snapshots" else a.target.parent
    drafts = f"{parent}/" if a.stage == "draft" else "drafts/"
    beats = f" (`{a.beats}`)" if a.beats else ""
    what = "a beat card for one chapter" if a.stage == "beats" else "one drafted chapter"
    task = TASK.format(what=what, raw=raw_dir(), drafts=drafts,
                       extra=EXTRA[a.stage].format(beats=beats))
    a.dir.mkdir(parents=True, exist_ok=True)
    p = a.dir / "prompt.md"
    p.write_text(f"{task}\n\n---\n\n# TARGET: {a.target}\n\n{body(a.target)}\n", encoding="utf-8")
    print(f"wrote {p}: give it to a fresh-context subagent with file tools, as its whole task; "
          f"save its JSON reply as {a.dir / 'reply.json'} and run `add`")
    return 0


def parse(reply: str) -> list[dict]:
    m = re.search(r"\[.*\]", reply, re.S)
    if not m:
        raise ValueError("no JSON array in the reply")
    return [i for i in json.loads(m.group(0)) if isinstance(i, dict) and isinstance(i.get("quote"), str)]


def verify(ev: dict) -> bool:
    f, q = Path(str(ev.get("file", "")).split("#")[0]), norm(str(ev.get("quote", "")))
    if not q or not f.is_file():
        return False
    return q in norm(f.read_text(encoding="utf-8"))


def cmd_add(a) -> int:
    try:
        flags = parse(a.reply.read_text(encoding="utf-8"))
    except (ValueError, json.JSONDecodeError) as e:
        print(f"unreadable reply ({e})", file=sys.stderr)
        return 1
    flat = norm(body(a.target))
    kept = []
    for f in flags:
        if not norm(f["quote"]) or norm(f["quote"]) not in flat:
            continue
        f["kind"] = f.get("kind") if f.get("kind") in KINDS else "logic"
        f["evidence"] = [dict(e, verified=verify(e)) for e in f.get("evidence") or [] if isinstance(e, dict)]
        f["unverified"] = f["kind"] == "canon" and not any(e["verified"] for e in f["evidence"])
        kept.append(f)
    rec = {"target": str(a.target), "returned": len(flags), "dropped_inexact": len(flags) - len(kept),
           "flags": kept}
    (a.dir / "flags.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    out = [f"# Logic and canon reader — {a.target}\n\n{len(kept)} flag(s), "
           f"{len(flags) - len(kept)} dropped as inexact quotes.\n"]
    for k, f in enumerate(kept, 1):
        mark = " — evidence not found in the cited file" if f["unverified"] else ""
        out.append(f"\n## {k}. [{f['kind']}] «{f['quote']}»{mark}\n\n{f.get('question', '')}\n")
        for e in f["evidence"]:
            out.append(f"\n- {'✓' if e['verified'] else '✗'} `{e.get('file')}`: «{e.get('quote')}»")
        out.append("\n")
    (a.dir / "report.md").write_text("".join(out), encoding="utf-8")
    unver = sum(f["unverified"] for f in kept)
    print(f"wrote {a.dir / 'report.md'}: {len(kept)} flag(s), {len(flags) - len(kept)} inexact dropped, "
          f"{unver} canon flag(s) with unverified evidence")
    return 0


def sentence_span(flat: str, i: int, j: int) -> tuple[int, int]:
    """Widen [i, j) to the sentence (or markdown line) around it."""
    s = max(flat.rfind(c, 0, i) for c in ".!?…\n") + 1
    ends = [k for k in (flat.find(c, j) for c in ".!?…\n") if k >= 0]
    return s, (min(ends) + 1 if ends else len(flat))


def locate(flat: str, quote: str) -> tuple[int, int] | None:
    q = norm(quote)
    i = flat.find(q)
    return (i, i + len(q)) if q and i >= 0 else None


def hits(flat: str, anchor: str, quotes: list[str]) -> list[int]:
    a = locate(flat, anchor)
    if not a:
        return []
    s, e = sentence_span(flat, *a)
    out = []
    for n, q in enumerate(quotes):
        b = locate(flat, q)
        if b and b[0] < e and b[1] > s:
            out.append(n)
    return out


def cmd_eval(a) -> int:
    cases = json.loads(a.cases.read_text(encoding="utf-8"))["cases"]
    total, found, base_found = {}, {}, {}
    unmatched_all = 0
    flags_all = 0
    lines = []
    for c in cases:
        run = a.runs / c["id"]
        tgt = run / "target.md"
        rec_p = run / "flags.json"
        if not tgt.is_file() or not rec_p.is_file():
            lines.append(f"\n{c['id']}: no run ({run})")
            continue
        # anchors and flags are located in the same text the reader saw
        flat = norm(tgt.read_text(encoding="utf-8"))
        flags = json.loads(rec_p.read_text(encoding="utf-8"))["flags"]
        quotes = [f["quote"] for f in flags]
        base_quotes = []
        if a.baseline and (a.baseline / f"{c['id']}.json").is_file():
            base_quotes = json.loads((a.baseline / f"{c['id']}.json").read_text(encoding="utf-8"))
        matched = set()
        flags_all += len(flags)
        lines.append(f"\n## {c['id']} — {len(flags)} flag(s)")
        for it in c["items"]:
            k = it["kind"]
            total[k] = total.get(k, 0) + 1
            if not locate(flat, it["anchor"]):
                lines.append(f"  ! {it['id']}: anchor not in target")
                continue
            h = hits(flat, it["anchor"], quotes)
            bh = hits(flat, it["anchor"], base_quotes)
            matched.update(h)
            if h:
                found[k] = found.get(k, 0) + 1
            if bh:
                base_found[k] = base_found.get(k, 0) + 1
            mark = "HIT " if h else "miss"
            lines.append(f"  {mark} {it['id']} [{k}] «{it['anchor']}»" + ("  (baseline hit)" if bh else ""))
            for n in h:
                lines.append(f"       ↳ [{flags[n]['kind']}] {flags[n].get('question', '')}")
        rest = [f for n, f in enumerate(flags) if n not in matched]
        unmatched_all += len(rest)
        for f in rest:
            lines.append(f"  ?    [{f['kind']}] «{f['quote']}» — {f.get('question', '')}")
    n_total, n_found, n_base = sum(total.values()), sum(found.values()), sum(base_found.values())
    print(f"recall {n_found}/{n_total}" + (f" (baseline {n_base}/{n_total})" if a.baseline else "")
          + f"; flags {flags_all}, unmatched {unmatched_all} (judge by hand)")
    for k in KINDS:
        if k in total:
            b = f", baseline {base_found.get(k, 0)}" if a.baseline else ""
            print(f"  {k:9} {found.get(k, 0)}/{total[k]}{b}")
    print("\n".join(lines))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prompt")
    p.add_argument("target", type=Path)
    p.add_argument("--stage", choices=("beats", "draft"), required=True)
    p.add_argument("--dir", type=Path, required=True, help="<book>/logic/<stem>-<stage>/")
    p.add_argument("--beats", type=Path, help="draft stage: the chapter's beat file")
    p = sub.add_parser("add")
    p.add_argument("target", type=Path)
    p.add_argument("--dir", type=Path, required=True)
    p.add_argument("--reply", type=Path, required=True, help="the subagent's JSON reply")
    p = sub.add_parser("eval")
    p.add_argument("cases", type=Path)
    p.add_argument("--runs", type=Path, required=True, help="one dir per case id: target.md, flags.json")
    p.add_argument("--baseline", type=Path, help="<case id>.json: list of quotes the old pipeline flagged")
    a = ap.parse_args()
    if a.cmd in ("prompt", "add") and not a.target.is_file():
        usage(f"no such file: {a.target}")
    return {"prompt": cmd_prompt, "add": cmd_add, "eval": cmd_eval}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
