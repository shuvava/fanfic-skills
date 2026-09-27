---
name: publish
description: >
  Serialise the fic while it is still being written: gate the next chapter, export it in the
  platform's format, publish it (the user confirms every publication), record what readers got,
  and push typo-only errata. Use when the user says "publish the next chapter", "publish chapter
  5", "what's published", "fix a typo in the published chapter", "опубликуй главу", "выложи
  следующую главу", "что уже опубликовано", "исправь опечатку в опубликованной", "update the
  annotation", "обнови аннотацию", or a scheduled publishing run starts. Platforms: author.today
  now; one adapter per platform.
---

# Publish

Readers remember what they read. A published chapter outranks the draft and the outline, and its
text changes only by errata — typos, never rewrites.

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
  schedule:                         # optional: delayed publication on a fixed interval
    every_days: 2                   # one chapter every N days, counted from the last on the ledger
    time: "19:00"                   # readers' local time
    tz: Europe/Moscow               # readers' time zone — not the browser's
  after_record:                     # optional: what closing a run does without asking
    mark_outline: true              # note the chapter as published in the book's outline
    cleanup_rounds: true            # delete the chapter's intermediate illustration rounds
    commit: true                    # commit the project repo
  author-today:
    work_edit_url: https://author.today/work/<workId>/edit/content
```

`schedule` replaces `per_week` for the buffer (`7 / every_days` chapters a week). `after_record` is
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
```

It lists chapters in order with the published version, **DRIFTED** where the draft changed after
publication, the stages `wiki/log.md` records for each (`write✓ reconcile✗ naturalize✓`), the next
chapter, and the buffer — drafted, unpublished chapters in weeks at the cadence. Report the table.
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
| Illustration | `illustration:` in frontmatter if `plan/illustration/` has an approved image for this chapter | `warning` — offer `illustrate` step 14 first; after publication the picture is locked out |

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
  --tz Europe/Moscow
```

It counts from the latest date on the ledger — a delayed chapter whose timer has not fired counts —
adds the interval, and moves to the first slot still ahead if publishing stalled. It prints the
readers' local time and the UTC moment the platform's timer takes. The user's request to publish
the next chapter, with the standing schedule, is the yes for that slot; say the date in the report.
A date the user names outranks the slot. A time the user did not give is `schedule.time`, and the
report says it was the default.

### 5. Record

After the user confirms the chapter is live and gives or confirms its URL:

```bash
python3 <scripts>/publication.py record drafts/book-01/ch05-<slug>.md --platform author-today \
  --url <chapter url>
```

It freezes the draft into `snapshots/ch05-published-author-today-v1.md`, adds the `published:`
entry to the draft's frontmatter, and appends a ledger row. For a delayed publication pass
`--date <timer date>`. Then append to `wiki/log.md`:

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

## Errata — typos only

The user edits the published chapter's draft, then:

```bash
python3 <scripts>/publication.py errata-check drafts/book-01/ch05-<slug>.md --platform author-today
```

It diffs the reader-visible text against the last published version and sorts every change into
**typo** (one misspelt word, a punctuation mark, a split or merged word) or **REWRITE** (anything
that changes wording, adds or removes a word, or touches paragraph count). Exit 1 on any rewrite.

- **Rewrites do not go out.** Show them; the user reverts them or keeps them for a later edition —
  this project publishes typo-only.
- **Non-standard orthography is not a typo.** `canon/overview.md` `## Non-standard orthography`
  records the author's deliberate forms (`какой то`, `кому нибудь`). The script passes
  `кому нибудь → кому-нибудь` as typo-sized; you must not. Check every typo row against that list
  and drop any "fix" of a recorded form — a reader's correction included.
- Then export, put the new text on the platform (same flow, editing the existing chapter), verify,
  get the user's yes, and `record` — which writes `v<N+1>`. Log it as `publish | b<NN>/ch<NN> errata
  → author-today v<N+1>` with `typos=<n>`.
- If `translations/` exists, the chapter's translations are now stale: `translation.py status`, then
  `translate` updates only the changed blocks.

## Lint

```bash
python3 <scripts>/publication.py lint
```

Cross-checks frontmatter, snapshots and ledger, and reports every published chapter whose draft
changed since. `wiki-lint` runs it too.

## Rules

- **The user makes every chapter public.** Ask per chapter; scheduled runs stop before publishing.
  A standing `schedule` sets the date, never the decision to publish.
- **Never sign in or handle credentials.** The user's Chrome session is theirs.
- **In order, no skips.** The script enforces it; do not work around it with a hand-edited ledger.
- **Published text changes only through errata**, and errata are typo-only.
- **No completion claim without the script's output** — `round-trip: identical`, `verify`'s result,
  `record`'s lines — pasted in the report (§10).
- **Plugin files stay book-agnostic.** A lesson from a run goes into the adapter as a platform fact
  or a flow step; the run's specifics go into the project's `publish/platforms/<platform>.md`.
- Content on the site follows the platform's rules; the user is the publisher of record.
