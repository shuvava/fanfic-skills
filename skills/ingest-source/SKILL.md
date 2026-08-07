---
name: ingest-source
description: >
  Read source material (a chapter, novel, transcript, or supplementary text) and compile it into the
  canon tier of the wiki — character pages, voice cards with verbatim dialogue, world rules, plot state,
  and the forbidden list. Use when the user says "ingest chapter 3", "process this book", "add this
  source to the wiki", "extract the canon", or drops new material into raw/. Writes only to wiki/canon/.
---

# Ingest Source

Compile one source chunk into the canon tier. A single ingest typically touches 8–15 pages.

Follow `${CLAUDE_PLUGIN_ROOT}/CONVENTIONS.md`. **All output is written in `wiki_language` from
`CANON.md`; verbatim quotations are copied exactly from `raw/` and never translated.**

## Before starting

1. Read `CANON.md` — conventions and language settings.
2. Read `wiki/index.md` — what already exists.
3. Read the last few `wiki/log.md` entries — what was recently ingested.
4. **Check the log for this source.** Never ingest the same source twice; it duplicates claims and
   inflates confidence in things canon said once.

## The six extraction buckets

See `references/extraction-checklist.md` for full field lists and page templates.

### 1. Characters → `wiki/canon/characters/<name>.md`
Identity, physical traits, personality (strengths, flaws, fears, values), the want/need split,
backstory revealed, relationships and how behavior shifts per person, arc position, mannerisms.

**The `## Would never do` section is the highest-value part of the page and the most commonly
skipped.** Every time canon shows a character refusing, declining, or holding a line under pressure,
that is evidence. Record it with a citation.

### 2. Voice → `wiki/canon/voices/<name>.md`

**Extract dialogue verbatim in the source language. Never paraphrase, never translate.** Pull at
least five representative lines per major character — lines that really show who they are. Then
analyze, writing the analysis in `wiki_language`:

- **Vocabulary** — actual words, register, syllable length, how likely each is in casual speech
- **Cultural touchpoints** — references, slang, era markers, how in or out of sync with peers
- **Willingness to speak plainly** vs. deflect
- **Volume** — talkative or reticent
- **Code-switching** — how speech shifts per interlocutor, including literal language switches
- **Fluency and accent** — note it; never phonetically spell out an accent in generated prose
- **Verbal tics** — cap at three; more makes a caricature

Then invert: rewrite two or three verbatim lines a *different* way (in the source language) and record
why the character would not say it that way. Knowing what they would not say is as important as
knowing what they would, and this table is what prevents voice drift at drafting time.

**Language-specific features to capture** where the source language has them: formal/informal address
(ты/вы, tu/vous, 敬語), grammatical gender in self-reference, diminutives, honorifics, particles,
verb aspect habits, dialect markers. These carry enormous characterization weight and are invisible if
the card is written in English.

### 3. World rules → `wiki/canon/world/<topic>.md`
The rule **and its limits and costs** — limitations matter more than powers. A rule with no recorded
limit is a rule the writer can cheat with. Also: geography, culture, politics, history, daily-life
texture, technology level.

### 4. Plot state → `wiki/canon/plot/<source>.md`
Summary, events in order, threads opened, threads closed, foreshadowing planted and unpaid.
Then update `plot/threads.md` (the ledger) and `plot/timeline.md`.

### 5. Narrative mechanics → `wiki/canon/overview.md`
POV person, tense, narrative distance, whose head we may enter, chapter and scene structure, how
chapters open and close, tone words, themes, motifs, and **style and spelling conventions** — invented
name spellings, capitalization, how thoughts and letters are formatted, and any orthographic
conventions specific to the source language. Top continuity trap; record explicitly.

### 6. Forbidden → `wiki/canon/forbidden.md`
Anything this source establishes that a continuation must not violate.

## Citation and contradiction discipline

Every claim gets `[src: <file>#<location>]`, or `(inferred)` if reasoned rather than read.

When a new source contradicts an existing page, **do not silently overwrite.** Add the new claim, keep
the old, record both under `## Contradictions` with citations. The user adjudicates.

## Finishing

1. Update `wiki/index.md` — every new or changed page, one line each.
2. Append to `wiki/log.md`: `## [YYYY-MM-DD] ingest | <source>` plus pages touched.
3. Report to the user (in their language): what was learned, pages changed, contradictions surfaced,
   and what questions the source raised that the wiki still cannot answer.

## Rules

- **Never edit or translate anything in `raw/`.**
- **Never write outside `wiki/canon/`.** Ingest produces canon and nothing else.
- **Never fill a section with plausible filler.** "Not established in ingested sources" is a correct
  and useful entry.
- Prefer many small ingests to one large one. Read long sources in bounded spans and write
  incrementally.

## Reference

`references/extraction-checklist.md` — complete capture list and page templates.
