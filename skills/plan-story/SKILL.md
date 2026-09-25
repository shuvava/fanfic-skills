---
name: plan-story
description: >
  Interview the user to establish what fic they actually want to write, before any outline or prose
  exists. Produces plan/STORY_INTENT.md. Use when the user says "let's plan the story", "I want to write
  a fic about X", "help me figure out what to write", "start planning", or asks to write a chapter in a
  project that has no story intent yet. One question at a time, each with a recommended answer.
---

# Plan Story

Establish authorial intent through a relentless one-question-at-a-time interview. This is the first
human gate in the pipeline and the highest-leverage one — misalignment here costs a rewrite of
everything downstream.

Follow `../../CONVENTIONS.md`. The interview happens in the user's language; the
artifact is written in `wiki_language`.

## The interview protocol

Adapted from the "grilling" collaboration pattern. Follow it exactly — the discipline is the point.

**Read `plan/HARNESS.md` first if it exists.** It may add project-specific questions to the tree,
learned from earlier rounds. Its questions are asked alongside the standard ones, in the same
one-at-a-time discipline.

**Read `plan/SERIES_ARC.md` and `plan/IDEAS.md` if they exist.** They hold decided-nothing candidate
material from `brainstorm`: a series destination with its ladder, and shortlisted ideas. Use them as
recommendation sources, not as answers — nothing there passed a gate. If `SERIES_ARC.md` names which
rung this book is, its start and end states answer the placement questions and constrain what the fic
may resolve; state that rather than asking. **If an earlier book is already drafted, read its ending
and `drafts/continuity.md` before asking anything about placement** — the drafted text is this book's
actual start state, and where it disagrees with the ladder, the text wins and the ladder is stale. If the user is planning a series and neither file exists,
offer `brainstorm` first — grilling someone toward a premise they have not yet found is the wrong
tool.

**Look for the source author's own statements** — entries cited `[author: ...]` in `plan/IDEAS.md` or
`wiki/fanon/proposed/` (`../../CONVENTIONS.md` §2). Where the author has said what they intended, that
is your recommended answer to the matching question, attributed as theirs. It is not canon and does
not bind the user.

**Look up facts. Ask only decisions.**
Anything discoverable in `wiki/canon/` must be read, never asked. Do not ask "who is the protagonist's
sister?" — read it. Ask only what is genuinely the user's call: what they want this fic to *be*.

**One question at a time.**
Ask a single question, wait for the answer, then ask the next. Asking several at once is bewildering
and produces shallow answers. Do not batch. Do not present a numbered list of six questions.

**Always attach your recommended answer.**
Every question comes with what you would choose and one line of why. Ratifying a recommendation is
cheap; composing from scratch is expensive. The user should be able to say "yes" and move on.

**Walk the decision tree in dependency order.**
Resolve upstream decisions before those that depend on them. Timeline placement constrains which
characters are alive and available; POV constrains what the reader can know; those come before scene
specifics.

**Stop at shared understanding.**
When the decisions are resolved, summarize everything back and ask the user to confirm. **Do not
write the artifact or proceed to outlining until they confirm.**

## The decision tree

Walk roughly in this order, skipping anything the user already specified and pruning branches their
answers make irrelevant.

**Root — what kind of fic**
1. Premise in one sentence. (Recommend a shortlisted `arc` idea from `plan/IDEAS.md` if there is one,
   otherwise one drawn from an unpaid thread in `plot/threads.md`.)
2. Relationship to canon: continuation · interquel · AU · canon-divergence · fix-it · crossover.
3. Scope: one-shot · short multichapter · long fic. This sets how much planning follows.

**Placement**
4. Where in the timeline. (Check `plot/timeline.md` and state what is established there.)
5. What canon state is assumed true at the start — which threads are open, who knows what.

**Perspective**
6. POV character(s). (Recommend based on which voice cards are strongest; say which are thin.)
7. POV mode and tense — default is whatever `canon/overview.md` records; deviation is a choice.

