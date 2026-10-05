#!/usr/bin/env python3
"""Track which chapters are published where, and keep published text from changing silently.

Standard library only. Run from the project root.

    python3 publication.py status  --platform author-today [--per-week 2 | --every-days 2 | --weekdays mon-fri]
    python3 publication.py record  <draft.md> --platform author-today --url <chapter url> [--date YYYY-MM-DD]
    python3 publication.py next-slot --platform author-today --every-days 2 --time 19:00 --tz Europe/Moscow
    python3 publication.py next-slot --platform author-today --weekdays mon-fri --after 2026-10-12 --count 10
    python3 publication.py reschedule <draft.md> --platform author-today --date YYYY-MM-DD
    python3 publication.py cleanup-rounds <draft.md> [--dry-run]
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
three records. `next-slot` gives the next date on a fixed schedule — every N days or on set
weekdays — counted from the last publication in the ledger (or from `--after`, with `--count` for
a run of slots). `reschedule` moves a delayed publication whose timer has not fired to a new date
in the frontmatter and the ledger, after the user changed the timer on the site. `cleanup-rounds` deletes a chapter's intermediate illustration
rounds once its approved image is placed.

Exit: 0 ok, 1 violations / drift / lint findings, 2 refused (order, nothing to record),
3 bad path or not published.
"""

from __future__ import annotations

import argparse
import datetime as dt
from zoneinfo import ZoneInfo
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
    rows, nxt, unpublished, queued, issues = [], None, 0, 0, 0
    today = dt.date.today().isoformat()
    for d in drafts():
        cid, last = chapter_id(d), latest(d, args.platform)
        drift = drifted(d, args.platform)
        if last:
            state = f"v{last['version']} {last.get('date', '')}" + (" DRIFTED" if drift else "")
            issues += bool(drift)
            queued += last["version"] == "1" and last.get("date", "") > today   # timer not fired yet
        else:
            state = "—"
            unpublished += 1
            nxt = nxt or d
        rows.append((label(cid), d.name, state, gate_marks(cid, d)))
    print(f"| chapter | draft | {args.platform} | log |\n|---|---|---|---|")
    for r in rows:
        print("| " + " | ".join(r) + " |")
    if args.weekdays:
        per_week, cadence = len(args.weekdays), f"{len(args.weekdays)}/week on {format_days(args.weekdays)}"
    elif args.every_days:
        per_week, cadence = 7 / args.every_days, f"one every {args.every_days:g} days"
    else:
        per_week, cadence = args.per_week, f"{args.per_week:g}/week"
    last = last_date(args.platform)
    if last and last > dt.date.today():
        print(f"\nscheduled ahead: last publication on the ledger is {last} (timer not fired yet)")
    print(f"\nnext: {label(chapter_id(nxt))} {nxt}" if nxt else "\nnext: nothing drafted is unpublished")
    ahead = unpublished + queued
    print(f"buffer: {queued} on timers + {unpublished} drafted = {ahead / per_week:.1f} weeks at {cadence}"
          + ("  ← under one week" if ahead < per_week else ""))
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


def ledger_rows() -> list[list[str]]:
    if not LEDGER.is_file():
        return []
    rows = []
    for ln in LEDGER.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) == 7 and cells[0].isdigit():
            rows.append(cells)
    return rows


def last_date(platform: str) -> dt.date | None:
    """The latest publication date on the ledger for a platform — a delayed one may be in the future."""
    dates = [dt.date.fromisoformat(r[4]) for r in ledger_rows() if r[2] == platform and r[3] == "1"]
    return max(dates) if dates else None


DAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


