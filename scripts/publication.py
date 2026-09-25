#!/usr/bin/env python3
"""Track which chapters are published where, and keep published text from changing silently.

Standard library only. Run from the project root.

    python3 publication.py status  --platform author-today [--per-week 2]
    python3 publication.py record  <draft.md> --platform author-today --url <chapter url> [--date YYYY-MM-DD]
    python3 publication.py errata-check <draft.md> --platform author-today
    python3 publication.py lint

Why this exists
---------------
A published chapter is what readers remember. It outranks the draft and the outline, and it
may only change by errata — typos, not rewrites. Three records say what was published, and
this script keeps them in step:

- the draft's frontmatter `published:` list — one entry per platform version;
- `snapshots/ch<NN>-published-<platform>-v<N>.md` — the draft exactly as it went out;
- `publish/LEDGER.md` — one row per publication, the project-wide view.

`status` lists chapters in order with what is published, what drifted since, and the next
chapter to publish with the drafted buffer in weeks. `record` writes all three records after a
publication and refuses to skip a chapter. `errata-check` diffs the draft's reader-visible text
against the last published version and passes only typo-sized changes. `lint` cross-checks the
three records.

Exit: 0 ok, 1 violations / drift / lint findings, 2 refused (order, nothing to record),
3 bad path or not published.
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_chapter import parse, plain_lines  # noqa: E402

LEDGER = Path("publish/LEDGER.md")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
ENTRY_RE = re.compile(r"^\s+-\s*\{(.*)\}\s*$")
LOG = Path("wiki/log.md")
LEDGER_HEAD = """---
type: publication-ledger
---

# Publication ledger

One row per publication; written by `publication.py record`. Errata add a row with the next version.

