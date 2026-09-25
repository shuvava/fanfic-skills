---
name: develop-character
description: >
  Develop a character into a full profile — their own story, want, need, wound, stakes, relationships,
  what they do off-page, and how they change — so no character reads as scenery for the protagonist.
  Use when the user says "develop this character", "flesh out X", "who is X really", "проработай
  персонажа", or when another stage finds a character above the depth threshold
  (`CONVENTIONS.md` §11) without a profile. Works for canon characters (extends, never edits canon)
  and for new characters (creates `fanon-proposed`). Asks decisions one at a time.
---

# Develop Character

Give a character a life of their own, then check that the plan actually lets them live it.

Follow `../../CONVENTIONS.md`, especially §2 (tiers), §5 (honest silence) and §11 (depth threshold).
The profile is written in `wiki_language`.

## Why this stage exists

A pipeline records what it is told to record, and loses the rest. Voice cards make a character
*sound* right; nothing made a character *want* anything. The result is predictable: secondary
characters who exist to hand the protagonist information, obstacles or approval, and who stop
existing between his scenes. Readers call it cardboard.

The craft consensus is old and simple. Every character is the hero of their own story: they have
goals of their own, a need under the goal, a wound under the need, and something at stake that is
not the protagonist's problem. A character who only supports the protagonist creates no resistance,
outside or inside, and a scene without resistance has no tension.

## Where this sits

- **Before drafting**, whenever a character crosses the §11 threshold. `write-chapter` treats a
  missing profile for a chapter's above-threshold character as `blocking`, the same way it treats a
  missing voice card before a first line.
- **During planning**, when `plan-story` builds the cast or `plan-chapters` finds a character above
  the threshold. There it is a `warning` — cheap to fix, expensive to discover in chapter 30.
- **On request**, for any character.

Profile one character per run. A batch of twelve thin profiles is worse than three deep ones.

## 1. Load context

1. `CANON.md`, `plan/HARNESS.md` if present.
2. The book's `STORY_INTENT.md` — premise, central conflict, cast, constraints (especially any
   rule about how fast the world is revealed).
3. `outline.md` — **every scene the character appears in**. List them before anything else; the
   threshold and the cardboard check both run on that list.
4. `wiki/canon/characters/<name>.md` and `wiki/canon/voices/<name>.md` if the character is canon —
   including `## Would never do`, `## Contradictions` and every `не установлено` field.
5. Composite pages the character may live on (`*-персонал.md`, `друзья-*.md` and the like).
6. `wiki/fanon/` pages about the character, and `plan/IDEAS.md` entries naming them.
7. `canon/plot/threads.md` — open threads the character touches.

**Look up facts. Ask only decisions.** Anything the wiki answers is read, cited and stated, never
asked. "Canon has him lose his first duel [src: ...]" is a statement.

## 2. Build the profile, one decision at a time

Walk the sections below in order. For each field:

- **Canon answers it** → state it with `[src: ...]`.
- **Canon is silent** → say so, then ask **one** question with your recommended answer and one line
  of why. The user's answer becomes `fanon-proposed`. Never quietly invent.
- **Canon contradicts the plan** → stop and raise it as a conflict (§3 severity), not as a question
  of taste.

Recommend answers that **pull against the protagonist** somewhere. A character whose every want is
served by helping him is the failure this skill exists to prevent.

### Profile sections

| Section | What it holds |
|---|---|
| **Own story** | One paragraph: the book this character would star in. If you cannot write it, the character is not yet a person. |
| **Want** | The external goal they would name themselves. |
| **Need** | What they actually lack — usually something they would deny. |
| **Wound / false belief** | The past event or conviction the need grows from. Only what shapes the present. |
| **Stakes in this book** | What they stand to lose or gain — **not through the protagonist**. |
| **Backstory** | Only what drives present behaviour. Mark `(inferred)` where it is derived. |
| **Character** | Strengths, weaknesses, defining contradiction. |
| **Relationships** | For each significant character: what they want from them, what they think of them. Not only the protagonist. |
| **Off-page life** | What they do between the protagonist's scenes; where their goal grinds against his. |
| **Shift** | How they differ by the end of the book, however slightly. |
| **Would never do** | Canon lines copied with citations, plus fanon additions marked as such. |
| **Voice** | Link to the voice card, or its status and when it is needed. |
| **Reveal schedule** | What the reader learns about them, and when. A profile is the planner's knowledge, not text to be dumped into a chapter. |

Stop at shared understanding: summarise the profile and ask the user to confirm before writing.

## 3. The cardboard check

Run it against the **scene list**, not the profile. A beautiful profile the outline never uses is
still a cardboard character on the page.

| # | Check | Fails when |
|---|---|---|
| 1 | Own goal | Every want is about the protagonist |
| 2 | Acts on it | No scene where they pursue their own goal |
| 3 | Diverges | Their interest never conflicts with his |
| 4 | Not a dispenser | Every appearance hands him information, permission or rescue |
| 5 | Moves | Nothing about them shifts or is revealed by the end |

Report each check with the scenes that pass or fail it. **A failed check is a finding about the
outline**, not the profile: propose the smallest scene change that fixes it and hand it to
`plan-chapters` or the beats. Do not edit the outline from here.

## Artifacts

- **New character** → `wiki/fanon/proposed/characters/<name>.md`, `tier: fanon-proposed`.
- **Canon character** → `wiki/fanon/proposed/characters/<name>.md` as an **extension**: canon facts
  are cited, never rewritten; `wiki/canon/` is not touched, ever (§2).
- If a profile already exists, update it in place and note what changed.
- Update the `Profile` column of the book's `STORY_INTENT.md` cast table.
- If the character has dialogue and no voice card, say so and name the chapter where it is needed.

Frontmatter:

```yaml
---
tier: fanon-proposed
type: character-profile
name: <name>
canon_page: <path or none>
book: <NN>
proposed_by: develop-character
proposed: <YYYY-MM-DD>
---
```

Append to `wiki/log.md`:

```
## [YYYY-MM-DD] develop-character | <name> — cardboard check <n>/5
   metrics: book=<NN> scenes=<n> fanon_fields=<n> outline_findings=<n>
```

## Rules

- **Never batch questions.** One at a time, with a recommendation.
- **Never ask what the wiki can answer.** Read it and cite it.
- **Never edit `wiki/canon/`.** Canon characters are extended in `wiki/fanon/proposed/`.
- **Never resolve a canon contradiction as taste.** It is a conflict; raise it.
- **No completion claim without fresh evidence** (§10): the cardboard check is run on the current
  outline this session.
- **Depth is not exposition.** The profile is for the planner; the reveal schedule decides what the
  reader gets and when.
- Keep it proportional: a character just over the threshold needs want, stakes, one relationship,
  and the cardboard check — not a biography.
