#!/usr/bin/env python3
"""Translate a fic chapter on an OpenRouter model, block for block, into the translate skill's layout.

Standard library only. Run from the project root, after `translation.py prepare` and the glossary gate.

    # the key: OPENROUTER_API_KEY in the shell, or in .env at the project root (gitignored)
    python3 openrouter_translate.py drafts/book-01/ch05-<slug>.md --lang en --model <openrouter id>
    python3 openrouter_translate.py drafts/book-01/ch05-<slug>.md --lang en --blocks 3,7-9   # stale update
    python3 openrouter_translate.py drafts/book-01/ch05-<slug>.md --lang en --dry-run        # print, send nothing
    python3 openrouter_translate.py drafts/book-01/ch05-<slug>.md --lang en --model <id> \
        --out translations/en/book-01/bakeoff/ch05-<model>.md                                 # a bake-off entry
    python3 openrouter_translate.py drafts/book-01/ch05-<slug>.md --lang en --model <strong id> --harvest

What it sends
-------------
The frozen source (`translations/<lang>/[book-NN/]snapshots/chNN-source.md`, written by `prepare`) in
chunks of whole paragraphs, cut at scene breaks and at --chunk-chars. Every item goes out numbered
`[[N]]` with its block number and must come back with the same numbers — a reply that drops, merges
or adds an item is retried once and then refused, so nothing misaligned is written. With each chunk
go `STYLE.md`, `GLOSSARY.md`, `plan/HARNESS.md` → `## Translation` if present, and the last
translated paragraphs before the chunk, for voice continuity. Of `GLOSSARY.md` and `PHRASEBOOK.md`
only the rows whose `Match` occurs in the chunk are sent: a series-long glossary would otherwise
bury the ten entries that matter under four hundred that do not.

Harvest
-------
`--harvest` translates nothing. One request sends the whole chapter to (usually) a strong model and
asks for every name, term, idiom, proverb, slang word, catchphrase and pun the glossary and
phrasebook do not yet cover, each with a proposed rendering. Proposals whose `source` is not an
exact quote from the chapter are dropped and reported. The rest go to
`translations/<lang>/[book-NN/]proposals/chNN.md` with an empty `Keep` column; the user ticks `[x]`
(editing `Target` freely), and `translation.py accept` moves the ticked rows into the glossary or
phrasebook. A cheaper model then translates with those decisions in hand — the expensive judgement
is paid for once and reused in every later chapter.

Scope: chapters under `drafts/` or `raw/` (a `raw/` chapter needs `--source` so `prepare`
freezes a copy under translations/<lang>/…/snapshots/).

Model: --model, else `translation_model:` in CANON.md. No default: pick one on openrouter.ai/models.
Exit codes: 0 written, 1 a request or a reply failed (nothing written), 3 usage error.
"""

from __future__ import annotations

import argparse
import datetime as dt
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
from export_chapter import FRONTMATTER_RE, frontmatter_value, parse  # noqa: E402
from translation import (ROOT, blocks, load_all, source_snapshot, stem_rx,  # noqa: E402
                         target_path)

API = "https://openrouter.ai/api/v1/chat/completions"
TRANSIENT = {429, 500, 502, 503, 504, 520, 522, 524}
ITEM_RE = re.compile(r"^\[\[(\w+)\]\]\s?(.*)$")

SYSTEM = """You are a literary translator. Translate a chapter of fiction from {src} into {tgt}.

Rules, in order of priority:
1. Meaning is untouchable: same events, facts, order and speaker intent. Add nothing, drop nothing.
   A different verb is a different fact.
2. One output item per input item, same [[N]] numbers, same order. Never merge, split, skip or add
   items. Each item is one paragraph; write it on one line after its [[N]] marker.
3. Voice before smoothness. Keep the narrator's irony, rhythm, exclamations, ellipses and scare
   quotes; ironic ceremony about trivial things is the joke — translate it as ceremony.
4. Names and terms exactly as the fixed renderings give them; idioms and phrases from that list by
   default, bent only as far as the sentence needs. Anything not listed: follow STYLE.
5. Proverbs and idioms: the target language's own idiom for the same thought; if none, a plain
   literal rendering that keeps the thought. Never a different proverb.
6. Dialogue punctuation, quotation marks and spelling follow STYLE, not the source's conventions.
7. No notes, glosses, brackets, explanations or commentary anywhere in the output. Output only the
   numbered items.

Items marked [[T]] are the chapter title, [[H]] the chapter heading, and an item starting with
"IMAGE CAPTION:" is a picture's caption — translate it and drop that prefix.
{extra}"""


