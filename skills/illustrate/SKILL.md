---
name: illustrate
description: >
  Use when ONLY when the user asks for chapter-scoped image-generation prompts whose
  characters look the same across many images: "illustrate chapter N", "image for chapter X",
  "make an illustration for chapter 2 of book 3", "character reference sheet", "image prompt",
  "prompt for Nano Banana / FLUX / OpenRouter", "иллюстрация к главе", "промпт для
  картинки", or wants to fix how a character or the art style looks. Three phases: style lock,
  character lock, per-chapter prompt. Writes prompts; runs generation itself when the project
  sets image_autorun and no decision is pending. Do NOT use for a single book cover with title
  and emblem — that's cover. Requires at least one chapter outline to exist (run plan-chapters
  first if missing).
---

# Illustrate

## Mode
**Mixed.** Phase 1 (style lock) and Phase 2 (character lock) run **inline** — the user
approves the style and each character's look, with iterate-and-revise rounds. Phase 3
(per-chapter prompt generation) runs as a **subagent** — the prompt is the output, the user
judges by the image, no follow-up loop on Phase 3 itself.

## Inputs required
- At least one chapter outline (`<book>/outline.md`) — required for Phase 3
- `CANON.md` (language settings, character list, `illustration_required` per book)
- `wiki/canon/characters/<each>.md` and `wiki/canon/voices/<each>.md` — what the characters look/sound like
- `references/pitfalls.md` — the checklists (read at the named steps, every time)
- `references/models.md` — model prompt limits and request shapes (Phase 1 model choice)
- `references/templates.md` — file formats (before creating any file)
- `OPENROUTER_API_KEY` per §12 — only for generation phases
- For Phase 2: previous approved character pictures (so new characters match the locked style)

## Skip-if-loaded
For inline Phase 1+2, before reading canon pages, check whether each was already loaded this
session and no `ingest-source` has happened since. Character sheets persist; re-reading wastes
context during long Phase 2 sessions.

## Persistent state
- `plan/illustration/style.md` — the locked series-wide image style (Phase 1)
- `plan/illustration/characters/<slug>.md` — locked character look per character (Phase 2)
- `plan/illustration/book-<NN>/ch<NN>.md` — per-chapter chosen scene + prompt + generation params (Phase 3)
- `<book>/drafts/ch<NN>-<slug>.md` `illustration:` frontmatter — set when an image is approved and placed
- `wiki/log.md` — append the `illustrate | …` line for each phase

A picture per chapter, the same faces in every picture, one style for the whole series.

Follow `../../CONVENTIONS.md`, especially §1 (language), §2 (tiers), §5 (honest silence), §8 (book
scope), §10 (completion claims) and §12 (secrets). Reference files:

| File | Holds | Read |
|---|---|---|
| [references/pitfalls.md](references/pitfalls.md) | Checklists: identity blocks (I), world elements (W), scene composition (S), edits and repairs (E) | At the steps below that name a list — every time, not from memory |
| [references/models.md](references/models.md) | Prompt limits, reference slots, prices, request shape | Phase 1 model choice; any new model |
| [references/templates.md](references/templates.md) | File formats for every artifact | Before creating a file |

## Why it is built this way

An image model has no memory. Every generation reads the prompt fresh, so a character stays the same
only if the prompt that describes them stays the same — **the same words, in the same order** — and,
better still, if the same approved picture of them is attached as a reference. Paraphrase once to fit
a shot and the model draws a cousin. So the design separates what never changes from what changes
every chapter:

| Layer | Changes | Where it lives |
|---|---|---|
| **Style** | Never within a series | `plan/illustration/STYLE.md`, locked block |
| **Identity** | Only when the story changes the character permanently | `characters/<name>-v<N>.md`, locked blocks + reference image |
| **World** | Only by a new version | `world/<name>-v<N>.md` — costumes, props, places, creatures, the era guard |
| **Scene** | Every chapter | `book-<NN>/ch<NN>.md` |

Locked blocks are pasted, never rewritten. Everything that belongs to one chapter — clothes, wounds,
expression, pose, place, light — goes into the scene section.

## Settings

`CANON.md` carries two keys for this skill; add them on first run and say so:

```yaml
image_prompt_language: en      # language of prompt blocks; default en — see models.md
image_autorun: false           # true — Claude runs single generations itself (see "Running generation")
illustration_required: false   # true — every chapter; planned — chapters the outline marks; per book: {1: true, 2: planned}
picture_every_words: 5000      # with planned: target density for plan-chapters, one picture per this many words; per book
```

