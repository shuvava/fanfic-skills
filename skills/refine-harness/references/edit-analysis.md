# Edit Analysis

How to turn a diff into a refinement proposal.

---

## Diffing

```bash
diff -u drafts/snapshots/ch07-v0.md drafts/ch07-the-garden.md
git diff --word-diff=porcelain HEAD~1 -- drafts/ch07-the-garden.md   # if versioned
```

Word-level diff beats line-level for prose — a reflowed paragraph looks like a total rewrite at line
granularity and like three changed words at word granularity.

Compute `edit_rate` = changed words / drafted words. Track it; a single value means nothing.

**If no snapshot exists**, the chapter predates snapshotting. Say so and exclude it. Do not
reconstruct what Claude "probably wrote" — that is fabricated evidence.

---

## Classifying an edit

Ask in order:

**1. Did it change a fact?** → wiki gap, not a harness issue. Check whether the canon page was wrong,
thin, or missing, and propose an ingest or a lint. Never "fix" this by adding a drafting rule.

**2. Did it change how a specific character sounds?** → voice card notes. The narrowest and most
common target.

**3. Did it change structure or length?** → `CANON.md` preferences.

**4. Does it recur across characters and chapters?** → `plan/HARNESS.md` drafting rule.

**5. None of the above?** → taste. Ignore it. Most single edits mean nothing, and treating them as
signal is how a harness fills with rules that describe one afternoon's mood.

---

## Patterns worth catching

These recur across projects and are usually real:

| Pattern | Looks like | Usual fix |
|---|---|---|
| Tic overuse | Same verbal tic trimmed in most scenes | Voice note: cap it further, or drop it entirely |
| Register creep | Formality or address forms corrected repeatedly | Voice note on the relationship table |
| Description bloat | Setting paragraphs consistently cut | Harness drafting rule with a target ratio |
| Dialogue starvation | User expanding exchanges | Harness rule: more beats per scene |
| Chapter overshoot | Consistent trimming to a shorter length | `CANON.md` length preference |
| Opening formula | Chapter openings always rewritten | Harness rule citing `canon/overview.md` |
| Modernism | Anachronistic word choices flagged | Voice note listing forbidden register |
| Over-assertion | Many `reconcile` rejections in one category | Reconcile bias: propose less there |
| Canon amnesia | Same blocking conflict recurring | Not a harness fix — the canon page is buried or thin; propose surfacing it in the beat card's deps |

---

## Writing a proposal

Bad — vague, unevidenced, unactionable:

> Claude should write better dialogue for Anna.

Good — specific, evidenced, testable:

> **Pattern:** Anna's verbal tic (trailing "ну вот") appears in 11 of 14 scenes; you cut it in 9.
> **Evidence:** ch03 (3 cuts), ch05 (4), ch07 (2).
> **Target:** `wiki/fanon/voices/anna-notes.md`
> **Change:** Cap the tic at once per chapter, in moments of genuine hesitation only.
> **Recommend:** accept — the canon card records it as a stress marker, and current usage flattens it
> into a filler word.

Every proposal states the pattern, counts the instances, names the chapters, names one target file,
and gives a concrete change. If any of those is missing, it isn't ready to propose.

---

## Anti-patterns

- **Proposing from one chapter.** Three instances, two chapters, minimum.
- **Reading `edit_rate` as quality.** It measures how much the user changed. A chapter they loved and
  polished heavily scores worse than a mediocre one they left alone. Trends only, never single values.
- **Fixing wiki gaps with harness rules.** If Claude got a fact wrong, the wiki was thin. Adding a
  drafting rule papers over it and the gap stays.
- **Accumulating.** Prune every run. The marginal rule is always the weakest.
- **Refining canon voice cards.** `wiki/canon/voices/` records what the source says. Claude's failures
  go in fanon notes, beside it, never into it.
