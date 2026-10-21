---
name: refine-harness
description: >
  Use when ONLY when the user asks to learn from past sessions and tune the drafting
  harness: "refine", "learn from my edits", "tune the harness", "why do I keep fixing the
  same thing", "обучись на моих правках", "улучши процесс". Diffs the user's edits against
  Claude's drafts, reviews rejected proposals, and proposes changes to voice cards, project
  preferences, and drafting rules. Every refinement is ratified by the user; nothing is
  applied automatically. Do NOT use to audit the wiki — that's wiki-lint. Do NOT use to write
  or reconcile — that's write-chapter / reconcile. Best run after several chapters and
  reconcile rounds have accumulated signal.
---

# Refine Harness

## Mode
Subagent. Reads many files (drafts/snapshots, current drafts, wiki/log.md, plan/HARNESS.md
bias sections, all fanon-proposed entries), produces a small set of proposed changes. The
user ratifies each change; the subagent never edits anything on its own.

## Inputs required
- All `<book>/drafts/snapshots/ch<NN>-v0.md` (Claude's untouched drafts) and the current
  `<book>/drafts/ch<NN>-<slug>.md` (user-edited) — to diff
- `<book>/drafts/snapshots/ch<NN>-published-<platform>-v<N>.md` — published-chapter snapshots
  (cleanest edit signal)
- `wiki/log.md` — append-only operation history; rejected proposals are signal
- `wiki/fanon/proposed/` — accumulated proposals and the user's verdicts on them
- `plan/HARNESS.md` — current harness rules (the target of proposed changes)
- `CANON.md` (language settings, comic register, divergences)

## Persistent state
- `plan/HARNESS.md` — proposed-changes section appended with each suggestion
- `wiki/log.md` — append the `refine-harness | …` line
- Refinement itself stays in the conversation until the user ratifies; nothing is written
  to `wiki/canon/`, `wiki/fanon/`, or any draft.

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
exists, say so — the chapter predates snapshotting and cannot contribute edit signal. Ignore
`![…](…)` image lines and the `illustration:` frontmatter key: `illustrate` places them after the
snapshot exists, and they are not the user editing prose.

**Published chapters give two signals — keep them apart** (`../../CONVENTIONS.md` §13). `v0` →
`snapshots/ch<NN>-published-<platform>-v1.md` is the user's complete edit before readers saw it: the
cleanest signal there is, and the one to diff for published chapters. Diffs between later
`published-v<N>` are errata — typos readers or the user caught — and count as evidence only for
spelling habits, never for style.

**In a series, gather across every book.** `plan/HARNESS.md` is series-wide, and the edit signal from
book 1 is exactly what should stop book 2 repeating its mistakes. Do weight recency: a habit the user
corrected in book 1 and stopped correcting in book 2 is a rule that already landed, not a live one.

**Rejections.** Proposals `reconcile` raised and the user rejected. Repeated rejections of the same
*kind* mean Claude is over-asserting in a category.

**Conflicts.** Blocking conflicts from `plan-chapters` and the beat gate. Repeats mean Claude keeps
forgetting the same canon.

**Lint findings.** Issues `wiki-lint` reports more than once.

**Naturalness decisions.** The `<book>/naturalness/*.md` review files and the `naturalize` lines in
`log.md`. A user rewriting sentences by hand in a chapter that `naturalize` passed means a kind of
clumsiness the editor does not see — propose a `## Naturalness examples` row for it. A falling share
of accepted-as-is fixes means the editor's rewrites drift from the user's taste even where it finds
the right places.

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

`## Naturalness examples` is written by `naturalize` from the user's own verdicts, so it skips the
three-instance rule — and grows fastest. Past twenty rows, propose keeping the most instructive: one
row per *kind* of verdict (a joke kept, a proverb restored, a plan idea made concrete) outweighs five
rows of the same kind.

## Rules

- **No completion claim without fresh evidence** — `../../CONVENTIONS.md` §10. A metric quoted in a
  proposal is recomputed from `wiki/log.md` and the snapshots, never recalled.
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
