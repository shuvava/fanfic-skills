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
    from their `snapshots/ch<NN>-published-*` copy where one exists, since that is what readers read —
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
  outranks the plan, and **published text outranks both** (`../../CONVENTIONS.md` §13): where they
  disagree, the published chapter is right, then the draft, and the outline is stale.
- **Is this chapter already published?** `published:` in its frontmatter → redrafting it is
  `blocking`. Readers have it; a changed chapter goes out only as typo-only errata through `publish`.
- **Did the previous chapter end on a cut?** Then this chapter opens in the same minute and settles
  it — first scene, first lines. A cut the next chapter forgets was a cheat.
- **Is anything missing that you would have to invent?** Name it now. Inventing it mid-draft buries a
  fanon assertion inside three thousand words where `reconcile` has to dig it out.

**Raise concerns before drafting, not inside the draft.** If nothing is wrong, say so in one line and
continue — a clean review is a real result and costs a sentence.

A concern that changes the shape of the chapter goes back to `plan-chapters`. One that changes a
detail can be resolved here with the user and noted in the beats.

## 3. Beat out the chapter

Write `<book>/beats/ch<NN>.md` in `wiki_language`: two short sections for the user who reviews it,
then one card per scene for the drafter:

```markdown
## <"In short", in wiki_language>
4–6 sentences: what happens, why, and what the reader should understand or feel when the chapter ends.

## <"To decide", in wiki_language>
1. <question> — <recommended answer, one line of why>
(or one line: nothing to decide)

## Scene <n> — <slug>
- **POV:** <character>
- **Setting:** <where, when>
- **Goal:** what the POV character wants entering the scene
- **Conflict:** what opposes it
- **Outcome:** how it ends — usually worse than it started
- **Reaction / dilemma / decision:** the emotional beat that follows
- **Point:** what the reader must understand when the scene ends — the realisation, subtext or irony
  the scene exists for, stated plainly and with its *because*. Not the outcome restated
- **Canon deps:** [src: ...] entries this scene relies on. For every rule of how the world works, the
  line from `raw/` itself, with the author's hedges, and who in the world knows it (see *Who knows what*)
- **Fanon deps:** [fanon: ...]
- **Voice notes:** which cards to re-read before each character's first line
- **Constraints:** anything from forbidden.md or load-bearing canon that applies
- **Precedent:** a canon scene of the same kind — an exam, a lecture, a sparring match — [src: ...], or `none`
- **What is new:** what this scene has that the precedent does not — stakes, obstacle, outcome,
  information. At least two; a different room does not count
- **Event:** what happens on the page that changes the situation — not only what the POV thinks about it
- **Cut:** last scene only, when the outline marks one — the exact line or action the chapter stops
  on, and why the reader cares how it turns out. Omit the field for a closed ending
- **Picture:** the scene that holds the outline row's `picture`, if it has one — the moment, who is
  in it, and what must be visible on the page for it to be drawn. Omit it everywhere else
```

**The two top sections are for the reviewer, and they are written last.** A card is 1000+ words of
apparatus the drafter needs — goals, dependencies, citations, conflict tables — and the person at the
beat gate has to find the chapter and the questions inside it. On a real run a world detail the user
later questioned in the finished prose had been written in the beats all along, too deep in a dense card to catch.

- **In short** retells the chapter the way you would tell a friend about it, in your own words.
  Close the cards and write it. The rules are the synopsis rules (`plan-chapters` → Synopsis and
  annotation): events in order, motives named, plain sentences. No field names, no `[src:]`, no
  scene numbers, no copied `Point`. The reader of this section knows the world, so world words need
  no explaining. End on what the reader should take away, and name the chapter's `Point` in everyday
  words.
- **To decide** lists every question the user must answer before drafting, pulled up from wherever
  it arose (the outline review, a missing voice card, a conflict the check found). Each has your
  recommendation. Write the question the way you would ask it aloud, not in editor's terms. Nothing
  to decide is one line, and a real result.
