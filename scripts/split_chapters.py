#!/usr/bin/env python3
"""Split a single-file source into one file per chapter.

Standard library only, no dependencies, any language. Splitting is a mechanical
reshaping of `raw/`, never an edit of it: the tool copies bytes and does not
touch a single character of text. That promise is enforced, not asserted --
every run concatenates its own output back together and compares it to the
input, and refuses to write anything unless the two are byte-identical.

Why bother: ingest is per-chapter, so a chapter needs to be addressable. A
single 500k-character file makes `[src: book.md#Chapter 4]` unverifiable in
practice, lets a read wander into chapter 40, and makes the style fingerprint
measure the whole novel when the wiki has read six chapters of it.

    python3 split_chapters.py raw/book.md --list
    python3 split_chapters.py raw/book.md --out-dir raw
"""

import argparse
import os
import re
import sys

DEFAULT_PATTERN = r"^##\s+\S"


def find_headings(lines, pattern):
    rx = re.compile(pattern)
    return [i for i, line in enumerate(lines) if rx.search(line)]


def build_parts(lines, starts):
    """Return [(label, start, end)] covering every line exactly once."""
    parts = []
    if not starts:
        return parts
    if starts[0] > 0:
        parts.append(("_meta", 0, starts[0]))
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        parts.append((None, start, end))
    return parts


def name_for(index, total, width):
    return "ch{:0{w}d}".format(index, w=width)


def heading_text(line):
    return line.strip().lstrip("#").strip()


def main():
    ap = argparse.ArgumentParser(
        description="Split a single-file source into one file per chapter.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("source", help="the single file to split")
    ap.add_argument(
        "--out-dir",
        default=None,
        help="where to write the parts (default: the source's own directory)",
    )
    ap.add_argument(
        "--pattern",
        default=DEFAULT_PATTERN,
        help=r"regex marking a chapter start (default: %(default)s)",
    )
    ap.add_argument(
        "--list",
        action="store_true",
        help="show the split points and the resulting files, write nothing",
    )
    ap.add_argument(
        "--keep-source",
        action="store_true",
        help="leave the original file in place (default: remove it after a "
        "verified split, so raw/ holds one representation, not two)",
    )
    args = ap.parse_args()

    with open(args.source, "rb") as fh:
        original = fh.read()
    text = original.decode("utf-8")
    lines = text.splitlines(keepends=True)

    starts = find_headings(lines, args.pattern)
    if not starts:
        sys.exit(
            "No chapter headings matched {!r}.\n"
            "Inspect the file's headings and pass --pattern.".format(args.pattern)
        )

    parts = build_parts(lines, starts)
    chapters = [p for p in parts if p[0] is None]
    width = max(2, len(str(len(chapters))))
    out_dir = args.out_dir or os.path.dirname(args.source) or "."

    planned = []
    n = 0
    for label, start, end in parts:
        if label == "_meta":
            name = "_meta"
            title = "(preamble: frontmatter and title)"
        else:
            n += 1
            name = name_for(n, len(chapters), width)
            title = heading_text(lines[start])
        planned.append((name, title, start, end))

    print("{} chapter(s) found in {}".format(len(chapters), args.source))
    print()
    for name, title, start, end in planned:
        words = len("".join(lines[start:end]).split())
        print(
            "  {:<8} lines {:>5}-{:<5} {:>7} words  {}".format(
                name + ".md", start + 1, end, words, title
            )
        )
    print()

    if args.list:
        print("--list: nothing written.")
        return

    # Verify the round trip BEFORE touching the filesystem. A split that loses
    # or reorders a byte is a silent corruption of the one thing in the project
    # that is supposed to be immutable, and it would be discovered chapters
    # later as a citation that does not resolve.
    rebuilt = "".join("".join(lines[s:e]) for _, _, s, e in planned).encode("utf-8")
    if rebuilt != original:
        sys.exit(
            "Round-trip check FAILED: the parts do not reassemble into the "
            "source. Nothing was written."
        )

    os.makedirs(out_dir, exist_ok=True)
    written = []
    for name, _, start, end in planned:
        path = os.path.join(out_dir, name + ".md")
        if os.path.exists(path):
            sys.exit("Refusing to overwrite existing file: {}".format(path))
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("".join(lines[start:end]))
        written.append(path)

    # Re-read from disk. The in-memory check proves the arithmetic; this proves
    # what actually landed.
    on_disk = b""
    for path in written:
        with open(path, "rb") as fh:
            on_disk += fh.read()
    if on_disk != original:
        sys.exit(
            "Round-trip check FAILED after writing. The files in {} do not "
            "reassemble into {}. Delete them and investigate.".format(
                out_dir, args.source
            )
        )

    print("Round trip verified: {} bytes in, {} bytes out.".format(
        len(original), len(on_disk)
    ))
    print("Wrote {} file(s) to {}/".format(len(written), out_dir.rstrip("/")))

    if not args.keep_source:
        os.remove(args.source)
        print("Removed {} (its content is now in the parts above).".format(args.source))
    else:
        print("Kept {} (--keep-source).".format(args.source))

    print()
    print("Citation remap: [src: {}#<heading>] -> [src: <chapter file>#<heading>]".format(
        os.path.basename(args.source)
    ))


if __name__ == "__main__":
    main()
