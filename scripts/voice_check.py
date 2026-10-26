#!/usr/bin/env python3
"""Voice pass: a fresh-context reader checks every line of dialogue against the speakers' voice cards.

Standard library only. Run from the project root, in `write-chapter` §7 — after the user's
revisions and before `reconcile`.

    python3 voice_check.py prompt <draft> --dir <out>
    python3 voice_check.py add    <draft> --dir <out> --reply <reply.json>
    python3 voice_check.py apply  <draft> --dir <out> [--skip 2,5]

`<out>` is `<book>/voices/<chapter stem>/`.

Why a separate pass
-------------------
The drafter writes dialogue against the cards (`write-chapter` §4), and the user's revisions then
rewrite lines one at a time, each judged by its sense. On a real run the user asked, in three
chapters running, to "run every line through the voice cards", and each time the pass found lines
that had drifted: a character speaking in another's clipped manner, a title shortened that the
card always gives in full, a tic taken from a profile line the canon card contradicts. The check
is mechanical enough to run every time and needs the cards, not the conversation, so a subagent
does it and the session only sees the fixes.

What the reader gets
--------------------
`prompt.md`: the task, the list of voice cards and profiles under `wiki/`, and every line of
dialogue numbered, with the paragraph before it for attribution. The reader opens the cards itself.
It returns one JSON object: {speakers: [{who, card}], checked: n, flags: [{n, quote, who, card,
rule, problem, fix}]}, where `fix` replaces `quote` in the draft.

What comes back
---------------
`add` keeps a flag only if its quote occurs exactly once in the draft and its fix differs from it;
writes `<out>/flags.json` and `<out>/report.md` (before → after, the card's rule). `apply` makes
the replacements, skipping the numbers given with `--skip`, and reports any quote that no longer
occurs once (the draft changed since `add`).

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

# a line of dialogue opens with a dash (markdown-escaped or not) or an opening quotation mark
DIALOGUE_RE = re.compile(r"^(\\?[-–—]\s|[«“„\"])")

TASK = """You check the dialogue of one drafted chapter of a fan continuation against the voice \
cards of the people who speak. You are not an editor of plot, logic or narration: only how each \
line sounds in its speaker's mouth.