- **Draft from the scenes, never from In short.** It compresses, and a draft written from it loses
  what the compression dropped. When the user edits the cards, rewrite In short to match.
- Check it for runs copied from the plan:
  ```bash
  python3 <scripts>/synopsis_check.py <book>/beats/ch<NN>.md --section "<In short heading>" \
    --against <book>/outline.md
  ```

**Write the Point first, and write it with its *because*.** A card whose goal, conflict and outcome
are all correct still loses a scene whose meaning lives in subtext. "The engagement is broken off" is an outcome. "Breaking it off is the kind move, because her father needs the dowry back more than he needs an ally — and whoever returns it first makes the other the debtor" is a point. Measured on a
real run: scenes drafted from cards without it were plausible and on-brief, and the source's author
read every one as a different scene — the meaning was gone before a word of prose existed, and no
drafter can restore a point the card never carried. If you cannot state the point, the scene does not
have one yet: ask, don't draft.

**Run the swap test on every card with a precedent.** Paste the canon scene in place of this one: if
nothing downstream would notice, the scene is a re-staging, not a scene — rebeat it before drafting.
The precedent is also where a card goes wrong quietly: "fill the format from the canon scene" is an instruction to re-stage it, and a real author read the result as the same scene, beat for beat.

**Run `naturalize` in plan mode over the cards' `Point` and `Event`** (unless `CANON.md` sets
`naturalness: off`), and show its review file with the beats. A point written as concept-speak is
drafted as concept-speak: on a real run a piece of the plan's abstract shorthand reappeared in later files word for word.

**Show the beats to the user before drafting.** This is the cheapest gate in the pipeline — fixing a
beat costs a line, fixing drafted prose costs a scene. Lead with In short and To decide, pasted into
the conversation, and point to the file for the cards. The user decides from the top sections and
opens the cards when something needs a closer look. An answer to To decide goes into the cards, and
In short is rewritten if the answer changed the chapter.

**Who knows what — check every mechanic against `raw/` before the beat gate.** A card that leans on
how the world works (how healing reaches a wound, what a material does, what a guild teaches) is where
invented canon enters unseen, and the user then has to catch it line by line. For each such rule:

- **Quote `raw/`, not the wiki.** A wiki page is a summary and drops the author's hedges: «примерно
  девять из десяти, если не врать» becomes «90%» on the page, and the draft then states as a measured
  fact what the narrator only guessed — about something else. Carry the hedge with the quote.
- **Check what the world already has** in that field — artefacts, guild practice, known techniques —
  before inventing one. A new mechanic drafted without them contradicts the canon it skipped.
- **Name who knows it.** The world knows what canon shows people knowing. The protagonist knows what
  happened on the page, and only the way he met it: he *watched* the far end of the pole, so he did not
  *feel* it. A side character says only what they could have learned. **The protagonist's own
  discoveries are unknown to the world** unless canon says otherwise; a mechanic in which «village
  healers have always done» what the hero found out alone in chapter 9 is `blocking`. The reverse holds
  too: the hero does not outknow an institution that simply has not taught him yet.
- **Use the locals' words.** The narrator's vocabulary — modern slang, his name for a phenomenon — does
  not go into the mouths or the records of people who never had it. If the narrator calls it «the
  green glow» and the locals say «the gift», a healer's journal says «the gift».

Measured on a real run: in one chapter's beats and prose the user caught seven such slips — the world
knowing the hero's discovery, a rule read off a wiki summary that the source does not state, a
narrator's guess turned into a figure, the hero feeling what he had only watched, the narrator's word
in a lecturer's mouth. Every one was a fact or logic fix, and every one was in the plan before any
prose existed.

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
- **Nobody knows more than they could.** Before a character, the narrator or «everyone» knows
  something, the card says where it came from (*Who knows what* above). Locals speak in their own words,
  not the narrator's.
