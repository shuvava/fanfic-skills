---
name: plan-chapters
description: >
  Expand the story intent into a hierarchical outline — arc, chapters, scenes — and run the canon
  conflict check over the plan before any prose exists. Use when the user says "outline the story",
  "plan the chapters", "expand the plan", "break this into chapters", "outline book 2", or after
  plan-story finishes. Handles both a standalone work and one book of a multi-book series, keeping
  each book's plan separate and its start state matched to the previous book's end state.
  Surfaces canon contradictions at planning time, when they cost one question instead of a rewrite.
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

**Layer 4 — Scene list.** One row per scene: POV, setting, goal, conflict, outcome, characters
present, canon and fanon entries it depends on.

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
- **Every scene has a conflict and a change.** A Layer 4 row whose `outcome` restates its `goal` is a
  scene with nothing in it. Cut it, or give it opposition.
- **Every row traces upward.** Each Layer 3 chapter implements a sentence of Layer 2; each Layer 4
  scene sits inside a Layer 3 chapter. An orphan is either a missing beat upstream or scope creep.
- **Every intent element lands.** Walk `STORY_INTENT.md`'s premise, themes, central conflict and cast
  — each should be findable in the outline. Anything unlanded is a gap to name now, not at chapter 9.
- **Names and numbers are consistent** across layers: one spelling per character, chapter numbers
  contiguous from 1, POV characters drawn from the intent's cast.

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

## Artifacts

`<book>/outline.md` — all four layers, `tier: fanon-proposed`, with every canon dependency cited. In
a series its frontmatter carries `book: <NN>` and `rung: <NN>`, and it opens with the start state it
was planned against, so the next book can check itself against something written down.

`<book>/conflicts.md` — the lint report:

```markdown
| Severity | Scene | Conflict | Canon says | Plan says | Resolution |
|---|---|---|---|---|---|
```

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
```
Drop `b<NN>` and `book=` in a flat project.

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
- Keep it proportional: a one-shot needs Layers 1 and 4 only. Do not build a four-layer hierarchy for
  two thousand words.
