# Canon-Check Table

Reference for `write-chapter` §5 — the 19 rows that get checked on every chapter draft before hand-off.

| Check | Verify |
|---|---|
| Language | Is the prose in `output_language`? Are quoted canon lines untouched? |
| Style fingerprint | Run the script below. Report its table and fix anything outside tolerance. |
| Orthography | Is every rule in `## Non-standard orthography` reproduced, not corrected? |
| Voice | Does each character's dialogue survive comparison to their verbatim lines? |
| Register | Are address forms and honorifics consistent with the relationship table? |
| Forbidden | Does anything violate `forbidden.md`? |
| Would-never-do | Does any character act outside their recorded code? |
| World limits | Are costs honored? |
| Who knows | Every rule of the world on the page traces to a `raw/` line; nobody knows what they could not have learned; the hero's discoveries stay his; locals use their own words |
| Timeline | Any conflict with `timeline.md`? |
| Picture | The outline's picture moment is on the page as an action with visible detail — who, where, what they hold — not only summarised or thought about |
| Ending | A cut stops on its moment with nothing after it; a closed ending carries no bolted-on omen; a previous chapter's cut is settled in the opening |
| Beats | Does each scene deliver its card's goal, conflict, and outcome? |
| Point | Can a reader reach each card's point from the page alone, its *because* included? Quote the lines that carry it. A point no line carries is missing from the scene, however well the outcome lands |
| Precedent | Does any scene repeat a canon scene's shape — same staging, same moves, same observations? List every narrator observation re-performed from canon; each is cut or turned into an acknowledged callback |
| Event | Does the chapter contain the external event its card named, on the page? |
| Part | A climax chapter: the protagonist's deciding act and its cost are on the page. An aftermath chapter: a consequence happens on the page and the decision is spoken or done. Any chapter: what the next rows need planted is planted |
| New assertions | What does this chapter establish that no tier records? |
| Logic reader | Run the logic reader subagent over the draft. Fix what evidence settles before hand-off (your edit: update the v0 snapshot); questions for the user go at the top of the hand-off, before the naturalness review. Report flagged / fixed / asked |
| Naturalness | Run `naturalize` in prose mode once the rows above pass (skip if `naturalness: off`), outside readers included (`critics:` in `CANON.md`). Report its counts — flagged, auto-repaired, left for review, and per critic — and the review file's path |

## When a check fails

A failed check is a symptom. Patching the sentence that tripped it leaves the cause in place and
the same defect returns next chapter — this is the single most common way a project accumulates
the same edit forever, and it is what `refine-harness` later has to clean up in bulk.

Locate the cause before revising:

| Cause | How it looks | Where the fix belongs |
|---|---|---|
| **Prose** | The beat was right; the sentence executed it wrong | The draft. Revise and move on |
| **Beat** | The scene card asked for something the wiki forbids | `<book>/beats/ch<NN>.md`, then redraft that scene |
| **Outline** | The scene should not exist in this shape at all | `plan-chapters` — it is one row, not one chapter |
| **Wiki** | The page you drafted against is thin, silent, or misread the source | `ingest-source` for the missing span, or fix the canon page against `raw/` |
| **Harness** | You did the same wrong thing you did last chapter | `refine-harness` — the default needs changing, not this draft |

State the cause you settled on before revising. "Voice drifted because `canon/voices/<x>.md`
records four verbatim lines and none of them in an argument" is actionable; "fixed the dialogue"
is not, and it will be fixed again next chapter.

**Three strikes.** If three revision passes have not cleared the same check, stop revising.
Three failures on one check is not a prose problem — it is a thin page, a wrong beat, or a
harness default working against you. Say so, name the suspected cause, and hand it to the user
instead of attempting a fourth pass.

## Style fingerprint — measured, not judged

```bash
python3 <scripts>/style_fingerprint.py check <drafts>/ch<NN>-<slug>.md --against <ingested chapters>
```

`<ingested chapters>` is the same span `canon/overview.md` records under `## Style fingerprint`
(e.g. `raw/ch01.md raw/ch02.md ...`), **not** `raw/*.md`. Checking a draft against uningested
chapters grades it on a target no page in the wiki describes.

It prints every feature that drifted, with the source value, the draft value and the delta, and
exits non-zero when anything is outside tolerance. Revise the draft and re-run until it passes,
or state plainly which deltas you are leaving and why. A first draft typically comes back with
the source's strongest punctuation habits at a fraction of their density — that is the normal
failure and it is worth one revision pass, because it is the difference between prose that reads
like the author and prose that reads like a competent imitation.

**Naturalness runs last** because every other row can rewrite sentences, and a fix reviewed
before a canon revision would be reviewed twice. In `auto-safe` mode its repairs are Claude's own
edits: apply them and update `snapshots/ch<NN>-v0.md` before hand-off (§4), so the snapshot stays
"what Claude produced" and `refine-harness` does not count the repairs as user edits. Fixes the
user accepts from the review file are theirs — they land after hand-off and never touch the
snapshot.

**Outside readers are part of this row, not an extra pass.** Your own reading misses what another
reader catches: on a blind read of three published chapters, the user found a real defect in 22
of 29 sentences they had let through, and no single critic caught more than half of them. Two
outside models plus a fresh-context Claude caught 20. Their flags reach the user only through
`naturalize`'s review file, after you have sorted them against the user's verdicts — never as a
raw list.

**Report violations rather than silently fixing them.** A deliberate divergence is legitimate;
the user decides which it is. This applies to canon, not to the fingerprint: a style delta is
a defect to fix, not a choice to surface.

## Logic reader — invocation pattern

```bash
D=<book>/logic/ch<NN>-draft
python3 <scripts>/logic_reader.py prompt <draft> --stage draft --beats <book>/beats/ch<NN>.md --dir $D
```

Same subagent hand-off and sorting as at the beat gate (see `references/canon-check-table.md`).
Fix what evidence settles before hand-off (your edit: update the v0 snapshot); questions for the
user go at the top of the hand-off, before the naturalness review. Report flagged / fixed /
asked.
