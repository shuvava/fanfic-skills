---
name: wiki-lint
description: >
  Health-check the wiki — tier violations, uncited claims, contradictions, thin voice cards, language
  drift, orphan pages, stale threads. Use when the user says "lint the wiki", "check the story bible",
  "audit the wiki", "is my wiki healthy", or after several ingests or chapters. Read-only by default;
  reports and proposes fixes rather than applying them.
---

# Wiki Lint

Audit and report. **Read-only by default** — propose fixes, apply only on confirmation.

Follow `../../CONVENTIONS.md`. Report in the user's language.

## Checks

### Tier integrity — highest severity
- **Canon contamination** — anything in `wiki/canon/` whose provenance traces to `drafts/`, `plan/`,
  or `fanon/` rather than `raw/`. Severity `critical`. Generated fiction must never become canon.
- **Unratified promotions** — entries in `wiki/fanon/` with no `## Ratified` record.
- **Missing tier field** — any page without `tier` in frontmatter.
- **Cross-tier citation** — a `canon` page citing `[fanon: ...]`.

### Language
- **Language drift** — wiki pages written in a language other than `wiki_language`, or prose in a
  language other than `output_language`. Common after a long session in the user's language.
- **Translated quotations** — verbatim lines in voice cards that do not match the text in `raw/`.
  Severity `critical` for voice cards: a translated quote silently destroys the card's usefulness.
- **Missing language markers** — voice cards for a source language with address forms, honorifics, or
  aspect distinctions that record none.

### Claim integrity
- **Uncited claims** — any factual statement with no `[src: ...]`, `[fanon: ...]`, or `(inferred)`.
  Severity `high`: after a few weeks an uncited claim is indistinguishable from a hallucination.
- **Unresolved contradictions** — populated `## Contradictions` sections. List for adjudication; do
  not resolve unilaterally.
- **Stale claims** — statements a later-ingested source supersedes. Check `log.md` ordering.
- **Broken anchors** — citations pointing at files or headings that no longer exist.
- **Volume-less citation** — a `[src:]` naming a bare `ch<NN>.md` while `raw/` holds more than one
  volume directory. Severity `high`: it resolves against no file, and in a series it is ambiguous
  between volumes that both have that chapter number. Usually means a `raw/` migration
  (`CONVENTIONS.md` §8) rewrote the files but not the wiki.
- **Claim/source mismatch** — a claim whose citation resolves but whose *content* the cited span does
  not support. Severity `high`. This is the one defect the wiki cannot show you: the page reads
  clean, the anchor resolves, and the claim is wrong.

  It comes from summarization, not from invention. Two adjacent statements in the source get merged
  into one, and the merge asserts something neither said. Observed in a real extraction: canon said
  commoners brawl at markets *and, separately,* that aristocratic rank is tangled by kinship; the
  page recorded "brawls happen among commoners and among aristocrats too" — a claim canon never
  makes, carrying a citation that resolves perfectly.

  **Verifying this means re-reading the cited chapter**, so scope it: check the claims added by the
  most recent ingest (from `log.md`), not the whole wiki, and prefer claims that merge two facts,
  quantify something, or assert a cause. Run it over everything only when the user asks for a deep
  audit. Report the claim, the quoted span, and what the span actually supports.

### Style fidelity

Run the measurement rather than eyeballing the page:

```bash
python3 <scripts>/style_fingerprint.py measure <ingested chapters>
python3 <scripts>/style_fingerprint.py check drafts/**/ch<NN>-*.md --against <ingested chapters>
```

`<ingested chapters>` is the span recorded in `overview.md`'s `## Style fingerprint` header comment
— **not** `raw/*.md`, which covers the whole book including everything the wiki has not read.

Compare the first against what `overview.md` records, and run the second for every drafted chapter.

- **Fingerprint measured over uningested material** — `overview.md` recording a span wider than
  `log.md` shows ingested, or recording no span at all. Severity `high`: every drafted chapter is
  then checked against a corpus no wiki page describes. The classic symptom is a chapter length
  equal to the whole book's word count with a range of zero, which means it was measured over an
  unsplit single file.

