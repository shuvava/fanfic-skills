# Cross-Book Conflict Lint — Series-Only Checks

Reference for the cross-book section of the conflict lint. Series only. These are the failures a per-book lint cannot see, and they are the expensive ones — each is discovered three books later otherwise.

A seed check is cheap to run and impossible to run late: by the time book 4 needs the object planted in book 2, book 2 is drafted and the fix costs a rewrite of a published chapter or a coincidence the reader will notice.

## The checks

| Check | What goes wrong | Severity |
|---|---|---|
| **Start-state drift** | A scene assumes a state the previous book's drafted ending contradicts. | `blocking` |
| **Prior-fanon contradiction** | A scene contradicts a `fanon-established` fact an earlier book set. | `warning` — the user may be retconning on purpose, but it is never a silent change |
| **Continuity-ledger contradiction** | A scene contradicts `drafts/continuity.md` — something the earlier prose actually said. | `blocking`. The published text is not revisable by a plan |
| **Published contradiction** | A scene contradicts a chapter with `published:` in its frontmatter, or re-plans one (`../../CONVENTIONS.md` §13). Applies within a book too. | Live chapter: `blocking` — readers have it; only typo-only errata can change it. Queued (timer not fired): `warning` — the fix may be the queued chapter, re-uploaded under its timer; the user decides |
| **Undelivered rung** | The Layer 2 ending does not reach this rung's end state. | `blocking` — the next book's start state is already written against it |
| **Unplanted seed** | A `SERIES_ARC.md` seed with `Plant in` = this book that no scene plants. | `blocking` — the payoff book has nothing to pay off |
| **Unpaid seed** | A seed with `Payoff target` = this book that no scene pays. | `warning`; either schedule it here or move the target and say so |
| **Premature payoff** | A scene resolves a thread or seed reserved for a later rung. | `warning` — spending it now leaves the later book with a hole |
| **Ladder overreach** | The outline delivers a state two or more rungs ahead. | `notice`; the ladder is wrong, not the book. Update `SERIES_ARC.md` |

## How the checks compose with the per-book lint

The per-book conflict lint (in the body of `plan-chapters`) handles within-this-book conflicts: canon violations, forbidden-list violations, fanon-proposed contradictions, would-never-do, world-limit, thread status, unsupported assertions. The cross-book checks handle between-this-book-and-everything-earlier conflicts.

Both run on the same scene list, in the same run. The output is one combined conflicts file (`<book>/conflicts.md`) with severity, scene, conflict, canon says, plan says, resolution columns. The user walks through the rows in severity order (`blocking` first, then `warning`, then `notice`).

## Resolving a blocking conflict

Present it plainly, with both sides and their citations, then ask a single question:

> Scene 7 has her using the family name openly. Canon establishes she abandoned it after the trial
> [src: ch12.md#...] and `forbidden.md` records that as a hard line.
> Is this an intentional divergence, or should the scene change?

Three outcomes:

- **Intentional** → record in `CANON.md` `divergences`, tag the fact `fanon-divergence`, continue.
- **Error** → revise the scene.
- **Canon was wrong** → the wiki misread the source. Re-check `raw/` and fix the canon page. This is the only circumstance in which a canon page changes, and it requires re-reading the source.

Never resolve a blocking conflict unilaterally. Never proceed past one unresolved.
