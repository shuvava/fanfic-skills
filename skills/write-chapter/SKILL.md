---
name: write-chapter
description: >
  Decompose one chapter into scene beats, then draft it in the source language against the canon wiki,
  then canon-check the draft. Use when the user says "write chapter 4", "draft the next chapter",
  "write the scene where X", "write chapter 2 of book 3", or "continue the story" in a project that
  has an outline. Requires an outline — run plan-chapters first if it is missing.
---

# Write Chapter

Beat out one chapter, draft it, check it. One chapter at a time.

Follow `../../CONVENTIONS.md`. **Prose is written in `output_language` from
`CANON.md` — by default, the source's language.** If `output_language` differs from `source_language`,
say so before drafting and confirm.

## 1. Load context

**Resolve the book first** per `../../CONVENTIONS.md` §8. `<book>/` and `<drafts>/` below are
`plan/` and `drafts/` in a flat project, and `plan/book-<NN>-<slug>/` and `drafts/book-<NN>/` in a
series. Chapter numbers restart per book: "chapter 2" means chapter 2 *of the current book*. If the
user names a chapter that exists in more than one book and the current book is ambiguous, ask which
— drafting into the wrong book's directory is discovered late and by hand.

Then, in this order:

1. `CANON.md` — language, divergences, preferences
2. `plan/HARNESS.md` if it exists — project-local drafting rules learned from your past edits.
   Precedence: `CANON.md` > `HARNESS.md` > plugin defaults.
3. `<book>/STORY_INTENT.md` — constraints and load-bearing canon
4. `<book>/outline.md` — this chapter's row and its scenes
5. `canon/overview.md` — POV, tense, distance, structure, orthographic conventions
6. `canon/forbidden.md` — read before beating, not after
7. `canon/characters/<name>.md` for everyone in the chapter — especially `## Would never do`
8. `canon/voices/<name>.md` for everyone with dialogue — especially verbatim lines and
   `## Would never say`
9. `canon/world/<topic>.md` for any system the chapter touches — especially `## Limits and costs`
10. `wiki/fanon/` entries the chapter depends on
11. `drafts/continuity.md` (series-wide, not per book) and summaries of the previous two chapters —
    for the first chapter of a book, those are the last two chapters of the book before it

**Carry summaries, not full prose.** Loading the whole manuscript dilutes attention and degrades
consistency faster than it helps. Summaries plus the wiki is the stronger context.

If a needed page does not exist, say so and offer to ingest more source material. **Do not improvise
canon to fill the gap.**

## 2. Review the outline critically

The outline was written in another session, possibly another week, against a wiki that has since been
ingested into. **Read it as a critic before you use it as instructions**, and raise what you find
before any prose exists — that is the same economics as the conflict lint, one question against one
rewritten scene.

Read this chapter's row and its scenes and ask:

- **Is it still true?** Has an ingest since the plan landed changed a fact the chapter leans on? Does
  `drafts/continuity.md` record something the earlier chapters actually said that the plan assumed
  differently?
- **Is it executable as written?** A scene whose `conflict` column is empty, or whose `outcome`
  restates its `goal`, cannot be drafted into anything — it will come out as connective tissue.
- **Does the previous chapter's draft leave the characters where this one starts?** Drafted text
  outranks the plan. Where they disagree, the draft is right and the outline is stale.
- **Is anything missing that you would have to invent?** Name it now. Inventing it mid-draft buries a
  fanon assertion inside three thousand words where `reconcile` has to dig it out.

**Raise concerns before drafting, not inside the draft.** If nothing is wrong, say so in one line and
continue — a clean review is a real result and costs a sentence.

A concern that changes the shape of the chapter goes back to `plan-chapters`. One that changes a
detail can be resolved here with the user and noted in the beats.

## 3. Beat out the chapter

Write `<book>/beats/ch<NN>.md` — one card per scene, in `wiki_language`:

```markdown
## Scene <n> — <slug>
- **POV:** <character>
- **Setting:** <where, when>
- **Goal:** what the POV character wants entering the scene
- **Conflict:** what opposes it
- **Outcome:** how it ends — usually worse than it started
- **Reaction / dilemma / decision:** the emotional beat that follows
- **Point:** what the reader must understand when the scene ends — the realisation, subtext or irony
  the scene exists for, stated plainly and with its *because*. Not the outcome restated
- **Canon deps:** [src: ...] entries this scene relies on
- **Fanon deps:** [fanon: ...]
- **Voice notes:** which cards to re-read before each character's first line
- **Constraints:** anything from forbidden.md or load-bearing canon that applies
- **Precedent:** a canon scene of the same kind — an exam, a lecture, a sparring match — [src: ...], or `none`
- **What is new:** what this scene has that the precedent does not — stakes, obstacle, outcome,
  information. At least two; a different room does not count
- **Event:** what happens on the page that changes the situation — not only what the POV thinks about it
```

