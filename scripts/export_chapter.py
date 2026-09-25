#!/usr/bin/env python3
"""Export a chapter draft in a publishing platform's format, and verify text against it.

Standard library only.

    python3 export_chapter.py export <draft.md> --platform author-today --out <file.html>
    python3 export_chapter.py verify <draft.md> --against <file.html|file.txt>
    python3 export_chapter.py platforms

Why this exists
---------------
A draft is not publishable text: it carries frontmatter, markdown escapes (`\\-` for a
dialogue dash), a `## Глава N.` heading, and `![…](…)` illustration lines relative to the
drafts folder. Stripping those by hand is where a paragraph, a dash or a picture goes
missing, and nobody notices until a reader does.

`export` writes the platform's markup and a `<out>.json` sidecar (title, images in order with the
paragraph each follows, word count). `verify` reduces both sides to plain text — one
paragraph per line, whitespace collapsed — and diffs them: run it on the export (round-trip)
and later on the text read back from the site. Exit 0 identical, 1 differs, 3 bad path.
That is the evidence that what readers get is what the draft says.

Formats: `author-today` (HTML fragment for the chapter editor) and `plain` (text for any
editor that takes paste). A new platform is a new entry in FORMATS.
"""

from __future__ import annotations

import argparse
import difflib
import html
import json
import os
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
HEADING_RE = re.compile(r"^#+\s+(.*?)\s*$")
IMAGE_RE = re.compile(r"^!\[([^\]\n]*)\]\(([^)\n]*)\)\s*$")
SCENE_BREAK_RE = re.compile(r"^(\*\s*){3,}$|^(-\s*){3,}$")
ESCAPE_RE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!>~|])")

FORMATS = {
    "author-today": {
        "ext": ".html",
        "paragraph": "<p>{}</p>",
        "break": '<p style="text-align: center;">* * *</p>',
        "image": '<p style="text-align: center;"><img src="{src}" alt="{alt}"></p>',
        "strong": "<strong>{}</strong>", "em": "<em>{}</em>", "escape": True,
        "join": "\n",
    },
    "plain": {
        "ext": ".txt",
        "paragraph": "{}", "break": "* * *", "image": "[иллюстрация: {alt}]",
        "strong": "{}", "em": "{}", "escape": False, "join": "\n\n",
    },
}
DEFAULT_TITLE = "{heading} {title}"


def frontmatter_value(front: str, key: str) -> str:
    m = re.search(rf"^{key}:\s*(.*?)\s*$", front, re.MULTILINE)
    return m.group(1).strip().strip('"\'') if m else ""


def parse(draft: Path) -> dict:
    """The draft as blocks: ('p', text) / ('break',) / ('image', src, alt), plus its title."""
    text = draft.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    front, body = (m.group(1), text[m.end():]) if m else ("", text)
    heading, blocks = "", []
    for para in re.split(r"\n[ \t]*\n", body):
        lines = [ln.strip() for ln in para.strip().splitlines() if ln.strip()]
        if not lines:
            continue
        h = HEADING_RE.match(lines[0])
        if h and len(lines) == 1:
            heading = heading or ESCAPE_RE.sub(r"\1", h.group(1))
            continue
        img = IMAGE_RE.match(lines[0])
        if img and len(lines) == 1:
            src = os.path.normpath(draft.parent / img.group(2))
            blocks.append(("image", os.path.relpath(src), img.group(1)))
        elif len(lines) == 1 and SCENE_BREAK_RE.match(lines[0]):
            blocks.append(("break",))
        else:
            blocks.append(("p", " ".join(lines)))
    return {"front": front, "heading": heading, "title": frontmatter_value(front, "title"),
            "blocks": blocks}


def inline(text: str, fmt: dict) -> str:
    """Markdown emphasis → platform markup; escapes resolved; HTML-escaped where needed."""
    text = ESCAPE_RE.sub(lambda m: f"\x00{ord(m.group(1))}\x00", text)
    if fmt["escape"]:
        text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(\S.*?\S|\S)\*\*", lambda m: fmt["strong"].format(m.group(1)), text)
    text = re.sub(r"(?<![\w*])\*(\S.*?\S|\S)\*(?![\w*])", lambda m: fmt["em"].format(m.group(1)), text)
    return re.sub(r"\x00(\d+)\x00", lambda m: chr(int(m.group(1))), text)


def render(doc: dict, platform: str, base: Path) -> str:
    """base: the export's folder — image paths are written relative to it, so the file previews."""
    fmt, out = FORMATS[platform], []
    for b in doc["blocks"]:
        if b[0] == "p":
            out.append(fmt["paragraph"].format(inline(b[1], fmt)))
        elif b[0] == "break":
            out.append(fmt["break"])
        else:
            alt = html.escape(b[2]) if fmt["escape"] else b[2]
            src = os.path.relpath(b[1], base).replace(os.sep, "/")
            out.append(fmt["image"].format(src=src, alt=alt))
    return fmt["join"].join(out) + "\n"


