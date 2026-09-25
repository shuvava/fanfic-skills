---
name: naturalize
description: >
  Find sentences a native speaker would not write — model-sounding prose and concept-speak in plans —
  and propose the plainest natural fix, without touching the author's jokes or the meaning. Use when
  the user says "the text sounds mechanical", "it reads like AI", "fix clumsy phrasing", "почисти
  корявые фразы", "текст механический", "проверь естественность", or when write-chapter,
  plan-story or plan-chapters reach their naturalness step. Works on chapters (prose mode) and on
  plans — STORY_INTENT, outline, beat cards (plan mode). Mode per project: off / review / auto-safe.
---

# Naturalize

Read the text the way a native reader does, and flag what they would stumble on.

Follow `../../CONVENTIONS.md`. Work in the text's own language; this skill never translates.

## Why this stage exists

A model writes sentences that are grammatical and still not ones a person would write: a thought
compressed into abstract shorthand, a collocation that almost exists, an image that does not form.
Measured on a real run, the author-reader of a Russian series rejected a plan premise — «собирает
пати чужими руками и не становясь ничьим человеком» — as *коряво*, and found the same defect
throughout the chapters. Three instruments were tried against it and missed it:

- **The style fingerprint** counts punctuation. Clumsy construction keeps the right punctuation.
- **A frequency list of overused words** finds habits («ровно», «только вот»), not constructions:
  every word in the rejected premise is ordinary.
- **A model fine-tuned on the author** measures sounding *like the author*. Clumsiness is about
  sounding like *a person*; a tuned-model checker flagged punctuation, and the reader called its
  edits "very minor".

What caught it was reading. This skill is that reader.

## Mode

Read `naturalness:` from `CANON.md` (default `review` when absent):

| Mode | Prose (chapters) | Plans |
|---|---|---|
| `off` | skipped | skipped |
| `review` | review file for the user; nothing applied until they decide | review file |
| `auto-safe` | **repairs** applied (see below), everything else to the review file | review file — **always** |

Plans are never auto-applied in any mode: a plan edit changes what the book is about.

**A published chapter** (`published:` in its frontmatter, `../../CONVENTIONS.md` §13) is always
`review`, whatever the mode, and an accepted fix reaches readers only through `publish` errata — so
only typo-sized fixes can. Say so in the review file's header rather than proposing rewrites the
user cannot ship.

## Two readings

**Prose mode** — chapters. Flag only what a reader stumbles on as an *error*:

- a broken fixed expression or collocation (the word that almost belongs there);
- agreement or government errors; a sentence whose end no longer connects to its start;
- an image or comparison that does not form a picture;
- a **garbled proverb or idiom — restore the canonical form, never paraphrase it.** On the real run
  «своё отдать легко, чужое возвращать нечем» was "fixed" into a different thought; it was a broken
  «берёшь чужие и на время, а отдаёшь свои и навсегда». A paraphrase changes the meaning; the
  proverb carries it.

**Do not flag the author's comic register.** Deliberately pompous, bureaucratic or ceremonious phrasing
about trivial things is the narrator's irony, not officialese — the reader judged «о чём
красноречивее всего свидетельствовало целое эссе о любви к императору» and «с той особой
вежливостью, какая бывает у людей, которые заранее знают, что им не откажут» *funnier* than their
plain rewrites. Read `## Comic register` in `canon/overview.md` first; anything it records as a
device is not a defect. Nor are the source's non-standard orthography, slang or coinages.

**Plan mode** — STORY_INTENT, outline rows, beat-card `Point` and `Event`. Here the defect is
**concept-speak**: abstract nouns, planner's jargon, a summary nobody would say aloud («кооперация
против косной иерархии», «возврат приходит от людей и не приходит от институтов»). The fix is not a
simpler abstraction but **concrete everyday language — an image or a sharp contrast**, the way the
user would explain the idea to a friend. The reader's own fixes on the real run set the bar:
«действуя чужими руками, как серый кардинал»; «можно ли работать в одной команде как партнёры, а не
как начальник и дурак». The editor's first attempts («не власть и не Академия», «любой союз означает,
что ты чей-то») were simpler and still *криво*.

## Fixing

- **Never change meaning, facts or action.** A different verb is a different fact: «уверенно она это
  делала» → «отказывала» was rejected. If the context does not settle the meaning, flag without a
  rewrite.
- **The smallest repair.** Mend the broken place; do not rewrite the sentence around it.
- **The plainest natural phrasing wins.** Do not replace one flourish with another.
- **Never add meaning in plan mode.** «независимость в одиночку не берётся» became «ты просто один —
  и тебя съедят» on the real run; the second half was invented. A plan fix restates, it does not
  extend.
