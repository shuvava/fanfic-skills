---
name: plan-chapters
description: >
  Use when ONLY when the user wants to expand a confirmed story intent into a chapter outline:
  "outline the story", "plan the chapters", "expand the plan", "break this into chapters",
  "outline book 2", "составь план глав", "разбей на главы", "напиши синопсис",
  "нужна аннотация". Requires plan/STORY_INTENT.md from plan-story. Produces the outline
  (Layer 1–4), the canon conflict check (CONFLICTS.md), and (from the finished outline) the
  synopsis and reader annotation. Do NOT use when no STORY_INTENT.md exists yet — that's
  plan-story first. Do NOT use when the user wants to draft prose — that's write-chapter.
---

# Plan Chapters

## Mode
Inline. Heavy Q&A — one observed session had 9 clarifying questions in a row, each
ratifying a layer of the outline. The user is in the loop throughout because misalignment
at planning time costs one question; misalignment after drafting costs a rewrite.

## Inputs required
- `plan/STORY_INTENT.md` (required) — from `plan-story`. If missing, redirect to plan-story.
- `CANON.md` (language settings, divergences)
- `wiki/canon/` (full — overview, world/constraints, world/география, forbidden, characters, voices)
- `plan/HARNESS.md` if it exists — project-local planning rules
- `plan/SERIES_ARC.md` if it exists — to resolve which book this is in a series
- `plan/IDEAS.md` if it exists — candidate material from `brainstorm`
- For a series book ≥2: the previous book's `outline.md` (start state) and `drafts/continuity.md`

## Skip-if-loaded
Before reading the canon wiki, check whether each file was already read this session. If yes
and no `ingest-source` / `write-chapter` / `reconcile` has happened since, reuse the
in-context content. The wiki is the largest single read in the pipeline; re-reading it costs
~3–5 K tokens of dead context per pass.

## Persistent state
- `<book>/outline.md` — the outline (Layer 1 part cards, Layer 2 part card paragraphs, Layer 3 chapter rows, Layer 4 scene lists)
- `<book>/conflicts.md` — the canon conflict check (7 checks)
- `<book>/SYNOPSIS.md` — `## Synopsis` (for the editor) and `## Annotation` (for readers)
- `plan/HARNESS.md` if it gets updated with new project-specific rules learned

Expand intent into a structured outline, ratifying each level with the user, then lint the plan
against canon before anyone writes a word.

Follow `../../CONVENTIONS.md`. The outline is written in `wiki_language`.

## 0. Resolve which book this is

**Do this before reading anything else.** This skill outlines *one book*. In a series it is one rung
of the ladder, not the whole thing, and its artifacts must not collide with the previous book's.

Determine layout and current book per `../../CONVENTIONS.md` §8:

- No `plan/SERIES_ARC.md`, or a ladder with one rung → **flat**. Paths are `plan/outline.md`,
  `plan/conflicts.md`. Skip the rest of this section.
- Otherwise → **series**. Resolve `current_book` from `CANON.md`, else from the highest-numbered
  `plan/book-*/` with undrafted chapters, else ask. State which book you are outlining and which rung
  of the ladder it is before expanding anything.
- If the project is flat but the user is asking for a second book, run the flat → series migration in
  §8 first, then continue. Do not plan book 2 into `plan/outline.md` — that file is book 1's.

`<book>/` below means the resolved book directory in a series, and `plan/` in a flat project.

## Prerequisites

Read `<book>/STORY_INTENT.md`. If it does not exist, run `plan-story` first — outlining without
established intent produces a plan the user did not ask for.

Also load, in this order:

1. **`canon/world/constraints.md`** — the flat ledger of what the world does not permit, one row per
   rule with its cost. Read it *first*. It is the cheapest way to catch a plan that needs a rule the
   world does not have, and its second section ("what canon does not establish") tells you which
   silences a scene would be quietly filling in.
2. **`canon/world/география.md`** — places and how they relate. Any scene that moves a character
   between two places is checked here: if canon states no distance or travel time, the plan is
   inventing one, and that is a `notice` needing ratification, not a detail.
3. `canon/overview.md` (structure conventions), `canon/plot/threads.md` (what is open),
   `canon/plot/timeline.md`, `canon/forbidden.md`.