**Write the Point first, and write it with its *because*.** A card whose goal, conflict and outcome
are all correct still loses a scene whose meaning lives in subtext. "Losses are counted and accepted"
is an outcome. "Four dead is lucky, because the beasts' strength cores are worth more than soldiers —
and the loot is split only at the end, so the dead drop out of the share" is a point. Measured on a
real run: scenes drafted from cards without it were plausible and on-brief, and the source's author
read every one as a different scene — the meaning was gone before a word of prose existed, and no
drafter can restore a point the card never carried. If you cannot state the point, the scene does not
have one yet: ask, don't draft.

**Run the swap test on every card with a precedent.** Paste the canon scene in place of this one: if
nothing downstream would notice, the scene is a re-staging, not a scene — rebeat it before drafting.
The precedent is also where a card goes wrong quietly: "fill the format from the entrance exam" is an
instruction to re-stage it, and a real author read the result as the same scene *один в один*.

**Show the beats to the user before drafting.** This is the cheapest gate in the pipeline — fixing a
beat costs a line, fixing drafted prose costs a scene.

**Profile gate.** Every character in the chapter above the depth threshold
(`../../CONVENTIONS.md` §11) needs a profile in `wiki/fanon/proposed/characters/` — read it before
beating their scenes, especially `Want`, `Stakes` and `Off-page life`, so the character pursues
something of their own on the page. **A missing profile is `blocking`:** run `develop-character`
first, exactly as a missing voice card blocks a first line.

Run the same conflict check as `plan-chapters` over the beats, since beat-level detail surfaces
contradictions the scene list was too coarse to show — including its cross-book checks in a series,
where a beat contradicting `drafts/continuity.md` or an earlier book's ratified fanon is `blocking`.
A `blocking` conflict stops drafting.

## 4. Draft

- **Match the container exactly** — POV person, tense, narrative distance, chapter length, opening and
  closing habits from `canon/overview.md`.
- **Hit the numbers in `## Style fingerprint`.** Chapter length in words and each recorded punctuation
  frequency are targets, not flavor. Prose written against a qualitative note ("uses ellipsis
  heavily") lands at a fraction of the source's density every time, because nothing forces a count.
  Any punctuation habit the table records at 10+ per 1000 words must land within ±15% of its source
  value — the checker fails the draft outside that band. After drafting, count those features in your
  own text, report the counts, and revise until they are inside the band.
- **Obey `## Non-standard orthography` literally, and do not improve it.** Where the source departs
  from standard spelling or punctuation, reproduce the departure. Your instinct will be to correct it
  — that instinct is the failure mode. If the page records that the author writes `какой то` without
  the hyphen, every such form in your draft is written without the hyphen.
- **Write dialogue against the voice cards, not from memory.** Before each character's first line,
  re-read their verbatim canon lines. Check each drafted line against the `would never say` table.
- **Honor the language-specific markers** the voice cards record — address forms, diminutives,
  honorifics, register shifts, aspect habits. These carry more characterization weight than adjectives
  and are the first thing to go wrong when a model drifts toward generic prose.
- **Use the source's orthographic conventions** — dialogue punctuation (guillemets, em-dashes,
  quotation marks), paragraph habits, how thoughts and letters are set.
- **Respect world limits.** If a rule has a recorded cost, pay it in the prose.
- **Canon dependencies are constraints, not ingredients.** What a card lists under `Canon deps` is
  what the prose must not contradict — it is not a parts list to assemble the scene from. An
  observation, joke or description the narrator already made in canon (noticing the windows are on
  the "wrong" side, the bored examiner handing out sheets) may return only as an acknowledged
  callback — "как и на вступительных" — never re-performed as a fresh discovery. A chapter built from
  canon's details reads as a collage even when no sentence is copied: measured on a real run, a
  drafted exam chapter shared **0%** of its 4-word sequences with the canon exam, and the author still
  recognised it as the same scene. The defect is structural, so no n-gram check will catch it — only
  reading the draft against the precedent will.
- **Deploy verbal tics sparingly** — three per character is the cap, and not all three every scene.
- **Carry the comic register, delivery included.** Read `## Comic register` in `canon/overview.md`
  before drafting and hit its counts. A first draft reliably keeps the *device* — the source's
  signature ironic move — and loses the *delivery*: exclamations, stacked terminal marks, ellipsis,
  the punctuation that makes a narrator sound like they are talking rather than composing. Measured on
  a real run, a draft matched the author's scare-quoting to within 4% while dropping his exclamations
  by 92%. The jokes were structurally right and the voice was gone. **Humour that is merely
  well-formed is not this author's humour.**

Write to `<drafts>/ch<NN>-<slug>.md` with frontmatter recording `tier: generated`, POV, timeline
position, threads touched, and `book: <NN>` in a series.

**Then immediately write an untouched copy to `<drafts>/snapshots/ch<NN>-v0.md`.**

