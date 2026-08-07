---
name: wiki-init
description: >
  Scaffold a new fanfic project — the tiered canon/fanon wiki, the CANON.md schema, and source language
  detection. Use when the user says "set up a story bible", "start a fanfic project", "init a canon wiki",
  "I have a book in markdown and want to write fanfic", or points at source material and asks where to
  begin. Creates raw/ + wiki/canon/ + wiki/fanon/ + wiki/drafts/ and detects the source language.
---

# Wiki Init

Scaffold the project. Read `${CLAUDE_PLUGIN_ROOT}/CONVENTIONS.md` first — it defines language
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

## 3. Place source material

Copy (never move — preserve the user's original) source files into `raw/`. State plainly in `CANON.md`
that `raw/` is never edited and never translated.

## 4. Write CANON.md

Use the template in `references/canon-schema.md`. Fill in title, author, detected language, ingest
granularity, and leave the `divergences` and `preferences` sections empty for now.

## 5. Seed the wiki

Create `index.md`, `log.md`, and an empty `canon/forbidden.md` with only its header — **in the source
language**. Do not populate anything else. An empty wiki is correct; a hallucinated one is poison,
because every later stage treats wiki pages as fact.

## 6. Report and hand off

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