**Substance**
8. What the fic is *about* thematically — the question it asks.
9. Central conflict and what changes by the end.
10. Which characters carry it; any OCs.
11. Ships, if any, and their canon status.

**Constraints**
12. Rating and content boundaries.
13. Which canon facts are load-bearing — must not be contradicted under any circumstances.
14. Sanctioned invention space — where the user *wants* you to invent, since canon is silent.
15. Intentional divergences — what this fic deliberately changes about canon, and why.
16. Length target and chapter count, if known.
17. Language confirmation — only if the user has signalled they want output in a language other than
    `source_language`. Otherwise do not ask; the default holds.

## Fill gaps from canon, flag gaps in canon

While interviewing, watch for two things:

- **Answers already in canon** — read them and state them rather than asking. "Canon places this three
  years after the war and has her still in the capital — I'll assume that unless you want otherwise."
- **Gaps canon cannot fill** — when a decision requires a fact the wiki does not have, say so
  explicitly and offer the options: ingest more source material, or invent and tag it `fanon-proposed`.
  Never quietly invent.

## The artifact

On confirmation, write `STORY_INTENT.md` in `wiki_language` — at `plan/` in a flat project, in the
book's directory in a series (`../../CONVENTIONS.md` §8). **One intent per book.** Book 2 gets its
own premise, its own load-bearing list and its own divergences; overwriting book 1's intent destroys
the record of what its outline was linted against.

```markdown
---
tier: fanon-proposed
type: story-intent
created: <YYYY-MM-DD>
language: <output_language>
---

# <working title>

## Premise
One sentence.

## Relationship to canon
<continuation | AU | canon-divergence | ...> and what that means concretely.

## Placement
Timeline position, assumed canon state, which threads are open at the start.
[src: ...] for each canon fact relied on.

## Perspective
POV, mode, tense — and whether each matches canon or deliberately departs.

## Themes and central conflict
What the fic asks; what changes.

## Cast
| Character | Role | Voice card status | Profile | Notes |

`Profile` — status of the `develop-character` profile for anyone above the depth threshold
(`CONVENTIONS.md` §11): `done`, `needed before ch<NN>`, or `below threshold`.

## Load-bearing canon
Facts that must not be contradicted. Each cited. **This list feeds the conflict linter.**

## Sanctioned invention
Where canon is silent and the user has approved invention. Each becomes `fanon-proposed`.

## Divergences
| What changes from canon | Why | Canon fact overridden |

## Constraints
Rating, boundaries, length target, chapter count.
```

Also append each divergence to `CANON.md`'s `divergences` table, and each sanctioned invention to
`wiki/fanon/proposed/`.

**Then run `naturalize` in plan mode over the new `STORY_INTENT.md`** (unless `CANON.md` sets
`naturalness: off`) and hand the user its review file. The intent is the text every later stage copies
from, so concept-speak written here spreads: on a real run the premise's «не становясь ничьим
человеком» — rejected by the user as *коряво* — reappeared in the cover brief verbatim. The user's own
fix («действуя чужими руками, как серый кардинал») was an image, not a simpler abstraction; aim there.

If an idea from `plan/IDEAS.md` fed this intent, mark it `promoted` there and note which section took
it. An idea file where nothing is ever marked promoted is a busy one, not a productive one.

Append to `wiki/log.md`: `## [YYYY-MM-DD] plan-story | b<NN> <working title>` (drop `b<NN>` when
flat).

## Rules

- **Never batch questions.** One at a time, with a recommendation, waiting for the answer.
- **Never ask what the wiki can answer.** Read it.
- **Never proceed without explicit confirmation** that shared understanding is reached.
- **Never invent canon.** Invention goes to `fanon-proposed` with the user's approval, never into
  `wiki/canon/`.
- If the user says "just decide for me," give specific recommendations and still get one explicit
  confirmation before writing the artifact.
- Keep it proportional: a one-shot may need six questions, a long fic twenty. Do not grill a drabble.
