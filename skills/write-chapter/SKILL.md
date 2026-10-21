---
name: write-chapter
description: >
  Use when ONLY when the user asks to draft a new chapter or scene: "write chapter N",
  "draft the next chapter", "write the scene where X", "write chapter 2 of book 3",
  "continue the story", "напиши главу", "напиши следующую главу", "напиши сцену где…".
  Requires a chapter outline (run plan-chapters first if missing). Do NOT use when the user
  wants to outline first — that's plan-chapters. Do NOT use when the user wants to audit an
  existing chapter against canon — that's reconcile.
---

# Write Chapter

## Mode
Inline. The user iterates on the draft — asks "why did X do Y?", requests rewrites of
specific scenes, pushes back on voice or pacing. This follow-up loop needs the full canon
context in the main session, which is why write-chapter is not a subagent.

## Inputs required
- `<book>/outline.md` (required) — this chapter's row, its part's card, and the next 2–3 chapters' rows
- `CANON.md` (language settings, divergences, preferences)
- `plan/HARNESS.md` if it exists — project-local drafting rules learned from past edits
- `wiki/canon/` (full — overview, forbidden, characters, voices, world)
- `wiki/fanon/` entries the chapter depends on
- `drafts/continuity.md` (series-wide, not per book) and summaries of the previous two chapters

## Skip-if-loaded
The canon wiki is the largest single read in the pipeline. Before reading these files, check
whether each was already loaded in this session and no `ingest-source` / `reconcile` /
`naturalize` has happened since. Re-reading costs ~5–8 K tokens per chapter; skipping when
safe is the biggest single-context win for this skill.

Skip candidates:
- `wiki/canon/overview.md`, `wiki/canon/forbidden.md`
- `wiki/canon/characters/<each relevant>.md`, `wiki/canon/voices/<each with dialogue>.md`
- `wiki/canon/world/<each relevant>.md`
- `drafts/continuity.md`
- `CANON.md`

If any is missing from context, or any staleness trigger fires, read fresh.

## Persistent state
- `<book>/drafts/ch<NN>-<slug>.md` — the chapter draft (`tier: generated`)
- `<book>/drafts/snapshots/ch<NN>-v0.md` — frozen untouched copy (the baseline `refine-harness` diffs against)
- `<book>/beats/ch<NN>.md` — the scene beat sheet (input from plan-chapters, may be updated)
- `<book>/naturalness/ch<NN>-<slug>.md` — naturalize's review inbox (when `naturalize` runs)
- `<book>/logic/ch<NN>-draft/` — logic reader's flags (when logic reader runs)
- `wiki/log.md` — append the `write | …` line with metrics

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
4. `<book>/outline.md` — this chapter's row and its scenes, and its part (`plan-chapters` → *Parts*):
   - the part's Layer 2 paragraph and card, and where this chapter sits in it — opening, middle,
     climax or aftermath;
   - the rows of the next two or three chapters, so the chapter can plant what they will use;
   - for a part's first chapter, the previous part's `After` line — the decision this part starts from;
   - for a climax or aftermath chapter, the rows of the part's inciting and complication chapters, so
     the climax answers what was planted.

   Rows and cards only, never their chapters' prose. An outline with parts but no cards is a gap to
   name in §2 and send back to `plan-chapters`, not to fill in here.
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
  outranks the plan, and **text that has gone out outranks both** (`../../CONVENTIONS.md` §13):
  where they disagree, the chapter readers have is right, then the draft, and the outline is stale.
- **Has this chapter gone out?** `published:` in its frontmatter — `publication.py status` says
  **live** or **queued**. Live → redrafting it is `blocking`: readers have it, and a change goes out
  only as typo-only errata through `publish`. Queued (on a timer that has not fired) → redraft it
  only when the user asks; then `reconcile`, and `publish` → Editing a queued chapter re-uploads it
  under the same timer. Unasked, a needed change to a queued chapter is a finding for the user.
- **Did the previous chapter end on a cut?** Then this chapter opens in the same minute and settles
  it — first scene, first lines. A cut the next chapter forgets was a cheat.
- **What does it do for its part?** Does the row match its place on the part card — an opening that
  raises the question, a middle that makes the trouble harder from a new side, a climax the
  protagonist decides, an aftermath that ends in the card's decision? Does a later row in the part
  need something planted here that the scenes do not plant?
- **Is anything missing that you would have to invent?** Name it now. Inventing it mid-draft buries a
  fanon assertion inside three thousand words where `reconcile` has to dig it out.

**Raise concerns before drafting, not inside the draft.** If nothing is wrong, say so in one line and
continue — a clean review is a real result and costs a sentence.

A concern that changes the shape of the chapter goes back to `plan-chapters`. One that changes a
detail can be resolved here with the user and noted in the beats.

## 3. Beat out the chapter

Write `<book>/beats/ch<NN>.md` in `wiki_language`: two short sections for the user who reviews it,
then one card per scene for the drafter. The full template, conventions for In short / To decide,
the Point and Precedent checks, the Three Ways a Joke Fails examples, and the Who Knows What
mechanics check all live in [references/beat-card-template.md](references/beat-card-template.md).
Read that file before writing the first card.

