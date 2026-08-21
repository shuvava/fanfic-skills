---
name: wiki-init
description: >
  Scaffold a new fanfic project — the tiered canon/fanon wiki, the CANON.md schema, and source language
  detection. Use when the user says "set up a story bible", "start a fanfic project", "init a canon wiki",
  "I have a book in markdown and want to write fanfic", or points at source material and asks where to
  begin. Creates raw/ + wiki/canon/ + wiki/fanon/ + wiki/drafts/ and detects the source language.
---

# Wiki Init

Scaffold the project. Read `../../CONVENTIONS.md` first — it defines language
preservation, provenance tiers, and citation format used by every other skill.

## 1. Detect the source language

Read a representative sample of the material in `raw/` (or wherever the user points) and identify its
language. **Report the detection to the user and confirm it.**

Record in `CANON.md`:

```yaml
source_language: <ISO 639-1 code>
wiki_language: <same as source by default>
output_language: <same as source by default>
```

Do not ask the user what language they want unless they raise it. The default is: the source's
language, everywhere. Confirm the detection, mention the default, and move on.

If `raw/` is multilingual, record the primary language and note the others — code-switching in the
source is characterization data that voice cards will need.

## 2. Create the structure

```
project-root/
├── CANON.md                    # schema, conventions, language, divergences
├── raw/                        # immutable sources — never edited, never translated
├── plan/                       # STORY_INTENT.md, outline.md, conflicts.md, HARNESS.md
│   └── beats/                  # ch<NN>.md — one beat sheet per chapter
├── drafts/                     # tier: generated — chapters + continuity.md
│   └── snapshots/              # untouched first drafts, for edit-diff feedback
│                               # a series nests both per book — CONVENTIONS.md §8
└── wiki/
    ├── index.md                # catalog of every page
    ├── log.md                  # append-only operation history
    ├── canon/                  # tier: canon — READ-ONLY after ingest
    │   ├── overview.md         # POV, tense, tone, structure, style conventions
    │   ├── forbidden.md        # what a continuation must never do
    │   ├── characters/
    │   ├── voices/             # verbatim dialogue — always source language
    │   ├── world/
    │   └── plot/               # per-source summaries, timeline.md, threads.md
    └── fanon/                  # tier: fanon-established — invented, user-ratified
        ├── proposed/           # tier: fanon-proposed — awaiting ratification
        ├── characters/         # OCs and canon characters' fic-only developments
        └── world/
```

**`plan/` and `drafts/` sit at the project root, not under `wiki/`.** Every other skill writes
`plan/outline.md`, `plan/beats/ch<NN>.md`, and `drafts/ch<NN>-<slug>.md` — root-relative. An earlier
version of this tree nested them under `wiki/`, and a real run created both: `plan/` at the root,
`drafts/` under `wiki/`, and two empty directories nobody wrote to. Create exactly the paths above.

**Initialize flat, even when the user says "series".** `layout: flat` in `CANON.md`; `plan-chapters`
migrates to the per-book layout when a second book is actually planned (`../../CONVENTIONS.md` §8).
Creating `plan/book-01-untitled/` at init names a book before its premise exists, and the name is
then wrong in every path for the rest of the project.

## 3. Place source material

Copy (never move — preserve the user's original) source files into `raw/`. State plainly in `CANON.md`
that `raw/` is never edited and never translated.

## 4. Split a single-file source into chapters

If `raw/` holds one file containing many chapters, **offer to split it** before anything is ingested:

```bash
python3 <scripts>/split_chapters.py raw/<file>.md --list   # inspect the split points
python3 <scripts>/split_chapters.py raw/<file>.md          # write raw/ch01.md ...
```

**If the source is one volume of a series, split into a volume directory instead** — see
`../../CONVENTIONS.md` §8:

```bash
python3 <scripts>/split_chapters.py raw/<file>.md --out-dir raw/book-<NN>
```

The volume number comes from the source's own numbering (a `num:` field, the title, or the user),
**not** from any fic ladder. Every volume restarts at chapter 1, so two volumes split flat into the
same `raw/` overwrite each other file for file, and the survivor's chapters are silently a mix of
both. Ask whether more volumes exist before splitting the first one; converting later costs a rewrite
of every citation in the wiki.

(`<scripts>` is resolved at run time — `../../CONVENTIONS.md` §7.)

Splitting is not an edit of `raw/`: the tool copies bytes, and every run reassembles its own output
and refuses to write unless it is byte-identical to the input. Run `--list` first and confirm the
chapter count with the user. If the headings do not match the default `^##\s+\S`, pass `--pattern`.

This is worth doing before the first ingest, because three later problems are all the same problem:

- **The style fingerprint measures the file, not the chapter.** Against one 85,000-word file,
  `measure` reports chapter length as 85,000 words with a range of zero. Split, and it reports a
  true mean and spread across real chapters. That number ends up in `overview.md` and later grades
  drafted prose.
- **Citations stop being verifiable.** `[src: book.md#Глава 4]` points into half a megabyte;
  `[src: ch04.md#Глава 4]` points into 7,000 characters. `wiki-lint` requires going back to `raw/`
  to repair a quotation, and at the first size that is expensive enough to skip.
- **Reads wander ahead.** Nothing bounds a read of a whole-novel file to the chapter being ingested.

If the source is already one file per chapter, skip this step. If the user declines the split,
record `raw_layout: single-file` in `CANON.md` so later skills know the fingerprint is corpus-wide
and citations are coarse.

## 5. Write CANON.md

Use the template in `references/canon-schema.md`. Fill in title, author, detected language, ingest
granularity, and leave the `divergences` and `preferences` sections empty for now.

## 6. Seed the wiki

Create `index.md`, `log.md`, and an empty `canon/forbidden.md` with only its header — **in the source
language**. Do not populate anything else. An empty wiki is correct; a hallucinated one is poison,
because every later stage treats wiki pages as fact.

## 7. Report and hand off

Tell the user (in their language) what was created, what language the wiki will be maintained in, and
that the next step is `ingest-source`. Recommend chapter-by-chapter ingest over whole-book — smaller
ingests produce sharper pages and surface drift early.

## Rules

- **Refuse to overwrite.** If `wiki/` exists and is non-empty, stop and offer to ingest into it instead.
- **Never invent canon during init.**
- Suggest `git init` if unversioned. The wiki's value depends on being able to diff and revert a bad
  ingest.

## Reference

`references/canon-schema.md` — the CANON.md template.