4. `plan/HARNESS.md` if it exists — it may add project-specific checks to the conflict lint.
5. `plan/IDEAS.md` and `plan/SERIES_ARC.md` if they exist. `episode` ideas scoped to this book are
   Layer 4 candidates — offer them while building the scene list. **Their `check` field is not a
   clearance:** anything marked `light` had a smell test, not a lint, and every idea that reaches the
   scene list goes through the full conflict lint below like any other scene. If `SERIES_ARC.md`
   names a rung for this book, its end state is what the outline must actually deliver, and any
   `seed` due to be planted here belongs in a scene.

If the two derived pages do not exist, say so and offer to build them from the world pages. Linting a
plan without them means holding every world page in mind at once, which is how a world-logic gap
reaches the draft.

### Books before this one

Skip in a flat project. In a series, everything the earlier books established is context this outline
is answerable to, and none of it is in `wiki/canon/`:

6. **The previous book's rung** in `SERIES_ARC.md` — its end state is this book's start state.
7. **`drafts/continuity.md`** — what the fic itself has established across all books. This is the
   ledger that carries between books; it is not per-book and it is not optional reading.
8. **The previous book's `outline.md`**, and the summaries of its last two chapters. Summaries, not
   prose — loading a finished book to plan the next one dilutes attention for no gain.
9. **`wiki/fanon/`** — inventions the earlier books made and the user ratified. In book 2 these are
   as binding as canon in practice: contradicting one is not a fresh invention, it is the series
   forgetting itself. Anything still in `wiki/fanon/proposed/` from an earlier book means that book
   was never reconciled — say so and offer to run `reconcile` before outlining on top of it.

**Gate the start state.** Before Layer 1, state the previous book's end state and this book's start
state side by side and confirm they match. A mismatch is `blocking`: either the ladder is stale
because book N-1 ended somewhere else than planned — update `SERIES_ARC.md` — or this book is about
to ignore what the last one cost. Never resolve it by quietly outlining from the ladder's version
when the drafted book says otherwise; **the drafted book wins**, because it is what the reader read.

## Expand in layers, ratifying each

Expand the smallest complete statement of the story outward. **Show each level to the user and get
agreement before expanding it** — corrections are cheap at one paragraph and expensive at forty scenes.

**Layer 1 — One paragraph.** Setup, two or three complications, ending. Five sentences.

**Layer 2 — Arc synopsis.** One page. Each sentence of Layer 1 becomes a paragraph, each ending in a
complication or reversal. **Each paragraph is a part of the book** — `§N` with a title — and each part
is an arc with its own card (see *Parts* below).

**Layer 3 — Chapter list.** Grouped by part: one block per Layer 2 paragraph, headed with the same
number, title and its chapter range, so the retelling of a part and its chapters are visibly the same
stretch of story. One row per chapter: number, working title, POV, what happens, what
changes, which threads it touches, its **cut** where it has one — the moment inside a scene
where the chapter breaks off (see *Chapter endings* below) — and its **picture** where it has one
(see *Chapter pictures* below). **Numbering restarts at 1 in every book** — book 2 chapter 1 is
`b02/ch01`, not `ch09`. Continuing the count across books makes the chapter number a global
identifier that no file name carries, and the first cross-book reference then points at the wrong
chapter.

**Layer 4 — Scene list.** One row per scene: POV, setting, goal, conflict, outcome, point,
characters present, canon and fanon entries it depends on. `point` is what the reader must understand
when the scene ends — subtext and irony included, with its *because* — and `write-chapter` carries
it onto the beat card unchanged.

**Two kinds of cause.** Every act in a row or a scene says why, and says who will ever know it:
- **On the page** — «потому что …» in the plan's language: the reader sees it or is told it. «Анна
  просит сама: без отряда ей не сдать зачёт».
- **Offstage** — the same marker the plan's language uses for it (Russian «за кадром: …»): the
  author's logic that the narrator and the reader do not know, or only guess. Add when someone
  will guess it: «за кадром: наставник сам подбросил ей это задание, хочет проверить; Марк
  догадается в гл. 12». The drafter keeps the act consistent with it and no one says it aloud who cannot know it.

On a real book a part's rows carried neither: the user marked four flags of 32 «the answer is in my
head», and most of the rest were causes the plan meant and never wrote — some for the page, some only
to keep the logic straight (a superior quietly pushing someone, a rule bent for one student). Writing them down is
cheap; the next stage reads the row, not the planner's head.

