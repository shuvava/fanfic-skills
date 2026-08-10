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

### Style fidelity

Run the measurement rather than eyeballing the page:

```bash
python3 ../../scripts/style_fingerprint.py measure raw/*.md
python3 ../../scripts/style_fingerprint.py check drafts/ch<NN>-*.md --against raw/*.md
```

Compare the first against what `overview.md` records, and run the second for every drafted chapter.

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
- **Missing would-never-do** — character pages with that section empty or absent. Most-skipped,
  highest-value; flag every instance.
- **Missing world limits** — world pages recording a rule but no limits or costs.
- **Named but pageless** — entities referenced across the wiki with no page.
- **Empty forbidden list** — fewer than three entries after multiple ingests means it is not being
  maintained.
- **Stale threads** — `threads.md` entries marked `open` with no activity across recent chapters.

### Harness
- **Missing snapshots** — chapters in `drafts/` with no `drafts/snapshots/ch<NN>-v0.md`. Without one,
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
- **Plan drift** — `plan/outline.md` scenes that no longer match drafted chapters.

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

- **Never auto-fix contradictions.** The user decides which source wins.
- **Never fabricate a citation** to clear an uncited-claim finding. Re-read `raw/` or delete the claim.
- **Never repair a translated quotation from memory.** Go back to `raw/` and copy it.
- Report honestly when the wiki is healthy. A clean lint is a real result.