- **Canon dependencies are constraints, not ingredients.** What a card lists under `Canon deps` is
  what the prose must not contradict — it is not a parts list to assemble the scene from. An
  observation, joke or description the narrator already made in canon (the same odd detail of a room, the same bored official) may return only as an acknowledged callback — "like last time" — never re-performed as a fresh discovery. A chapter built from
  canon's details reads as a collage even when no sentence is copied: measured on a real run, a drafted chapter shared **0%** of its 4-word sequences with its canon precedent, and the author still recognised it as the same scene. The defect is structural, so no n-gram check will catch it — only
  reading the draft against the precedent will.
- **Write sentences a person would write.** Read `## Naturalness examples` and `## Overused patterns`
  in `plan/HARNESS.md` before drafting, if present — they are this user's verdicts on what reads as
  machine prose. Preventing a clumsy sentence is cheaper than reviewing it later.
- **Write for the reader who has forgotten canon.** At its first use in this book, gloss every world
  word — abbreviation, term, rank, mark — in half a sentence, even when canon explained it volumes
  ago. A clipped order says who does what («Ты держишь дверь, я лезу в окно», not «Ты — дверь, я —
  окно»). A price says what it pays for, who pays, and in what unit. If saying it plainly needs a
  world fact the wiki does not settle, put it under the card's decisions rather than inventing it in
  the prose (`naturalize` → *Two readings*).
- **Deploy verbal tics sparingly** — three per character is the cap, and not all three every scene.
- **Carry the comic register, delivery included.** Read `## Comic register` in `canon/overview.md`
  before drafting and hit its counts. A first draft reliably keeps the *device* — the source's
  signature ironic move — and loses the *delivery*: exclamations, stacked terminal marks, ellipsis,
  the punctuation that makes a narrator sound like they are talking rather than composing. Measured on
  a real run, a draft matched the author's scare-quoting to within 4% while dropping his exclamations
  by 92%. The jokes were structurally right and the voice was gone. **Humour that is merely
  well-formed is not this author's humour.** The counts cut both ways: a later draft ran scare
  quotes at three times the author's rate, and the quotes stopped marking anything.
- **Let the narrator be funny, not only remark on funny things.** Counts are the floor. On a real run
  a chapter brought to the author's numbers read as unchanged, and the one the user called organic
  gave the narrator his comic behaviour back. Use the `Comic moves of the narrator` recorded in
  `## Comic register`, at least one per scene: a boast that gives itself away, petty counting, a
  shamelessly practical plan, the good retort that arrives once the other person has left.
  The default a model drifts to is a narrator who is wise and fair and ends the chapter by explaining
  what everyone felt, and that narrator is not funny. Where the source's narrator draws a conclusion,
  keep it to a sentence or two and end on a sting, not a summary.
- **End where the card says.** On a cut, stop on the line or the unfinished action — no reflection
  after it; the narrator's conclusion opens the next chapter. On a closed ending, end as the source
  does, and do not add a hook line: «Что-то мне подсказывало…» is weaker than no hook at all
  (`plan-chapters` → *Chapter endings*).
