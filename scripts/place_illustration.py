#!/usr/bin/env python3
"""Put an approved chapter illustration into the draft, right after the moment it shows.

Standard library only.

    python3 place_illustration.py <draft.md> --image <path> --anchor "<verbatim quote>" \
        [--caption "<alt text>"] [--dry-run]

Why this exists
---------------
`illustrate` picks each chapter's moment with a short verbatim anchor quote. The quote is
also a locator: the image belongs after the paragraph that contains it. Doing that by hand
is where it goes wrong — an anchor typed with the chapter's markdown escapes (`\\-`) or
without them, a second insert on re-approval, an image path that renders from one folder
and not another. The script makes placement checkable: the anchor is found exactly once
or nothing is written.

Behaviour
- Matching ignores markdown backslash escapes and collapses whitespace, both sides.
- Anchor found 0 or 2+ times → exit 2, nothing written; the message says which.
- Any earlier image line for this chapter (the path in frontmatter `illustration:`, or the
  same `--image`) is removed first, so re-approval moves the picture instead of adding one.
- The link is written relative to the draft, so it renders in any markdown viewer.
- Frontmatter gets `illustration: <path relative to the project root>` (the cwd).

- A published chapter (frontmatter `published:`) is refused: readers have its text, and a
  picture added later is a change `publish` has to make, not a silent edit.

Exit: 0 placed (or unchanged), 2 anchor not found / ambiguous, 3 bad path, 4 published.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"\\(.)", r"\1", text)).strip()


def split_frontmatter(text: str) -> tuple[str, str]:
    m = FRONTMATTER_RE.match(text)
    return (m.group(1), text[m.end():]) if m else ("", text)


def paragraph_spans(body: str) -> list[tuple[int, int]]:
    """(start, end) offsets of each run of non-blank lines; end excludes the trailing newline."""
    spans, start, pos = [], None, 0
    for line in body.splitlines(keepends=True):
        blank = not line.strip()
        if not blank and start is None:
            start = pos
        if blank and start is not None:
            spans.append((start, pos - 1))
            start = None
        pos += len(line)
    if start is not None:
        spans.append((start, len(body.rstrip("\n"))))
    return spans


def set_key(front: str, key: str, value: str) -> str:
    line = f"{key}: {value}"
    pattern = re.compile(rf"^{re.escape(key)}:.*$", re.MULTILINE)
    return pattern.sub(line, front) if pattern.search(front) else f"{front}\n{line}".lstrip("\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("draft", type=Path)
    ap.add_argument("--image", type=Path, required=True, help="approved image, path from project root")
    ap.add_argument("--anchor", required=True, help="verbatim anchor quote from the illustration file")
    ap.add_argument("--caption", default="", help="alt text; the moment in a few words")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    for p in (args.draft, args.image):
        if not p.is_file():
            print(f"not a file: {p}", file=sys.stderr)
            return 3

    text = args.draft.read_text(encoding="utf-8")
    front, body = split_frontmatter(text)
    head_lines = text[: len(text) - len(body)].count("\n")
    if re.search(r"^published:", front, re.MULTILINE):
        print(f"refused: {args.draft} is published — its text changes only through publish errata",
              file=sys.stderr)
        return 4
    old = re.search(r"^illustration:\s*(\S+)", front, re.MULTILINE)
    stale = {os.path.normpath(args.image)}
    if old:
        stale.add(os.path.normpath(old.group(1)))

    # Drop earlier placements of this chapter's image — exactly the "\n\n<line>" we insert.
    def unplace(m: re.Match) -> str:
        target = os.path.relpath(os.path.normpath(args.draft.parent / m.group(1)))
        return "" if target in stale else m.group(0)
    body = re.sub(r"\n\n!\[[^\]\n]*\]\(([^)\n]*)\)[ \t]*(?=\n|\Z)", unplace, body)

    needle = normalise(args.anchor.strip("«»\"“” "))
    spans = paragraph_spans(body)
    hits = [(s, e) for s, e in spans if needle in normalise(body[s:e])]
    total = sum(normalise(body[s:e]).count(needle) for s, e in spans)
    if total != 1:
        where = ", ".join(f"line {head_lines + body[:s].count(chr(10)) + 1}" for s, _ in hits) or "nowhere"
        print(f"anchor found {total}× ({where}) in {args.draft}; nothing written.\n"
              f"  anchor: {needle}", file=sys.stderr)
        return 2

    # Splice by offset: every other byte of the draft stays as it was, so refine-harness
    # diffs see one added line and nothing else.
    s, e = hits[0]
    link = os.path.relpath(args.image, args.draft.parent).replace(os.sep, "/")
    body = f"{body[:e]}\n\n![{args.caption}]({link}){body[e:]}"
    rel_image = os.path.relpath(args.image).replace(os.sep, "/")
    new = (f"---\n{set_key(front, 'illustration', rel_image)}\n---\n" if front else "") + body

    line_no = new[: new.index(f"]({link})")].count("\n") + 1
    preview = body[s:e].splitlines()[-1][:70]
    if new == text:
        print(f"unchanged: {args.draft}:{line_no} already has {link}")
        return 0
    if args.dry_run:
        print(f"would place {link} at {args.draft}:{line_no}, after: {preview}…")
        return 0
    args.draft.write_text(new, encoding="utf-8")
    print(f"placed {link} at {args.draft}:{line_no}, after: {preview}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())
