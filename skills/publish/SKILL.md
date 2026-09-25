---
name: publish
description: >
  Serialise the fic while it is still being written: gate the next chapter, export it in the
  platform's format, publish it (the user confirms every publication), record what readers got,
  and push typo-only errata. Use when the user says "publish the next chapter", "publish chapter
  5", "what's published", "fix a typo in the published chapter", "опубликуй главу", "выложи
  следующую главу", "что уже опубликовано", "исправь опечатку в опубликованной", or a scheduled
  publishing run starts. Platforms: author.today now; one adapter per platform.
---

# Publish

Readers remember what they read. A published chapter outranks the draft and the outline, and its
text changes only by errata — typos, never rewrites.

Follow `../../CONVENTIONS.md`, especially §8 (book scope), §10 (completion claims) and §13
(publication). Platform specifics live in one adapter per platform:

| Platform | Adapter | Status |
|---|---|---|
| author.today | [references/platforms/author-today.md](references/platforms/author-today.md) | export, records and browser flow built; delayed publication **not yet mapped** |

## Settings

`CANON.md`, added on first run (say so):

```yaml
publishing:
  platforms: [author-today]
  per_week: 2                       # cadence; sets the buffer warning
  chapter_title: "{heading} {title}"  # draft heading + frontmatter title: "Глава 3. <title>"
  author-today:
    work_edit_url: https://author.today/work/<workId>/edit/content
```

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
```

It lists chapters in order with the published version, **DRIFTED** where the draft changed after
publication, the stages `wiki/log.md` records for each (`write✓ reconcile✗ naturalize✓`), the next
chapter, and the buffer — drafted, unpublished chapters in weeks at the cadence. Report the table.
Under one week of buffer, say so plainly: the schedule is about to overtake the writing.

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

### 5. Record

After the user confirms the chapter is live and gives or confirms its URL:

```bash
python3 <scripts>/publication.py record drafts/book-01/ch05-<slug>.md --platform author-today \
  --url <chapter url>
```

It freezes the draft into `snapshots/ch05-published-author-today-v1.md`, adds the `published:`
entry to the draft's frontmatter, and appends a ledger row. Then append to `wiki/log.md`:

```
## [YYYY-MM-DD] publish | b<NN>/ch<NN> <title> → author-today v1
   metrics: words=<n> images=<n> verify=identical|manual buffer_weeks=<n.n> url=<url>
```

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

## Lint

```bash
python3 <scripts>/publication.py lint
```

Cross-checks frontmatter, snapshots and ledger, and reports every published chapter whose draft
changed since. `wiki-lint` runs it too.

## Rules

- **The user makes every chapter public.** Ask per chapter; scheduled runs stop before publishing.
- **Never sign in or handle credentials.** The user's Chrome session is theirs.
- **In order, no skips.** The script enforces it; do not work around it with a hand-edited ledger.
- **Published text changes only through errata**, and errata are typo-only.
- **No completion claim without the script's output** — `round-trip: identical`, `verify`'s result,
  `record`'s lines — pasted in the report (§10).
- **Plugin files stay book-agnostic.** A lesson from a run goes into the adapter as a platform fact
  or a flow step; the run's specifics go into the project's `publish/platforms/<platform>.md`.
- Content on the site follows the platform's rules; the user is the publisher of record.