Stop at four layers. Beat-level decomposition belongs to `write-chapter`, one chapter at a time —
beating out forty scenes in advance is work that gets thrown away when chapter 3 changes. **The same
refusal applies upward: outline one book.** If the user asks to outline the whole series, outline
this book and leave the rest as ladder rungs in `SERIES_ARC.md` — four layers across ten books is the
same waste an order of magnitude larger, and it gets discarded when book 2 changes.

**Match the source's structural conventions** from `canon/overview.md`: chapter length, scene count,
how chapters open and close. A continuation that reads right structurally matters as much as voice.

### Parts

A part is a stretch of chapters that works as a small story of its own: it raises a question, the
protagonist answers it in person, in a climax on the page, and the answer costs something. Novelists
call it a sequence, screenwriters a sequence or a mini-movie, web-serial authors an arc. All three
describe the same unit and the same failure without it: a long middle where chapters happen and
nothing is decided. A serial reader feels that first — the payoff for chapter 2's setup cannot wait
until chapter 30 with nothing answered in between.

**A part ends when it has answered its question,** not at a length. No source gives a standard length
in chapters, and none has reader-retention data to set one; a part of five chapters and one of fifteen
are both fine. **A book with one part** — one question, one climax, typical of a short book — gets no
card: the synopsis check below already holds its inciting event, climax and resolution. Write
`one part — the book` under Layer 2 and move on.

**The part card.** Write it under the part's Layer 2 paragraph, when that paragraph is ratified —
before the part is broken into chapters, while moving its borders costs a sentence. Seven lines, plain
words, each a picture, not a concept: not «she gains confidence» but «she speaks first at the council».

```markdown
- **Question:** what the reader waits to find out in this part — one question
- **Before → after:** the protagonist in the part's first chapter and in its last, two pictures
- **Inciting event:** chapter and event that open the part
- **Climax:** chapter; what the protagonist does in person, and the two options chosen between
- **Cost:** what the protagonist loses or pays
- **After:** where the reaction is, and the decision that hands the story to the next part
- **Threads:** each thread the part touches — `closed here` or `carried on`
```

Invented example, «Хроники Севера»:

```markdown
- **Question:** Найдёт ли Анна в совете голоса, о которых не узнает Марк?
- **Before → after:** Анна сидит в совете, а голосует за неё Марк → Анна голосует сама, но платить за место нечем
- **Inciting event:** гл. 3 — Марк её голосом проваливает закон её дома
- **Climax:** гл. 9 — на закрытом заседании Анна при всех рвёт доверенность; выбор между местом без голоса и голосом без денег
- **Cost:** род Марка забирает взнос за её место
- **After:** гл. 10 — Анна закладывает материнские серьги, чтобы внести взнос до пятницы, и решает просить денег у купцов
- **Threads:** доверенность — closed here; купеческая гильдия — carried on
```

**Where the reflection goes.** After a climax the protagonist reacts, weighs what is left and decides
— Swain's sequel: reaction, dilemma, decision. It is a job, not a kind of chapter, and its length is
the pacing control: a sentence keeps speed, a chapter buys belief.

- **By default it opens the next chapter**, as with a cut (*Chapter endings*): the climax chapter
  stops on the act or its immediate result, and the next chapter's first scene carries the reaction.
- **A chapter of aftermath** is for a climax with a high cost. It shows a consequence happening on the
  page — not only thoughts about one — lets at least two characters feel the cost differently, and
  ends on the decision the `After` line names.
- **At most one pause chapter** follows a climax: a chapter where the protagonist only reacts and
  nothing new happens on the page. A longer pause after a peak is the advice serial authors give
  against, and it is where an aftermath turns into filler. Chapters after the climax that carry
  their own event — a consequence arriving, another thread moving — are not a pause and do not
  count: on a real run the first version of this check counted every chapter after a climax and
  fired on three parts whose aftermath chapters each had an event.
- **The reflection ends in a decision.** One that ends in a mood leaves the next part without a goal.

**Threads.** Every thread the part touches is marked `closed here` or `carried on`. Authorities
disagree on whether subplots close before or after the main climax, so the mark records a choice
instead of enforcing a rule — what it catches is a thread that simply stops.

**A book already being published.** Write cards for every part, the published ones included. For a
published part the card is a reference: its checks report, and nothing in published chapters changes
(`../../CONVENTIONS.md` §13). For an unwritten part a finding is a plan fix, made now.

### Chapter endings