def parse_weekdays(text: str) -> list[int]:
    """`mon-fri`, `mon,wed,fri` or `mon-wed,sat` → sorted weekday numbers (Monday = 0)."""
    out = set()
    for part in text.lower().split(","):
        a, _, b = part.strip().partition("-")
        if a not in DAYS or (b and b not in DAYS):
            raise argparse.ArgumentTypeError(f"weekdays: want mon..sun, got {part!r}")
        i, j = DAYS.index(a), DAYS.index(b or a)
        out.update(range(i, j + 1) if i <= j else [*range(i, 7), *range(0, j + 1)])
    return sorted(out)


def format_days(days: list[int]) -> str:
    return ",".join(DAYS[d] for d in days)


def following(day: dt.date, args) -> dt.date:
    """The schedule's next publishing day after `day`."""
    if not args.weekdays:
        return day + dt.timedelta(days=args.every_days)
    day += dt.timedelta(days=1)
    while day.weekday() not in args.weekdays:
        day += dt.timedelta(days=1)
    return day


def cmd_next_slot(args) -> int:
    """Next moments on the schedule after the last publication (or --after), never in the past."""
    tz = ZoneInfo(args.tz)
    hh, mm = (int(x) for x in args.time.split(":"))
    now = dt.datetime.now(tz)
    last = dt.date.fromisoformat(args.after) if args.after else last_date(args.platform)
    day = following(last, args) if last else now.date()
    min_ahead = dt.timedelta(minutes=args.min_ahead)
    while (dt.datetime.combine(day, dt.time(hh, mm), tzinfo=tz) < now + min_ahead
           or (args.weekdays and day.weekday() not in args.weekdays)):
        day += dt.timedelta(days=1)                       # a gap in publishing: first free slot from today
    print(f"{'counting after' if args.after else 'last on ledger'}: {last or '—'}")
    for n in range(args.count):
        slot = dt.datetime.combine(day, dt.time(hh, mm), tzinfo=tz)
        utc = slot.astimezone(dt.timezone.utc)
        if args.count == 1:
            print(f"next slot: {day.isoformat()} {DAYS[day.weekday()]} {slot:%H:%M} {args.tz}  =  "
                  f"{utc:%Y-%m-%dT%H:%M:%SZ}")
            print(f"date={day.isoformat()}")
            print(f"utc={utc:%Y-%m-%dT%H:%M:%SZ}")
        else:
            print(f"slot {n + 1}: {day.isoformat()} {DAYS[day.weekday()]} {slot:%H:%M} {args.tz}  =  "
                  f"{utc:%Y-%m-%dT%H:%M:%SZ}")
        day = following(day, args)
    return 0


def cmd_reschedule(args) -> int:
    """Move a delayed publication to a new date in the frontmatter entry and its ledger row."""
    d, new = args.draft, dt.date.fromisoformat(args.date)
    last = latest(d, args.platform)
    if not last:
        print(f"{d} is not published on {args.platform}", file=sys.stderr)
        return 3
    old = dt.date.fromisoformat(last["date"])
    if old <= dt.date.today() or new <= dt.date.today():
        print(f"refused: {label(chapter_id(d))} v{last['version']} date {old} → {new} — only a timer "
              "that has not fired moves, and only to a day still ahead", file=sys.stderr)
        return 2
    text = d.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    entry = re.compile(rf"^(\s+-\s*\{{platform:\s*{re.escape(args.platform)},\s*version:\s*"
                       rf"{last['version']},\s*date:\s*){old.isoformat()}", re.M)
    front, hits = entry.subn(rf"\g<1>{new.isoformat()}", m.group(1))
    if hits != 1:
        print(f"refused: frontmatter entry for v{last['version']} not found once in {d}", file=sys.stderr)
        return 2
    rows = LEDGER.read_text(encoding="utf-8").splitlines(keepends=True)
    want = [args.platform, last["version"], old.isoformat(), str(d)]

    def key(ln: str) -> list[str]:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        return cells[2:5] + cells[6:7] if len(cells) == 7 else []

    idx = [i for i, ln in enumerate(rows) if key(ln) == want]
    if len(idx) != 1:
        print(f"refused: ledger row for {d} v{last['version']} {old} not found once", file=sys.stderr)
        return 2
    d.write_text("---\n" + front + "\n---\n" + text[m.end():], encoding="utf-8")
    rows[idx[0]] = rows[idx[0]].replace(f"| {old.isoformat()} |", f"| {new.isoformat()} |", 1)
    LEDGER.write_text("".join(rows), encoding="utf-8")
    print(f"rescheduled {label(chapter_id(d))} {args.platform} v{last['version']}: {old} → {new}")
    return 0


IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}


def cmd_cleanup_rounds(args) -> int:
    """Delete ch<NN>-* image rounds beside the approved `illustration:` image; keep the approved one."""
    m = FRONTMATTER_RE.match(args.draft.read_text(encoding="utf-8"))
    ill = re.search(r"^illustration:\s*(\S+)", m.group(1), re.M) if m else None
    if not ill:
        print(f"{args.draft}: no `illustration:` in frontmatter — nothing to clean", file=sys.stderr)
        return 0
    approved = Path(ill.group(1))
    if not approved.is_file():
        print(f"refused: approved image {approved} is missing — not deleting its rounds", file=sys.stderr)
        return 2
    num = re.match(r"(ch\d+)", args.draft.name).group(1)
    rounds = sorted(p for p in approved.parent.glob(f"{num}-*")
                    if p.is_file() and p.suffix.lower() in IMAGE_EXT and p.resolve() != approved.resolve())
    for p in rounds:
        if not args.dry_run:
            p.unlink()
        print(f"{'would delete' if args.dry_run else 'deleted'}: {p}")
    print(f"{len(rounds)} round file(s); kept {approved}")
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
    rows = ledger_rows()
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
    s.add_argument("--every-days", type=float, help="fixed interval; overrides --per-week")
    s.add_argument("--weekdays", type=parse_weekdays, help="publishing days, e.g. mon-fri; overrides --per-week")
    n = sub.add_parser("next-slot")
    n.add_argument("--platform", required=True)
    g = n.add_mutually_exclusive_group(required=True)
    g.add_argument("--every-days", type=int)
    g.add_argument("--weekdays", type=parse_weekdays, help="publishing days, e.g. mon-fri or mon,wed,fri")
    n.add_argument("--after", help="count from this date (YYYY-MM-DD) instead of the ledger's last")
    n.add_argument("--count", type=int, default=1, help="how many consecutive slots to list")
    n.add_argument("--time", default="19:00", help="readers' local time, HH:MM")
    n.add_argument("--tz", default="UTC", help="readers' time zone, e.g. Europe/Moscow")
    n.add_argument("--min-ahead", type=int, default=60, help="minutes a slot must be ahead of now")
    c = sub.add_parser("cleanup-rounds")
    c.add_argument("draft", type=Path)
    c.add_argument("--dry-run", action="store_true")
    r = sub.add_parser("record")
    r.add_argument("draft", type=Path)
    r.add_argument("--platform", required=True)
    r.add_argument("--url", required=True)
    r.add_argument("--date")
    rs = sub.add_parser("reschedule")
    rs.add_argument("draft", type=Path)
    rs.add_argument("--platform", required=True)
    rs.add_argument("--date", required=True, help="new publication date, YYYY-MM-DD")
    e = sub.add_parser("errata-check")
    e.add_argument("draft", type=Path)
    e.add_argument("--platform", required=True)
    sub.add_parser("lint")
    args = ap.parse_args()
    if getattr(args, "draft", None) and not args.draft.is_file():
        print(f"not a file: {args.draft}", file=sys.stderr)
        return 3
    return {"status": cmd_status, "record": cmd_record, "errata-check": cmd_errata,
            "lint": cmd_lint, "next-slot": cmd_next_slot, "reschedule": cmd_reschedule,
            "cleanup-rounds": cmd_cleanup_rounds}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