- **Project examples outrank these rules.** Read `## Naturalness examples` in `plan/HARNESS.md` before
  reading the text: they are this user's verdicts and the best evidence of their taste.
- **Read `## Overused patterns`** in `plan/HARNESS.md` if present, as places to look first — not as
  words to delete on sight. A pattern the author also uses is fine where he would use it.

## What counts as a repair (auto-safe)

Applied without asking only when **all** hold:

1. the flag is a broken collocation/idiom, an agreement or government error, or a garbled proverb
   restored to its canonical form;
2. at most three words change, and every content word of the original survives or is the
   canonical form's own;
3. a second read of before and after, asked only "same facts, same meaning, same speaker intent?",
   answers yes.

Anything else goes to the review file. Every applied repair is still listed in it, marked applied,
so the user can revert it. Repairs are Claude's own edits: apply them before the chapter's
`snapshots/ch<NN>-v0.md` is frozen (`write-chapter` §4), so the snapshot stays "what Claude produced".

## The review file

Write `<book>/naturalness/<name>.md` — `<name>` is the chapter file's stem or the plan file's name:

```markdown
---
type: naturalness-review
target: <path>
mode: prose | plan
date: <YYYY-MM-DD>
---

### 1. <what is wrong, one line>
- было: <exact quote>
- стало: <proposed fix, or empty when meaning is unclear>
- решение: [ ] принять  [ ] отклонить  [ ] свой вариант:
```

Quotes must be exact substrings of the target — check each one before writing the file, and drop or
re-quote any that do not match. Section labels follow `wiki_language`.

Tell the user where the file is and how many items it holds, in one line. **Do not print the items
into the conversation** unless asked: the file is where they decide.

## Applying decisions

When the user says the review is done ("apply naturalness for ch05", "примени правки"):

1. Apply every `принять` and every `свой вариант` to the target, by exact-quote replacement. A quote
   that no longer matches (the text changed since) is reported, not guessed.
2. After a replacement inside a larger sentence, re-read the joined sentence: a fix quoted from mid-
   sentence can leave the old head or tail dangling. This happened on the real run twice.
3. Record every **rejection** and every **own variant** in `plan/HARNESS.md` → `## Naturalness
   examples` (below). These are the user's explicit verdicts, ratified in the review file itself, so
   they go in directly — the three-instance rule of `refine-harness` is for inferred patterns, not
   stated ones. Bump the harness revision and log it.
4. Log to `wiki/log.md`:
   ```
   ## [YYYY-MM-DD] naturalize | <target> — <n> flagged, <n> accepted, <n> own, <n> rejected, <n> auto
   ```

### `## Naturalness examples` in `plan/HARNESS.md`

```markdown
## Naturalness examples

| Mode | Было | Вердикт | Почему |
|---|---|---|---|
| prose | «о чём красноречивее всего свидетельствовало…» | keep — оригинал смешнее | ирония рассказчика |
| plan | «не становясь ничьим человеком» | → «действуя чужими руками, как серый кардинал» | образ вместо понятия |
```

Keep at most twenty rows; `refine-harness` prunes to the most instructive when it grows past that.

## When to run

| Caller | Mode | On what |
|---|---|---|
| `plan-story` | plan | `STORY_INTENT.md`, before presenting it for ratification |
| `plan-chapters` | plan | Layers 1–2 and the scene list's `point` column |
| `write-chapter` §3 | plan | Beat cards' `Point` and `Event`, before the beat gate |
| `write-chapter` §5 | prose | The draft, after the canon check passes — skip `![…](…)` image lines; they are placed by `illustrate` |
| The user | either | Any file, any time |

## Overused patterns (optional)

After a few chapters exist, measure what the drafts overuse relative to the source:

```bash
python3 <scripts>/overused_patterns.py --drafts <drafts>/ch*.md --against <ingested chapters>
```

Resolve `<scripts>` per `../../CONVENTIONS.md` §7. It prints a table of words and short phrases the
drafts use far more often than the source, with both rates. Offer the top entries to the user; the
ones they confirm go to `plan/HARNESS.md` → `## Overused patterns` as places to look. It needs a few
thousand words of drafts to say anything; below that it says so.

## Rules

- **Meaning is untouchable.** A naturalness fix that changes what happens is a defect, not a fix.
- **The author's humour is not a defect.** When unsure whether a stiff phrase is a joke, leave it.
- **Plans are reviewed, never auto-applied.**
- **The user's verdicts are the calibration.** Rules here are defaults; `## Naturalness examples` is
  what this user actually wants.
- **No completion claim without fresh evidence** (`../../CONVENTIONS.md` §10): "applied 7 fixes"
  means the target was re-read after writing and each replacement is present.
