# Illustration file templates

Prose around the blocks is in `wiki_language`. The fenced `locked-*` and `prompt` blocks are in
`image_prompt_language` (default English). `prompt_budget.py` finds blocks by their fence tag, so the
tags are part of the format, not decoration.

## `plan/illustration/STYLE.md` — one per project (= one per series)

````markdown
---
type: illustration-style
status: draft            # draft → locked
version: 1
locked: <YYYY-MM-DD>     # set on lock
target_model:            # chosen after the bake-off
fallback_models: [black-forest-labs/flux.2-pro]
aspect_ratio: "3:2"
resolution: 2K
---

# Стиль иллюстраций

## Замысел
Two or three sentences in wiki_language: what the pictures should feel like and why it fits this
series (genre, tone, audience). The user's words, not ours.

## Locked blocks

```locked-full
Style: <medium — e.g. digital painting in the manner of a 1990s fantasy paperback cover>;
<line and edge treatment>; <palette>; <lighting habit>; <texture/grain>; <level of detail and
realism>; <framing habit>.
```

```locked-short
Style: <the same medium, palette and lighting in one line>.
```

## Style reference image
`plan/illustration/refs/style-v1.png` — optional; attached last when used.

## Test prompt
Neutral scene with no named characters, used to judge the style alone.

```prompt
SHOT: <a neutral scene from the series' world — a street, a room, a landscape>.
<locked-full style block>
AVOID: text, watermark, signature.
```

## Bake-off
Same test prompt, same resolution, several models — before `target_model` is chosen.

| Model · file | Cost | What the user saw | Verdict |
|---|---|---|---|

## Iterations
| # | Date | Model | Seed | What the user said | What changed |
|---|---|---|---|---|---|

## Versions
| v | Locked | Applies from | Why changed |
|---|---|---|---|
| 1 | | b01/ch01 | — |
````

## `plan/illustration/characters/<name>-v<N>.md` — one file per identity version

A new version is created only when the character's appearance changes **permanently** in the story
(grows up, loses an eye, changes hairstyle for good). Temporary state — a torn shirt, a bruise, armour
for one fight — goes in the chapter prompt's SCENE, never here.

````markdown
---
type: illustration-character
name: <name as in the wiki>
prompt_name: <transliterated name used inside prompts, fixed forever — e.g. Lilia>
version: 1
status: draft            # draft → locked
applies_from: b01/ch01
applies_to: <b02/ch11 or open>
canon_page: wiki/canon/characters/<name>.md
profile: wiki/fanon/proposed/characters/<name>.md
locked: <YYYY-MM-DD>
---

# <name> — облик v1

## Visual facts
| Feature | Value | Source |
|---|---|---|
| Age as drawn | ~9 | [src: book-01/ch07.md#Глава 7] |
| Hair | blue-black, <cut> | [src: …] / [visual: 2026-09-21] |
| Eyes | | |
| Build, height | | |
| Face | distinguishing marks first | |
| Skin | | |
| Signature clothing | what they wear when nothing says otherwise | |
| Signature prop | | |
| Posture / habit | from `## Mannerisms` | |

`[visual: <date>]` marks a decision made for illustration because canon is silent. It is not a
story fact and does not reach the wiki or the prose unless the user promotes it the normal way.

## Locked blocks

```locked-full
Lilia: <distinguishing features first>, <age and build>, <face>, <hair>, <eyes>, <skin>,
<signature clothing>, <signature prop>, <typical posture>.
```

```locked-short
Lilia: <the three features that identify her at thumbnail size>, <age>, <signature clothing>.
```

## Reference sheet prompt

```prompt
SHOT: Character reference sheet of one person on a plain light-grey background: full body front
view, three-quarter view, side profile, and a close-up of the face, same person in all four,
neutral expression, even studio light.
CHARACTER:
<locked-full block>
<locked-full style block>
AVOID: text labels, other people, props not listed, background scenery.
```

## Reference images
| Version | File | Model | Seed | Approved |
|---|---|---|---|---|
| v1 | `plan/illustration/refs/<prompt_name>-v1.png` | | | <YYYY-MM-DD> |

## Iterations
| # | Date | Model | Seed | What the user said | What changed |
|---|---|---|---|---|---|
````

## `plan/illustration/book-<NN>/ch<NN>.md` — one per chapter image

Flat layout: `plan/illustration/ch<NN>.md`.

````markdown
---
type: illustration-prompt
chapter: b01/ch05
source: drafts/book-01/ch05-<slug>.md
model: google/gemini-3.1-flash-image
style: STYLE.md v1 (full)
characters: [Lilia v1 (full), Nelot v1 (short)]
elements: [era v2 (full), <place> v1 (short)]
aspect_ratio: "3:2"
status: draft            # draft → generated (on the user's approval)
image: plan/illustration/images/book-01/ch05.png   # set on approval: = ch05-r<N>.png, date
---

# b01/ch05 — иллюстрация

## Moment
What is happening, in wiki_language, two or three sentences.

> «Anchor quote from the chapter, verbatim, source language.» [chapter: b01/ch05]

Why this moment: its visual payoff, and what it does not give away.

## Candidates considered
| # | Moment | Anchor | Characters | Payoff | Spoils |
|---|---|---|---|---|---|

## Prompt

```prompt
SHOT: <one sentence — who does what, where, everyone's posture, camera distance and angle>.
CHARACTERS:
Image 1 is Lilia, the girl, as on her reference sheet. <Lilia locked block, verbatim>
Image 2 is Nelot, the boy, as on his reference sheet. <Nelot locked block, verbatim>
SCENE: <per-chapter state: expression, pose; what each hand does and holds>; <who wears what>;
<background people: number, place, ordinary faces>; <setting with canon details, element blocks>;
<light>; <mood>.
<style locked block, verbatim>
AVOID: watermark, signature, faceless or blank-faced people, anyone else with Lilia's or Nelot's
face; <era guard, verbatim>; <failures seen in earlier rounds>.
```

## Request
```json
{
  "model": "google/gemini-3.1-flash-image",
  "prompt": "<the prompt above>",
  "aspect_ratio": "3:2",
  "resolution": "2K",
  "input_references": [
    {"type": "image_url", "image_url": {"url": "plan/illustration/refs/Lilia-v1.png"}},
    {"type": "image_url", "image_url": {"url": "plan/illustration/refs/Nelot-v1.png"}}
  ]
}
```
Local paths are placeholders: send each file as a `data:image/png;base64,…` URL or an HTTPS URL.

## Iterations
| # | Date | Model | Seed | What the user said / what the review found | What changed (pitfall ids) |
|---|---|---|---|---|---|

## Budget check
Paste the `prompt_budget.py check` output here per round, dated, exit code included.
````

## `plan/illustration/book-<NN>/ch<NN>-edit.md` — image edits for one chapter

Also `characters/<name>-v<N>-edit.md` for a reference sheet. No locked blocks by design; budget
check only. One change per block, each block labelled so `--block <label>` survives insertions.

````markdown
---
type: illustration-edit
base_image: plan/illustration/images/book-01/ch05-r5.png (блоки 2–5, цепочкой)
sheet: plan/illustration/book-01/ch05.md
---

# b01/ch05 — правки по картинке

Блок 2. <what is wrong, who said so, canon quote if the fix rests on canon>.

```prompt 2
Edit Image 1. Make exactly one change: <the change, with where and what touches what>. Keep
everything else exactly as it is: <the faces, eyes, hair and anything the chain has already fixed>.
```

Цепочка: `2` (r5→r6) → `3` → `4`; colour fixes last.
````
