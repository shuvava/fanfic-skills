---
name: plan-chapters
description: >
  Expand the story intent into a hierarchical outline — arc, chapters, scenes — and run the canon
  conflict check over the plan before any prose exists. Use when the user says "outline the story",
  "plan the chapters", "expand the plan", "break this into chapters", or after plan-story finishes.
  Surfaces canon contradictions at planning time, when they cost one question instead of a rewrite.
---

# Plan Chapters

Expand intent into a structured outline, ratifying each level with the user, then lint the plan
against canon before anyone writes a word.

Follow `../../CONVENTIONS.md`. The outline is written in `wiki_language`.

## Prerequisites

Read `plan/STORY_INTENT.md`. If it does not exist, run `plan-story` first — outlining without
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

If the two derived pages do not exist, say so and offer to build them from the world pages. Linting a
plan without them means holding every world page in mind at once, which is how a world-logic gap
reaches the draft.

## Expand in layers, ratifying each

Expand the smallest complete statement of the story outward. **Show each level to the user and get
agreement before expanding it** — corrections are cheap at one paragraph and expensive at forty scenes.

**Layer 1 — One paragraph.** Setup, two or three complications, ending. Five sentences.

**Layer 2 — Arc synopsis.** One page. Each sentence of Layer 1 becomes a paragraph, each ending in a
complication or reversal.

**Layer 3 — Chapter list.** One row per chapter: number, working title, POV, what happens, what
changes, which threads it touches.

**Layer 4 — Scene list.** One row per scene: POV, setting, goal, conflict, outcome, characters
present, canon and fanon entries it depends on.

Stop at four layers. Beat-level decomposition belongs to `write-chapter`, one chapter at a time —
beating out forty scenes in advance is work that gets thrown away when chapter 3 changes.

**Match the source's structural conventions** from `canon/overview.md`: chapter length, scene count,
how chapters open and close. A continuation that reads right structurally matters as much as voice.

## The conflict lint

**This is the stage the pipeline exists for.** Run it over the completed scene list, before drafting.

For every scene, resolve the entities and facts it depends on against the wiki, and classify each
against `plan/STORY_INTENT.md`'s load-bearing list and `canon/forbidden.md`:

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

`plan/outline.md` — all four layers, `tier: fanon-proposed`, with every canon dependency cited.

`plan/conflicts.md` — the lint report:

```markdown
| Severity | Scene | Conflict | Canon says | Plan says | Resolution |
|---|---|---|---|---|---|
```

Facts the plan invents go to `wiki/fanon/proposed/` — not into `wiki/canon/`, ever.

Append to `wiki/log.md`:
```
## [YYYY-MM-DD] plan-chapters | <n> chapters, <n> conflicts (<n> blocking)
   metrics: chapters=<n> scenes=<n> blocking=<n> warnings=<n> notices=<n>
```

## Rules

- **Ratify each layer before expanding it.**
- **Never let a blocking conflict through to drafting.**
- **The plan is `fanon-proposed`, not canon.** It cannot edit `wiki/canon/`.
- Report honestly when the plan is clean. Zero conflicts is a real result.
- Keep it proportional: a one-shot needs Layers 1 and 4 only. Do not build a four-layer hierarchy for
  two thousand words.