The ending that makes a reader open the next chapter is a **cut**: the chapter stops inside a scene,
at a moment whose outcome the reader cares about, and the next chapter opens in the same minute. It
matters most in a serial, where the reader decides at the last line whether to come back. Source
authors who write to a fixed chapter length do this often — they cut the stream at its tensest point
and put the narrator's reflection at the start of the next chapter, not at the end of this one.

**Pick the moment by its stakes, not by a quota.** Test: imagine the next chapter opening on the
worst outcome. If the reader would not mind either way, the moment is too weak to cut on. Moments
that pass:

- the protagonist's secret is about to come out;
- someone is about to be hurt, or already is and help is not coming;
- a fact arrives that breaks a plan;
- someone with power over the protagonist has asked, and the answer is due now.

Invented examples. Strong: the healer on duty counts his fee while the loser of a duel bleeds, and
Anna could heal him herself — at the cost of showing that she can. Weak: a stranger at the notice
board glances at her; whether he moves aside decides nothing.

**A chapter with no such moment ends closed**, as the source ends its chapters — a sting is fine.
Do not bolt a hook onto it:

- **a vague omen** («Что-то подсказывало мне, что это еще не конец») names nothing;
- **an invented scene** added at the end to make a cliffhanger is a staged moment in a voice that
  is not the narrator's;
- **cutting the chapter's point** to make room for a hook loses what the chapter was for;
- **a spoiler** («Тогда я еще не знал, что…») spends a later payoff;
- **a cheat** — a threat the next chapter dismisses in its first line — teaches the reader to
  stop trusting the endings.

A cut per chapter is a quota, and a quota fills with weak moments: in a real run, cutting every other
chapter put a cut on a glance nobody cared about, and the user rejected it. Mark cuts in the Layer 3
rows where a moment passes the test and nowhere else. The row after a cut opens with its continuation.

### Chapter pictures

Only when `illustration_required` is `planned` for this book (`illustrate` → Settings; per-book,
`../../CONVENTIONS.md` §8). With `true`, every chapter gets a picture and the column is not needed;
with `false`, there are no pictures.

A picture costs rounds of generation and review — on a real run, most of the time spent on a chapter.
Readers of serials treat chapter art as a bonus, not an expectation, and a professionally illustrated
novel carries roughly one insert per five thousand words. So the outline decides **once per book**
which chapters get one, instead of every chapter asking.

**Pick by the moment, not by a quota.** A row gets a `picture` only when one of these holds:

- **an important character's first appearance** — their sheet is built now and every later picture
  reuses it;
- **a key moment** — an arc's climax, a fight, a reveal, or a cut that passes the stakes test
  (*Chapter endings*);
- **something the reader wants to see** — a place, a creature or an object the text cannot fully show.

Write the cell as the moment in one line, who is in it, and why it passes:
`рыцарь у ворот, один + конь — первое появление` (invented). **Prefer at most two characters.** A
crowded frame or two figures in contact costs the most rounds; give it only to a moment worth them.

**Spacing.** `picture_every_words` (`illustrate` → Settings, default 5000) is the target density:
about one picture per that many words of the book. The source's chapter length from
`canon/overview.md` turns it into chapters — with 1000-word chapters, about one in five. It is a
target, not a quota: a stretch where nothing passes the test stays unillustrated, and two strong
moments may sit in neighbouring chapters.

**Switching a book that is already being drafted** to `planned`: mark only rows not yet drafted.
Chapters already illustrated keep their pictures.

### Self-review before showing a layer

Ratification is only as good as what you hand over, and a user cannot ratify vagueness — they read
"and then they confront him" as shorthand for something you have already worked out, when it is
usually shorthand for nothing. Audit your own layer before presenting it:

- **No placeholders.** No `TBD`, no `(details later)`, no "something happens that forces the choice".
  If you do not know what happens, that is a question to ask, not a row to write.
- **No borrowed rows.** "Like chapter 4 but at the palace" is not a chapter. Write it out.
- **Plain words, not concept-speak.** A row the user would not say aloud to a friend — abstract nouns,
  planner's jargon ("cooperation against rigid hierarchy") — is drafted the same way later. Run
  `naturalize` in plan mode over Layers 1–2 and the `point` column (unless `naturalness: off`) and
  hand its review file over with the layer.
- **Every scene has a conflict and a change.** A Layer 4 row whose `outcome` restates its `goal` is a
  scene with nothing in it. Cut it, or give it opposition.