| book | ch | platform | version | date | url | draft |
|---|---|---|---|---|---|---|
"""


# --------------------------------------------------------------------------- #
# Chapters and their records
# --------------------------------------------------------------------------- #

def chapter_id(draft: Path) -> tuple[int, int]:
    book = re.search(r"book-(\d+)", str(draft.parent))
    ch = re.match(r"ch(\d+)", draft.name)
    if not ch:
        sys.exit(f"not a chapter draft (want ch<NN>-<slug>.md): {draft}")
    return (int(book.group(1)) if book else 0, int(ch.group(1)))


def label(cid: tuple[int, int]) -> str:
    return f"b{cid[0]:02d}/ch{cid[1]:02d}" if cid[0] else f"ch{cid[1]:02d}"


def drafts() -> list[Path]:
    found = [p for p in Path("drafts").rglob("ch[0-9]*-*.md") if "snapshots" not in p.parts]
    return sorted(found, key=chapter_id)


def published(draft: Path) -> list[dict]:
    m = FRONTMATTER_RE.match(draft.read_text(encoding="utf-8"))
    if not m:
        return []
    out, inside = [], False
    for line in m.group(1).splitlines():
        if re.match(r"^published:\s*$", line):
            inside = True
            continue
        if inside:
            e = ENTRY_RE.match(line)
            if not e:
                break
            fields = dict(kv.split(":", 1) for kv in re.split(r",\s*(?=\w+:)", e.group(1)))
            out.append({k.strip(): v.strip() for k, v in fields.items()})
    return out


def latest(draft: Path, platform: str) -> dict | None:
    versions = [e for e in published(draft) if e.get("platform") == platform]
    return max(versions, key=lambda e: int(e["version"])) if versions else None


def snapshot_path(draft: Path, platform: str, version: int) -> Path:
    num = re.match(r"(ch\d+)", draft.name).group(1)
    return draft.parent / "snapshots" / f"{num}-published-{platform}-v{version}.md"


def drifted(draft: Path, platform: str) -> bool | None:
    last = latest(draft, platform)
    if not last:
        return None
    snap = snapshot_path(draft, platform, int(last["version"]))
    return not snap.is_file() or plain_lines(parse(snap)) != plain_lines(parse(draft))


def add_entry(draft: Path, entry: str) -> None:
    text = draft.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    front = m.group(1) if m else ""
    lines = front.splitlines()
    if any(re.match(r"^published:\s*$", ln) for ln in lines):
        i = next(i for i, ln in enumerate(lines) if re.match(r"^published:\s*$", ln)) + 1
        while i < len(lines) and ENTRY_RE.match(lines[i]):
            i += 1
        lines.insert(i, f"  - {{{entry}}}")
    else:
        lines += ["published:", f"  - {{{entry}}}"]
    body = text[m.end():] if m else text
    draft.write_text("---\n" + "\n".join(lines) + "\n---\n" + body, encoding="utf-8")


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #

def gate_marks(cid: tuple[int, int], draft: Path) -> str:
    """Which pipeline stages wiki/log.md records for this chapter — evidence, not a verdict."""
    if not LOG.is_file():
        return "no wiki/log.md"
    lab = label(cid)
    heads = [ln for ln in LOG.read_text(encoding="utf-8").splitlines() if ln.startswith("## [")]
    stages = ("write", "reconcile", "naturalize")
    # Stages name a chapter as b01/ch05 or by its draft path; accept either.
    hits = {s: any(f"] {s} |" in h and (lab in h or draft.name in h) for h in heads) for s in stages}
    return " ".join(f"{s}{'✓' if ok else '✗'}" for s, ok in hits.items())


def cmd_status(args) -> int:
    rows, nxt, unpublished, issues = [], None, 0, 0
    for d in drafts():
        cid, last = chapter_id(d), latest(d, args.platform)
        drift = drifted(d, args.platform)
        if last:
            state = f"v{last['version']} {last.get('date', '')}" + (" DRIFTED" if drift else "")
            issues += bool(drift)
        else:
            state = "—"
            unpublished += 1
            nxt = nxt or d
        rows.append((label(cid), d.name, state, gate_marks(cid, d)))
    print(f"| chapter | draft | {args.platform} | log |\n|---|---|---|---|")
    for r in rows:
        print("| " + " | ".join(r) + " |")
    if nxt:
        print(f"\nnext: {label(chapter_id(nxt))} {nxt}")
        print(f"buffer: {unpublished} drafted, unpublished = {unpublished / args.per_week:.1f} weeks "
              f"at {args.per_week}/week" + ("  ← under one week" if unpublished < args.per_week else ""))
    else:
        print("\nnext: nothing drafted is unpublished — buffer 0 weeks")
    if issues:
        print(f"\n{issues} published chapter(s) drifted from their published text: "
              "errata-check them, or restore the draft", file=sys.stderr)
    return 1 if issues else 0


def cmd_record(args) -> int:
    d = args.draft
    cid, last = chapter_id(d), latest(d, args.platform)
    if not last:
        earlier = [p for p in drafts() if chapter_id(p) < cid and not latest(p, args.platform)]
        if earlier:
            print(f"refused: {', '.join(label(chapter_id(p)) for p in earlier)} not published on "
                  f"{args.platform} yet — chapters go out in order", file=sys.stderr)
            return 2
    elif not drifted(d, args.platform):
        print(f"refused: {label(cid)} unchanged since v{last['version']} — nothing to record",
              file=sys.stderr)
        return 2
    version = int(last["version"]) + 1 if last else 1
    date = args.date or dt.date.today().isoformat()

    snap = snapshot_path(d, args.platform, version)
    snap.parent.mkdir(parents=True, exist_ok=True)
    snap.write_text(d.read_text(encoding="utf-8"), encoding="utf-8")
    add_entry(d, f"platform: {args.platform}, version: {version}, date: {date}, url: {args.url}")
    if not LEDGER.is_file():
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        LEDGER.write_text(LEDGER_HEAD, encoding="utf-8")
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(f"| {cid[0]:02d} | {cid[1]:02d} | {args.platform} | {version} | {date} | {args.url} | {d} |\n")
    print(f"recorded {label(cid)} {args.platform} v{version} {date}\n  snapshot: {snap}\n  ledger: {LEDGER}")
    return 0


TOKEN_RE = re.compile(r"\w+|[^\w\s]")


def small_edit(a: str, b: str) -> bool:
    return difflib.SequenceMatcher(None, a, b).ratio() >= 0.6 and abs(len(a) - len(b)) <= 2


def typo_sized(a: list[str], b: list[str]) -> bool:
    """One misspelt word, a punctuation fix, or a split/merged word — nothing that changes wording."""
    wa = [t for t in a if re.match(r"\w", t)]
    wb = [t for t in b if re.match(r"\w", t)]
    if not wa and not wb:
        return len(a) + len(b) <= 3                       # punctuation only
    if len(wa) == len(wb) == 1:
        return small_edit(wa[0].lower(), wb[0].lower())   # misspelling
    if "".join(wa).lower() == "".join(wb).lower():
        return True                                       # «кое что» ↔ «кое-что», split or merge
    return False


def cmd_errata(args) -> int:
    d = args.draft
    last = latest(d, args.platform)
    if not last:
        print(f"{d} is not published on {args.platform}", file=sys.stderr)
        return 3
    snap = snapshot_path(d, args.platform, int(last["version"]))
    if not snap.is_file():
        print(f"missing snapshot {snap} — run lint", file=sys.stderr)
        return 3
    old, new = plain_lines(parse(snap)), plain_lines(parse(d))
    if len(old) != len(new):
        print(f"REWRITE: paragraph count {len(old)} → {len(new)}; errata may not add, remove, "
              "split or merge paragraphs")
        return 1
    fixes, bad = [], []
    for n, (pa, pb) in enumerate(zip(old, new), 1):
        if pa == pb:
            continue
        ta, tb = TOKEN_RE.findall(pa), TOKEN_RE.findall(pb)
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes():
            if op == "equal":
                continue
            ctx = " ".join(ta[max(0, i1 - 4): i2 + 4])
            item = f"¶{n}: «{' '.join(ta[i1:i2])}» → «{' '.join(tb[j1:j2])}»   …{ctx}…"
            (fixes if typo_sized(ta[i1:i2], tb[j1:j2]) else bad).append(item)
    for f in fixes:
        print(f"typo   {f}")
    for b in bad:
        print(f"REWRITE {b}")
    if not fixes and not bad:
        print(f"no reader-visible change since v{last['version']}")
    print(f"\n{len(fixes)} typo-sized, {len(bad)} rewrite-sized change(s) against v{last['version']}")
    return 1 if bad else 0


def cmd_lint(args) -> int:
    findings = []
    rows = []
    if LEDGER.is_file():
        for ln in LEDGER.read_text(encoding="utf-8").splitlines():
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) == 7 and cells[0].isdigit():
                rows.append(cells)
    ledger = {(r[6], r[2], r[3]) for r in rows}
    seen = set()
    for d in drafts():
        for e in published(d):
            key = (str(d), e.get("platform", ""), e.get("version", ""))
            seen.add(key)
            if key not in ledger:
                findings.append(f"{d}: frontmatter has {e.get('platform')} v{e.get('version')}, ledger does not")
            if not snapshot_path(d, key[1], int(key[2] or 0)).is_file():
                findings.append(f"{d}: missing snapshot for {key[1]} v{key[2]}")
        for platform in {e.get("platform") for e in published(d)}:
            if drifted(d, platform):
                findings.append(f"{d}: text changed since last {platform} publication — errata-check it")
    for key in ledger - seen:
        findings.append(f"ledger row {key[1]} v{key[2]} for {key[0]}: no matching frontmatter entry")
    for f in findings:
        print(f)
    print(f"{len(findings)} finding(s)")
    return 1 if findings else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status")
    s.add_argument("--platform", required=True)
    s.add_argument("--per-week", type=float, default=2)
    r = sub.add_parser("record")
    r.add_argument("draft", type=Path)
    r.add_argument("--platform", required=True)
    r.add_argument("--url", required=True)
    r.add_argument("--date")
    e = sub.add_parser("errata-check")
    e.add_argument("draft", type=Path)
    e.add_argument("--platform", required=True)
    sub.add_parser("lint")
    args = ap.parse_args()
    if getattr(args, "draft", None) and not args.draft.is_file():
        print(f"not a file: {args.draft}", file=sys.stderr)
        return 3
    return {"status": cmd_status, "record": cmd_record, "errata-check": cmd_errata,
            "lint": cmd_lint}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