- **Three ways a joke fails in the draft** (from a user's verdicts on a test chapter; examples invented):
  - *A punchline that negates instead of reversing.* «Мои друзья не приносили мне пирожки — они их
    уносили» is weaker than the antithesis said straight: «Его друзья носили ему пирожки. Мои — уносили
    их у меня!»
  - *A gag the reader has to solve.* If the point sits in an inference two lines away («Карту,
    кстати, Анна читала прекрасно. Причем обе»), most readers see no joke. Set the premise up where it
    will be seen, then let the line land by itself.
  - *A shorthand label for an idea.* «завидовал ему за пятерых с пирожками» packs a paragraph of
    reasoning into a phrase the reader has not been given. Name the thing: «за друзей, которые
    были у него с детства».
  Broken collocations kill jokes too («город не выдал мне ни одного друга» → «друзей мне в этом
  городе не полагалось»): the comic line is the one sentence that must read effortlessly.

Write to `<drafts>/ch<NN>-<slug>.md` with frontmatter recording `tier: generated`, POV, timeline
position, threads touched, and `book: <NN>` in a series. **Redrafting a chapter that already has
`illustration:` in its frontmatter:** keep the key, then re-run `place_illustration.py` from
`illustrate` step 14 — the anchor may no longer exist, and a moment the chapter lost is the user's
call, not a silent drop.

**Then immediately write an untouched copy to `<drafts>/snapshots/ch<NN>-v0.md`.**

This snapshot is the baseline `refine-harness` diffs the user's edits against — the only record of
what Claude produced before anyone touched it. Without it there is no feedback signal and refinement
has nothing to learn from.

**It is frozen the moment the chapter is handed to the user** (§6). Until then Claude's own passes —
the fingerprint revisions and `naturalize` repairs in §5 — update it, because they are still what
Claude produced. After hand-off it never changes: **a revision the user asks for is a user edit, even
when Claude types it.** "This is unclear", "that reads clumsy", "add a joke here" — each is the user's
correction, and it is exactly the signal the snapshot exists to keep. Measured on a real run: with the
snapshot overwritten after each requested revision, three chapters showed an edit rate of 0, 0 and
0.07 while the log recorded twenty revisions the user had asked for — the signal survived only in
prose log entries and had to be collected by hand.

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
| Who knows | Every rule of the world on the page traces to a `raw/` line; nobody knows what they could not have learned; the hero's discoveries stay his; locals use their own words |
| Timeline | Any conflict with `timeline.md`? |
| Picture | The outline's picture moment is on the page as an action with visible detail — who, where, what they hold — not only summarised or thought about |
| Ending | A cut stops on its moment with nothing after it; a closed ending carries no bolted-on omen; a previous chapter's cut is settled in the opening |
| Beats | Does each scene deliver its card's goal, conflict, and outcome? |
| Point | Can a reader reach each card's point from the page alone, its *because* included? Quote the lines that carry it. A point no line carries is missing from the scene, however well the outcome lands |
| Precedent | Does any scene repeat a canon scene's shape — same staging, same moves, same observations? List every narrator observation re-performed from canon; each is cut or turned into an acknowledged callback |
| Event | Does the chapter contain the external event its card named, on the page? |
| New assertions | What does this chapter establish that no tier records? |
| Naturalness | Run `naturalize` in prose mode once the rows above pass (skip if `naturalness: off`), outside readers included (`critics:` in `CANON.md`). Report its counts — flagged, auto-repaired, left for review, and per critic — and the review file's path |

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

**Naturalness runs last** because every other row can rewrite sentences, and a fix reviewed before a
canon revision would be reviewed twice. In `auto-safe` mode its repairs are Claude's own edits: apply
them and update `snapshots/ch<NN>-v0.md` before hand-off (§4), so the snapshot stays "what Claude
produced" and `refine-harness` does not count the repairs as user edits. Fixes the user accepts from
the review file are theirs — they land after hand-off and never touch the snapshot.

**Outside readers are part of this row, not an extra pass.** Your own reading misses what another
reader catches: on a blind read of three published chapters, the user found a real defect in 22 of 29
sentences they had let through, and no single critic caught more than half of them. Two outside
models plus a fresh-context Claude caught 20. Their flags reach the user only through `naturalize`'s review file, after you have
sorted them against the user's verdicts — never as a raw list.

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
   metrics: book=<NN> words=<n> beats=<n> blocking=<n> warnings=<n> natural=<flagged>/<auto> critics=<name>:<kept>/<flagged>,…
```
Drop `b<NN>/` and `book=` in a flat project.
Then suggest running `reconcile`.

**If `illustration_required` is true for this chapter's book (`CANON.md`, per-book setting —
`../../CONVENTIONS.md` §8), or it is `planned` and the outline row has a `picture`, the chapter is
not finished without its picture.** Under `planned` with no `picture` in the row, the chapter is
finished after `reconcile` — do not offer `illustrate`.
After `reconcile`, go straight on to `illustrate` Phase 3 and offer its candidate moments in the same
reply as the reconcile report. Do not wait to be asked: on a real run the user had to point out that a
chapter handed off as done had no picture, when every chapter before it had one.

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