def plain_lines(doc: dict) -> list[str]:
    """Reader-visible text, one paragraph per line — what verify compares."""
    lines = []
    for b in doc["blocks"]:
        if b[0] == "p":
            t = ESCAPE_RE.sub(r"\1", b[1])
            t = re.sub(r"\*\*(\S.*?\S|\S)\*\*", r"\1", t)
            lines.append(re.sub(r"(?<![\w*])\*(\S.*?\S|\S)\*(?![\w*])", r"\1", t))
        elif b[0] == "break":
            lines.append("* * *")
    return [normalise(ln) for ln in lines if normalise(ln)]


def normalise(line: str) -> str:
    return re.sub(r"\s+", " ", line.replace(" ", " ")).strip()


def text_lines(path: Path) -> list[str]:
    """Plain text of an export or a read-back: HTML if it has tags, else blank-line paragraphs."""
    raw = path.read_text(encoding="utf-8")
    if re.search(r"<(p|div|br|img)\b", raw, re.IGNORECASE):
        raw = re.sub(r"<img\b[^>]*>", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"<br\s*/?>|</(p|div|h\d)>", "\n", raw, flags=re.IGNORECASE)
        raw = html.unescape(re.sub(r"<[^>]+>", "", raw))
        lines = raw.splitlines()
    else:
        lines = re.split(r"\n[ \t]*\n", raw) if "\n\n" in raw else raw.splitlines()
    out = [normalise(ln) for ln in lines]
    return [ln for ln in out if ln and not re.fullmatch(r"\[иллюстрация: .*\]", ln)]


def cmd_export(args) -> int:
    doc = parse(args.draft)
    fmt = FORMATS[args.platform]
    out = args.out or args.draft.with_suffix(fmt["ext"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(doc, args.platform, out.parent), encoding="utf-8")
    title = args.title_format.format(heading=doc["heading"], title=doc["title"]).strip()
    images, para = [], 0
    for b in doc["blocks"]:
        if b[0] == "image":
            images.append({"src": b[1], "alt": b[2], "after_paragraph": para,
                           "exists": Path(b[1]).is_file()})
        else:
            para += 1
    words = sum(len(re.findall(r"\w+", ln)) for ln in plain_lines(doc))
    meta = {"draft": str(args.draft), "platform": args.platform, "title": title,
            "paragraphs": para, "words": words, "images": images}
    sidecar = out.with_name(out.name + ".json")
    sidecar.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                                        encoding="utf-8")
    missing = [i["src"] for i in images if not i["exists"]]
    print(f"exported {args.draft} → {out}\n  title: {title}\n  paragraphs: {para}, words: {words}, "
          f"images: {len(images)}" + (f"\n  MISSING image files: {', '.join(missing)}" if missing else ""))
    same = plain_lines(doc) == text_lines(out)
    print(f"  round-trip: {'identical' if same else 'DIFFERS — run verify'}")
    return 0 if same and not missing else 1


def cmd_verify(args) -> int:
    a, b = plain_lines(parse(args.draft)), text_lines(args.against)
    if a == b:
        print(f"identical: {len(a)} paragraphs, {sum(len(x) for x in a)} characters")
        return 0
    diff = list(difflib.unified_diff(a, b, "draft", str(args.against), n=1, lineterm=""))
    print("\n".join(diff[: args.max_lines]))
    if len(diff) > args.max_lines:
        print(f"… {len(diff) - args.max_lines} more diff lines")
    print(f"DIFFERS: draft {len(a)} paragraphs, {args.against} {len(b)}", file=sys.stderr)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("draft", type=Path)
    e.add_argument("--platform", choices=sorted(FORMATS), required=True)
    e.add_argument("--out", type=Path)
    e.add_argument("--title-format", default=DEFAULT_TITLE,
                   help=f"chapter title from {{heading}} and frontmatter {{title}}; default {DEFAULT_TITLE!r}")
    v = sub.add_parser("verify")
    v.add_argument("draft", type=Path)
    v.add_argument("--against", type=Path, required=True)
    v.add_argument("--max-lines", type=int, default=60)
    sub.add_parser("platforms")
    args = ap.parse_args()

    if args.cmd == "platforms":
        for name, fmt in FORMATS.items():
            print(f"{name}\t{fmt['ext']}")
        return 0
    for p in [args.draft] + ([args.against] if args.cmd == "verify" else []):
        if not p.is_file():
            print(f"not a file: {p}", file=sys.stderr)
            return 3
    return cmd_export(args) if args.cmd == "export" else cmd_verify(args)


if __name__ == "__main__":
    sys.exit(main())
