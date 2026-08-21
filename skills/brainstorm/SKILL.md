---
name: brainstorm
description: >
  Generate, discuss, and cull story ideas before any intent or outline exists — series destination,
  per-book arcs, and "what if" episode ideas — checking each against canon as it goes and recording
  what survives. Use when the user says "brainstorm", "what should the next book be", "I have an
  idea — what if...", "where is this series going", "let's think about future books", or asks for
  ideas rather than a plan. Produces plan/SERIES_ARC.md and plan/IDEAS.md, which plan-story and
  plan-chapters read as candidate input.
---

# Brainstorm

Divergent stage. Generate ideas, pressure-test them against canon, kill most of them, and keep the
survivors somewhere the planning stages will find them.

Follow `../../CONVENTIONS.md`. The session happens in the user's language; artifacts are written in
`wiki_language`.

## Where this sits

`plan-story` is convergent by design — one question at a time, each with a recommendation, narrowing
to a confirmed decision. That discipline is wrong for figuring out *what the story could be*. This
skill is the stage before it: volume first, commitment last.

```
brainstorm    → SERIES_ARC.md + IDEAS.md    [no gate — nothing is committed here]
plan-story    → STORY_INTENT.md             [grilling gate]
plan-chapters → outline + conflicts         [conflict gate]
```

Everything this skill produces is a *candidate*. It is outside the provenance tiers entirely — not
`canon`, not even `fanon-proposed`. An idea is not a fact about the world; it is a thing the user
might decide later. Nothing here is ever read at drafting time.

Read `plan/HARNESS.md` if it exists.

## Three scopes

| Scope | What it is | Consumed by |
|---|---|---|
| `arc` | What happens across a book, or across the series | `plan-story` — premise, themes, divergences |
| `episode` | A "what if" — one situation and what it forces | `plan-chapters` — Layer 4 scene list |
| `seed` | Something planted in one book to pay off in a later one | Both, across books |

They interleave, and that is the point — do not split the session into phases. "What if he kisses
her" is an episode idea that implies an arc idea (the relationship is how he changes), which may
imply a seed (what he gives up for it surfaces four books later). Follow the thought where it goes
and tag each idea as it lands.

## The series destination

If the user is planning more than one book, establish the destination **first**. It is the single
most useful thing in the session, because it converts free association into two sharp operations:

- **Generator** — "he is at X, the destination is Y, what is the next rung?" This proposes candidate
  *books*, not just scenes, and it is a far better prompt than open riffing.
- **Filter** — every idea becomes judgeable. A romance subplot is good if the relationship is *how*
  he learns what the destination demands, or *what* he trades away to reach it. It is a detour if he
  ends it unchanged. Without a destination there is no way to tell those apart, and every idea looks
  equally fine.

Write it to `plan/SERIES_ARC.md`:

```markdown
---
type: series-arc
status: provisional
created: <YYYY-MM-DD>
language: <wiki_language>
---

# <series working title>

## Destination
What is true when the series ends.
Canon status: <compatible | divergence | canon-silent>, cited.

## Ladder
| Book | Start state | End state | What changes him | Detail |
|---|---|---|---|---|
| 1 | ... | ... | ... | detailed |
| 2 | ... | ... | ... | detailed |
| 3–N | ... | ... | ... | provisional |

## Cross-book seeds
| Seed | Plant in | Payoff target | Status |
```

`Plant in` and `Payoff target` are book numbers matching the ladder. `Status` is one of `pending`,
`planted (b<NN>/ch<NN>)`, `paid`, `dropped` — `plan-chapters` reads it to check that a book plants
what it owes and pays what is due, and `wiki-lint` flags a seed whose payoff book drafted without it.

**Book N's end state is book N+1's start state.** Enforce it. That single constraint is most of the
artifact's value — it is what stops book 4 from quietly ignoring what book 3 cost him.

**Check the destination against canon once, at the top.** If canon forbids it — the throne abolished,
the character barred, the war already lost — the whole series is a canon-divergence and belongs in
`CANON.md` `divergences` before any book is planned. Discovering this at book 3 is expensive and
entirely avoidable.

**The destination is the most load-bearing invention in the project.** Say so. Everything downstream
depends on it, and nothing downstream should mistake it for something extracted from the source.

### Do not plan ten books

`plan-chapters` refuses to beat out forty scenes in advance because that work gets thrown away when
chapter 3 changes. The same holds an order of magnitude up: ten detailed books get thrown away when
book 2 changes.

- **Destination** — firm
- **Next one or two rungs** — detailed enough to hand to `plan-story`
- **Everything beyond** — one line each, marked provisional, a trajectory shape and nothing more

A ten-book ladder where rungs 4–10 are each a sentence is a correct artifact. One where they are each
a page is waste that will also constrain you wrongly.

## Generating

**Ask the user first, then offer.** A session where you propose and they react produces your book,
not theirs. Open each thread by asking what they have, and add yours after. When they are dry, then
generate freely.

Three generators, in order of yield:

1. **Unpaid threads** — `canon/plot/threads.md` entries still `open`. The source already set these
   up; using one costs no invention and it will read as continuation rather than departure.
2. **Canon's silences** — `canon/world/constraints.md` §"what canon does not establish". This is
   where invention is sanctioned by definition, and it is the highest-value place to invent because
   nothing has to be overridden.
3. **The ladder gap** — the distance between where he is and the next rung. Ask what would have to
   happen, and what it would cost.

