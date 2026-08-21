---
name: refine-harness
description: >
  Learn from what actually happened — diff the user's edits against Claude's drafts, review rejected
  proposals and recurring conflicts, and propose refinements to voice cards, project preferences, and
  the drafting harness. Use when the user says "refine", "learn from my edits", "why do I keep fixing
  the same thing", "tune the harness", or after several chapters are done. Every refinement is ratified
  by the user; nothing is applied automatically.
---

# Refine Harness

Close the loop. Read the trajectory the project has already generated, find repeated patterns, and
propose changes to how the pipeline works.

Follow `../../CONVENTIONS.md`. Analysis in the user's language; artifacts in
`wiki_language`.

## What this is and is not

The pipeline generates a signal it currently discards: the difference between what Claude wrote and
what the user kept. That difference is the most honest feedback available, and it costs nothing to
collect because the user produces it anyway.

**The user is the reward function.** There is no ground truth for prose quality — no milestone
reached, no test passing. A system that refined itself against its own judgment of its own output
would drift confidently in whatever direction it already leaned. So refinement proposes, the user
disposes. Every change is ratified.

**Refinement changes how Claude works, never what is true in the story.** It may adjust drafting
instructions, grilling questions, and beat checks. It may not touch `wiki/canon/`, and it may not
promote anything between tiers. Those are `reconcile`'s job and canon's wall.

## 1. Gather trajectory

Read across the whole project history, not just the last chapter. Patterns need repetition to be real.

**Edit diffs — the primary signal.** For each chapter, diff its `snapshots/ch<NN>-v0.md` (Claude's
untouched draft) against the current `ch<NN>-*.md` in the same drafts directory. If no snapshot
exists, say so — the chapter predates snapshotting and cannot contribute edit signal.

**In a series, gather across every book.** `plan/HARNESS.md` is series-wide, and the edit signal from
book 1 is exactly what should stop book 2 repeating its mistakes. Do weight recency: a habit the user
corrected in book 1 and stopped correcting in book 2 is a rule that already landed, not a live one.

**Rejections.** Proposals `reconcile` raised and the user rejected. Repeated rejections of the same
*kind* mean Claude is over-asserting in a category.

**Conflicts.** Blocking conflicts from `plan-chapters` and the beat gate. Repeats mean Claude keeps
forgetting the same canon.

**Lint findings.** Issues `wiki-lint` reports more than once.

**Metrics.** The `metrics:` lines in `log.md`, for trend.

## 2. Classify the edits

Every edit falls into a category, and the category determines what to propose:

| Category | Example | Refine |
|---|---|---|
| **Voice** | A tic trimmed, register corrected, address form changed | Voice card drafting notes |
| **Structure** | Scenes cut, chapters split, openings rewritten | `CANON.md` preferences |
| **Length** | Consistent trimming or expansion | `CANON.md` preferences |
| **Register / language** | Formality, diminutives, honorifics adjusted | Voice card language markers |
| **Pacing** | Description cut, dialogue expanded | Harness drafting rules |
| **Factual** | Canon corrections | **Not a harness issue** — a wiki gap; propose an ingest |
| **Taste** | Rephrasing with no pattern | Ignore. Not every edit means something. |

**Distinguish correction from preference.** A factual fix means the wiki was wrong or thin — the
remedy is ingesting more source, not changing the harness. A stylistic fix repeated across chapters is
a preference the harness should absorb.

## 3. Require evidence

**Three or more instances across at least two chapters before proposing anything.** One edit is taste;
two is coincidence; three is a pattern. State the count and cite the chapters in every proposal.

Propose no more than five refinements per run. A harness that grows unboundedly becomes a second
system nobody reads, and the marginal rule is always the weakest one.

## 4. Propose

Present as a table, each row with its evidence:

```markdown
| # | Pattern | Evidence | Target | Proposed change |
|---|---|---|---|---|
```

Three targets, in order of preference — always prefer the narrowest one that fits:

**Voice cards** (`wiki/fanon/voices/<name>-notes.md`, `tier: fanon-established`) — drafting notes
attached to a character. The narrowest target and usually the right one, because most edits are about
one character's voice. **Never edit `wiki/canon/voices/` — canon voice cards record what the source
says, not what Claude keeps getting wrong.**

**`CANON.md` preferences** — project-wide settings the user would have stated up front if they'd known:
chapter length, scene count, rating boundaries, structural habits.

**`plan/HARNESS.md`** — instructions that change how a stage behaves: extra drafting rules, extra
grilling questions, extra beat-gate checks, reconcile bias. Use only when the pattern is genuinely
cross-cutting and doesn't belong to a character or a setting.

For each proposal, recommend accept / edit / reject with one line of reasoning, as `plan-story` does.
The user's answer decides. **Silence is not consent.**

## 5. Apply and record

Write only ratified refinements. Bump `plan/HARNESS.md`'s `revision` and append to its revision log
with the evidence that justified the change.

Append to `wiki/log.md`:
```
## [YYYY-MM-DD] refine-harness | rev <n> — <n> ratified, <n> rejected
   metrics: edit_rate=<x> reject_rate=<x> blocking_per_plan=<x>
```

Report the trend across runs. If `edit_rate` isn't falling after several refinements, say so plainly —
the refinements aren't working, and the honest move is to propose fewer and ask what the user is
actually correcting for. **Read the metric carefully:** it measures how much the user changed, not how
good the chapter was. A chapter they loved and polished heavily scores worse than one they shrugged at.
Only trends across many chapters mean anything.

## 6. Prune

Every run, review existing harness rules. Propose removing any that:
- No longer match the user's edits
- Contradict a newer rule
- Were ratified but the pattern hasn't recurred in several chapters
- Duplicate something now in `CANON.md`

An accumulating harness is the failure mode here. Removal is as valuable as addition.

## Rules

- **Never apply a refinement without explicit ratification.**
- **Never write to `wiki/canon/`.** Canon reflects the source, never Claude's performance.
- **Never write to the plugin's own SKILL.md files.** The harness is project-local; one book's habits
  must not leak into the next.
- **Never override a language setting, a tier rule, or a gate.** The harness tunes how a stage works,
  never whether it runs.
- **Never propose from a single instance.** Three, across two chapters, with citations.
- If there is no trajectory yet — no snapshots, one chapter, no rejections — say so and stop. Refining
  from nothing produces confident noise.

## Reference

`references/edit-analysis.md` — how to diff, classify, and turn patterns into proposals.