How to work:
1. For each numbered line below, decide who speaks it (the paragraph before it and the line's \
own tag say). Lines the narrator speaks aloud count: the narrator has a card too. The whole chapter \
is at `{draft}`: open it when the paragraph before is not enough.
2. For each speaker, open their voice card from the list below — a card under `wiki/canon/voices/` \
first, then one under `wiki/fanon/`. Use a profile's voice section only where there is no card. \
Where a profile and a card disagree on how someone talks, the card is right: say so in `problem`.
3. Check every line of theirs against the card: vocabulary and register, address forms and \
titles (as the card gives them, in full where it does), tics and verbal habits (at most three \
per character per chapter, not all in every scene), sentence length and rhythm, the card's \
"would never say" list, and the verbatim lines as a model of manner. A line that sounds like \
another character's card is a flag. Where a card's rule depends on the place or the company \
(titles at the gate but names in the field, formal before elders), find in the chapter where and \
before whom the line is said before you flag it.
4. For each line that fails, write the smallest fix that makes it sound like the speaker. Keep \
what the line says and does in the scene: the information, the answer, the joke, its length \
within a few words. Keep the chapter's orthography and dialogue punctuation exactly as they are. \
Never change the meaning.

Not a flag: a line that fits the card but could be better written; narration; a line whose \
speaker is not in the list of cards (name them in `speakers` with card "none").

Answer with one JSON object only, nothing before or after:
{"speakers": [{"who": "<name>", "card": "<path or none>"}],
 "checked": <number of lines checked>,
 "flags": [{"n": <line number>, "quote": "<exact text from the line, the part to replace>",
   "who": "<speaker>", "card": "<card path>",
   "rule": "<the card's words this line breaks, copied>",
   "problem": "<what is wrong, one line, in the chapter's language>",
   "fix": "<replacement for quote>"}]}
`quote` is copied character for character from the line (it may be the whole line or a part); \
`fix` replaces exactly that text."""


def usage(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(3)


def body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if m:
        text = text[m.end():]
    return "\n".join(l for l in text.splitlines() if not IMAGE_RE.match(l.strip()))


def dialogue(text: str) -> list[tuple[str, str]]:
    """(line, the paragraph before it) for every paragraph that opens as speech."""
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    return [(p, paras[i - 1] if i else "") for i, p in enumerate(paras)
            if DIALOGUE_RE.match(p) and not p.startswith("#")]


def cards() -> list[str]:
    out = sorted(str(p) for p in Path("wiki/canon/voices").glob("*.md"))
    out += sorted(str(p) for p in Path("wiki/fanon").rglob("voices/*.md"))
    out += sorted(f"{p} (profile)" for p in Path("wiki/fanon").rglob("characters/*.md"))
    return out


def cmd_prompt(a) -> int:
    lines = dialogue(body(a.draft))
    if not lines:
        usage(f"no dialogue found in {a.draft}")
    a.dir.mkdir(parents=True, exist_ok=True)
    out = [TASK.replace("{draft}", str(a.draft)), "\n\n---\n\n# Voice cards and profiles\n\n"]
    out += [f"- `{c}`\n" for c in cards()] or ["(none found under wiki/)\n"]
    out.append(f"\n# Dialogue of {a.draft}\n")
    for n, (line, before) in enumerate(lines, 1):
        ctx = before if len(before) <= 300 else "…" + before[-300:]
        out.append(f"\n## {n}\n\nBefore: {ctx or '(chapter start)'}\n\n{line}\n")
    p = a.dir / "prompt.md"
    p.write_text("".join(out), encoding="utf-8")
    print(f"wrote {p}: {len(lines)} line(s); give it to a fresh-context subagent with file tools, as its "
          f"whole task; save its JSON reply as {a.dir / 'reply.json'} and run `add`")
    return 0


def cmd_add(a) -> int:
    text = a.draft.read_text(encoding="utf-8")
    reply = a.reply.read_text(encoding="utf-8")
    m = re.search(r"\{.*\}", reply, re.S)
    try:
        rec = json.loads(m.group(0)) if m else None
    except json.JSONDecodeError:
        rec = None
    if not isinstance(rec, dict):
        print(f"unreadable reply {a.reply}", file=sys.stderr)
        return 1
    kept, dropped = [], 0
    for f in rec.get("flags") or []:
        if not isinstance(f, dict):
            continue
        q, fix = str(f.get("quote", "")), str(f.get("fix", ""))
        if not q or q == fix or text.count(q) != 1:
            dropped += 1
            continue
        kept.append(f)
    kept.sort(key=lambda f: text.index(f["quote"]))
    checked = rec.get("checked", "?")
    (a.dir / "flags.json").write_text(json.dumps(
        {"draft": str(a.draft), "checked": checked, "speakers": rec.get("speakers", []),
         "dropped_inexact": dropped, "flags": kept}, ensure_ascii=False, indent=1), encoding="utf-8")
    out = [f"# Voice pass — {a.draft}\n\n{checked} line(s) checked, {len(kept)} to fix, "
           f"{dropped} dropped (quote not found once in the draft).\n"]
    for k, f in enumerate(kept, 1):
        out.append(f"\n## {k}. {f.get('who', '?')} — {f.get('problem', '')}\n\n"
                   f"- before: «{f['quote']}»\n- after: «{f['fix']}»\n"
                   f"- card `{f.get('card', '?')}`: «{f.get('rule', '')}»\n")
    (a.dir / "report.md").write_text("".join(out), encoding="utf-8")
    print(f"wrote {a.dir / 'report.md'}: {checked} checked, {len(kept)} to fix, {dropped} inexact dropped")
    return 0


def cmd_apply(a) -> int:
    rec = json.loads((a.dir / "flags.json").read_text(encoding="utf-8"))
    skip = {int(x) for x in a.skip.split(",") if x.strip()} if a.skip else set()
    text = a.draft.read_text(encoding="utf-8")
    done, failed = [], []
    for k, f in enumerate(rec["flags"], 1):
        if k in skip:
            continue
        if text.count(f["quote"]) != 1:
            failed.append(k)
            continue
        text = text.replace(f["quote"], f["fix"])
        done.append(k)
    a.draft.write_text(text, encoding="utf-8")
    print(f"applied {len(done)}: {done or '-'}; skipped {sorted(skip) or '-'}; "
          f"not found once (draft changed): {failed or '-'}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("prompt", "add", "apply"):
        p = sub.add_parser(name)
        p.add_argument("draft", type=Path)
        p.add_argument("--dir", type=Path, required=True, help="<book>/voices/<chapter stem>/")
        if name == "add":
            p.add_argument("--reply", type=Path, required=True)
        if name == "apply":
            p.add_argument("--skip", help="comma-separated report numbers to leave as they are")
    a = ap.parse_args()
    if not a.draft.is_file():
        usage(f"no such file: {a.draft}")
    return {"prompt": cmd_prompt, "add": cmd_add, "apply": cmd_apply}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
