---
name: translate
description: >
  Translate the fic, chapter by chapter, from the language it is written in into English (or
  another target language), keeping names and terms consistent across the whole series, every
  paragraph aligned with the original, and the meaning, jokes and voices intact. Use when the user
  says "translate chapter 5", "translate the book into English", "make an English version",
  "update the translation", "the original changed — fix the translation", "переведи главу на
  английский", "переведи книгу", "сделай английскую версию", "обнови перевод". Translates the
  user's chapters (drafts/ or raw/), never the wiki.
---

# Translate

A translation is a second edition of the chapter, not a paraphrase of it. A reader of the English
must get the same events, the same point, the same jokes, and the same people — and chapter 12 must
call the heroine and her school what chapter 1 called them.

Follow `../../CONVENTIONS.md`, especially §1 (language), §8 (book scope), §10 (completion claims)
and §13 (publication). Resolve `<scripts>` per §7. All commands run from the project root.

## What it translates, and what it never does

| Input | Translated? |
|---|---|
| `path/to/chapter.md` — the user's data | **yes** — this skill's only input |
| a published snapshot of a chapter (§13) | yes — it is the same chapter, as readers got it |
| `wiki/`, `plan/` | never. Canon quotations stay in the source language under every setting; the wiki is a working tool, not a publication |

**Translations are downstream only.** No stage reads `translations/` as a source of facts: the wiki,
plans and drafts stay in `output_language`, and a fact exists in the fic only if it exists in the
original chapter. A translator's fix that changes a fact is a defect — it goes to the notes as a
question about the original, never into the translation alone.

## Settings

`CANON.md`, added on first run (say so):

```yaml
translations: [en]          # target languages; default en
translation_engine: claude  # claude | openrouter — who writes the first full translation
translation_model: <id>     # openrouter only: the OpenRouter model id; no default, the user picks
```

The source language is the chapter's own — `output_language`. Target ≠ source is the whole point, so
§1's "never silently switch languages" is satisfied by the user asking; still name the pair once at
the start of a run ("ru → en").

## Layout

Series-wide files sit at the language root; chapters mirror `drafts/` (§8):

```
translations/<lang>/
  STYLE.md                         # decisions: names, address, dialogue, humour, orthography …
  GLOSSARY.md                      # every name and term, one rendering each — the script reads it
  PHRASEBOOK.md                    # idioms, proverbs, slang, catchphrases, puns — same columns
  book-<NN>/                       # flat projects: no book level
    ch<NN>-<slug>.md               # the translation, same stem as the draft
    snapshots/ch<NN>-source.md     # the exact source text translated (translation.py prepare)
    snapshots/ch<NN>-v0.md         # Claude's first full translation, before the user edits
    notes/ch<NN>.md                # translator's notes: questions and choices for the user
    proposals/ch<NN>.md            # harvest: proposed glossary/phrasebook rows, ticked by the user
    bakeoff/ch<NN>-<model>.md      # model comparison entries (--out); never read by other stages
```

## First run: STYLE.md and GLOSSARY.md

Before chapter 1, settle the decisions every later chapter depends on. Interview **one question at a
time, each with a recommended answer** (the `plan-story` pattern), and answer from the wiki and
`CANON.md` whatever they already settle. Write `STYLE.md` as a table of decision → rule → example,
invented or from the drafts — never a translated canon quotation. The questions:

| Decision | Recommended default | Why it must be decided once |
|---|---|---|
| Names | transliterate plainly (Анна → Anna, Марк → Mark); a canon name with an official edition in the target language takes that edition's form | two renderings of one name read as two people |
| Patronymics, diminutives, nicknames | keep the form the speaker uses; a diminutive stays a diminutive (Аннушка → Annushka), not "little Anna" | who uses which form *is* the relationship |
| ты / вы and other address forms | carry the shift through first name vs. title + surname, and through diction; never add "thou" | English has no pronoun for it; the register must go somewhere |
| Invented terms, ranks, spells, institutions | translate the meaning when the original is a meaningful word (Северная Академия → Northern Academy); transliterate when it is a coinage | a reader must be able to parse the world the way the original reader does |
| Dialogue punctuation | the target language's own (English: quotation marks), never the source's dashes | foreign punctuation reads as a typo, not as flavour |
| System text, stat blocks, messages, letters | same layout and markers as the original, text translated | layout is how the reader recognises the device |
| Spelling variety | US or UK — one | mixed spelling reads as sloppiness |
| The author's non-standard orthography | not reproduced unless it marks a character's speech; recorded here so nobody "restores" it in the original | it is a fact about the source language, usually untranslatable |
| Profanity and slang | same strength, target-language idiom | softening or sharpening changes the character |
| Cultural references, units, money | keep, no in-text explanations | a gloss inside the prose is the translator talking |