For characters, `## Would never do` is a generator too, not only a constraint: the interesting
episode is the one that puts a character one step from the line they will not cross.

## An idea is not an image

"He kisses her" is an image. Record ideas as a hypothetical with a consequence:

> **What if** he kisses her → **which forces** her to choose between him and the oath → **which
> changes** his standing with the order, permanently.

If an idea has no "which forces", it is not yet an idea and the discussion is not finished. Ideas
recorded as one-line images lose the reasoning that made them good, and three weeks later nobody can
reconstruct why that one was on the shortlist.

## Checking against canon — two speeds

A full `plan-chapters` conflict lint here is both too expensive and premature; most of these ideas
will be killed anyway.

| Depth | When | What it is |
|---|---|---|
| `light` | While riffing | A sanity check from what is already loaded. One line, no re-reading. |
| `verified` | On shortlisting | Real check against `forbidden.md`, the timeline, and load-bearing facts. Cited. |

Light check, inline, one line, non-blocking:

> Works — she is unattached at that point in the timeline.
> Conflicts: canon has her out of the capital by then [src: ch12.md#...]. Divergence, or move it?

**Record which depth was applied.** An idea marked simply "validated" gives false comfort downstream;
`plan-chapters` needs to know what still requires linting. A `light` check is a smell test, not a
clearance.

Do not stop the session to resolve a conflict. Note it and keep going — that is the difference
between this stage and the planning gates. A conflicting idea can be a deliberate divergence, and
that decision belongs to `plan-story`, not here.

## Discriminating

**The failure mode of this stage is agreeing with everything.** Thirty ideas all met with enthusiasm
is thirty ideas with no signal in them, and it is worse than five, because the user now has to do the
culling you were there to help with.

So take a position on every idea. Say which of two you would keep and why. Say when an idea is a
weaker version of one already on the list. **Kill ideas out loud** — an idea nobody argued against
was never tested.

Useful things to say, all of which are discriminations rather than encouragement:

- This one does not move him along the ladder — he ends it the same person.
- This is the same idea as #7 wearing different clothes.
- Canon already did this [src: ...]; reusing it will read as repetition, not echo.
- This needs him to act against `## Would never do`. Is that the point, or an accident?
- This is a good scene with nowhere to sit — no book on the ladder has room for it. Keep as a seed?

**Merging is a first-class move.** Two weak ideas often combine into one strong one. Record the
lineage — `#7 + #12 → #19` — rather than silently rewriting, or you lose why the merged form is
better than either parent and you will re-propose the parents next session.

## The ideas file

`plan/IDEAS.md`. A holding pen, not a tier.

```markdown
---
type: ideas
created: <YYYY-MM-DD>
language: <wiki_language>
---

## Live
| # | Scope | Book | Idea (what if → forces → changes) | Status | Check | Lineage |
|---|---|---|---|---|---|---|

## Killed
| # | Idea | Why killed | Date |
```

- `status`: `raw` · `discussed` · `shortlisted` · `promoted` · `killed`
- `check`: `none` · `light` · `verified` — plus the conflict, if any
- `book`: a ladder rung, or `unassigned`. Unassigned is a real and common answer.
- `lineage`: merge parents, or the generator it came from

**Killed ideas stay, with the reason.** This is the same discipline `reconcile` applies to rejections
— without it the identical idea returns next session and you argue it again from scratch. The killed
list is the cheapest part of the file to maintain and the part that saves the most time.

**Prune the live list.** An `IDEAS.md` with eighty live entries is a landfill, and its signal is
gone. Anything `raw` that has survived two sessions without being discussed is not interesting;
propose killing it.

## Handing off

Nothing here is committed, so there is no confirmation gate — but say plainly where the session
landed and what the next stage should take from it:

- **Shortlisted `arc` ideas** → the premise question in `plan-story`. Name the one you would pick.
- **`episode` ideas for the book being planned** → `plan-chapters` Layer 4 candidates, still needing
  a real conflict lint.
- **`seed` entries** → the `SERIES_ARC.md` seed table.

When an idea is taken up by a planning stage, mark it `promoted` and note which artifact took it.
That closes the loop, and it is how you tell a productive idea file from a busy one.

Append to `wiki/log.md`:
```
## [YYYY-MM-DD] brainstorm | <n> new, <n> killed, <n> shortlisted
   metrics: generated=<n> killed=<n> shortlisted=<n> kill_rate=<x>
```

A healthy `kill_rate` is high. A session that killed nothing did not discriminate.

## Rules

- **Never write to `wiki/`.** Not `canon/`, not `fanon/`. Ideas are candidates, and a candidate in
  the fanon tier is bloat that dilutes the entries that matter at drafting time.
- **Never write `plot/threads.md`.** It is canon-tier and records what *the source* left open. Read
  it as a generator; our threads are ours and live in `IDEAS.md`.
- **Never let an idea become a decision here.** Commitment happens in `plan-story`, with its gate.
  If the user tries to settle the whole book in this session, that is fine — hand off to `plan-story`
  rather than writing `STORY_INTENT.md` yourself.
- **Never invent canon to make an idea work.** If an idea needs a fact the wiki does not have, say
  so: it is either sanctioned invention for `plan-story` to approve, or a reason to ingest more.
- Ask before you offer. Kill out loud. Record the reason.
- Keep it proportional. A one-shot needs no `SERIES_ARC.md` at all.