**Show the beats to the user before drafting.** This is the cheapest gate in the pipeline — fixing a
beat costs a line, fixing drafted prose costs a scene. Lead with In short and To decide, pasted into
the conversation, and point to the file for the cards. The user decides from the top sections and
opens the cards when something needs a closer look. An answer to To decide goes into the cards, and
In short is rewritten if the answer changed the chapter.

**Logic and canon reader — before the beat gate.** You check the beats against what you believe;
a reader with fresh context and `raw/` at hand does not share your beliefs. Unless `CANON.md` sets
`logic_reader: off`:

```bash
D=<book>/logic/ch<NN>-beats
python3 <scripts>/logic_reader.py prompt <book>/beats/ch<NN>.md --stage beats --dir $D
```

Give the subagent only this, nothing of the conversation: «Working directory: <project root>. Read
`$D/prompt.md` — it is your whole task. Write the JSON array to `$D/reply.json`.» Then
`python3 <scripts>/logic_reader.py add <book>/beats/ch<NN>.md --dir $D --reply $D/reply.json`
and sort `$D/report.md`:

- **Fix yourself** what verified evidence settles: a wrong citation, a hedge turned into a fact, a
  fact `raw/` contradicts. These are your slips, not the user's decisions.
- **Drop** what the wiki, an earlier chapter or a recorded user decision already answers.
- **Ask** the rest in To decide, in the reader's words, each with your recommendation. A question
  marked "evidence not found" is a lead to check, not a fact.

Delete `$D` once the answers are in the cards, as with critic replies.

**Breaks reader — two runs, before the beat gate.** The reader above checks claims; it reads past a
choice that contradicts no fact. This one lists every event in the beats, finds each one's cause and
what it contradicts — what the person said or feared a line earlier, their profile, an earlier
chapter — and flags an event with no cause, against what the story showed, or decided off the page.
On one book it caught about half of the user's objections of this kind at the beat stage, where the
facts reader caught none, and the user judged 27 of its 30 flags worth asking. Unless `CANON.md`
sets `logic_reader: off`:

```bash
D=<book>/logic/ch<NN>-beats-breaks
python3 <scripts>/logic_reader.py prompt <book>/beats/ch<NN>.md --stage beats --check breaks --dir $D
```

The prompt carries the user's past questions from `## Logic examples` in `plan/HARNESS.md` — keep
that section filled: after each chapter, add a question the user asked about logic that no reader
raised (what was written, what the user asked, the kind of break in one line). Give `$D/prompt.md`
to **two** fresh-context subagents in parallel, each told to write `$D/reply1.json` or
`$D/reply2.json`: the runs share only about half their flags, and the flags one run found are as
often right as the ones both found. Then
`python3 <scripts>/logic_reader.py add <book>/beats/ch<NN>.md --dir $D --reply $D/reply1.json --reply $D/reply2.json`
merges them by sentence. Sort `$D/report.md`:

- **Fix yourself** a cause that is in your head but not in the card: write it into the card. A flag
  of this kind — the intent was right, the card did not say it — is common, and not a false alarm.
- **Drop** a flag the card already answers in so many words, or one the user decided for this
  exact break before, recorded in the beat file.
- **Ask** everything else in To decide, in the reader's words, each with your recommendation —
  including a break you made on purpose: say it is deliberate and why, and let the user keep or
  fix it. When the break is against an earlier chapter, say which side looks wrong; the earlier
  chapter may be the one to fix (a queued one can still change: `CONVENTIONS.md` §13, `publish` → Editing a queued chapter).

Put the questions you ask from either reader through `naturalize` in plan mode first (unless
`naturalness: off`): the reader writes compressed, and the user asks what a question means instead
of answering it. **Ask in story order, one scene at a time:** settle every question
about scene 1 and write the answers into its card before you ask about scene 2 — a cause fixed early
often answers a flag further on, so re-read the remaining flags after each scene and drop the ones the
fix settled. The report is already in story order. Delete `$D` once the answers are in the cards.

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

Run every row of the canon-check table explicitly and report. The full 19-row table, the cause-
finding protocol (prose / beat / outline / wiki / harness), the three-strikes rule, the style
fingerprint invocation, the logic reader invocation, and the naturalness-last ordering live in
[references/canon-check-table.md](references/canon-check-table.md). Read that file before running
the check.

## 6. Hand off

Drafts are `tier: generated`. **Never write chapter content into `wiki/canon/` — not ever.** New
assertions from the chapter are handed to `reconcile`, which routes them through user review.

Append to `wiki/log.md`:
```
## [YYYY-MM-DD] write | b<NN>/ch<NN> <title>
   metrics: book=<NN> words=<n> beats=<n> blocking=<n> warnings=<n> natural=<flagged>/<auto> critics=<name>:<kept>/<flagged>,… logic=<flagged>/<fixed>/<asked> breaks=<flagged>/<fixed>/<asked>
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
