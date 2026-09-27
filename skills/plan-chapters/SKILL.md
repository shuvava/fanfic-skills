---
name: plan-chapters
description: >
  Expand the story intent into a hierarchical outline — arc, chapters, scenes — and run the canon
  conflict check over the plan before any prose exists. Use when the user says "outline the story",
  "plan the chapters", "expand the plan", "break this into chapters", "outline book 2", or after
  plan-story finishes. Handles both a standalone work and one book of a multi-book series, keeping
  each book's plan separate and its start state matched to the previous book's end state.
  Surfaces canon contradictions at planning time, when they cost one question instead of a rewrite.
  Also writes the book's synopsis and reader annotation from the finished outline — use when the
  user says "write the synopsis", "we need an annotation", "напиши синопсис", "нужна аннотация".
---

# Plan Chapters

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
complication or reversal.

**Layer 3 — Chapter list.** One row per chapter: number, working title, POV, what happens, what
changes, which threads it touches. **Numbering restarts at 1 in every book** — book 2 chapter 1 is
`b02/ch01`, not `ch09`. Continuing the count across books makes the chapter number a global
identifier that no file name carries, and the first cross-book reference then points at the wrong
chapter.

**Layer 4 — Scene list.** One row per scene: POV, setting, goal, conflict, outcome, point,
characters present, canon and fanon entries it depends on. `point` is what the reader must understand
when the scene ends — subtext and irony included, with its *because* — and `write-chapter` carries
it onto the beat card unchanged.

Stop at four layers. Beat-level decomposition belongs to `write-chapter`, one chapter at a time —
beating out forty scenes in advance is work that gets thrown away when chapter 3 changes. **The same
refusal applies upward: outline one book.** If the user asks to outline the whole series, outline
this book and leave the rest as ladder rungs in `SERIES_ARC.md` — four layers across ten books is the
same waste an order of magnitude larger, and it gets discarded when book 2 changes.

**Match the source's structural conventions** from `canon/overview.md`: chapter length, scene count,
how chapters open and close. A continuation that reads right structurally matters as much as voice.

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
- **Every row traces upward.** Each Layer 3 chapter implements a sentence of Layer 2; each Layer 4
  scene sits inside a Layer 3 chapter. An orphan is either a missing beat upstream or scope creep.
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
- **Fold test.** If the next chapter could open with one line summarising this one and lose nothing,
  merge them.
- **Every character above the depth threshold has a profile** (`../../CONVENTIONS.md` §11). A
  character who has a line, appears in two scenes, or acts on a scene's goal without a profile in
  `wiki/fanon/proposed/characters/` is a `warning` — offer `develop-character`. Then look at the scene
  list the way its cardboard check does: a character whose every appearance serves the protagonist is
  an outline problem to fix now, not a prose problem to discover at chapter 30.

### Synopsis check — Layers 1–2

Before showing Layer 2, fill in the fields a publisher's synopsis form asks for, one line each,
from Layers 1–2 alone. Treat the form as a test: a field you cannot fill from the layers is a hole
in the story, not in the form, and here it costs one question.

| Field | Filled when | Typical hole |
|---|---|---|
| Setting | place, time and the circumstances the conflict depends on | rarely fails — canon supplies it |
| Protagonist | who, what they want, what in them stands in the way | no want: the hero only reacts, all book |
| Antagonist | a person, or opposing circumstances named concretely ("the rule that…", not "obstacles") | complications that share no source, so nothing pushes back twice |
| Inciting event | the event that makes the central question urgent | the "book starts early" check above |
| Climax | a scene on the page where the central conflict is decided by what the protagonist does | a result reported instead of a scene where it is decided |
| Twist | a reversal the reader did not expect that follows from something planted earlier — name where | none, or one with nothing planted: a coincidence |
| Resolution | what differs from the start state, for the protagonist and for the central conflict | the ending restates the start |
| Main intrigue | the one question the reader carries across the book; answered here or handed to the next rung | a list of subplots and no single question |

Invented example, «Хроники Севера»: "Anna wins the trial" is a result, not a climax. The climax is
the scene where she testifies against Mark in open court, knowing it costs her the family name.

**Before calling a field a hole, read the protagonist's profile** in `wiki/fanon/proposed/characters/`.
Its ratified shift section says where the change happens and what kind of change it is. Layer 2 may
give that scene one clause. On a real run, a check made from the layers alone recommended a new scene
for a change the profile had already placed, and the user had to be asked again. Where the profile
and the intent describe the change differently, that mismatch is the finding. Fix the intent's
wording; do not add a scene.

"Circumstances" as antagonist and "no twist" are legitimate answers when they are chosen. Record
them as choices. In a series, a main intrigue handed forward must exist in the next rung of
`SERIES_ARC.md` or as a seed there; otherwise the book ends on a question nobody plans to answer.
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

Series only. These are the failures a per-book lint cannot see, and they are the expensive ones —
each is discovered three books later otherwise.

| Check | What goes wrong | Severity |
|---|---|---|
| **Start-state drift** | A scene assumes a state the previous book's drafted ending contradicts. | `blocking` |
| **Prior-fanon contradiction** | A scene contradicts a `fanon-established` fact an earlier book set. | `warning` — the user may be retconning on purpose, but it is never a silent change |
| **Continuity-ledger contradiction** | A scene contradicts `drafts/continuity.md` — something the earlier prose actually said. | `blocking`. The published text is not revisable by a plan |
| **Published contradiction** | A scene contradicts a chapter with `published:` in its frontmatter, or re-plans one (`../../CONVENTIONS.md` §13). Applies within a book too. | `blocking` — readers have it; only typo-only errata can change it |
| **Undelivered rung** | The Layer 2 ending does not reach this rung's end state. | `blocking` — the next book's start state is already written against it |
| **Unplanted seed** | A `SERIES_ARC.md` seed with `Plant in` = this book that no scene plants. | `blocking` — the payoff book has nothing to pay off |
| **Unpaid seed** | A seed with `Payoff target` = this book that no scene pays. | `warning`; either schedule it here or move the target and say so |
| **Premature payoff** | A scene resolves a thread or seed reserved for a later rung. | `warning` — spending it now leaves the later book with a hole |
| **Ladder overreach** | The outline delivers a state two or more rungs ahead. | `notice`; the ladder is wrong, not the book. Update `SERIES_ARC.md` |

