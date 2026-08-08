---
name: write-chapter
description: >
  Decompose one chapter into scene beats, then draft it in the source language against the canon wiki,
  then canon-check the draft. Use when the user says "write chapter 4", "draft the next chapter",
  "write the scene where X", or "continue the story" in a project that has an outline. Requires
  plan/outline.md — run plan-chapters first if it is missing.
---

# Write Chapter

Beat out one chapter, draft it, check it. One chapter at a time.

Follow `${CLAUDE_PLUGIN_ROOT}/CONVENTIONS.md`. **Prose is written in `output_language` from
`CANON.md` — by default, the source's language.** If `output_language` differs from `source_language`,
say so before drafting and confirm.

## 1. Load context

In this order:

1. `CANON.md` — language, divergences, preferences
2. `plan/HARNESS.md` if it exists — project-local drafting rules learned from your past edits.
   Precedence: `CANON.md` > `HARNESS.md` > plugin defaults.
3. `plan/STORY_INTENT.md` — constraints and load-bearing canon
4. `plan/outline.md` — this chapter's row and its scenes
5. `canon/overview.md` — POV, tense, distance, structure, orthographic conventions
6. `canon/forbidden.md` — read before beating, not after
7. `canon/characters/<name>.md` for everyone in the chapter — especially `## Would never do`
8. `canon/voices/<name>.md` for everyone with dialogue — especially verbatim lines and
   `## Would never say`
9. `canon/world/<topic>.md` for any system the chapter touches — especially `## Limits and costs`
10. `wiki/fanon/` entries the chapter depends on
11. `drafts/continuity.md` and summaries of the previous two chapters

**Carry summaries, not full prose.** Loading the whole manuscript dilutes attention and degrades
consistency faster than it helps. Summaries plus the wiki is the stronger context.

If a needed page does not exist, say so and offer to ingest more source material. **Do not improvise
canon to fill the gap.**

## 2. Beat out the chapter

Write `plan/beats/ch<NN>.md` — one card per scene, in `wiki_language`:

```markdown
## Scene <n> — <slug>
- **POV:** <character>
- **Setting:** <where, when>
- **Goal:** what the POV character wants entering the scene
- **Conflict:** what opposes it
- **Outcome:** how it ends — usually worse than it started
- **Reaction / dilemma / decision:** the emotional beat that follows
- **Canon deps:** [src: ...] entries this scene relies on
- **Fanon deps:** [fanon: ...]
- **Voice notes:** which cards to re-read before each character's first line
- **Constraints:** anything from forbidden.md or load-bearing canon that applies
```

**Show the beats to the user before drafting.** This is the cheapest gate in the pipeline — fixing a
beat costs a line, fixing drafted prose costs a scene.

Run the same conflict check as `plan-chapters` over the beats, since beat-level detail surfaces
contradictions the scene list was too coarse to show. A `blocking` conflict stops drafting.

## 3. Draft

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
- **Deploy verbal tics sparingly** — three per character is the cap, and not all three every scene.
- **Carry the comic register, delivery included.** Read `## Comic register` in `canon/overview.md`
  before drafting and hit its counts. A first draft reliably keeps the *device* — the source's
  signature ironic move — and loses the *delivery*: exclamations, stacked terminal marks, ellipsis,
  the punctuation that makes a narrator sound like they are talking rather than composing. Measured on
  a real run, a draft matched the author's scare-quoting to within 4% while dropping his exclamations
  by 92%. The jokes were structurally right and the voice was gone. **Humour that is merely
  well-formed is not this author's humour.**

Write to `drafts/ch<NN>-<slug>.md` with frontmatter recording `tier: generated`, POV, timeline
position, and threads touched.

**Then immediately write an untouched copy to `drafts/snapshots/ch<NN>-v0.md`.**

This snapshot is the baseline `refine-harness` diffs the user's edits against — the only record of
what Claude produced before anyone touched it. Write it once, at first draft, and never update it. If
the user asks for a revision before they've edited anything themselves, overwrite the snapshot too;
once they have edited, the snapshot is frozen. Without it there is no feedback signal and refinement
has nothing to learn from.

## 4. Canon-check the draft

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
| New assertions | What does this chapter establish that no tier records? |

Measure the style row rather than judging it:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/style_fingerprint.py check drafts/ch<NN>-<slug>.md --against raw/*.md
```

It prints every feature that drifted, with the source value, the draft value and the delta, and exits
non-zero when anything is outside tolerance. **Revise the draft and re-run until it passes, or state
plainly which deltas you are leaving and why.** A first draft typically comes back with the source's
strongest punctuation habits at a fraction of their density — that is the normal failure and it is
worth one revision pass, because it is the difference between prose that reads like the author and
prose that reads like a competent imitation.

**Report violations rather than silently fixing them.** A deliberate divergence is legitimate; the
user decides which it is. This applies to canon, not to the fingerprint: a style delta is a defect to
fix, not a choice to surface.

## 5. Hand off

Drafts are `tier: generated`. **Never write chapter content into `wiki/canon/` — not ever.** New
assertions from the chapter are handed to `reconcile`, which routes them through user review.

Append to `wiki/log.md`:
```
## [YYYY-MM-DD] write | ch<NN> <title>
   metrics: words=<n> beats=<n> blocking=<n> warnings=<n>
```
Then suggest running `reconcile`.

## Rules

- **The wiki is the authority, not recollection of the fandom.** If the wiki is silent, say so.
- **Never translate the source's dialogue into the prose.** Quote canon lines exactly if quoting.
- Deliberate divergence is fine; accidental drift is not. Ask which is happening when unsure.
- Follow the source's content level unless the user specifies otherwise. Never generate sexual content
  involving characters who are minors in canon, regardless of framing or aging-up claims.
- Fanfiction is generally treated as transformative when non-commercial; this is not legal advice.
  Decline requests to generate content for commercial sale of someone else's characters.
