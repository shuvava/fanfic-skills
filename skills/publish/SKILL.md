---
name: publish
description: >
  Use when ONLY when the user says "publish the next chapter", "publish chapter N",
  "upload chapter N", "publish a typo-only errata", "what's published", "обнови аннотацию",
  "опубликуй главу", "выложи главу", "что уже опубликовано", "исправь опечатку", or a
  scheduled publish run starts. The user confirms every publication — the subagent prints
  a question and waits for a clear yes before going live. Do NOT use for a book cover image —
  that's cover. Do NOT use to audit a chapter against canon — that's reconcile.
---

# Publish

## Mode
Subagent. Verified across 24 real publish runs in 23 sessions: 71% pure fire-and-forget,
17% brief acknowledgement, 0% mid-run interruptions, 4% mid-run text question (handled
internally). Each publication is gated by an explicit user yes before going live.

## Inputs required
- The chapter draft at `<book>/drafts/ch<NN>-<slug>.md` (with `published:` frontmatter)
- `<book>/outline.md` (to update the published note)
- `wiki/log.md` (to verify `write✓ reconcile✓ naturalize✓` stages for the gate)
- `publish/platforms/<platform>.md` (the work's per-platform notes)
- `references/platforms/<platform>.md` (the adapter — author.today for now)
- For typo errata: the live chapter URL

## Persistent state
- `publish/LEDGER.md` — one row per publication, written by `publication.py record`
- `publish/platforms/<platform>.md` — updated with posted annotation, run notes
- `publish/exports/<platform>/b<NN>-ch<NN>.html` (+ `.json` sidecar) — what was uploaded
- `publish/readback/<platform>/b<NN>-ch<NN>.txt` — verification result
- `<book>/drafts/snapshots/ch<NN>-published-<platform>-v<N>.md` — frozen published snapshot
- `<book>/drafts/ch<NN>-<slug>.md` `published:` frontmatter — entry added on record
- `wiki/log.md` — append the `publish | …` line

Readers remember what they read. A chapter that has gone out (**live**) outranks the draft and the
outline, and its text changes only by errata — typos, never rewrites. A chapter on a timer that has
not fired (**queued**) has no readers yet: at the user's request it is rewritten and re-uploaded
under the same timer (Editing a queued chapter, below).

Follow `../../CONVENTIONS.md`, especially §8 (book scope), §10 (completion claims) and §13
(publication). Platform specifics live in one adapter per platform:

| Platform | Adapter | Status |
|---|---|---|
| author.today | [references/platforms/author-today.md](references/platforms/author-today.md) | export, records, browser flow and delayed publication built |

## Settings

`CANON.md`, added on first run (say so):

```yaml
publishing:
  platforms: [author-today]
  per_week: 2                       # cadence; sets the buffer warning
  chapter_title: "{heading} {title}"  # draft heading + frontmatter title: "Глава 3. <title>"
  schedule:                         # optional: delayed publication on a fixed schedule
    every_days: 2                   # one chapter every N days, counted from the last on the ledger
    # weekdays: mon-fri             # or: on these days only (mon-fri, mon,wed,fri); replaces every_days
    time: "19:00"                   # readers' local time
    tz: Europe/Moscow               # readers' time zone — not the browser's
  after_record:                     # optional: what closing a run does without asking
    mark_outline: true              # note the chapter as published in the book's outline
    cleanup_rounds: true            # delete the chapter's intermediate illustration rounds
    commit: true                    # commit the project repo
  author-today:
    work_edit_url: https://author.today/work/<workId>/edit/content
```

`schedule` replaces `per_week` for the buffer (`7 / every_days` chapters a week, or the number of
`weekdays`). Pass the schedule's key to the script as `--every-days N` or `--weekdays <days>`. `after_record` is
the user's standing permission for those three steps; without it each is offered, not done.

**The plugin knows platforms; the project knows its book.** The adapter holds what is true of the
platform for every project. Everything about *this* work — its ids and URLs, the user's decisions
(cadence, images, errata policy), what past runs observed (chapter ids, counters, read-back
results) — goes in the project's `publish/platforms/<platform>.md`, created on first run. Read it
after the adapter; never write a work id, chapter id, title or run date into the plugin.

Everything this skill writes lives under `publish/` at the project root, plus the two records it
keeps on each draft (§13): the frontmatter `published:` list and
`<drafts>/snapshots/ch<NN>-published-<platform>-v<N>.md`.

```
publish/
  LEDGER.md                                  # one row per publication, written by the script
  platforms/<platform>.md                    # this work on that platform: ids, decisions, run notes
  exports/<platform>/b<NN>-ch<NN>.html|.txt  # what was pasted, + .json sidecar (title, images)
  readback/<platform>/b<NN>-ch<NN>.md        # read-back result: paragraphs, characters, diffs
```

Resolve `<scripts>` per §7. All commands run from the project root.

## Status — "what's published", and the start of every run

```bash
python3 <scripts>/publication.py status --platform author-today --per-week 2
python3 <scripts>/publication.py status --platform author-today --every-days 2   # with `schedule`
python3 <scripts>/publication.py status --platform author-today --weekdays mon-fri
```

It lists chapters in order with the published version, **live** or **queued** (timer not fired),
**DRIFTED** where the draft changed after the last upload, the stages `wiki/log.md` records for each (`write✓ reconcile✗ naturalize✓`), the next
chapter, and the buffer — chapters on timers that have not fired plus drafted, unpublished ones, in
weeks at the cadence. Report the table.
Under one week of buffer, say so plainly: the schedule is about to overtake the writing.
Also compare the annotation on the site with the book's `SYNOPSIS.md` (Book page, below), and say
if they differ.

## Book page — the annotation

The annotation is the first text a reader sees, before any chapter. It comes from the `## Annotation`
section of the book's `SYNOPSIS.md`. **Never use `## Synopsis`**: it contains the ending. If there is
no `SYNOPSIS.md`, offer `plan-chapters` → Synopsis and annotation first. Do not write an annotation
here: text that no outline check has seen is how a blurb ends up promising a book that does not
exist.

1. Check for spoilers against the reveal section of every profile the annotation mentions, the same
   check as the gate below. The reader sees it before chapter 1.
2. Show the text with its character count and the platform's limit from the adapter. **Ask the user
   and wait for a yes.** The annotation is public.
3. Put it on the platform by the adapter's flow, then read it back.
4. Record the posted text and date under `## Annotation on the site` in the project's
   `publish/platforms/<platform>.md`. Status compares against this record.

Changing the annotation later is not errata. It is not chapter text, and it may change when the
outline changes. But it is public, so every change needs the user's yes. When the outline turns in
a direction the posted annotation no longer describes, say so. An annotation that promises a
different book loses exactly the readers it attracted.

## Publish the next chapter

Always the **next** chapter — the script refuses to record one out of order. A request for a later
chapter is answered with which earlier ones are still unpublished.

### 1. Gate

Every row is evidence from this session (§10), not memory:

| Check | How | Fails → |
|---|---|---|
| Canon check passed | the chapter's **latest** `write` log entry: `blocking=0` in its metrics, or its checks written out in the entry's lines (fingerprint in band, facts checked). Older entries do not count — a rewrite resets the check. No evidence either way → ask | `blocking` — run `write-chapter` §5 |
| Reconciled | `reconcile✓` in status. Every fact a reader sees must be ratified fanon: a public invention that later gets "fixed" is a continuity error readers notice | `blocking` — run `reconcile` for this chapter |
| Naturalness reviewed | `naturalize✓`, unless `naturalness: off` | `warning` — the user may publish anyway |
| No drift in earlier chapters | status shows no DRIFTED | `blocking` — errata or restore first |
| Spoilers | the chapter against the reveal section of every profile it mentions — `## Reveal schedule`, or its `wiki_language` name (`## Раскрытие читателю`) — in `wiki/fanon/proposed/characters/`; its picture per `illustrate` step 3. A hint earlier than scheduled is noted in that profile, so later chapters do not re-reveal it | `warning` — the user decides |
| Book page | first chapter only: the project's platform notes record an annotation on the site | `warning` — offer Book page above. The first chapter makes the work visible, and a work page without an annotation is one readers skip |
| Illustration | `illustration:` in frontmatter if `plan/illustration/` has an approved image for this chapter; with `illustration_required` true in `CANON.md` for the chapter's book (per-book setting, §8), the key must be there whether or not an image exists | `warning` — offer `illustrate` step 14 first; after publication the picture is locked out. **`blocking`** where `illustration_required` is true for the chapter's book, or `planned` and the outline row has a `picture` — run `illustrate` Phase 3. Under `planned` with no `picture` in the row: no check |

Report the table. A `blocking` row stops the run; say what to run.

### 2. Export and round-trip

```bash
python3 <scripts>/export_chapter.py export drafts/book-01/ch05-<slug>.md --platform author-today \
  --out publish/exports/author-today/b01-ch05.html --title-format "{heading} {title}"
```

It strips frontmatter, markdown escapes and the heading, turns image lines into `<img>` at their
place, writes a `.json` sidecar with the title, paragraph and word counts and the image files, and
reports `round-trip: identical` — the export's text equals the draft's. Anything else, or `MISSING
image files`, stops the run: fix the cause, never hand-edit the export.

### 3. Put it on the platform

Follow the adapter's `## Flow`. Without a browser, or when the user prefers, they publish by hand:
hand them the title, the export path and the image files in order from the sidecar, and wait for
the chapter's URL. The HTML export's image paths are relative to the export, so opening it in a
browser shows the chapter with its picture — select all, copy, paste into the platform's editor; a
`plain` export (`--platform plain`) is the fallback for editors that drop formatting.

The flow runs in the user's own Chrome (Claude in Chrome), which is already signed
in. **Never sign in, never type a password**: signed out → stop and ask the user to sign in.
Upload as an unpublished draft first, then read the text back into
`publish/readback/<platform>/b<NN>-ch<NN>.txt` and verify it:

```bash
python3 <scripts>/export_chapter.py verify drafts/book-01/ch05-<slug>.md \
  --against publish/readback/author-today/b01-ch05.txt
```

A difference is reported line by line; an editor's autocorrect (quotes, dashes) shows up here, not
in a reader's comment.

### 4. Publish — the user's yes, every time

Making a chapter public is the user's action. **Ask in chat, per chapter, and wait for a clear yes**
— "publish b01/ch05 now?" with the title, word count and the verify result. A yes for one chapter
is not a yes for the next. A **scheduled run never publishes**: it runs status, the gate, the export
and the upload as a draft, then stops and tells the user the chapter is ready for their yes. If the
platform has its own delayed publication, the user may approve a date in chat and the run sets it
— that approval is the yes.

**Fixed interval.** With `publishing.schedule` set and no date in the user's request, the date is
the next slot, not a question:

```bash
python3 <scripts>/publication.py next-slot --platform author-today --every-days 2 --time 19:00 \
  --tz Europe/Moscow                                    # or --weekdays mon-fri
```

It counts from the latest date on the ledger — a delayed chapter whose timer has not fired counts —
takes the schedule's next day, and moves to the first slot still ahead if publishing stalled. It prints the
readers' local time and the UTC moment the platform's timer takes. The user's request to publish
the next chapter, with the standing schedule, is the yes for that slot; say the date in the report.
A date the user names outranks the slot. A time the user did not give is `schedule.time`, and the
report says it was the default.

### Changing the schedule

A new cadence is the user's decision; they name it and the chapter it starts from. Chapters already
on timers keep their dates unless the user asks to move them too. Then:

1. Update `publishing.schedule` (and `per_week`) in `CANON.md`.
2. List the new dates for the queued chapters, counting from the date of the last chapter that keeps
   its timer:
   ```bash
   python3 <scripts>/publication.py next-slot --platform author-today --weekdays mon-fri \
     --after <last kept date> --count <queued chapters> --time 19:00 --tz Europe/Moscow
   ```
   Show the table (chapter, old date, new date) — that table, approved, is the yes for every move in it.
3. Move each timer on the site (the adapter's **Moving a timer**), confirm the saved time, then:
   ```bash
   python3 <scripts>/publication.py reschedule drafts/book-01/ch14-<slug>.md --platform author-today \
     --date <new date>
   ```
   It rewrites the date in the draft's `published:` entry and its ledger row, and refuses a timer that
   has already fired. Move one chapter at a time, site first, so a failure leaves records and site in
   step. Earlier dates first when moving forward; later first when moving back — the order on the
   site never inverts.
4. Update the outline's published note, log `## [date] publish | schedule → <cadence> from b<NN>/ch<NN>`
   with the moves, and commit.

### 5. Record

After the user confirms the chapter is live and gives or confirms its URL:

```bash
python3 <scripts>/publication.py record drafts/book-01/ch05-<slug>.md --platform author-today \
  --url <chapter url>
```

It freezes the draft into `snapshots/ch05-published-author-today-v1.md`, adds the `published:`
entry to the draft's frontmatter, and appends a ledger row. For a delayed publication pass
`--date <timer date>`. A queued chapter re-recorded after a re-upload keeps its timer date on its
own; a different `--date` is refused — move the timer with `reschedule`. Then append to `wiki/log.md`:

```
## [YYYY-MM-DD] publish | b<NN>/ch<NN> <title> → author-today v1
   metrics: words=<n> images=<n> verify=identical|manual buffer_weeks=<n.n> url=<url>
```

### 6. Close the run

Each step runs without asking when `publishing.after_record` enables it; otherwise offer it in one
line.

1. **Mark the outline** (`mark_outline`). The book's `outline.md` carries a published note next to
   the chapter list (`CONVENTIONS.md` §13 — published text outranks the plan). Add this chapter with
   its platform, date and, for a timer, the time: «гл. 7 — 2026-09-30 (по таймеру, 19:00 МСК)».
   Edit the existing note; create one under the block's heading if there is none.
2. **Delete illustration rounds** (`cleanup_rounds`), only after the approved image is placed:
   ```bash
   python3 <scripts>/publication.py cleanup-rounds drafts/book-01/ch05-<slug>.md
   ```
   It deletes the `ch<NN>-*` image files beside the draft's `illustration:` image and keeps that
   one; prompt and edit files (`.md`) stay — they are the illustration's history. Also clear this
   run's scratch files.
3. **Commit the project** (`commit`) — only if the project is a git repo. Stage the files this run
   and the chapter's earlier stages created or changed (draft, snapshots, beats, reviews,
   illustration files, exports, read-back, ledger, platform notes, wiki, outline); list them first
   and never stage `.env` or anything `.gitignore` excludes. One commit per chapter, message
   `Publish b<NN>/ch<NN> «<title>» on <platform>` plus the timer date if delayed. Never push unless
   the user asks.

## Editing a queued chapter, errata, and lint

The three side flows — re-uploading a queued chapter under its existing timer, pushing typo-only errata to a live chapter, and the publication lint — live in [references/scenarios.md](references/scenarios.md). Read that file before running any of them.

## Rules

- **The user makes every chapter public.** Ask per chapter; scheduled runs stop before publishing.
  A standing `schedule` sets the date, never the decision to publish.
- **Never sign in or handle credentials.** The user's Chrome session is theirs.
- **In order, no skips.** The script enforces it; do not work around it with a hand-edited ledger.
- **Live text changes only through errata**, and errata are typo-only. A queued chapter changes
  only when the user asks, and goes back under the same timer.
- **No completion claim without the script's output** — `round-trip: identical`, `verify`'s result,
  `record`'s lines — pasted in the report (§10).
- **Plugin files stay book-agnostic.** A lesson from a run goes into the adapter as a platform fact
  or a flow step; the run's specifics go into the project's `publish/platforms/<platform>.md`.
- Content on the site follows the platform's rules; the user is the publisher of record.