def refuse_scope(path: Path) -> str | None:
    parts = path.resolve().relative_to(Path.cwd().resolve()).parts if \
        path.resolve().is_relative_to(Path.cwd().resolve()) else ()
    if not parts:
        return f"{path} is outside the project"
    if parts[0] != "drafts" and parts[0] != "raw":
        return f"{path} is not a chapter under drafts/ or raw/"
    return None


def parse_blocks_arg(spec: str, n: int) -> set[int]:
    out: set[int] = set()
    for part in spec.split(","):
        a, _, b = part.strip().partition("-")
        out.update(range(int(a), int(b or a) + 1))
    bad = [i for i in out if not 1 <= i <= n]
    if bad:
        sys.exit(f"--blocks out of range 1–{n}: {sorted(bad)}")
    return out


def read_section(path: Path, heading: str) -> str:
    if not path.is_file():
        return ""
    m = re.search(rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)", path.read_text(encoding="utf-8"),
                  re.M | re.S)
    return m.group(1).strip() if m else ""


def extra_context(lang: str) -> str:
    out = []
    p = ROOT / lang / "STYLE.md"
    if p.is_file():
        out.append(f"\n--- STYLE.md ---\n{p.read_text(encoding='utf-8').strip()}")
    harness = read_section(Path("plan/HARNESS.md"), "Translation")
    if harness:
        out.append(f"\n--- Project translation rules ---\n{harness}")
    return "\n".join(out)


def relevant(entries: list[dict], text: str) -> str:
    """The glossary and phrasebook rows that occur in this text, as a compact table."""
    rows = [e for e in entries if any(stem_rx(m).search(text) for m in e["match"])]
    if not rows:
        return ""
    lines = [f"- {e['source'] or e['match'][0]} → {e['target']}"
             + (f" (never: {', '.join(e['avoid'])})" if e["avoid"] else "")
             + (f" — {e['note']}" if e["note"] else "") for e in rows]
    return "Fixed renderings for this passage (names exact; phrases may bend to fit the sentence):\n" \
        + "\n".join(lines) + "\n\n"


HARVEST = """You prepare a {src} → {tgt} translation of a fiction chapter. Do NOT translate the chapter.

List every item in it that a translator must render the same way every time or that needs a
deliberate decision: character names and nicknames, diminutives, clans and families, places,
institutions, ranks, invented terms, idioms, proverbs, slang, recurring catchphrases, puns and
wordplay, ironic stock phrases. Skip anything the existing glossary and phrasebook already cover.

For each item give the rendering you recommend, following STYLE, and say why in the note — for a
pun or an idiom with no clean equivalent, give the alternatives too.

Reply with a JSON array only, no prose, no code fence. Each element:
{{"source": "<exact quote from the chapter, as it appears>",
  "match": "<comma-separated stems; end a stem with * to cover inflected forms>",
  "target": "<recommended rendering>",
  "avoid": "<comma-separated renderings that must never appear, or empty>",
  "kind": "name|term|place|clan|rank|title|idiom|proverb|slang|catchphrase|pun",
  "note": "<why; alternatives>",
  "block": <the [[N]] number it first occurs in>}}
{extra}"""