- **Unmeasured style fingerprint** — `canon/overview.md` describing style habits in adjectives
  ("uses ellipsis heavily", "short paragraphs") with no counts. Severity `high`: an uncountable note
  cannot be checked, and drafted prose satisfies it at any density. Propose measuring from `raw/`.
- **Missing non-standard orthography section** — after ingesting a source that departs from standard
  spelling or punctuation anywhere, `overview.md` recording no such rule. A model drafting against
  the wiki will restore the standard silently.
- **Fingerprint drift in drafts** — drafted chapters whose measured word count or punctuation
  frequencies fall outside the recorded fingerprint. Report the measured value against the target;
  this is the cheapest objective signal the wiki has about drift.

### Coverage
- **Thin voice cards** — fewer than five verbatim lines. Report the count.
- **Rule with no recorded limit** — a `world/` page asserting a capability, technology, or creature
  behavior with no `## Ограничения и цены` / limits-and-costs entry. Severity `medium`: a rule with
  no recorded limit is one the drafter can cheat with, and the cheat is invisible at review.
- **Stale derived page** — `world/constraints.md` or `world/география.md` whose `sources_ingested`
  is behind `log.md`, or absent entirely. Severity `medium`: `plan-chapters` reads both first, so a
  stale ledger silently narrows what the conflict lint can catch.
- **Unmapped location** — a place named in `plot/` or in a beat sheet with no row in
  `world/география.md`. Severity `low`, but it is the usual first symptom of a geography that
  contradicts itself two chapters later.
- **Invented distance or unit** — a draft or plan stating a travel time, distance, or calendar unit
  that `география.md` records as not established. Severity `warning`: it is fanon asserted as canon.
- **Missing would-never-do** — character pages with that section empty or absent. Most-skipped,
  highest-value; flag every instance.
- **Non-template character page** — a `characters/` page missing any required heading from
  `../ingest-source/references/extraction-checklist.md` §1. Severity `medium`. **Additional
  headings are fine** — a composite page needs its roster table, a character may earn a
  page-specific section. The defect is a required heading that is *absent* or *renamed away*
  (`## Личность/способности` standing in for `## Personality` + `## Mannerisms`), because that is
  what silently drops content. Check the required set is present; ignore the surplus.
  The heading set is not bureaucracy: a page written in a bespoke shape loses whichever detail had
  no home in it, and `## Mannerisms` is the reliable casualty. Propose adding the missing headings
  with `не установлено`, which converts an invisible omission into a visible gap.
- **Outgrown composite page** — a character with three or more canon facts living as a row in a
  composite page (a family, a squad) instead of their own page. Severity `medium`: a table cell has
  no `## Mannerisms` or `## Would never do`, so those facts were never capturable. Propose the split.
- **Malformed heading** — a page heading that is truncated, misspelled, or otherwise not one of
  the template's. Severity `low` on its own, but it silently defeats every other structural check:
  a page whose `## Правило` was written `## Прави` reads fine to a human and is invisible to any
  lint matching on heading names. Two world pages in a real wiki carried this for six ingests.
- **Social rule with no mechanism** — a `world/` page recording a custom, hierarchy, or friction as
  outcome only ("brawls break out at markets") where canon explained the cause. Severity `low`, and
  the fix is a re-read: the cause is usually one clause away from the outcome in the source.
- **Missing world limits** — world pages recording a rule but no limits or costs.
- **Named but pageless** — entities referenced across the wiki with no page.
- **Empty forbidden list** — fewer than three entries after multiple ingests means it is not being
  maintained.
- **Stale threads** — `threads.md` entries marked `open` with no activity across recent chapters.

### Ideas and series arc

Only if `plan/IDEAS.md` or `plan/SERIES_ARC.md` exist — they are optional.

- **Ladder discontinuity** — a `SERIES_ARC.md` rung whose start state does not match the previous
  rung's end state. Severity `high`: that mismatch is the whole reason the ladder exists, and a break
  in it means one book is about to ignore what the last one cost.
- **Unchecked destination** — `SERIES_ARC.md` with no canon status on its destination, or a
  destination contradicting `forbidden.md` with no matching row in `CANON.md` `divergences`. Severity
  `high`: the series premise is then an unrecorded divergence, and every book inherits it.