`GLOSSARY.md` is a markdown table the script reads by its column names — keep them:

```markdown
| Source | Match | Target | Avoid | Kind | Note |
|---|---|---|---|---|---|
| Анна | Анн* | Anna | Anne, Ann | name | диминутив Аннушка → Annushka |
| Северная Академия | Академи* | Academy | Akademia | place | full: Northern Academy |
```

`Match` is a comma-separated list of stems; `*` matches any ending, so one row covers the inflected
forms. `Avoid` lists renderings that must never appear — the variants a model drifts into. Seed it
from the wiki's character and world pages, not from memory, and have the user ratify it.

`PHRASEBOOK.md` has the same columns for idioms, proverbs, slang, catchphrases and puns (`Kind`
says which). A name row is exact; a phrase row is a strong default the sentence may bend. Both
files are **the memory of the translation**: every decision made once is reused in every later
chapter, by whichever engine writes it, and `check` enforces their `Avoid` columns.

## Translate a chapter

### 1. Which text

- **Published chapter** (`published:` in frontmatter): translate the latest published snapshot —
  what readers got — with `--from`.
- **Unpublished**: the draft. If `wiki/log.md` has no `reconcile` for it, or the user has not
  edited it since `write-chapter`, say so and ask: translating text that will still change doubles
  the work, and `stale` will list every paragraph again.
- **In order** within a book, unless the user asks otherwise: the previous chapter's translation is
  the context for voice and for the terms the glossary does not hold.

### 2. Prepare

```bash
python3 <scripts>/translation.py prepare drafts/book-01/ch05-<slug>.md --lang en \
  [--from drafts/book-01/snapshots/ch05-published-<platform>-v<N>.md]
```

It freezes the source text into `snapshots/ch05-source.md`, prints the target path, the block
counts, the frontmatter the translation must carry, and every image line with its path rewritten
for the target's folder.

### 3. Glossary gate

```bash
python3 <scripts>/translation.py terms drafts/book-01/ch05-<slug>.md --lang en
```

It lists capitalised mid-sentence forms the glossary does not cover — candidates only: inflected
forms of one name appear separately, sentence-initial names are missed, and languages without
capitals get nothing from it. Read the chapter for the rest: invented common nouns, ranks, spells,
nicknames, a proverb or pun that will need a decision.

Show the user one table of the chapter's new terms with a proposed rendering and a reason each.
This is the cheap gate: a name fixed here costs one row; fixed after five chapters it costs a
search-and-replace across the book and a reader who already learned the wrong one. Ratified rows go
into `GLOSSARY.md`; a chapter with no new terms passes without a question.

**Harvest (optional, OpenRouter).** A strong model can do this reading instead, once per chapter:

```bash
python3 <scripts>/openrouter_translate.py drafts/book-01/ch05-<slug>.md --lang en --model <strong id> --harvest
python3 <scripts>/translation.py accept translations/en/book-01/proposals/ch05.md   # after the user ticks [x]
```

It writes `proposals/ch05.md` — names, terms, idioms, slang, puns the two files do not cover, each
with a rendering and a reason; items not quoted exactly from the chapter are dropped and reported.
The user ticks and edits; `accept` routes names and terms to `GLOSSARY.md`, phrases to
`PHRASEBOOK.md`, skipping duplicates. Then a cheaper model translates with those decisions. This
transfers **consistency and idiom choices**, which are listable; it does not transfer voice, irony or
rhythm, which live in whole sentences — judge those in the bake-off, not in the phrasebook.

### 4. Read before writing

