# Beat Card Template

Reference for `<book>/beats/ch<NN>.md` — the beat sheet `write-chapter` §3 produces and the gate reviews before drafting.

## Structure

```markdown
# <ch<NN>> — <chapter title>

## In short
<retells the chapter the way you would tell a friend about it, in your own words. The rules are
the synopsis rules from plan-chapters: events in order, motives named, plain sentences. No field
names, no [src:], no scene numbers, no copied Point. The reader of this section knows the world,
so world words need no explaining. End on what the reader should take away, and name the chapter's
Point in everyday words.>

## To decide
<every question the user must answer before drafting, pulled up from wherever it arose. Each has
your recommendation. Write the question the way you would ask it aloud, not in editor's terms.
Nothing to decide is one line, and a real result.>

---

# Scene 1: <short title>
- **Setting:** <where, when>
- **Goal:** what the POV character wants entering the scene
- **Conflict:** what opposes it
- **Outcome:** how it ends — usually worse than it started
- **Reaction / dilemma / decision:** the emotional beat that follows. Its length follows the
  chapter's place in the part: a phrase or a paragraph in the middle, to keep pace; before the
  climax, the dilemma written out as the card's two options; after the climax, the longest
  reaction in the part — and that one too ends in a decision
- **Point:** what the reader must understand when the scene ends — the realisation, subtext or
  irony the scene exists for, stated plainly and with its *because*. Not the outcome restated
- **Canon deps:** [src: ...] entries this scene relies on. For every rule of how the world works,
  the line from raw/ itself, with the author's hedges, and who in the world knows it (see *Who
  knows what*)
- **Fanon deps:** [fanon: ...]
- **Voice notes:** which cards to re-read before each character's first line
- **Constraints:** anything from forbidden.md or load-bearing canon that applies
- **Precedent:** a canon scene of the same kind — an exam, a lecture, a sparring match —
  [src: ...], or `none`
- **What is new:** what this scene has that the precedent does not — stakes, obstacle, outcome,
  information. At least two; a different room does not count
- **Event:** what happens on the page that changes the situation — not only what the POV thinks
  about it — and, for every act in it, its *because* (see *Give every act its cause*)
- **Cut:** last scene only, when the outline marks one — the exact line or action the chapter
  stops on, and why the reader cares how it turns out. Omit the field for a closed ending
- **Picture:** the scene that holds the outline row's picture, if it has one — the moment, who
  is in it, and what must be visible on the page for it to be drawn. Omit it everywhere else
```

## Conventions

**The two top sections are for the reviewer, and they are written last.** A card is 1000+ words
of apparatus the drafter needs — goals, dependencies, citations, conflict tables — and the person
at the beat gate has to find the chapter and the questions inside it. On a real run a world
detail the user later questioned in the finished prose had been written in the beats all along,
too deep in a dense card to catch.

**Draft from the scenes, never from In short.** It compresses, and a draft written from it loses
what the compression dropped. When the user edits the cards, rewrite In short to match.

**Check the In short section for runs copied from the plan:**

```bash
python3 <scripts>/synopsis_check.py <book>/beats/ch<NN>.md --section "<In short heading>" \
  --against <book>/outline.md
```

## The Point

**Write the Point first, and write it with its *because*.** A card whose goal, conflict and
outcome are all correct still loses a scene whose meaning lives in subtext. "The engagement is
broken off" is an outcome. "Breaking it off is the kind move, because her father needs the dowry
back more than he needs an ally — and whoever returns it first makes the other the debtor" is a
point.

Measured on a real run: scenes drafted from cards without it were plausible and on-brief, and the
source's author read every one as a different scene — the meaning was gone before a word of
prose existed, and no drafter can restore a point the card never carried. If you cannot state the
point, the scene does not have one yet: ask, don't draft.

## The Precedent

**Run the swap test on every card with a precedent.** Paste the canon scene in place of this one:
if nothing downstream would notice, the scene is a re-staging, not a scene — rebeat it before
drafting. The precedent is also where a card goes wrong quietly: "fill the format from the canon
scene" is an instruction to re-stage it, and a real author read the result as the same scene,
beat for beat.

## Give Every Act Its Cause

Every action, decision, refusal, silence and agreement in a card says why this person does it
here and now: a reason on the page, in an earlier chapter, or in their profile. When the reason
is a goal, say why they want it. A choice made off the page — a consent, a change of mind — is
a choice the reader never sees: put it in a scene or ask. On a real run most of what the user
rewrote in two drafted chapters was already in their beats, written as bare sequence ("one pushes
him; she hits back") with the reason only in the drafter's head. Where the reason is written, the
user can judge it in a line; where it is not, a reader cannot tell intent from a hole, and neither
can the drafter three scenes later. A character who acts against their own logic on purpose — for
the scene's emotion — still gets the card line *why*, and the user decides.

### A cause can be offstage

The outline marks it («за кадром: …» in a Russian plan): the author's logic that the POV
character and the reader do not know, or only guess. Carry it onto the card with the same marker.
Draft the act so it fits that cause; never let the narrator or anyone else state it unless they
could know it (*Who knows what*); leave at most a trace the POV can notice — and the guess itself
where the outline says the POV guesses. A cause that is offstage on the card is not a hole for
the breaks reader; one that is in no field at all is.

## Three Ways a Joke Fails in the Draft

From a user's verdicts on a test chapter; examples invented.

1. **A punchline that negates instead of reversing.** «Мои друзья не приносили мне пирожки — они их
   уносили» is weaker than the antithesis said straight: «Его друзья носили ему пирожки. Мои — уносили
   их у меня!»
2. **A gag the reader has to solve.** If the point sits in an inference two lines away («Карту,
   кстати, Анна читала прекрасно. Причем обе»), most readers see no joke. Set the premise up
   where it will be seen, then let the line land by itself.
3. **A shorthand label for an idea.** «завидовал ему за пятерых с пирожками» packs a paragraph
   of reasoning into a phrase the reader has not been given. Name the thing: «за друзей, которые
   были у него с детства».

Broken collocations kill jokes too («город не выдал мне ни одного друга» → «друзей мне в этом
городе не полагалось»): the comic line is the one sentence that must read effortlessly.

## Who Knows What — Mechanics Check

A card that leans on how the world works (how healing reaches a wound, what a material does,
what a guild teaches) is where invented canon enters unseen, and the user then has to catch it
line by line. For each such rule:

- **Quote `raw/`, not the wiki.** A wiki page is a summary and drops the author's hedges:
  «примерно девять из десяти, если не врать» becomes «90%» on the page, and the draft then
  states as a measured fact what the narrator only guessed — about something else. Carry the
  hedge with the quote.
- **Check what the world already has** in that field — artefacts, guild practice, known
  techniques — before inventing one. A new mechanic drafted without them contradicts the canon
  it skipped.
- **Name who knows it.** The world knows what canon shows people knowing. The protagonist
  knows what happened on the page, and only the way he met it: he *watched* the far end of the
  pole, so he did not *feel* it. A side character says only what they could have learned.
  **The protagonist's own discoveries are unknown to the world** unless canon says otherwise; a
  mechanic in which «village healers have always done» what the hero found out alone in chapter
  9 is `blocking`. The reverse holds too: the hero does not outknow an institution that simply
  has not taught him yet.
- **Use the locals' words.** The narrator's vocabulary — modern slang, his name for a
  phenomenon — does not go into the mouths or the records of people who never had it. If the
  narrator calls it «the green glow» and the locals say «the gift», a healer's journal says
  «the gift».