def harvest(args, src, snap, model, key, src_lang) -> int:
    entries = load_all(args.lang)
    known = "\n".join(f"- {e['source'] or e['match'][0]} → {e['target']}" for e in entries)
    system = HARVEST.format(src=src_lang, tgt=args.lang, extra=extra_context(args.lang)
                            + (f"\n\n--- Already decided ---\n{known}" if known else ""))
    items = [(str(n), b[1]) for n, b in enumerate(src, 1) if b[0] == "p"]
    user = "\n\n".join(f"[[{k}]] {t}" for k, t in items)
    if args.dry_run:
        print(f"=== system ===\n{system}\n\n=== chapter: {len(items)} paragraphs ===\n{user[:1500]}…")
        return 0
    try:
        reply, u = call(model, key, system, user)
    except RuntimeError as e:
        print(f"harvest failed: {e}", file=sys.stderr)
        return 1
    text = re.sub(r"^```\w*\s*|\s*```$", "", reply.strip())
    try:
        found = json.loads(text)
        assert isinstance(found, list)
    except (ValueError, AssertionError):
        print(f"reply is not a JSON array; nothing written. First 500 chars:\n{reply[:500]}",
              file=sys.stderr)
        return 1
    chapter = " ".join(t for _, t in items)
    kept, dropped = [], []
    for f in found:
        s = str(f.get("source", "")).strip()
        if not s or re.sub(r"\s+", " ", s) not in chapter:
            dropped.append(s or "(empty)")
            continue
        if not f.get("match"):
            f["match"] = s
        kept.append(f)
    out = args.out or (target_path(args.draft, args.lang).parent / "proposals"
                       / f"{re.match(r'(ch\d+)', args.draft.name).group(1)}.md")
    cell = lambda v: str(v or "").replace("|", "/").replace("\n", " ").strip()
    lines = ["---", "type: translation-proposals", f"source: {args.draft}", f"lang: {args.lang}",
             f"harvested_by: openrouter:{model}", f"date: {dt.date.today().isoformat()}", "---", "",
             f"# Proposals — {args.draft.name} → {args.lang}", "",
             "Tick `[x]` in Keep to accept a row (edit Target freely), then run "
             "`translation.py accept` on this file. Unticked rows are ignored.", "",
             "| Keep | Block | Kind | Source | Match | Target | Avoid | Note |",
             "|---|---|---|---|---|---|---|---|"]
    for f in sorted(kept, key=lambda f: (str(f.get("kind", "")), int(f.get("block") or 0))):
        lines.append("| [ ] | " + " | ".join(cell(f.get(c)) for c in
                     ("block", "kind", "source", "match", "target", "avoid", "note")) + " |")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}: {len(kept)} proposal(s) by {model}")
    if dropped:
        print(f"dropped {len(dropped)} not quoted exactly from the chapter: "
              + "; ".join(d[:50] for d in dropped[:8]))
    print(f"usage: prompt {u.get('prompt_tokens', 0)} tokens, completion {u.get('completion_tokens', 0)}"
          + (f", cost ${u['cost']:.4f}" if u.get("cost") else ""))
    return 0


def canon_value(key: str) -> str:
    p = Path("CANON.md")
    if not p.is_file():
        return ""
    m = FRONTMATTER_RE.match(p.read_text(encoding="utf-8"))
    return frontmatter_value(m.group(1), key) if m else ""


# --------------------------------------------------------------------------- #
# Chunks and the API
# --------------------------------------------------------------------------- #

def items_of(src: list[tuple], wanted: set[int], title: str, heading: str) -> list[list[tuple]]:
    """Chunks of (key, text): whole paragraphs, cut at scene breaks and at the size limit."""
    chunks, cur, size = [], [], 0
    head = [(k, v) for k, v in (("T", title), ("H", heading)) if v and ("T" in wanted or not wanted)]
    for n, b in enumerate(src, 1):
        if b[0] == "break":
            if cur:
                chunks.append(cur)
            cur, size = [], 0
            continue
        if wanted and n not in wanted:
            continue
        text = b[1] if b[0] == "p" else f"IMAGE CAPTION: {b[2]}"
        if cur and size + len(text) > ARGS.chunk_chars:
            chunks.append(cur)
            cur, size = [], 0
        cur.append((str(n), text))
        size += len(text)
    if cur:
        chunks.append(cur)
    if head:
        chunks = [head + chunks[0]] + chunks[1:] if chunks else [head]
    return chunks


