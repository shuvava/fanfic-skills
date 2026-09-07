---
name: reconcile
description: >
  After a chapter is drafted, extract what it established, check it against canon and existing fanon,
  and route each new fact through user review before promoting it. Use when the user says "reconcile",
  "update the wiki with the new chapter", "promote the fanon", or after write-chapter finishes. This is
  the gate that keeps generated fiction from contaminating extracted canon.
---

# Reconcile

Fold a finished chapter's assertions into the fanon tier — through review, never automatically.

Follow `../../CONVENTIONS.md`. Output in `wiki_language`; the review conversation in
the user's language.

## Why this gate exists

A compiled wiki answers confidently by design. If generated prose writes back into the tier the
drafter reads as truth, chapter 7 treats chapter 3's inventions as source material, and each chapter
is conditioned on a more synthetic corpus than the last. Canon fidelity rots quietly — the same
self-consuming loop that degrades generative systems trained on their own output.

The fix is cheap: generated facts are proposals, and promotion is a human action.

Read `plan/HARNESS.md` if it exists — its `## Reconcile bias` section records categories the user has
repeatedly rejected, and you should propose less aggressively there.

## 1. Extract assertions

Read the chapter and list every fact it establishes that is not already in the wiki. For each:

- The claim, stated plainly
- Where in the chapter it is asserted — `[fanon: ch<NN>-scene<N>]`
- What it is *about* (which character, place, rule, relationship)
- Whether it is load-bearing for future chapters or incidental colour

Skip incidental detail that no later chapter will need. A wiki that records every described curtain
becomes unusable.

## 2. Classify each assertion

| Class | Condition | Route |
|---|---|---|
| `duplicate` | Already recorded in some tier | Discard; note the existing entry |
| `extends` | Adds detail consistent with an existing fact | Propose as an addition |
| `new` | Canon is silent; no conflict | Propose as a new fanon entry |
| `conflicts-fanon` | Contradicts `fanon-established` | Flag — the fic contradicted itself |
| `conflicts-canon` | Contradicts a `canon` fact | **Critical.** Flag prominently |

A `conflicts-canon` finding at this stage means the drafting stage let something through that the
planning lint should have caught. Report it as a pipeline miss, not just a content issue, and say
which stage should have caught it.

## 3. Present the review inbox

Present as a table, in batches the user can actually work through:

```markdown
| # | Claim | Class | About | Where | Recommend |
|---|---|---|---|---|---|
```

For each, recommend accept / edit / reject with one line of reasoning. The user's decisions:

- **Accept** → write to `wiki/fanon/`, `tier: fanon-established`, with `## Ratified` recording the
  date and the chapter that created it
- **Edit** → accept the corrected form
- **Reject** → discard; note in the log so the same proposal does not return next chapter
- **Defer** → leave in `wiki/fanon/proposed/`

**Nothing is promoted without an explicit decision.** Silence is not consent.

## 4. Update the continuity ledger

Maintain `drafts/continuity.md` — what the fic itself has established, chapter by chapter, so chapter
7 stays consistent with chapter 3. **It is one file for the whole series, never per book**, and in a
series each row is keyed `b<NN>/ch<NN>`: it is the only thing that keeps book 3 consistent with book
1, and splitting it per book destroys exactly the consistency it exists to provide. This is distinct from `wiki/fanon/`: the ledger is a running record
of the text, while fanon entries are ratified world-facts. Both are read at drafting time; neither is
canon.

Also update:
- `<book>/outline.md` — the current book's outline (`../../CONVENTIONS.md` §8): mark the chapter
  drafted; adjust downstream scenes the chapter changed
- `plan/SERIES_ARC.md` if the chapter changed what this book ends with — the next rung's start state
  moves with it. A drafted ending that no longer matches the ladder is caught here or not at all
- `wiki/fanon/` thread status for fic-internal threads
- `wiki/index.md`

## 5. Report

Tell the user: what was accepted, what was rejected, any canon conflicts found, and whether the
chapter established anything that changes the plan for later chapters.

Append to `wiki/log.md`:
```
## [YYYY-MM-DD] reconcile | b<NN>/ch<NN> — <n> accepted, <n> rejected, <n> canon conflicts
   metrics: proposed=<n> accepted=<n> rejected=<n> reject_rate=<x>
```

If several chapters are now done, suggest running `refine-harness` — the edits and rejections
accumulated so far are the signal it learns from.

## Rules

- **No completion claim without fresh evidence** — `../../CONVENTIONS.md` §10. An accept count is
  read back out of `wiki/fanon/` after writing, never counted from the inbox you presented.
- **`wiki/canon/` is read-only.** Reconcile never writes there, edits there, or promotes anything to
  that tier. If the chapter contradicts canon, canon wins and the chapter is the thing that was wrong.
- **Never auto-accept.** Every promotion is an explicit user decision.
- **Never fabricate a provenance anchor.** If you cannot point at where in the chapter a claim is
  asserted, it is not an assertion from the chapter.
- Reject aggressively. A fanon tier bloated with incidental detail is worse than a sparse one, because
  it dilutes the entries that matter at drafting time.