- `STYLE.md`, `GLOSSARY.md`, and `plan/HARNESS.md` → `## Translation` if present.
- The previous chapter's translation, at least its last scene.
- The chapter's beat card `Point` lines (`plan/…/beats/ch<NN>.md`) — what each scene is *for*. A
  scene whose point is dark irony translated as plain reporting keeps every fact and loses the scene.
- `wiki/canon/overview.md` → `## Comic register` and the voice cards of everyone who speaks. The
  cards are in the source language; they say how each person talks, and `STYLE.md` says how that
  register lands in the target.

### 5. Translate

**Engine.** `translation_engine: claude` (default): write it yourself, as below. `openrouter`: a
model on OpenRouter writes it with the same rules, on the user's key and money:

```bash
python3 <scripts>/openrouter_translate.py drafts/book-01/ch05-<slug>.md --lang en [--model <id>]
python3 <scripts>/openrouter_translate.py drafts/book-01/ch05-<slug>.md --lang en --dry-run  # see the requests
```

Before the first command that needs the key, follow `../../CONVENTIONS.md` §12 (`.env` gitignored,
never read). The script sends the frozen source in numbered chunks with `STYLE.md`, `GLOSSARY.md`
and `## Translation` from the harness, refuses a reply whose items do not match (nothing written),
writes the file with its frontmatter, and prints token use and cost. It refuses anything outside
`drafts/`. Everything after this step — check, meaning pass, notes, naturalize, v0 — is the same:
**the OpenRouter model drafts, Claude still checks.** Record the engine in the log line
(`engine=openrouter:<id>`); `refine-harness`-style learning compares engines only if the log says
which wrote what.

Each chunk carries only the glossary and phrasebook rows that occur in it, so the files can grow
for a whole series without crowding the prompt.

**Bake-off before choosing a model.** Translate one representative chapter with each candidate into
its own file, `check` each, then read them side by side with the user:

```bash
python3 <scripts>/openrouter_translate.py drafts/book-01/ch01-<slug>.md --lang en --model <id> \
  --out translations/en/book-01/bakeoff/ch01-<model-slug>.md
```

Compare `check` errors and ratio warnings, the meaning pass (facts, point, intent), and the user's
read on voice and jokes; report the cost each run printed. Include the cheap model **with** a
harvested phrasebook as its own entry — that is the evidence for whether the split pays. The
winner goes to `translation_model` in `CANON.md`; bake-off files are not translations and no
stage reads them.


Write `translations/<lang>/<book>/ch<NN>-<slug>.md`: the frontmatter `prepare` printed plus a
translated `title:`, the heading translated, then the body **block for block** — one translated
paragraph for each source paragraph, scene breaks and image lines where they were (image alt text
translated, path as `prepare` printed it). Translate scene by scene, reading each scene in the
original whole before writing it.

- **Meaning is untouchable.** Same events, same facts, same order, nothing added, nothing dropped.
  A different verb is a different fact.
- **Voice before smoothness.** A clipped speaker stays clipped; a pompous narrator stays pompous.
  Ironic ceremony about trivial things is the joke — it is translated as ceremony, never flattened
  into plain statement.
- **Proverbs and idioms**: the target's own idiom for *the same thought*; if none exists, a plain
  literal rendering that keeps the thought. Never a different proverb that happens to be nearby.
- **Wordplay**: find an equivalent that does the same job in the same place; when none works, keep
  the literal and put the pun in the notes with options. Never a footnote in the prose.
- **Do not fix the original.** A sentence that is ambiguous or looks wrong is translated as
  faithfully as possible and raised in the notes.
- **Names and terms** exactly as `GLOSSARY.md` has them, in every paragraph.

### 6. Check

```bash
python3 <scripts>/translation.py check translations/en/book-01/ch05-<slug>.md
```

| Finding | Meaning | Action |
|---|---|---|
| block sequences differ | a paragraph dropped, merged, split, or an image moved | **error** — fix the alignment; nothing else is checked until it passes |
| untranslated text | letters of the source's script in the target | **error** — translate it, or add a deliberate keep to `STYLE.md` and render it in the target script |
| glossary `Avoid` variant | a name or term drifted | **error** — use the glossary form |
| length ratio far from median | a sentence may be missing or invented | re-read that paragraph against the original |
| digits missing | a number changed or was spelled out | confirm it is the same number |
| source term, no target term | often a pronoun — sometimes a dropped name | glance, no action if a pronoun carries it |

