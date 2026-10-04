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
Measured on a real run, the author-reader of a Russian series rejected a plan premise written as abstract shorthand as clumsy, and found the same defect
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
- a **garbled proverb or idiom — restore the canonical form, never paraphrase it.** «Семь раз проверь, один раз отрежь» "fixed" into «проверяй всё тщательно» is a different thought; it is a broken «семь раз отмерь, один раз отрежь». A paraphrase changes the meaning; the
  proverb carries it.

**Also flag what a reader who has forgotten canon cannot follow.** Not an error but a gap: the
sentence is fine for someone who remembers two volumes back and opaque to everyone else. Three kinds:

- **A world word with no gloss at its first use in this book** — an abbreviation, term, rank or mark.
  Canon having explained it volumes ago does not count; a repeat far from the first use needs the
  gloss again. «У неё на рукаве "СК"» → «нашивка "СК" — "стража ключей"».
- **A clipped line that assumes the listener knows his part** — a character speaking in a list of
  bare verbs or roles. «Ты — дверь, я — окно» → «Ты держишь дверь, я лезу в окно». Keep the
  character's terseness; add only who does what.
- **A price or payment without what it is for and who pays** — and the unit named: «три серых» →
  «три серых камня». «Платит тот, кто проиграл» on a page about a duel and a doctor is ambiguous
  between the two.

Gloss once, in half a sentence, in the narrator's or speaker's own manner; do not re-explain what the
reader met a page ago. Such a fix adds words, so it is never an auto-safe repair. **If spelling the
thing out requires a fact canon and fanon do not settle** — who receives the money, which body
answers to which — flag it without a rewrite and ask: on a real run, making a fee explicit exposed
that the draft had quietly sent a guild's share somewhere canon did not allow.

**Do not flag the author's comic register.** Deliberately pompous, bureaucratic or ceremonious phrasing
about trivial things is the narrator's irony, not officialese — on a real run the reader judged two such sentences *funnier* than their plain rewrites — the kind that hand over a spoon «с торжественностью, достойной коронации». Read `## Comic register` in `canon/overview.md` first; anything it records as a
device is not a defect. Nor are the source's non-standard orthography, slang or coinages.

**Plan mode** — STORY_INTENT, outline rows, beat-card `Point` and `Event`. Here the defect is
**concept-speak**: abstract nouns, planner's jargon, a summary nobody would say aloud («реализует стратегию независимости через горизонтальные связи», «ресурс доверия конвертируется в лояльность»). The fix is not a
simpler abstraction but **concrete everyday language — an image or a sharp contrast**, the way the
user would explain the idea to a friend. The bar is an image anyone would say aloud — «друзья, которые помогут, хотя ничего не обещали», not «связи вместо власти». On the real run the editor's first attempts were simpler abstractions and the reader still called them clumsy; the fixes they accepted were images and sharp contrasts.

## Fixing

- **Never change meaning, facts or action.** A different verb is a different fact: «судя по тому, как привычно он это делал» → «воровал» adds a fact the sentence does not state. If the context does not settle the meaning, flag without a
  rewrite.
- **The smallest repair.** Mend the broken place; do not rewrite the sentence around it.
- **The plainest natural phrasing wins.** Do not replace one flourish with another.
- **Never add meaning in plan mode.** «доверие не покупается» → «доверие не покупается, а покупателей презирают» invents the second half. A plan fix restates, it does not
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
`snapshots/ch<NN>-v0.md` is frozen at hand-off (`write-chapter` §4), so the snapshot stays "what Claude
produced".

## The review file

Write `<book>/naturalness/<name>.md` — `<name>` is the chapter file's stem or the plan file's name:

```markdown
---
type: naturalness-review
target: <path>
mode: prose | plan
date: <YYYY-MM-DD>
---

### 1. <where a reader stumbles, one line, in plain words>
- было: <exact quote>
- стало: <proposed fix, or empty when meaning is unclear>
- решение: [ ] принять  [ ] отклонить  [ ] свой вариант:
- заметили: <who flagged it — claude-editor, then each outside critic; see Outside readers>
- прогноз: low | high — <the signals that decided it; see Shadow prediction>
```

Quotes must be exact substrings of the target — check each one before writing the file, and drop or
re-quote any that do not match. Section labels follow `wiki_language`.

**The heading is the reader's stumble, not the editor's diagnosis.** Write what a reader would ask
or feel: «непонятно, что значит "вес посредника"», «фразу приходится читать дважды», «так никто не
говорит». Never this skill's own terms (concept-speak, «понятие вместо образа», «образ не
складывается», «канцелярит»). On a real run the user could not tell what an item headed «понятие
вместо живой фразы» was about. A heading that needs this file to decode it fails the same test as
the sentence it flags.

Tell the user where the file is and how many items it holds, in one line. **Do not print the items
into the conversation** unless asked: the file is where they decide.

## Shadow prediction

Every item in the review file carries a `прогноз:` line (`../../CONVENTIONS.md` §9, *Shadow
prediction*). It predicts whether the user will decide anything other than `стало` as written.
Auto-applied repairs get one too: for them, a revert counts as a change. The prediction never
changes which items are shown or applied. Write it after adjudicating the critics, from these
signals:

- **`high` if any of these holds:**
  - the sentence carries a joke, the narrator's comic move, or the chapter's last lines;
  - the fix repairs reasoning: a claim the next line undoes, a count that does not add up, a
    character knowing what they could not know, "first" or "earlier" against the chapter's own
    order of events;
  - the fix changes more than three words, or rewrites the head or tail of the sentence;
  - `стало` is empty;
  - only one reader flagged it;
  - plan mode: the fix replaces an abstraction with an image.
- **`low`** only when no `high` signal holds and at least one of these does:
  - the fix is a repair class (broken collocation, agreement or government error, a proverb restored
    to its canonical form);
  - two or more readers flagged the same sentence;
  - a row in `## Naturalness examples` settled the same kind of case the same way.
- Neither list matches → `high`.

Name the signal, not a feeling: `прогноз: low — согласование, флаг у двух читателей`. A bare
`low` cannot be checked later when the prediction misses.

## Outside readers (prose mode)

Your reading is one reader. Measured on a real run: in a blind read of three published chapters, the
user marked a real defect in 22 of 29 sentences they had let through. No single critic found more
than half of those 22, and each found some that no other critic did. Other models, and a fresh
Claude that never saw the drafting, stumble on different sentences than you do. Their best catches
are logic the page undoes: a claim the next line contradicts, a count that does not add up, a
premise the reader was never given.

`critics:` in `CANON.md` lists them. `claude` is a fresh-context subagent; any other entry is an
OpenRouter model id and needs `OPENROUTER_API_KEY` (`../../CONVENTIONS.md` §7; without it, say so
once and run `claude` alone). Absent key in `CANON.md` means `[claude]`; `[]` turns outside readers off. They never run in plan mode, when
`naturalness: off`, or on a published chapter unless the user asks.

```yaml
critics: [claude, <openrouter id>, <openrouter id>]
```

Run them after your own reading and your auto-safe repairs, on the repaired text:

```bash
D=<book>/naturalness/critics/<chapter stem>
python3 <scripts>/critique.py run    <chapter> --dir $D   # the OpenRouter critics, in parallel
python3 <scripts>/critique.py prompt <chapter> --dir $D   # writes $D/prompt.md
```

Give `$D/prompt.md` to a subagent **as its whole task, with no summary of this conversation**. A
critic that shares the drafter's context shares its blind spots. Save its reply as
`$D/claude.reply.json`, then:

```bash
python3 <scripts>/critique.py add   <chapter> --dir $D --reply $D/claude.reply.json
python3 <scripts>/critique.py merge <chapter> --dir $D    # $D/merged.md, all flags by sentence
```

The script drops a quote that is not an exact substring of the chapter.

**Then you decide each sentence in `merged.md`.** A critic's flag is a claim, not a verdict:

- **Reject:**
  - the author's comic register;
  - the source's orthography or dialogue layout. On the real run two outside models "corrected"
    the author's dialogue punctuation;
  - word-order preferences with no stumble;
  - an overused pattern with no error;
  - anything whose fix changes a fact.
  
  `## Naturalness examples` outranks every critic.
- **Keep** the rest as review items, merged with your own item when you flagged the same sentence.
  `стало` is the critic's suggestion only if it passes Fixing above; otherwise write your own, or
  leave it empty.
- **Auto-safe mode:** a kept flag that meets all three repair conditions is applied like your own.
- **The review file's header:**
  - count what each critic raised and what you kept;
  - count rejections by reason, so the user can see what was filtered.

When the user's decisions are applied, add per-critic counts to the log line (`critics=gpt:3/5,…` =
accepted/shown). After a few chapters that is the evidence for dropping a critic that is mostly noise,
or adding one.

## Applying decisions

When the user says the review is done ("apply naturalness for ch05", "примени правки"):

1. Apply every `принять` and every `свой вариант` to the target, by exact-quote replacement. A quote
   that no longer matches (the text changed since) is reported, not guessed.
2. After a replacement inside a larger sentence, re-read the joined sentence: a fix quoted from mid-
   sentence can leave the old head or tail dangling. This happened on the real run twice.
   **Do not update the chapter's snapshot:** an accepted fix is the user's edit, and `refine-harness`
   learns from it (`write-chapter` §4).
3. Record every **rejection** and every **own variant** in `plan/HARNESS.md` → `## Naturalness
   examples` (below). These are the user's explicit verdicts, ratified in the review file itself, so
   they go in directly — the three-instance rule of `refine-harness` is for inferred patterns, not
   stated ones. Bump the harness revision and log it.
4. Score the predictions. A `принять` of `стало` as written, or an auto-repair left in place, is
   unchanged. Everything else is changed: `отклонить`, `свой вариант`, a reverted repair, a fix the
   user supplies where `стало` was empty.
5. Log to `wiki/log.md`:
   ```
   ## [YYYY-MM-DD] naturalize | <target> — <n> flagged, <n> accepted, <n> own, <n> rejected, <n> auto
      critics=<name>:<accepted>/<shown>,… shadow=low:<changed>/<n> high:<changed>/<n>
      miss: «<quote>» — <the signal it lacked>
   ```
   Write one `miss:` line per `low` item that changed, and none when nothing missed.

### `## Naturalness examples` in `plan/HARNESS.md`

```markdown
## Naturalness examples

| Mode | Было | Вердикт | Почему |
|---|---|---|---|
| prose | «с торжественностью, достойной коронации…» | keep — оригинал смешнее | ирония рассказчика |
| plan | «через горизонтальные связи» | → «друзья, которые помогут, хотя ничего не обещали» | образ вместо понятия |
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