This snapshot is the baseline `refine-harness` diffs the user's edits against — the only record of
what Claude produced before anyone touched it. Write it once, at first draft, and never update it. If
the user asks for a revision before they've edited anything themselves, overwrite the snapshot too;
once they have edited, the snapshot is frozen. Without it there is no feedback signal and refinement
has nothing to learn from.

## 5. Canon-check the draft

Run explicitly and report:

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
| Timeline | Any conflict with `timeline.md`? |
| Beats | Does each scene deliver its card's goal, conflict, and outcome? |
| Point | Can a reader reach each card's point from the page alone, its *because* included? Quote the lines that carry it. A point no line carries is missing from the scene, however well the outcome lands |
| Precedent | Does any scene repeat a canon scene's shape — same staging, same moves, same observations? List every narrator observation re-performed from canon; each is cut or turned into an acknowledged callback |
| Event | Does the chapter contain the external event its card named, on the page? |
| New assertions | What does this chapter establish that no tier records? |

Measure the style row rather than judging it:

```bash
python3 <scripts>/style_fingerprint.py check <drafts>/ch<NN>-<slug>.md --against <ingested chapters>
```

`<ingested chapters>` is the same span `canon/overview.md` records under `## Style fingerprint`
(e.g. `raw/ch01.md raw/ch02.md ...`), **not** `raw/*.md`. Checking a draft against uningested
chapters grades it on a target no page in the wiki describes.

It prints every feature that drifted, with the source value, the draft value and the delta, and exits
non-zero when anything is outside tolerance. **Revise the draft and re-run until it passes, or state
plainly which deltas you are leaving and why.** A first draft typically comes back with the source's
strongest punctuation habits at a fraction of their density — that is the normal failure and it is
worth one revision pass, because it is the difference between prose that reads like the author and
prose that reads like a competent imitation.

**Report violations rather than silently fixing them.** A deliberate divergence is legitimate; the
user decides which it is. This applies to canon, not to the fingerprint: a style delta is a defect to
fix, not a choice to surface.

### When a check fails, find the cause before fixing the prose

A failed check is a symptom. Patching the sentence that tripped it leaves the cause in place and the
same defect returns next chapter — this is the single most common way a project accumulates the same
edit forever, and it is what `refine-harness` later has to clean up in bulk.

Locate the cause before revising:

| Cause | How it looks | Where the fix belongs |
|---|---|---|
| **Prose** | The beat was right; the sentence executed it wrong | The draft. Revise and move on |
| **Beat** | The scene card asked for something the wiki forbids | `<book>/beats/ch<NN>.md`, then redraft that scene |
| **Outline** | The scene should not exist in this shape at all | `plan-chapters` — it is one row, not one chapter |
| **Wiki** | The page you drafted against is thin, silent, or misread the source | `ingest-source` for the missing span, or fix the canon page against `raw/` |
| **Harness** | You did the same wrong thing you did last chapter | `refine-harness` — the default needs changing, not this draft |

State the cause you settled on before revising. "Voice drifted because `canon/voices/<x>.md` records
four verbatim lines and none of them in an argument" is actionable; "fixed the dialogue" is not, and
it will be fixed again next chapter.

**Three strikes.** If three revision passes have not cleared the same check, stop revising. Three
failures on one check is not a prose problem — it is a thin page, a wrong beat, or a harness default
working against you. Say so, name the suspected cause, and hand it to the user instead of attempting
a fourth pass.

## 6. Hand off

Drafts are `tier: generated`. **Never write chapter content into `wiki/canon/` — not ever.** New
assertions from the chapter are handed to `reconcile`, which routes them through user review.

Append to `wiki/log.md`:
```
## [YYYY-MM-DD] write | b<NN>/ch<NN> <title>
   metrics: book=<NN> words=<n> beats=<n> blocking=<n> warnings=<n>
```
Drop `b<NN>/` and `book=` in a flat project.
Then suggest running `reconcile`.

## Rules

- **Review the outline before drafting against it.** Stale plans produce drafts that contradict
  chapters already written.
- **Fix the cause, not the symptom.** Three failed passes on one check means the cause is upstream.
- **No completion claim without fresh evidence** — `../../CONVENTIONS.md` §10. "Canon-clean" means
  the cited pages were re-read this session, not remembered.
- **The wiki is the authority, not recollection of the fandom.** If the wiki is silent, say so.
- **Never translate the source's dialogue into the prose.** Quote canon lines exactly if quoting.
- Deliberate divergence is fine; accidental drift is not. Ask which is happening when unsure.
- Follow the source's content level unless the user specifies otherwise. Never generate sexual content
  involving characters who are minors in canon, regardless of framing or aging-up claims.
- Fanfiction is generally treated as transformative when non-commercial; this is not legal advice.
  Decline requests to generate content for commercial sale of someone else's characters.