Exit 0 is required. Then **a meaning pass the script cannot do**: for each scene, re-read the original
and the translation side by side and ask only "same facts, same point, same speaker intent?" Fix
what fails; record what you cannot decide.

### 7. Notes for the user

Write `notes/ch<NN>.md`:

```markdown
---
type: translation-notes
target: translations/en/book-01/ch05-<slug>.md
date: <YYYY-MM-DD>
---

### 1. <pun | idiom | ambiguity | term | register>
- original: <exact quote from the source>
- translation: <exact quote from the translation>
- options: <alternatives, when there are any>
- decision: [ ] keep  [ ] option __  [ ] own:
```

Quotes are exact substrings of their files — check each before writing. A chapter with nothing to
decide gets no notes file. Tell the user the file and its item count in one line; do not print the
items unless asked.

### 8. Naturalness

Run `naturalize` in prose mode on the translation, under `CANON.md`'s `naturalness:` mode. It works
in the text's own language, so it now reads as a native English reader — which is what catches
translationese: calqued word order, source idioms rendered word for word, "said" chains copied from
dashes. Its meaning rule is this skill's meaning rule.

### 9. Freeze v0 and log

Once check passes and before the user edits — `cp` only if the file does not exist yet:

```bash
[ -f translations/en/book-01/snapshots/ch05-v0.md ] || \
  cp translations/en/book-01/ch05-<slug>.md translations/en/book-01/snapshots/ch05-v0.md
```

Append to `wiki/log.md`:

```
## [YYYY-MM-DD] translate | b01/ch05 → en
   metrics: engine=claude|openrouter:<id> paragraphs=<n> words_src=<n> words_tgt=<n> new_terms=<n> notes=<n> check_errors=0 ratio_warnings=<n>
```

## Applying the notes

When the user says the notes are done: apply every `option` and `own` by exact-quote replacement;
a decision that is a rule ("puns on names: keep the literal") goes into `STYLE.md`; a term goes into
`GLOSSARY.md`. Re-run `check`. Log `translate | b01/ch05 notes — <n> applied`.

## The original changed

A published chapter changes by errata; an unpublished one by any edit.

```bash
python3 <scripts>/translation.py status --lang en            # which translations are stale
python3 <scripts>/translation.py stale translations/en/book-01/ch05-<slug>.md
```

`stale` prints each changed source block with its number in the translation. Retranslate **only
those blocks** — a whole-chapter retranslation throws away the user's edits to the English — then
`prepare` again to refreeze the source (the translation keeps its frontmatter; `v0` is not
refrozen), `check`, and log `translate | b01/ch05 update — <n> blocks`. On the `openrouter` engine,
run `openrouter_translate.py … --blocks <numbers from stale>` **before** refreezing: it replaces only
those blocks and keeps every other paragraph as the user left it. A published translation
(if the user publishes one) follows §13 like any published text: errata only.

## Learning from the user's edits

After the user has edited a few translated chapters, diff `snapshots/ch<NN>-v0.md` against the
current file. Recurring changes are rules: a word the user always replaces, a register they always
lift, a name form they prefer. Propose them — the three-instance rule of `refine-harness` applies —
and ratified ones go to `STYLE.md` or `GLOSSARY.md`; a drafting habit goes to `plan/HARNESS.md` →
`## Translation`. One book's decisions stay in that project, never in this skill.

## Rules

- **The user's chapters only.** `drafts/` and `raw/` are translated; the wiki is never translated (§1).
- **Block for block.** One target paragraph per source paragraph; `check` refuses anything else.
- **One rendering per name and term**, from `GLOSSARY.md`, ratified before the chapter is written.
- **Meaning, point, jokes and voices survive**, or the item goes to the notes — never silently lost.
- **Never repair the original in the translation.** Raise it in the notes; the author fixes the source.
- **Stale means retranslate changed blocks only.**
- **No completion claim without fresh evidence** (§10): "chapter 5 translated" means `check` ran on
  the written file and exited 0, its summary line pasted, and the meaning pass named what it found.
