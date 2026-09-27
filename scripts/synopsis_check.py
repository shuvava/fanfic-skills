#!/usr/bin/env python3
"""Check a synopsis for the two mechanical signs of text written for insiders.

Standard library only, any language.

    python3 synopsis_check.py plan/SYNOPSIS.md --against plan/outline.md plan/STORY_INTENT.md \
        [--ngram 5] [--max-words 30]

Why this exists
---------------
A synopsis assembled from outline rows reads as a string of riddles: the outline's
compressed phrasing («не владеет ничем, включая собственное имя») is shorthand for people who
already know the story. On a real run such a synopsis was rejected whole as "not human
language", though every fact in it was right. Two signs of that are countable:

- **Copied phrases** — any run of `--ngram` words (default 5) that also occurs in a source
  file. A synopsis retold in fresh words shares names and short terms with the outline, not
  five-word runs.
- **Long sentences** — more than `--max-words` words (default 30). A sentence that has to be
  read twice usually is one.

Semicolons are counted too: a chain of clauses joined by «;» is an outline row, not prose.

What it cannot see: an unexplained world term, an aphorism in fresh words. Those stay with
the reread the skill asks for. Frontmatter, headings and blockquotes are skipped. Exit code 1
when anything is found, 0 when clean.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

WORD = re.compile(r"[^\W_]+(?:[-'][^\W_]+)*", re.UNICODE)
SENTENCE_END = re.compile(r"(?<=[.!?…])\s+(?=[«\"(]?[A-ZА-ЯЁ])")


def body_text(path: Path, sections: list[str] | None = None) -> str:
    """Prose lines of a markdown file, optionally only under the given `## ` headings."""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    keep, current = [], None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            continue
        if line.startswith("#") or line.lstrip().startswith(">"):
            continue
        if sections is not None and current not in sections:
            continue
        keep.append(line)
    return "\n".join(keep)


def words(text: str) -> list[str]:
    return [w.lower().replace("ё", "е") for w in WORD.findall(text)]


def ngrams(tokens: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def sentences(text: str) -> list[str]:
    flat = " ".join(line.strip().lstrip("-* ").strip() for line in text.splitlines() if line.strip())
    return [s.strip() for s in SENTENCE_END.split(flat) if s.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("synopsis", type=Path)
    ap.add_argument("--against", type=Path, nargs="+", required=True, help="outline, intent: the text not to copy")
    ap.add_argument("--section", action="append", help="only these `## ` sections of the synopsis (repeatable)")
    ap.add_argument("--ngram", type=int, default=5)
    ap.add_argument("--max-words", type=int, default=30)
    args = ap.parse_args()

    text = body_text(args.synopsis, args.section)
    source = set()
    for p in args.against:
        source |= ngrams(words(body_text(p)), args.ngram)

    found = 0
    copied = []
    for s in sentences(text):
        toks = words(s)
        hits = [" ".join(g) for g in ngrams(toks, args.ngram) if g in source]
        if hits:
            copied.append((s, hits))
    if copied:
        print(f"COPIED — {len(copied)} sentence(s) share a {args.ngram}-word run with the sources:")
        for s, hits in copied:
            print(f"  - {s}\n      run: «{hits[0]}»" + (f" (+{len(hits) - 1})" if len(hits) > 1 else ""))
        found += len(copied)

    long = [(len(words(s)), s) for s in sentences(text) if len(words(s)) > args.max_words]
    if long:
        print(f"LONG — {len(long)} sentence(s) over {args.max_words} words:")
        for n, s in long:
            print(f"  - ({n}) {s}")
        found += len(long)

    semis = text.count(";")
    if semis:
        print(f"SEMICOLONS — {semis}")
        found += semis

    total = sentences(text)
    avg = sum(len(words(s)) for s in total) / max(len(total), 1)
    print(f"sentences={len(total)} avg_words={avg:.1f} findings={found}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