A seed check is cheap to run and impossible to run late: by the time book 4 needs the object planted
in book 2, book 2 is drafted and the fix costs a rewrite of a published chapter or a coincidence the
reader will notice.

### Resolving a blocking conflict

Present it plainly, with both sides and their citations, then ask a single question:

> Scene 7 has her using the family name openly. Canon establishes she abandoned it after the trial
> [src: ch12.md#...] and `forbidden.md` records that as a hard line.
> Is this an intentional divergence, or should the scene change?

Three outcomes:
- **Intentional** → record in `CANON.md` `divergences`, tag the fact `fanon-divergence`, continue.
- **Error** → revise the scene.
- **Canon was wrong** → the wiki misread the source. Re-check `raw/` and fix the canon page. This is
  the only circumstance in which a canon page changes, and it requires re-reading the source.

Never resolve a blocking conflict unilaterally. Never proceed past one unresolved.

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

**The annotation** sells the premise:
- It goes up to the inciting event and no further. The climax, the twist and the ending never
  appear in it.
- Check it against the reveal section of every character profile it mentions. It is read before
  chapter 1, so anything scheduled for a later reveal is out.
- Give a situation and a question, not a list of themes. "A story about friendship and betrayal" is
  concept-speak, and every other book's annotation says the same thing.
- Match the book's voice. A first-person book often gets a first-person annotation. The voice may
  be the narrator's; the words must still be ones a stranger understands.
- Keep it short, a few hundred to a thousand characters. The platform's limit is in its `publish`
  adapter.

**The synopsis** retells the whole book, ending included, to someone who has never opened the
series. Write it the way a person retells a book to a friend, not the way the outline is written.
On a real run a synopsis assembled from outline rows was rejected whole ("not human language",
"much worse than the example"), though every fact in it was right. `synopsis_check.py` found that
half its sentences contained a five-word run copied from the outline. What the good example the
user supplied did, and the rejected one did not:

- **Tell it fresh, from the events.** Take from the outline *what happens and why*, then close it
  and write your own sentences. The outline's phrasing is shorthand for people who already know the
  story: paradox closers («получил допуск — и не владеет ничем, включая собственное имя»), a
  scene's meaning in place of the scene, a verdict at the end of every paragraph. In a synopsis
  these read as riddles.
- **One thread, told in steps.** Each paragraph is one step of the protagonist's story: situation →
  problem → what they try → what it costs → what changes. Subplots appear only where they hit that
  thread. Never "Meanwhile, in parallel…" — that is the outline's line structure showing through.
- **Few names.** Name the protagonist, the antagonist and the two or three people who change the
  plot, five or six in total. Everyone else is "a classmate", "two outcasts nobody else would
  take", "his brothers". A fight is told by its outcome and the protagonist's part in it, not a
  roll call of who struck what.
- **Explain every world word at first use, or drop it.** Before writing, list the words a stranger
  would not know: world terms, ranks, game jargon, creature and place names. Each one is explained in
  half a sentence where it first appears («ядро — источник силы внутри человека»), or replaced by a
  plain description («хищные цветы у воды»), or cut.
- **Name motives and feelings plainly.** «Она хочет, чтобы глава клуба её заметил», «он злится и
  решает отомстить». A reader follows people, not mechanisms.
- **Plain sentences.** Subject, verb, what happened, joined by «но», «поэтому», «тогда». Aim at
  15–20 words; none over 30. No semicolon chains, no colon lists, no dash that ends a paragraph on
  an aphorism.
- Present tense, third person. No project apparatus: thread codes, block and chapter numbers, tiers,
  `[src:]`. One to two pages.

Invented example, «Хроники Севера». Assembled from the outline, rejected:
> Анна получает место в совете, которого добивалась, — и не владеет в нём ничем, включая
> собственный голос; параллельно Марк ведёт проект, о котором не говорит вслух.

Retold:
> Анну принимают в совет. Но голосовать за неё там будет Марк: её место оплатил его род. Анна
> злится и решает найти в совете союзников, о которых Марк не узнает.

**Check before showing.** Run the mechanical check, fix everything it reports, then reread the text
as the stranger would:

```bash
python3 <scripts>/synopsis_check.py <book>/SYNOPSIS.md --section <synopsis heading> \
  --against <book>/outline.md <book>/STORY_INTENT.md
```

`COPIED` means a sentence carries a five-word run from the plan: rewrite it, do not reword around
the run. Then read it once more with two questions only: is there a word this reader does not know,
and is there a sentence you would not say aloud when retelling the book? The script cannot answer
either.

**Keep it current.** `derived_from` records the outline version it was built from. When Layer 1 or 2
changes, regenerate the synopsis in the same run, and ask the user before changing an annotation
already on a platform (`publish` → Book page). `wiki-lint` reports a synopsis older than its outline.

## Artifacts

`<book>/outline.md` — all four layers, `tier: fanon-proposed`, with every canon dependency cited. In
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
   metrics: book=<NN> chapters=<n> scenes=<n> blocking=<n> warnings=<n> notices=<n> seeds_planted=<n> seeds_paid=<n>
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
