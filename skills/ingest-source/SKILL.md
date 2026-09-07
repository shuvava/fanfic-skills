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

Follow `../../CONVENTIONS.md`. **All output is written in `wiki_language` from
`CANON.md`; verbatim quotations are copied exactly from `raw/` and never translated.**

## Before starting

1. Read `CANON.md` — conventions and language settings, including which source volume this material
   belongs to. Every `[src:]` you write carries the volume directory when `raw/` holds more than one
   (`../../CONVENTIONS.md` §4, §8); a bare `ch<NN>.md` in a multi-volume project is unresolvable.
2. Read `wiki/index.md` — what already exists.
3. Read the last few `wiki/log.md` entries — what was recently ingested.
4. **Check the log for this source.** Never ingest the same source twice; it duplicates claims and
   inflates confidence in things canon said once.

## The six extraction buckets

See `references/extraction-checklist.md` for full field lists and page templates.

### 1. Characters → `wiki/canon/characters/<name>.md`
Identity, physical traits, personality (strengths, flaws, fears, values), the want/need split,
backstory revealed, relationships and how behavior shifts per person, arc position, mannerisms.

**Use the template in `references/extraction-checklist.md` §1 verbatim — every heading, in order,
including the ones you have nothing for.** Write `не установлено` under an empty heading. An absent
heading and an empty heading look identical on the page and mean opposite things: one is a gap in
the wiki, the other is a gap in the world. Do not rename headings, merge them, or invent new ones;
`wiki-lint` checks for the exact set.

**One character, one page, once they have three or more canon facts.** Grouping minor characters
into a composite page (`characters/семья.md` with a row per person) is fine while each is a name and
a relation — but the moment canon gives one of them appearance, personality, and habits, a table cell
cannot hold them. In a real run a newly named sister arrived with hair, build, age, four personality
traits, and two physical mannerisms; she was written as one row of a family table, and **the
mannerisms were the part that vanished, because the composite page has no `## Mannerisms` slot to
drop them into.** The page shape decides what survives extraction. Split her out, leave a one-line
pointer in the composite page, and note the split in the report.

**The `## Would never do` section is the highest-value part of the page and the most commonly
skipped.** Every time canon shows a character refusing, declining, or holding a line under pressure,
that is evidence. Record it with a citation.

An observation is not a refusal. "Feels uncomfortable and says nothing" belongs under Personality;
this section is for lines held *under pressure*. Filling it with soft inferences is worse than
leaving it thin, because `plan-chapters` treats every row here as a hard behavioral constraint.

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

**This applies to social rules exactly as it does to physical ones. When canon explains *why* a
friction exists, record the mechanism, not just the outcome.** "Brawls break out at markets" is an
outcome a drafter can stage anywhere; "landed commoners rank townsfolk beneath them, townsfolk
consider themselves equal, and the two meet at markets" is a mechanism that says which scenes can
carry the brawl and which cannot. A summarizer under compression keeps outcomes and drops causes —
the outcome is the vivid part — and the resulting page reads complete while having lost the half
that constrains anything.

Then rebuild the two **derived** pages. Both carry `derived: true` and are regenerated from the topic
pages after every ingest — never edited by hand, never a source of new claims:

**`world/география.md`** — the spatial model. A locations table (place, type, relation to other
places, distance or travel time, citation) plus a rough relation sketch. Scattered topic pages
describe places; nothing describes how they *relate*, so "he rode there in a day" cannot be checked
against "the messenger took a week" until someone writes the contradiction.

Record what canon states and leave the rest empty. **An empty cell is a fact about the wiki, not
about the world** — it is the list of what to settle before planning, and filling it with a plausible
distance converts a known gap into invented canon. Note explicitly which units of distance and time
canon has named; if none, say so, because prose will otherwise invent leagues and weekdays.

**`world/constraints.md`** — the flat ledger of what the world does *not* permit: one row per rule
with its limit/cost and citation, aggregated across every world page. `plan-chapters` reads this
first. Checking an outline against eight prose pages is expensive enough to get skipped; checking it
against one table is not.

It needs a second section — **what canon does not establish** — listing the silences (no magic shown,
no other monsters in frame, no economy). Absence of a rule reads as permission to a drafting model.
Naming the silences is what turns them into a `notice` instead of a free pass.

### 4. Plot state → `wiki/canon/plot/<source>.md`
Summary, events in order, threads opened, threads closed, foreshadowing planted and unpaid.
Then update `plot/threads.md` (the ledger) and `plot/timeline.md`.