- **Every scene has a point, and it is not the outcome.** A row whose `point` is empty or restates
  `outcome` ("the heroes win") has not decided what the scene is *for*. Meaning that is not written
  here is lost downstream: every later stage — beat card, draft — can only keep or lose it, never add it.
- **Every row traces upward.** Each Layer 3 chapter implements a sentence of Layer 2 and sits in its
  part's block; each Layer 4 scene sits inside a Layer 3 chapter. An orphan is either a missing beat
  upstream or scope creep.
- **Every intent element lands.** Walk `STORY_INTENT.md`'s premise, themes, central conflict and cast
  — each should be findable in the outline. Anything unlanded is a gap to name now, not at chapter 9.
- **Names and numbers are consistent** across layers: one spelling per character, chapter numbers
  contiguous from 1, POV characters drawn from the intent's cast.
- **Every chapter has an event.** Something happens on the page that changes a situation — not only
  what the POV character thinks about it. A Layer 3 row whose "what changes" is a realization is a
  reaction chapter; reaction chapters never run two in a row.
- **The book starts early.** The inciting event — whatever makes this book's central question urgent —
  lands within the first ~10% of chapters. Setup that precedes it is compressed into it, not given its
  own run of chapters. A real reader's verdict on three setup chapters was *a plot without a plot*.
- **No re-staged canon scenes.** When a chapter's event has a canon precedent — an exam where canon
  already showed an exam — name the precedent in the row and say what differs. "The canon scene again,
  later" is a borrowed row.
- **Every cut passes the stakes test** (*Chapter endings*), and the row after it opens with its
  continuation. A cut on a moment that decides nothing is a `warning`.
- **Every picture passes the test** (*Chapter pictures*), and names its moment and who is in it.
  A gap of more than twice `picture_every_words` with no picture is a `warning` — name the strongest
  moment in it and let the user decide. Not a rule: a quiet stretch may stay quiet.
- **Fold test.** If the next chapter could open with one line summarising this one and lose nothing,
  merge them.
- **Every part passes the part checks.** Each is a `warning` that names the part and the chapter and
  asks — never a quota, and never a block. On a published part they report only. The seven checks
  (climax answers the question, protagonist decides on the page, cost is not "nothing", trouble
  grows from different sides, part is not the last one bigger, no thread drops silently,
  reflection ends in a decision) and a worked example live in
  [references/part-checks.md](references/part-checks.md).
- **Every character above the depth threshold has a profile** (`../../CONVENTIONS.md` §11). A
  character who has a line, appears in two scenes, or acts on a scene's goal without a profile in
  `wiki/fanon/proposed/characters/` is a `warning` — offer `develop-character`. Then look at the scene
  list the way its cardboard check does: a character whose every appearance serves the protagonist is
  an outline problem to fix now, not a prose problem to discover at chapter 30.

### Breaks reader — two runs, before showing a part

The self-review checks the shape of the plan; it does not ask *why* each person in a row does what
the row says. A fresh-context reader does. It lists every event in a part, looks for each one's
cause in the rows, the profiles, the written chapters and the source, and flags an act with no
cause, against what the story already showed, or decided off the page. On one book it caught the
user's own objections to a part about as often as it does on beat cards, and the user judged 31 of
its 32 flags on two versions of one part worth asking (27 real, 4 «the answer is in my head, not in
the row»). Most real flags were exactly that: a cause the planner meant and never wrote, which the
user then had to add by hand in the beats and the prose. On a version whose first chapters were
written, six of 13 flags were the plan contradicting those chapters. Unless `CANON.md` sets
`logic_reader: off`, run it for every part you are about to show, and again for a part whose rows an
edit changed (a promoted idea, a rebuilt part); skip a part whose chapters are all live.

Copy into `$D/part.md`, word for word, the part's Layer 2 paragraph and card, its Layer 3 block and
its Layer 4 block — the reader quotes the target and the script keeps only exact quotes. Then:

```bash
D=<book>/logic/part-<N>-breaks
python3 <scripts>/logic_reader.py prompt $D/part.md --stage outline --check breaks --dir $D
```

Give `$D/prompt.md` to **two** fresh-context subagents in parallel, nothing of the conversation:
«Working directory: <project root>. Read `$D/prompt.md` — it is your whole task. Write the JSON to
`$D/reply1.json`» (`reply2.json` for the second). Then
`python3 <scripts>/logic_reader.py add $D/part.md --dir $D --reply $D/reply1.json --reply $D/reply2.json`
and sort `$D/report.md`:

- **Fix yourself** a cause you know but the row does not say: write it into the row or the scene,
  on the page or offstage (*Two kinds of cause*). Do not count it as a false alarm — the next stage
  reads the row, not your head.
- **Drop** a flag the rows already answer in so many words, or one the user decided for this exact
  break before (log, beat file, IDEAS).
- **Ask** the rest with the layer, each with your recommendation, including a break made on purpose.
  When a row contradicts a written chapter, say which side looks wrong; a queued chapter can still
  change (`CONVENTIONS.md` §13).

**Put the questions through `naturalize` first** (plan mode, unless `naturalness: off`): the reader
writes compressed, and a question the user has to ask about is a question not answered. **Ask in
story order, one chapter at a time:** a flag on the part's paragraph or card goes with the chapter it
is about; settle that chapter and write the answers into its rows before the next, then re-read the
remaining flags and drop the ones the fix settled. Delete `$D` once the answers are in the rows.

### Synopsis check — Layers 1–2

Fill the publisher's synopsis form from Layers 1–2 alone — treat the form as a test. A field you
cannot fill from the layers is a hole in the story, not in the form. The full field table,
annotation rules, synopsis writing rules, and the mechanical check live in
[references/synopsis-checklist.md](references/synopsis-checklist.md).

Show the filled table with Layer 2. A field left empty is a question for the user, like a
placeholder.

**Report what the self-review found rather than silently fixing it.** "Clean — three scenes had no
conflict and were cut, the loyalty theme lands nowhere after chapter 5" is worth more than a
clean-looking layer, because it tells the user where the outline is weakest while it is still cheap.

## The conflict lint

**This is the stage the pipeline exists for.** Run it over the completed scene list, before drafting.

For every scene, resolve the entities and facts it depends on against the wiki, and classify each
against `<book>/STORY_INTENT.md`'s load-bearing list and `canon/forbidden.md`:

| Severity | Condition | Behavior |
|---|---|---|
| `blocking` | Scene contradicts a `canon` fact, or violates `forbidden.md` | Stop. Ask. |
| `warning` | Scene contradicts `fanon-established` | Report; user decides |
| `notice` | Contradicts `fanon-proposed`, or asserts something canon is silent on | Batch report |

Also check:
- **Timeline conflicts** — does scene placement contradict `timeline.md`? Are characters alive,
  present, and the right age?
- **Would-never-do violations** — does any scene require a character to act outside their recorded
  internal code? This is the most common source of "OOC" complaints and it is detectable here.
- **World-limit violations** — does a scene solve a problem with a system whose recorded costs it
  doesn't pay?
- **Thread status** — does a scene claim to advance a thread `threads.md` marks `paid` or `abandoned`?
- **Unsupported assertions** — facts the scene needs that no tier has. These are gaps, not conflicts.

### Cross-book checks

Series only. The full check table (start-state drift, prior-fanon contradiction, continuity-ledger
contradiction, published contradiction, undelivered rung, unplanted/unpaid seed, premature payoff,
ladder overreach) and the resolution protocol live in
[references/cross-book-checks.md](references/cross-book-checks.md).

A seed check is cheap to run and impossible to run late: by the time book 4 needs the object planted
in book 2, book 2 is drafted and the fix costs a rewrite of a published chapter or a coincidence the
reader will notice.

## Synopsis and annotation

Once the lint has no unresolved `blocking` conflict, write `<book>/SYNOPSIS.md`. For a book outlined
earlier, run only the synopsis check and this section when the user asks for a synopsis or an
annotation.

**It is derived, not a plan.** It is built from `STORY_INTENT.md`, Layers 1–2 of the outline, the
synopsis check and, in a series, the next rung of `SERIES_ARC.md`. Nothing downstream reads it as
input: beat cards, drafts and the lint read the outline. Two plot summaries that both steer the
writing will drift apart, and nothing can tell which one is right. If the synopsis needs something
the outline does not say, that is a gap in the outline. Fix the outline first.

For chapters already drafted, the text outranks their outline rows. For published chapters the
published text outranks everything (`../../CONVENTIONS.md` §13). Retell what the reader got.

Write it in `output_language`, not `wiki_language`: editors, contest juries and readers outside the
project read it. Then run `naturalize` in plan mode over it (unless `naturalness: off`). The
annotation is the first text a reader sees.