def call(model: str, key: str, system: str, user: str) -> tuple[str, dict]:
    body = {"model": model, "temperature": ARGS.temperature,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    req = urllib.request.Request(API, data=json.dumps(body).encode(), method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
        "X-Title": "fanfic-wiki translate"})
    for attempt in range(ARGS.retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                data = json.load(resp)
            if "error" in data:
                raise RuntimeError(json.dumps(data["error"], ensure_ascii=False))
            return data["choices"][0]["message"]["content"] or "", data.get("usage", {})
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            if e.code in TRANSIENT and attempt < ARGS.retries:
                print(f"  HTTP {e.code}, retrying in {5 * (attempt + 1)}s", file=sys.stderr)
                time.sleep(5 * (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {e.code}: {detail}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < ARGS.retries:
                time.sleep(5 * (attempt + 1))
                continue
            raise RuntimeError(f"network: {e}") from None
    raise RuntimeError("unreachable")


def parse_reply(reply: str, keys: list[str]) -> dict[str, str] | str:
    got: dict[str, str] = {}
    last = None
    for line in reply.strip().splitlines():
        m = ITEM_RE.match(line.strip())
        if m:
            last = m.group(1)
            if last in got:
                return f"item [[{last}]] appears twice"
            got[last] = m.group(2).strip()
        elif line.strip() and last:  # a paragraph the model wrapped onto a second line
            got[last] += " " + line.strip()
    if list(got) != keys:
        missing, extra = [k for k in keys if k not in got], [k for k in got if k not in keys]
        return f"items do not match — missing {missing or 'none'}, unexpected {extra or 'none'}"
    empty = [k for k, v in got.items() if not v]
    return f"empty items {empty}" if empty else got


# --------------------------------------------------------------------------- #
# Writing
# --------------------------------------------------------------------------- #

def existing_body(path: Path) -> tuple[str, str, list[str]]:
    """An existing translation as (frontmatter, heading line, raw block texts in order)."""
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    front, body = (m.group(1), text[m.end():]) if m else ("", text)
    raw = [b.strip() for b in re.split(r"\n[ \t]*\n", body) if b.strip()]
    heading = raw.pop(0) if raw and raw[0].startswith("#") else ""
    return front, heading, raw


def render(src: list[tuple], done: dict[str, str], out: Path, old: list[str] | None) -> list[str]:
    lines = []
    for n, b in enumerate(src, 1):
        k = str(n)
        if b[0] == "break":
            lines.append("* * *")
        elif k not in done:
            lines.append(old[n - 1])
        elif b[0] == "image":
            rel = os.path.relpath(b[1], out.parent).replace(os.sep, "/")
            lines.append(f"![{done[k]}]({rel})")
        else:
            lines.append(done[k])
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("draft", type=Path, help="the chapter draft under drafts/ (prepare it first)")
    ap.add_argument("--lang", required=True, help="target language code, e.g. en")
    ap.add_argument("--source-language", help="default: CANON.md output_language")
    ap.add_argument("--model", help="OpenRouter model id; default: CANON.md translation_model")
    ap.add_argument("--blocks", help="only these source blocks, e.g. 3,7-9 (a stale update); "
                                     "T = retranslate the title and heading too")
    ap.add_argument("--chunk-chars", type=int, default=6000, help="source characters per request")
    ap.add_argument("--context", type=int, default=3, help="translated paragraphs sent before a chunk")
    ap.add_argument("--temperature", type=float, default=0.3)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--dry-run", action="store_true", help="print the requests, send nothing")
    ap.add_argument("--out", type=Path, help="write here instead of the chapter's translation path "
                                             "(a bake-off entry; with --harvest, the proposals file)")
    ap.add_argument("--harvest", action="store_true",
                    help="translate nothing: propose glossary and phrasebook entries for this chapter")
    global ARGS
    ARGS = args = ap.parse_args()

    why = refuse_scope(args.draft)
    if why:
        print(f"refused: {why}", file=sys.stderr)
        return 3
    snap = source_snapshot(args.draft, args.lang)
    out = args.out or target_path(args.draft, args.lang)
    if not snap.is_file():
        print(f"no frozen source {snap} — run translation.py prepare first", file=sys.stderr)
        return 3
    model = args.model or canon_value("translation_model")
    if not model and not args.dry_run:
        print("no model: pass --model or set translation_model in CANON.md", file=sys.stderr)
        return 3
    src_lang = args.source_language or canon_value("output_language") or "the source language"

    src, doc = blocks(snap), parse(snap)
    for n, b in enumerate(src):  # carry image alt text: blocks() keeps only the path
        if b[0] == "image":
            alt = next(x[2] for x in parse(snap)["blocks"] if x[0] == "image" and x[1] == b[1])
            src[n] = ("image", b[1], alt)

    key = ""
    if not args.dry_run:
        load_env()
        key = os.environ.get("OPENROUTER_API_KEY", "")
        if not key:
            print("OPENROUTER_API_KEY is not set (shell or .env at the project root)", file=sys.stderr)
            return 3
    if args.harvest:
        return harvest(args, src, snap, model, key, src_lang)

    wanted: set[int] = set()
    old = None
    if args.blocks:
        if not out.is_file():
            print(f"--blocks updates an existing translation; {out} does not exist", file=sys.stderr)
            return 3
        spec = [p for p in args.blocks.split(",") if p.strip().upper() != "T"]
        wanted = parse_blocks_arg(",".join(spec), len(src)) if spec else set()
        if "T" in args.blocks.upper().split(","):
            wanted.add("T")
        front_old, heading_old, old = existing_body(out)
        if len(old) != len(src):
            print(f"{out} has {len(old)} blocks, the frozen source {len(src)} — run translation.py "
                  f"check and fix the alignment first", file=sys.stderr)
            return 3

    chunks = items_of(src, wanted, doc["title"], doc["heading"])
    system = SYSTEM.format(src=src_lang, tgt=args.lang, extra=extra_context(args.lang))
    entries = load_all(args.lang)

    done: dict[str, str] = {}
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0}
    for i, chunk in enumerate(chunks, 1):
        first = next((int(k) for k, _ in chunk if k.isdigit()), 1)
        prev = [done[str(n)] for n in range(max(1, first - args.context), first) if str(n) in done]
        if not prev and old:
            prev = [old[n - 1] for n in range(max(1, first - args.context), first)
                    if src[n - 1][0] == "p"]
        user = ""
        if prev:
            user += "Already translated, for continuity (do not output):\n" + "\n".join(prev) + "\n\n"
        user += relevant(entries, " ".join(t for _, t in chunk))
        user += "Translate these items:\n\n" + "\n\n".join(f"[[{k}]] {t}" for k, t in chunk)
        keys = [k for k, _ in chunk]
        if args.dry_run:
            if i == 1:
                print(f"=== system ===\n{system}\n")
            print(f"=== request {i}/{len(chunks)}: items {keys[0]}–{keys[-1]} ===\n{user}\n")
            continue
        for attempt in (1, 2):
            try:
                reply, u = call(model, key, system, user)
            except RuntimeError as e:
                print(f"request {i}/{len(chunks)} failed: {e}\nnothing written", file=sys.stderr)
                return 1
            for f in usage:
                usage[f] += u.get(f, 0) or 0
            got = parse_reply(reply, keys)
            if isinstance(got, dict):
                done.update(got)
                break
            print(f"  chunk {i}: {got}" + (" — retrying" if attempt == 1 else ""), file=sys.stderr)
        else:
            print(f"chunk {i} misaligned twice; nothing written", file=sys.stderr)
            return 1
        print(f"  chunk {i}/{len(chunks)}: {len(keys)} items")

    if args.dry_run:
        print(f"dry run: {len(chunks)} request(s), nothing sent, nothing written")
        return 0

    lines = render(src, done, out, old)
    if old is not None:
        front, heading = front_old, (f"## {done['H']}" if "H" in done else heading_old)
        if "T" in done:
            front = re.sub(r"^title:.*$", f"title: {json.dumps(done['T'], ensure_ascii=False)}",
                           front, flags=re.M)
    else:
        front = "\n".join([
            f"title: {json.dumps(done.get('T', ''), ensure_ascii=False)}",
            f"source: {args.draft}", f"source_snapshot: {snap}", f"lang: {args.lang}",
            f"translated_by: openrouter:{model}", f"date: {dt.date.today().isoformat()}"])
        heading = f"## {done['H']}" if "H" in done else ""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("---\n" + front + "\n---\n\n" + (heading + "\n\n" if heading else "")
                   + "\n\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}: {len(done)} item(s) translated by {model}")
    print(f"usage: prompt {usage['prompt_tokens']} tokens, completion {usage['completion_tokens']}"
          + (f", cost ${usage['cost']:.4f}" if usage["cost"] else ""))
    print(f"next: python3 <scripts>/translation.py check {out}")
    return 0


ARGS: argparse.Namespace

if __name__ == "__main__":
    sys.exit(main())