### 5. Narrative mechanics → `wiki/canon/overview.md`
POV person, tense, narrative distance, whose head we may enter, chapter and scene structure, how
chapters open and close, tone words, themes, motifs, and **style and spelling conventions** — invented
name spellings, capitalization, how thoughts and letters are formatted, and any orthographic
conventions specific to the source language. Top continuity trap; record explicitly.

**Measure these; do not estimate them.** Run:

```bash
python3 <scripts>/style_fingerprint.py measure raw/ch01.md raw/ch02.md ...   # ingested only
```

`<scripts>` is resolved at run time — see `../../CONVENTIONS.md` §7. It is **not** `../../scripts/`:
bash paths resolve against the project root, not against this file.

**Measure the ingested chapters only — never `raw/*.md`.** The glob covers the whole book, including
everything the wiki has not read, and the resulting numbers describe a corpus that does not exist
anywhere in the wiki. In a real run, `measure raw/*.md` over an unsplit 73-chapter file reported
chapter length as 85,481 words after six chapters had been ingested; that value was written into
`overview.md` as the target drafted prose would later be checked against.

This also keeps the fingerprint *honest as it grows*: after six chapters it describes six chapters,
and re-running it after each ingest sharpens it with material the wiki can actually cite.

Record the span in the table's header line, so a stale fingerprint is visible rather than silent:

```markdown
## Style fingerprint
<!-- measured over: ch01–ch06 (6 of 73 chapters ingested), YYYY-MM-DD -->
```

If the source was never split (`raw_layout: single-file` in `CANON.md`), say so in that comment and
treat chapter length as unmeasured rather than reporting the file's word count as a chapter's.

It prints the `## Style fingerprint` table ready to paste, plus candidate spellings to adjudicate.
Standard library only, works in any language. Re-run it as `raw/` grows — the numbers sharpen.

Two subsections of this page are load-bearing and both must be **counted, not described**:

- **`## Style fingerprint`** — a table of measured values: chapter length in words, the per-1000-word
  frequency of each punctuation habit that reads as a tic, the literal form of the dialogue marker.
  Adjectives do not transfer. A note reading "uses ellipsis heavily" was satisfied by prose carrying
  a quarter of the source's ellipsis density, because nothing in the note could be checked.
- **`## Non-standard orthography`** — every place the source departs from standard spelling or
  punctuation, each with its count and the instruction not to "correct" it. **A drafting model will
  silently repair the author back to the standard.** If the author writes a postfix particle
  unhyphenated hundreds of times, that is the author's norm and the page must say so in those terms.

  The script's *Candidates to adjudicate* section is the input to this, not the answer. It counts;
  **you decide**, because whether a form is non-standard is a fact about the language rather than
  about the text, and you know the language. Read the candidate lists — especially the grouped
  "short tokens that follow many different words", which is what a postfix particle looks like from
  the outside — and record the ones that genuinely depart from the standard.

See `references/extraction-checklist.md` §5 for both templates.

### 6. Forbidden → `wiki/canon/forbidden.md`
Anything this source establishes that a continuation must not violate.

## Citation and contradiction discipline

Every claim gets `[src: <file>#<location>]`, or `(inferred)` if reasoned rather than read.

When a new source contradicts an existing page, **do not silently overwrite.** Add the new claim, keep
the old, record both under `## Contradictions` with citations. The user adjudicates.

## Finishing

1. **Rebuild the derived pages** — `world/география.md` and `world/constraints.md` — and bump their
   `sources_ingested`. They are regenerated from the topic pages, never hand-edited. Skipping this is
   how `plan-chapters` ends up linting against a world two ingests out of date.
2. Update `wiki/index.md` — every new or changed page, one line each.
3. Append to `wiki/log.md`: `## [YYYY-MM-DD] ingest | <source>` plus pages touched.
4. Report to the user (in their language): what was learned, pages changed, contradictions surfaced,
   and what questions the source raised that the wiki still cannot answer. **Include the new gaps
   the derived pages exposed** — an unmapped place, a rule with no limit, a silence a plot might
   lean on. Those are the cheapest findings the ingest produces.

## Rules

- **No completion claim without fresh evidence** — `../../CONVENTIONS.md` §10. "Cited" means the
  `[src:]` path resolves against `raw/` as written; test it, do not assume the shape is right.
- **Never edit or translate anything in `raw/`.**
- **Never write outside `wiki/canon/`.** Ingest produces canon and nothing else.
- **Never fill a section with plausible filler.** "Not established in ingested sources" is a correct
  and useful entry.
- Prefer many small ingests to one large one. Read long sources in bounded spans and write
  incrementally.

## Reference

`references/extraction-checklist.md` — complete capture list and page templates.