```markdown
---
type: synopsis
book: <NN>
derived_from: outline.md <outline's last_updated>
created: <YYYY-MM-DD>
language: <output_language>
---

# <title>

## Setting
## Series position        (series only: book N, what the previous book left the protagonist with)
## Main characters        (3–6, one line each: who they are, what they want)
## Antagonist             (a person, or the circumstances, from the synopsis check)
## Annotation             (for readers, no spoilers)
## Synopsis               (for an editor, everything)
## Main intrigue          (and what carries into the next book)
```

The full annotation and synopsis writing rules, the mechanical check, and the worked example
live in [references/synopsis-checklist.md](references/synopsis-checklist.md). Read that file
before writing either.

**Check before showing.** Run the mechanical check listed in the reference, fix everything it
reports, then reread the text as the stranger would.

**Keep it current.** `derived_from` records the outline version it was built from. When Layer 1 or 2
changes, regenerate the synopsis in the same run, and ask the user before changing an annotation
already on a platform (`publish` → Book page). `wiki-lint` reports a synopsis older than its outline.

## Artifacts

`<book>/outline.md` — all four layers, `tier: fanon-proposed`, with every canon dependency cited,
each Layer 2 part followed by its card and Layer 3 grouped by part. In
a series its frontmatter carries `book: <NN>` and `rung: <NN>`, and it opens with the start state it
was planned against, so the next book can check itself against something written down.

`<book>/conflicts.md` — the lint report:

```markdown
| Severity | Scene | Conflict | Canon says | Plan says | Resolution |
|---|---|---|---|---|---|
```

`<book>/SYNOPSIS.md` — synopsis and annotation, derived from the outline (above).

Facts the plan invents go to `wiki/fanon/proposed/` — not into `wiki/canon/`, ever. The fanon tier is
series-wide and stays that way; it is not split per book, because book 3 needs what book 1 invented.

`plan/SERIES_ARC.md` is updated, never rewritten: this rung's end state is reconciled with what the
outline actually delivers, seeds planted here move to `planted (b<NN>/ch<NN>)`, seeds paid here move
to `paid`. If the outline changed what this book leaves the character with, the *next* rung's start
state changes with it — edit it now, or the ladder is broken the moment this book drafts.

Ideas from `plan/IDEAS.md` that became scenes are marked `promoted` there, with the scene that took
them. Ideas the lint killed move to its `## Killed` table with the conflict as the reason — otherwise
they return next brainstorm and get re-argued from scratch.

Append to `wiki/log.md`:
```
## [YYYY-MM-DD] plan-chapters | b<NN> — <n> chapters, <n> conflicts (<n> blocking)
   metrics: book=<NN> chapters=<n> scenes=<n> parts=<n> part_chapters=<n,n,...> blocking=<n> warnings=<n> notices=<n> seeds_planted=<n> seeds_paid=<n> breaks=<flagged>/<fixed>/<asked>
## [YYYY-MM-DD] plan-chapters | b<NN> synopsis — from outline <last_updated>
```
The synopsis line is logged whenever `SYNOPSIS.md` is written, alone on a synopsis-only run. Drop
`b<NN>` and `book=` in a flat project.

## Rules

- **Ratify each layer before expanding it**, and self-review it before showing it.
- **No completion claim without fresh evidence** — `../../CONVENTIONS.md` §10. "The lint is
  clean" means it was run over the finished scene list this session.
- **Never let a blocking conflict through to drafting.**
- **The plan is `fanon-proposed`, not canon.** It cannot edit `wiki/canon/`.
- **One book per run.** Resolve which book before Layer 1; never write into another book's directory.
- **The drafted text outranks the ladder.** Where `SERIES_ARC.md` and the previous book's chapters
  disagree, the chapters are right and the ladder gets corrected.
- Report honestly when the plan is clean. Zero conflicts is a real result.
- **The synopsis follows the outline, never leads it.** No stage drafts from `SYNOPSIS.md`, and a
  change that starts there goes into the outline first.
- Keep it proportional: a one-shot needs Layers 1 and 4 only. Do not build a four-layer hierarchy for
  two thousand words. Run its synopsis check over Layer 1, and write `SYNOPSIS.md` only on request.
  A one-shot has no parts and no cards.
- **Part checks warn, they never block.** Strict control of a plan makes generated stories less
  interesting, and a part that breaks a check on purpose is a choice to record, not a defect.