`illustration_required` is the user's rule that a chapter without a picture is not finished: `write-chapter`
hands off to Phase 3 after `reconcile`, and `publish` blocks a chapter that has none. Set it when the user
says every chapter needs a picture. It is a per-book setting (`../../CONVENTIONS.md` §8): a map by fic
book number when books differ — one book illustrated, the next text only.

`planned` puts the choice in the outline: `plan-chapters` marks the chapters that get a picture
(*Chapter pictures*), and only those are required. Under `planned` a picture outside the marks is
fine when the user asks for one, and is never required.

`image_autorun` is the user's standing permission to spend on image rounds. Default `false`; set it to
`true` only when the user asks for it, and say what it does and does not cover.

This is a language switch under §1, so **flag it once, in these terms**: *everything sent to the
model is English* — the whole prompt block is translated, whatever the source language. What stays
in the source language is only what the model never reads or must copy literally:

| Stays in source language | Why |
|---|---|
| File prose around the blocks (notes, facts tables, iteration logs) | For the user, in `wiki_language`; the model never sees it |
| Quotes from canon and the chapter | Verbatim is how a citation stays checkable (§1) |
| Text meant to appear *inside* the image, in quotation marks inside the English prompt | A sign in this world is not in English: `a wooden sign reading "Академия"` |

Each character gets a fixed `prompt_name` (a transliteration) chosen once and used in every prompt.

**API key.** The OpenRouter key lives in the project's single `.env` — set it up per
`../../CONVENTIONS.md` §12 before the first generation command you hand over.

## Phase 0 — Route

Read `CANON.md`, `plan/HARNESS.md` if present, and `plan/illustration/` if it exists. Then:

| State | Go to |
|---|---|
| No `STYLE.md`, or `status: draft` | Phase 1 — **even if the user asked for a character or a chapter** |
| User asks to change the style or a character | Phase 1 or 2 for that item |
| Chapter requested, a character in the chosen moment has no locked sheet for that chapter | Phase 2 for that character, then back |
| A recurring costume, prop, place or creature in the shot has no locked sheet | Phase 2b for it, then back |
| Style and cast locked | Phase 3 |

Resolve the book per §8. A chapter image is `b<NN>/ch<NN>` in a series.

**The style is always the first conversation.** A character block is written in the style's
vocabulary — "fine-boned face" means one thing in anime line art and another in oil — and the
reference sheet cannot be generated without it. If the user named a character, say that the style
comes first and why, then start Phase 1; facts about the character may be gathered meanwhile.

**Exception — the protagonist as the style's last test.** A style that lives in faces cannot be
judged on an unnamed extra. Once the model is chosen and the style draft has survived a round, the
user may move to the protagonist with the style still `draft`. Say so plainly: the style and the
protagonist's sheet are then locked **together**, and any later style change means regenerating that
sheet. Style feedback during character rounds edits the style block and is logged in `STYLE.md`.

## Phase 1 — Lock the style

A series with pictures in three styles reads as three series.

1. **Style before model.** Offer three directions, each a one-line pitch plus why it fits this
   series' genre and tone (`wiki/canon/overview.md`). Recommend one; the user picks or describes
   their own.
2. **A named reference** ("like *Oregairu*") → research that work's look on the web and translate it
   into traits: line, shading, eyes, hair, palette, light, proportions, backgrounds. Say which
   traits came from sources and which from your own knowledge. **Never put the title, a character
   or an artist's name in a prompt** — a franchise name pulls in its own characters' faces, and
   several providers refuse living-artist prompts. Record the reference in `STYLE.md` prose only.
3. **Draft both blocks and the test prompt.** `locked-full`: medium, line, palette, lighting,
   texture, detail level, framing habit. `locked-short`: medium, palette and lighting in one line.
   No subject matter in either — a style block that mentions swords makes every picture a sword
   picture. The test prompt is a neutral scene with no named characters; if the style lives in
   faces, include one unnamed figure.
4. **Compare models before choosing** — price and quality, not a default:
   - **Live prices** from OpenRouter (models.md, "Pricing"), converted to cost per image at the
     user's resolution.
   - A table: cost per image, reference slots, seed, prompt cap, public leaderboard Elo — and say
     that leaderboards have no per-style category and are dominated by photoreal votes.
   - The budget check on the test prompt for every candidate; drop models whose cap it breaks.
   - Project cost: chapters × images per chapter + characters × expected rounds.
   - A **bake-off**: the same test prompt on three or four candidates at 1K, usually under a dollar.
     Record each result in `STYLE.md` `## Bake-off` naming nickname, model id and output file
     (`Nano Banana 2 · google_gemini-3.1-flash-image.png`) — the user compares files. Show the
     images side by side with your verdict; count scene defects per model too (see "Reviewing").
   - Record `target_model`, fallbacks, `aspect_ratio`, `resolution`.
