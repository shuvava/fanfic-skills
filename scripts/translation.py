#!/usr/bin/env python3
"""Keep a chapter translation aligned with its source, its glossary, and later edits to the source.

Standard library only. Run from the project root.

    python3 translation.py prepare <draft.md> --lang en [--from <published snapshot>]
    python3 translation.py terms <draft.md> --lang en
    python3 translation.py check <translation.md>
    python3 translation.py stale <translation.md>
    python3 translation.py status --lang en
    python3 translation.py accept translations/en/book-01/proposals/ch05.md

Why this exists
---------------
A translation is written paragraph for paragraph: source block N is target block N. That one
rule turns the failures a reader would find into things a script can count:

- a dropped or merged paragraph → block sequences do not line up;
- a sentence dropped inside a paragraph → that paragraph's length ratio sits far from the
  chapter's median (a place to re-read, not a verdict);
- a name rendered two ways → a variant the glossary lists under `Avoid`;
- an untranslated word → letters of the source's script left in the target;
- an erratum to the source after translation → `stale` names the paragraphs to redo.

`prepare` freezes the exact source text being translated into
`translations/<lang>/[book-NN/]snapshots/chNN-source.md`; `stale` diffs the source's current
text against that freeze. `terms` lists capitalised mid-sentence forms the glossary does not
cover — candidates only: it does not know which are names, and inflected forms of one name
(`Анна`, `Анны`) are listed separately, sorted so they sit together. The model judges.

Exit codes: 0 pass, 1 findings (check errors, stale paragraphs), 3 bad path or frontmatter.
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import statistics
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_chapter import (ESCAPE_RE, FRONTMATTER_RE, IMAGE_RE, frontmatter_value,  # noqa: E402
                            normalise, parse)

ROOT = Path("translations")
RATIO_LOW, RATIO_HIGH, RATIO_MIN_CHARS = 0.6, 1.6, 80


# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #

def book_dir(draft: Path) -> str:
    m = re.search(r"(book-\d+)", str(draft.parent))
    return m.group(1) if m else ""


def target_path(draft: Path, lang: str) -> Path:
    name = re.sub(r"-published-.*?(?=\.md$)", "", draft.name)  # a published snapshot → chNN.md
    return ROOT / lang / book_dir(draft) / name


def source_snapshot(draft: Path, lang: str) -> Path:
    num = re.match(r"(ch\d+)", draft.name)
    if not num:
        sys.exit(f"not a chapter draft (want ch<NN>-<slug>.md): {draft}")
    return ROOT / lang / book_dir(draft) / "snapshots" / f"{num.group(1)}-source.md"


def freeze(src: Path, snap: Path, base: Path) -> None:
    """Copy src to snap, rebasing image paths so the frozen copy still points at the pictures.

    base: the folder image paths are relative to — the draft's. A published snapshot is a
    verbatim copy of the draft, so its paths are relative to the draft too, not to snapshots/.
    """
    def rebase(line: str) -> str:
        m = IMAGE_RE.match(line.strip())
        if not m or re.match(r"[a-z]+://", m.group(2)):
            return line
        rel = os.path.relpath(os.path.normpath(base / m.group(2)), snap.parent)
        return f"![{m.group(1)}]({rel.replace(os.sep, '/')})"
    snap.parent.mkdir(parents=True, exist_ok=True)
    lines = src.read_text(encoding="utf-8").split("\n")
    snap.write_text("\n".join(rebase(ln) for ln in lines), encoding="utf-8")


def front(path: Path) -> str:
    m = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    return m.group(1) if m else ""


# --------------------------------------------------------------------------- #
# Blocks: what gets aligned
# --------------------------------------------------------------------------- #

def clean(text: str) -> str:
    text = ESCAPE_RE.sub(r"\1", text)
    text = re.sub(r"\*\*(\S.*?\S|\S)\*\*", r"\1", text)
    text = re.sub(r"(?<![\w*])\*(\S.*?\S|\S)\*(?![\w*])", r"\1", text)
    return normalise(text)


def blocks(path: Path) -> list[tuple]:
    """('p', text) / ('break',) / ('image', normalised src) — heading excluded, checked apart."""
    out = []
    for b in parse(path)["blocks"]:
        if b[0] == "p":
            out.append(("p", clean(b[1])))
        elif b[0] == "image":
            out.append(("image", b[1]))
        else:
            out.append(("break",))
    return out


def shape(bs: list[tuple]) -> list[str]:
    return [b[0] if b[0] != "image" else f"image:{b[1]}" for b in bs]


def script_of(ch: str) -> str:
    try:
        return unicodedata.name(ch).split()[0]
    except ValueError:
        return ""


def dominant_script(text: str) -> str:
    counts: dict[str, int] = {}
    for ch in text:
        if ch.isalpha():
            s = script_of(ch)
            counts[s] = counts.get(s, 0) + 1
    return max(counts, key=counts.get) if counts else ""


# --------------------------------------------------------------------------- #
# Glossary
# --------------------------------------------------------------------------- #

def glossary_path(lang: str) -> Path:
    return ROOT / lang / "GLOSSARY.md"


def phrasebook_path(lang: str) -> Path:
    return ROOT / lang / "PHRASEBOOK.md"


# Names and world terms go to the glossary; everything phrasal to the phrasebook.
GLOSSARY_KINDS = {"name", "term", "place", "title", "rank", "clan"}
COLUMNS = ["Source", "Match", "Target", "Avoid", "Kind", "Note"]
HEADS = {
    "GLOSSARY.md": "# Glossary — {lang}\n\nOne rendering per name and term. Read by translation.py "
                   "(check, terms) and openrouter_translate.py; `Match` stems end in `*`.\n\n",
    "PHRASEBOOK.md": "# Phrasebook — {lang}\n\nIdioms, proverbs, slang, catchphrases and puns with "
                     "their ratified rendering. A strong default, not a mandate: a sentence may need "
                     "the phrase bent to fit.\n\n",
}


def load_all(lang: str, glossary: Path | None = None) -> list[dict]:
    return load_glossary(glossary or glossary_path(lang)) + load_glossary(phrasebook_path(lang))


def split_cell(cell: str) -> list[str]:
    return [x.strip().strip("`") for x in cell.split(",") if x.strip().strip("`")]


def load_glossary(path: Path) -> list[dict]:
    """Every markdown table row with Match and Target columns; header names, not positions."""
    if not path.is_file():
        return []
    entries, cols = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            cols = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cols is None:
            cols = [c.lower() for c in cells]
            continue
        if all(re.fullmatch(r":?-+:?", c) for c in cells):
            continue
        row = dict(zip(cols, cells))
        if "match" in row and "target" in row and row["match"] and row["target"]:
            entries.append({"match": split_cell(row["match"]), "target": row["target"].strip("`"),
                            "avoid": split_cell(row.get("avoid", "")),
                            "source": row.get("source", ""), "kind": row.get("kind", ""),
                            "note": row.get("note", ""), "row": row})
    return entries


def stem_rx(stem: str) -> re.Pattern:
    """`Анн*` matches every form starting with it; a bare form matches only itself. A `*` may
    close any word of a phrase — `Верн* щит*` matches «Верного щита» — because phrases inflect
    in every word."""
    body = "".join(r"\w*" if part == "*" else re.escape(part) for part in re.split(r"(\*)", stem))
    return re.compile(rf"(?<!\w){body}" + ("" if stem.endswith("*") else r"(?!\w)"), re.IGNORECASE)


def term_rx(term: str) -> re.Pattern:
    return re.compile(rf"(?<!\w){re.escape(term)}(?!\w)", re.IGNORECASE)


def target_rx(term: str) -> re.Pattern:
    """Target forms may inflect or take a possessive: match the start of the word."""
    return re.compile(rf"(?<!\w){re.escape(term)}", re.IGNORECASE)


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #

def cmd_prepare(args) -> int:
    src = args.source or args.draft
    for p in (args.draft, src):
        if not p.is_file():
            print(f"no such file: {p}", file=sys.stderr)
            return 3
    out, snap = target_path(args.draft, args.lang), source_snapshot(args.draft, args.lang)
    freeze(src, snap, args.draft.parent)
    bs, doc = blocks(snap), parse(snap)
    words = sum(len(re.findall(r"\w+", b[1])) for b in bs if b[0] == "p")
    print(f"froze {src} → {snap}")
    print(f"target: {out}{'  (exists — a retranslation overwrites it)' if out.is_file() else ''}")
    print(f"heading: {doc['heading'] or '(none)'}\ntitle: {doc['title'] or '(none)'}")
    print(f"blocks: {len(bs)} — paragraphs {sum(b[0] == 'p' for b in bs)}, "
          f"breaks {sum(b[0] == 'break' for b in bs)}, images {sum(b[0] == 'image' for b in bs)}; "
          f"words {words}")
    print("frontmatter for the translation:")
    print(f"  source: {args.draft}\n  source_snapshot: {snap}\n  lang: {args.lang}")
    images = [b for b in bs if b[0] == "image"]
    if images:
        print("image lines, paths relative to the target (translate only the alt text):")
        for n, b in enumerate(bs, 1):
            if b[0] == "image":
                rel = os.path.relpath(b[1], out.parent).replace(os.sep, "/")
                print(f"  block {n}: ![<alt>]({rel})")
    return 0


def cmd_terms(args) -> int:
    if not args.draft.is_file():
        print(f"no such file: {args.draft}", file=sys.stderr)
        return 3
    gloss = load_all(args.lang, args.glossary)
    rxs = [stem_rx(s) for e in gloss for s in e["match"]]
    counts: dict[str, int] = {}
    context: dict[str, str] = {}
    for b in blocks(args.draft):
        if b[0] != "p":
            continue
        for m in re.finditer(r"\w+(?:-\w+)*", b[1]):
            w = m.group(0)
            if not w[0].isupper() or len(w) < 2 or w.isupper() and len(w) > 4:
                continue
            before = b[1][: m.start()].rstrip()
            if not before or before[-1] in ".!?…:«\"„“—–-(":  # sentence or line start
                continue
            if any(rx.match(b[1], m.start()) for rx in rxs):  # also the first word of a phrase
                continue
            counts[w] = counts.get(w, 0) + 1
            context.setdefault(w, b[1][max(0, m.start() - 40): m.end() + 40])
    rows = sorted((w for w in counts if counts[w] >= args.min), key=str.lower)
    if not rows:
        print(f"no uncovered capitalised forms (glossary: {len(gloss)} entries)")
        return 0
    print(f"{len(rows)} capitalised mid-sentence form(s) not in the glossary "
          f"({len(gloss)} entries) — candidates, not a verdict:\n")
    print("| Form | Count | Context |\n|---|---|---|")
    for w in rows:
        print(f"| {w} | {counts[w]} | …{context[w].replace('|', '/')}… |")
    return 0


def cmd_check(args) -> int:
    tr = args.translation
    if not tr.is_file():
        print(f"no such file: {tr}", file=sys.stderr)
        return 3
    fm = front(tr)
    snap = Path(frontmatter_value(fm, "source_snapshot"))
    lang = frontmatter_value(fm, "lang")
    if not snap.is_file():
        print(f"frontmatter source_snapshot missing or not a file: {snap or '(none)'} — "
              f"run prepare first", file=sys.stderr)
        return 3
    s, t = blocks(snap), blocks(tr)
    errors, warnings, notices = [], [], []

    # 1. Alignment: the same sequence of paragraphs, breaks and images.
    if shape(s) != shape(t):
        sm = difflib.SequenceMatcher(a=shape(s), b=shape(t), autojunk=False)
        where = []
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op != "equal":
                first = s[i1] if i1 < i2 else t[j1]
                text = first[1][:70] if len(first) > 1 else "* * *"
                where.append(f"    {op}: source blocks {i1 + 1}–{i2}, translation blocks "
                             f"{j1 + 1}–{j2} — near «{text}»")
        errors.append("block sequences differ (paragraph dropped, merged, split, or image moved) "
                      "— nothing else is checked until they align:\n" + "\n".join(where[:8]))
        print_report(tr, snap, errors, warnings, notices)
        return 1
    if parse(snap)["heading"] and not parse(tr)["heading"]:
        errors.append("the source has a chapter heading; the translation has none")
    pairs = [(n, a[1], b[1]) for n, (a, b) in enumerate(zip(s, t), 1) if a[0] == "p"]

    # 2. Letters of the source's script left in the target.
    src_script = dominant_script(" ".join(a for _, a, _ in pairs))
    tgt_script = dominant_script(" ".join(b for _, _, b in pairs))
    if src_script and tgt_script and src_script != tgt_script:
        for n, _, b in pairs:
            left = sorted({w for w in re.findall(r"\w+", b)
                           if any(script_of(c) == src_script for c in w)})
            if left:
                errors.append(f"block {n}: untranslated {src_script.lower()} text: {', '.join(left[:6])}")

    # 3. Length ratio — where a sentence may have been dropped or added.
    ratios = [(n, len(b) / len(a)) for n, a, b in pairs if len(a) >= RATIO_MIN_CHARS]
    if len(ratios) >= 3:
        med = statistics.median(r for _, r in ratios)
        for n, r in ratios:
            if r < med * RATIO_LOW or r > med * RATIO_HIGH:
                warnings.append(f"block {n}: length ratio {r:.2f} vs chapter median {med:.2f} — "
                                f"re-read for {'an omission' if r < med else 'an addition'}")

    # 4. Numbers written as digits.
    for n, a, b in pairs:
        missing = [d for d in re.findall(r"\d+", a) if d not in re.findall(r"\d+", b)]
        if missing:
            warnings.append(f"block {n}: digits in source not in translation: {', '.join(missing)}")

    # 5. Glossary.
    gloss = load_all(lang, args.glossary)
    for e in gloss:
        srx, trx = [stem_rx(x) for x in e["match"]], target_rx(e["target"])
        for n, a, b in pairs:
            for v in e["avoid"]:
                if term_rx(v).search(b):
                    errors.append(f"block {n}: '{v}' — glossary renders {e['match'][0]} as "
                                  f"'{e['target']}'")
            if any(r.search(a) for r in srx) and not trx.search(b):
                why = "fine if a pronoun or rephrase carries it" if e["kind"] in GLOSSARY_KINDS \
                    or not e["kind"] else "fine if the sentence needed the phrase bent"
                notices.append(f"block {n}: source has {e['match'][0]}, translation lacks "
                               f"'{e['target']}' ({why})")

    print_report(tr, snap, errors, warnings, notices, len(pairs), len(gloss))
    return 1 if errors else 0


def print_report(tr, snap, errors, warnings, notices, paragraphs=0, gloss=0) -> None:
    print(f"check {tr} against {snap}: {paragraphs} paragraphs aligned, glossary {gloss} entries")
    for title, items in (("ERRORS", errors), ("warnings", warnings), ("notices", notices)):
        if items:
            print(f"\n{title} ({len(items)}):")
            print("\n".join(f"  - {i}" for i in items))
    print(f"\n{'FAIL' if errors else 'pass'}: {len(errors)} error(s), {len(warnings)} warning(s), "
          f"{len(notices)} notice(s)")


def cmd_stale(args) -> int:
    tr = args.translation
    if not tr.is_file():
        print(f"no such file: {tr}", file=sys.stderr)
        return 3
    fm = front(tr)
    src, snap = Path(frontmatter_value(fm, "source")), Path(frontmatter_value(fm, "source_snapshot"))
    if not src.is_file() or not snap.is_file():
        print(f"source or source_snapshot missing: {src} / {snap}", file=sys.stderr)
        return 3
    old, new = blocks(snap), blocks(src)
    if old == new:
        print(f"fresh: {src} unchanged since it was translated ({len(old)} blocks)")
        return 0
    print(f"STALE: {src} changed since {snap} was frozen. Blocks are numbered as in the "
          f"translation (the frozen source):")
    sm = difflib.SequenceMatcher(a=[repr(b) for b in old], b=[repr(b) for b in new], autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        where = f"blocks {i1 + 1}–{i2}" if i2 - i1 > 1 else f"block {i1 + 1}" if i2 > i1 \
            else f"after block {i1}"
        print(f"\n  {op} {where}:")
        for b in old[i1:i2]:
            print(f"    - {b[1] if len(b) > 1 else '* * *'}")
        for b in new[j1:j2]:
            print(f"    + {b[1] if len(b) > 1 else '* * *'}")
    print("\nRetranslate only these blocks, then run prepare again to refreeze the source, and check.")
    return 1


def cmd_accept(args) -> int:
    """Move the rows ticked `[x]` in a proposals file into GLOSSARY.md or PHRASEBOOK.md."""
    if not args.proposals.is_file():
        print(f"no such file: {args.proposals}", file=sys.stderr)
        return 3
    lang = frontmatter_value(front(args.proposals), "lang")
    rows = [e for e in load_glossary(args.proposals)
            if re.fullmatch(r"\[[xX]\]", e["row"].get("keep", "").strip())]
    if not rows:
        print("no rows ticked [x] — nothing accepted")
        return 0
    known = {(e["source"].strip().lower()) for e in load_all(lang)}
    added: dict[str, int] = {}
    for e in rows:
        if e["source"].strip().lower() in known:
            print(f"  skip (already there): {e['source']}")
            continue
        name = "GLOSSARY.md" if e["kind"].lower() in GLOSSARY_KINDS else "PHRASEBOOK.md"
        path = ROOT / lang / name
        if not path.is_file():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(HEADS[name].format(lang=lang) + "| " + " | ".join(COLUMNS) + " |\n|"
                            + "---|" * len(COLUMNS) + "\n", encoding="utf-8")
        cells = [e["row"].get(c.lower(), "").replace("|", "/") for c in COLUMNS]
        text = path.read_text(encoding="utf-8").rstrip("\n") + "\n| " + " | ".join(cells) + " |\n"
        path.write_text(text, encoding="utf-8")
        known.add(e["source"].strip().lower())
        added[name] = added.get(name, 0) + 1
    for name, n in added.items():
        print(f"accepted {n} row(s) → {ROOT / lang / name}")
    return 0


def cmd_status(args) -> int:
    drafts = sorted(p for p in Path("drafts").rglob("ch[0-9]*-*.md") if "snapshots" not in p.parts)
    if not drafts:
        print("no drafts under drafts/")
        return 0
    print(f"| Chapter | Translation ({args.lang}) | State |\n|---|---|---|")
    for d in drafts:
        tr = target_path(d, args.lang)
        chap = f"{book_dir(d)}/{d.name}".lstrip("/")
        if not tr.is_file():
            print(f"| {chap} | — | not translated |")
            continue
        snap = Path(frontmatter_value(front(tr), "source_snapshot"))
        state = "no source_snapshot" if not snap.is_file() else \
            "fresh" if blocks(snap) == blocks(d) else "STALE — run stale"
        print(f"| {chap} | {tr} | {state} |")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare", help="freeze the source text and print the target's frontmatter")
    p.add_argument("draft", type=Path)
    p.add_argument("--lang", required=True)
    p.add_argument("--from", dest="source", type=Path,
                   help="translate this file (e.g. the published snapshot) instead of the draft")
    t = sub.add_parser("terms", help="capitalised forms the glossary does not cover")
    t.add_argument("draft", type=Path)
    t.add_argument("--lang", required=True)
    t.add_argument("--glossary", type=Path)
    t.add_argument("--min", type=int, default=1, help="minimum occurrences (default 1)")
    c = sub.add_parser("check", help="alignment, leftover script, length ratios, digits, glossary")
    c.add_argument("translation", type=Path)
    c.add_argument("--glossary", type=Path)
    s = sub.add_parser("stale", help="source blocks changed since the translation was made")
    s.add_argument("translation", type=Path)
    a = sub.add_parser("accept", help="move rows ticked [x] in a proposals file into the glossary "
                                      "or phrasebook")
    a.add_argument("proposals", type=Path)
    st = sub.add_parser("status", help="every draft: translated, fresh or stale")
    st.add_argument("--lang", required=True)
    args = ap.parse_args()
    return {"prepare": cmd_prepare, "terms": cmd_terms, "check": cmd_check,
            "stale": cmd_stale, "status": cmd_status, "accept": cmd_accept}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