- **Over-detailed ladder** — rungs beyond the next two carrying more than a line. Severity `low`;
  it is planning that will be thrown away, and worse, it constrains wrongly in the meantime.
- **Idea landfill** — `IDEAS.md` with many `raw` entries untouched across several sessions. Severity
  `low`. Propose killing them; an idea list with no kills has no signal in it.
- **Ideas leaked into a tier** — brainstorm candidates written into `wiki/fanon/` or `wiki/canon/`.
  Severity `high` for fanon, `critical` for canon. Ideas are candidates, not facts.
- **Mixed layout** — a project with `plan/book-*/` directories that also has `plan/outline.md` or
  loose `drafts/ch*.md` at the root. Severity `high`: the migration in `CONVENTIONS.md` §8 was half
  done, and every skill now reads whichever it finds first.
- **Split continuity ledger** — a `continuity.md` inside a book directory. Severity `high`; the
  ledger is series-wide, and a per-book copy is how book 3 forgets book 1.
- **Seed past its payoff** — a `SERIES_ARC.md` seed whose `Payoff target` book is fully drafted and
  whose status is not `paid`. Severity `high`: the payoff window has closed.
- **Unplanted seed in a drafted book** — a seed whose `Plant in` book is drafted but which is still
  `pending`. Severity `high` for the same reason, one book earlier.
- **Book without a start state** — an `outline.md` with `book: <NN>` greater than 1 that records no
  start state. Severity `medium`; nothing downstream can check the ladder held.
- **Never-promoted ideas** — a shortlisted idea that plainly reached `outline.md` or
  `STORY_INTENT.md` but is still `shortlisted`. Severity `low`; the loop is not being closed, so
  the file cannot show which ideas actually paid off.

### Character depth

Per `../../CONVENTIONS.md` §11. For the current book's `outline.md`:

- List every character above the depth threshold (a line, two or more scenes, or agency in a scene).
- Report each one without a profile in `wiki/fanon/proposed/characters/` — `warning`, fix: run
  `develop-character`.
- For characters with a profile, re-run its cardboard check against the **current** scene list; a
  check that passed when the profile was written can fail after the outline changed — `notice`.
- A profile that edits or contradicts its canon page instead of extending it — `blocking` (tier
  integrity).

### Harness
- **Missing snapshots** — chapters in `drafts/` with no sibling `snapshots/ch<NN>-v0.md`. Without one,
  that chapter contributes no edit signal to `refine-harness`.
- **Stale harness rules** — rules in `plan/HARNESS.md` whose pattern has not recurred in several
  chapters. Propose pruning.
- **Contradictory harness rules** — rules that conflict with each other or with `CANON.md`.
  `CANON.md` wins.
- **Overreaching harness rules** — any rule attempting to override a language setting, a tier rule, or
  a gate. Severity `critical`: the harness tunes how a stage works, never whether it runs.

### Structure
- **Orphans** — pages with no inbound links from anywhere including `index.md`.
- **Index drift** — pages on disk missing from `index.md`, or index entries pointing at nothing.
- **Log gaps** — operations visible in the wiki with no `log.md` entry.
- **Plan drift** — outline scenes that no longer match drafted chapters, in any book.

## Report

```markdown
| Severity | Check | Page | Detail | Proposed fix |
|---|---|---|---|---|
```

Severity: `critical` (canon contamination, translated quotes) · `high` (uncited claims,
contradictions, missing would-never-do) · `medium` (thin cards, missing limits, language drift) ·
`low` (orphans, index drift).

## After reporting

Rank concrete next actions:
1. Which source material would fill the biggest gaps if ingested next
2. Which questions the user must answer that canon cannot
3. Which pages need a re-read of `raw/` to add or repair citations

Append: `## [YYYY-MM-DD] lint | <n> issues (<n> critical)`.

## Rules

- **No completion claim without fresh evidence** — `../../CONVENTIONS.md` §10. A check reported as
  passing was run this session; a check you did not run is reported as `not checked`, not as clean.
- **Never auto-fix contradictions.** The user decides which source wins.
- **Never fabricate a citation** to clear an uncited-claim finding. Re-read `raw/` or delete the claim.
- **Never repair a translated quotation from memory.** Go back to `raw/` and copy it.
- Report honestly when the wiki is healthy. A clean lint is a real result.