5. **Iterate on the chosen model.** Look at every result. Change **only** what the feedback names,
   log the round in `## Iterations`, hand back the revised prompt. Keep the seed between rounds on
   models that take one.
6. **Lock on explicit approval** — "yes", "approve", "lock it"; not silence, not "better". Set
   `status: locked`, `version`, `locked`; record a style reference image if the user saved one and
   confirm the file exists.

**Re-comparing a model later** (the user asks to try the runner-up): run the final prompts of a few
finished chapters unchanged, one generation each, into `images/book-<NN>/<model-nickname>/`. Compare
each against the target model's **first** generation of the same final prompt, not the edited,
approved image, sorting defects into identity (cheap to edit) and scene (costs a regeneration).
Record it in `STYLE.md` as a chapter bake-off with the verdict and what was not tested.

A locked style changes only by a new version, on the user's decision, from a book boundary. Say
plainly that earlier images will no longer match.

## Phase 2 — Lock a character

One character at a time, for every character who will be recognisable in a picture; background
figures are described in the scene and need no sheet.

1. **Gather.** Read the canon page's `## Physical`, `## Identity`, `## Mannerisms`, the
   develop-character profile, and `wiki/fanon/` notes on appearance — and search `raw/` when the wiki
   says appearance is undescribed (it can be wrong; record the gap in `wiki/log.md`, do not edit
   canon). Canon states appearance at a **point in the series**; establish which chapter range this
   version covers (`applies_from` / `applies_to`).
2. **Fill the `Visual facts` table**, including **height relative to every locked character this
   one will share a frame with** — the model cannot infer it from two separate sheets (**S17**).
   Canon answers → cite `[src: …]`. Canon silent → say so and ask **one** question at a time, with
   a recommendation and a line of why. The answer is tagged `[visual: <date>]` and never enters
   `wiki/` or prose unless the user promotes it through fanon. Relative height is always asked,
   never assumed: a "same height" nobody chose cost ch03 three rounds.
3. **Canon contradicts the request** → stop and ask, as a §3 conflict: intentional divergence for the
   pictures, or a mistake? Never settle it as taste.
4. **Write both locked blocks** and run **pitfalls I1–I13**. `locked-short` keeps the identifying
   features, age and signature clothing.
5. **Give the reference sheet prompt**: four views of the one person on a plain background, with the
   locked style. From the second character on, attach the first locked sheet as `Image 1`, labelled
   **style reference only** ("match its line work and colouring; the person in it is someone else
   and must not appear") — words alone let each sheet drift into a different hand.
6. **Iterate until the user is satisfied.** Review every image (below) against the facts table
   ("the scar is on the right; the table says left"). Revise only the clauses the feedback touches;
   log every round with what the user said and exactly what changed. Stuck or regressing → **E9,
   E10**; editing the sheet image → `<name>-v<N>-edit.md` (`type: illustration-edit`,
   `base_image:`, no locked blocks, budget check only) and **E1–E8**.
7. **Budget both blocks** against the target model and fallbacks — a block that alone eats half of
   an 800-character cap cannot share a shot.
8. **Lock on explicit approval.** Set `status: locked`, `locked`, and record the approved image in
   `## Reference images` — the user saves it to `plan/illustration/refs/<prompt_name>-v<N>.png`;
   confirm the file is there before saying it is recorded.
   Then delete the sheet's rounds and review crops and commit, as in Phase 3 step 15 — keep the
   approved `refs/` image, a face crop a prompt still references (move it to `refs/`), and the
   `.md` files; note the deletion in `## Reference images`.

**Versions.** When the story changes the character for good — grows up, is scarred, cuts her hair —
create `<name>-v<N+1>.md` with `applies_from`, set `applies_to` on the old one, and run steps 4–8
starting from the old blocks so everything unchanged stays word-for-word. Temporary state never
makes a version.

## Phase 2b — Lock a recurring element

Anything drawn in more than one chapter drifts like a face if described fresh each time: a uniform,
a signature weapon, a room, a lamp, a monster. Give it `plan/illustration/world/<name>-v<N>.md` with
the same mechanics as a character — cited facts, `[visual:]` decisions one at a time, both locked
blocks, an optional reference image, versions by chapter range, lock on explicit approval. Run
**pitfalls W1–W8** and **I10–I13**.

- **Places belong here, not in the wiki.** Canon facts are cited from `wiki/canon/world/`; the look
  chosen for the pictures is `[visual:]` and never written back, where prose would start treating
  "stone walls" as fact. A one-off place stays inside its SCENE.
- **`world/era.md`, the world guard** — the setting's technology and dress level as concrete
  exclusions ("no blazers, neckties, zippers, phones, ballpoint pens; any writing is <script>, never
  Latin letters"). Image models pull every "student" toward modern schoolwear, anime styles more so.
  Create it the first time an image shows an anachronism; it goes into every `AVOID:` verbatim.
- Chapter prompts paste element blocks into `SCENE:` like character blocks into `CHARACTERS:`, and
  only for elements the shot shows.

## Phase 3 — Chapter image

### Choose the moment

1. Read the chapter — `drafts/…/ch<NN>-<slug>.md`, or its beat sheet if not drafted; say which.
   **The outline row has a `picture`** (`illustration_required: planned`): that is the moment — find
   its anchor in the draft, state it in one line and go on to step 3. The user chose it when they
   ratified the outline. Offer candidates (step 2) only when the draft no longer contains that
   moment, or the user asks for another.
2. Otherwise offer **two or three candidate moments** (table in templates.md): what happens, a short verbatim
   anchor quote, who is in it, the visual payoff, what it gives away. Prefer one clear action and at
   most three recognisable characters. Recommend one; **explain the chosen scene to the user before
   any generation.** The anchor is also where the image will sit in the chapter (step 14), so copy
   it from the draft verbatim — escapes included — and make it long enough to occur **once**.
3. **Spoilers are a real cost** — less inside the chapter, where the image appears at its moment, than
   outside it: a chapter list, a thumbnail, a post announcing the chapter shows the picture before the
   text. Flag a picture of the chapter's turn or of anything a reveal schedule holds back; the user
   decides. Planted characters: **S15**.
4. Every recognisable character needs a locked sheet whose range covers this chapter; every
   recurring element in frame needs one too. Missing → `blocking`: Phase 2 / 2b, or the user
   chooses to render it unrecognisable. Two locked characters standing together need a height
   reference in `refs/` (**S17**) — build it before the first round.
5. **Read the chapter for the place:** who sits and who stands, what may not happen there, where the
   key props stand, what the room is furnished with (canon first, **S2, W1**).

### Compose

6. Build the prompt in this order:

   | Section | Content | Rule |
   |---|---|---|
   | `SHOT:` | One sentence: who does what, where; everyone's posture; camera distance and angle chosen so the key prop is in frame | Leads — an overloaded prompt loses its tail |
   | `CHARACTERS:` | `Image N is <prompt_name>, the boy/girl, as on the reference sheet.` + locked block | Verbatim; numbered in reference order |
   | `SCENE:` | Per-chapter state; hands and held objects; who wears what; background people; setting, props, element blocks; light; mood | Canon facts cited in the file prose |
   | style block | STYLE.md locked block | Verbatim, a section of its own |
   | `AVOID:` | Watermark, signature, faceless people, duplicate faces, the era guard, failures seen before | The API has no negative-prompt field (models.md) |

7. **Run pitfalls S1–S19** against the draft, item by item.
8. **Fit the budget of the chapter's model** — `target_model` from `STYLE.md`, or the model the user
   names for this chapter (record it in the file's `model:`). **Fit it without paraphrasing.** Over the soft limit → cut in this order: scene
   adjectives → background detail → least important character to `locked-short` → style to
   `locked-short` → drop a character → a model with more room. Never trim a locked block, a spatial
   constraint ("on the same step", "seated") or a
   protective phrase in AVOID ("faceless or blank-faced" is not a duplicate — **S13**); keep the era
   guard full when adults or writing are in frame (**S10**).
9. Fill the `## Request` block with the references in prompt order. Omit `seed` where the model does
   not list it; warn if the shot needs more references than the model accepts.

### Check, hand over, iterate

10. Run the budget check (below) and paste its output into `## Budget check`, dated per round.
11. Run the generation or hand the command over, per "Running generation" (below), with
    `--name ch<NN>-r<N>`.
12. Review each returned image (below). Log every round in `## Iterations`: what the user said,
    what you found, which pitfall ids it maps to, exactly what changed.
13. **Close the chapter on the user's explicit approval:** copy the approved round to
    `plan/illustration/images/book-<NN>/ch<NN>.png` and verify the copy (`cmp`); set
    `status: generated` and `image:` with the round it came from; append to `wiki/log.md`.
14. **Place it in the draft**, after the paragraph that holds the anchor:

    ```bash
    python3 "$SCRIPTS/place_illustration.py" drafts/book-01/ch05-<slug>.md \
      --image plan/illustration/images/book-01/ch05.png \
      --anchor "<anchor quote from ## Moment>" --caption "<the moment, a few words, wiki_language>"
    ```

    It writes one `![caption](../../plan/…)` line, relative to the draft so it renders anywhere, and
    `illustration:` in the draft's frontmatter; nothing else in the draft changes. Re-approval moves
    the picture rather than adding a second. **Anchor found 0 or 2+ times → nothing is written:** the
    user has edited the text since the moment was chosen — show them the nearest lines and ask where
    the picture goes, then re-run with an anchor that is unique. Never place it by guess. No draft
    yet (moment chosen from the beat sheet) → skip and say so; place it once the chapter is drafted.
    Do not touch `snapshots/` — `refine-harness` ignores image lines. Report the line it landed on.
    **A published chapter is refused (exit 4)** — place the picture before `publish`; after it, a
    new picture is the user's decision to republish, not a placement.
15. **Clean up, then commit — without asking.** Once the image is approved and placed, the rounds
    are leftovers: count `rounds=` for the log line from `## Iterations` first, then delete them and
    every crop you made while reviewing:

    ```bash
    python3 "$SCRIPTS/publication.py" cleanup-rounds drafts/book-01/ch05-<slug>.md   # keeps ch05.png
    rm -f <scratchpad>/*.png                                                        # review crops
    ```

    Add a `## Iterations` row saying the rounds were deleted and which one the approved image came
    from, then commit the chapter's files by explicit path (`git commit -o -- <paths>`): the project
    may be shared with parallel sessions, and a bare `git commit` sweeps up their staged work. Keep
    the prompt and edit `.md` files — they are the history. On a real run a user had to ask for this
    after every chapter; `publish`'s `cleanup_rounds` is only the fallback for a chapter closed
    before this step existed.

## Reviewing an image

Whenever the user shows or reports an image — bake-off, style round, character round, chapter:

1. **Check the file** is a real image (`file <path>`), then **look at the whole image**.
2. **Zoom in.** Crop every named character, every hand, every held object and whatever the user
   points at (`magick <img> -crop <w>x<h>+<x>+<y> +repage <scratch>.png`), and look at each crop.
   Compare faces, eyes and hair against the reference sheet and the previous good round side by
   side. The user will not name everything; a duplicate of the hero's face in the crowd or a
   floating arrow is yours to find.
3. **Sort every defect:**

   | Kind | Examples | Fix |
   |---|---|---|
   | **Style / identity** | line too heavy, palette off, wrong hair colour, face drifted | Edit the draft block (never a locked one) during Phases 1–2; in a chapter, an image edit with the reference attached |
   | **Composition** | wrong posture, wrong position, scale, key prop out of frame, anachronism | Regenerate with a revised SHOT/SCENE (**S**-list) |
   | **Detail** | floating object, extra hand or prop, wrong grip, a stool for a bench, a duplicate face | Edit the image (**E**-list) once the composition is liked; else fix in SCENE and regenerate |

   Scene defects never justify editing a style or identity block.
4. **Once the user likes a composition, stop regenerating.** Collect every remaining defect — theirs
   and yours — write one labelled edit block per defect in `ch<NN>-edit.md`, and give the chain
   order (**E2, E3**). Each edit's base is the previous result. At the end of the chain compare
   against the round before it: lost details (**E4, E5**), palette (**E6**).
5. Tell the user what you found and what you propose in one message, recommended option first.

## Running generation

The `image_autorun` rules (who runs what and when to stop and ask), the script invocation patterns, the budget check, the artifacts tree, and the log line formats all live in [references/generation.md](references/generation.md). Read that file before running any generation or writing any log line.

## Rules

- **Never edit a locked block to fit a shot.** Use its short variant, change the scene, or version it.
- **Never lock or close without the user's explicit approval.** "Better" is not approval.
- **One question at a time**, with a recommendation.
- **Never ask what the wiki answers.** Cite it.
- **Never let a `[visual:]` decision leak** into `wiki/` or chapter prose.
- **Never claim a prompt fits** without a fresh `prompt_budget.py check` of that file, its exit code
  and output pasted (§10). The check proves size and verbatim blocks, not that the picture will look
  right — only the user's eyes do.
- **Generate images yourself only under `image_autorun: true`** and none of the stop conditions in
  "Running generation", or when the user asks for that round.
- **Every workflow correction the user makes goes into this skill** — the process here, the lesson
  into `references/pitfalls.md` with an id and the failure that taught it.
