---
name: cover
description: >
  Make a book cover for a fic volume: author name, book title and number in the series, set with a
  real font over an aged-parchment or illustrated background, plus an optional emblem, checked
  against the publishing platform's size limits. Use when the user says "cover", "book cover",
  "обложка", "сделай обложку", "обложка для книги / тома", shows a cover to imitate, or gives
  upload rules like "не менее 200 пикселей в ширину и 285 в высоту". Text is always composed
  locally by `compose_cover.py`, never drawn by an image model.
---

# Cover

One image per book: who wrote it, what it is called, which book of the series it is.

Follow `../../CONVENTIONS.md`, especially §1 (language), §5 (honest silence), §8 (book scope),
§10 (completion claims) and §12 (secrets — the one `.env`). For illustrated backgrounds this skill
borrows `illustrate`'s style and generation tooling; read `../illustrate/SKILL.md` "Running
generation", and set up the key per §12, before handing over a command.

## Why it is built this way

| Decision | Reason |
|---|---|
| **Text is set by `compose_cover.py`, never by an image model** | Models misspell Cyrillic, invent letters and change a name between rounds. A cover with a wrong author name is unusable; a real font never misspells |
| **Background and text are separate layers** | The art can be regenerated or swapped without retyping; the title can be fixed without paying for a new image |
| **Procedural parchment is the default background** | Free, offline, reproducible by seed, and matches the classic typographic cover the source series uses |
| **Every output is checked against the platform limits** | The upload is refused otherwise; the check prints size, ratio and bytes — the §10 evidence |

## Settings

`CANON.md` carries the platform's upload rule; add it on first run from what the user gave and say so:

```yaml
cover_min_px: [200, 285]      # width, height — platform minimum
cover_max_mb: 15              # platform maximum file size
cover_size: [1200, 1800]      # what we render; 2:3, well above the minimum
```

Render large (≥ 1200 px wide) even when the minimum is tiny: platforms downscale for thumbnails
but never upscale well. A 1200×1800 JPEG at quality 92 is under 1 MB.

## Phase 0 — Route

Read `CANON.md`, `plan/SERIES_ARC.md`, the book's `STORY_INTENT.md`, and `plan/cover/` if it
exists. Resolve the book per §8.

| State | Go to |
|---|---|
| No `plan/cover/book-<NN>/COVER.md`, or facts table incomplete | Phase 1 |
| Facts locked, no direction chosen | Phase 2 |
| Direction chosen | Phase 3 |
| User sent an existing cover file to validate | Run `--check` only |

## Phase 1 — Lock the three facts

The cover must carry **author, book title, number in the series**. Fill the `Facts` table in
`COVER.md`, one question at a time, each with a recommendation:

1. **Author** — the *fic's* author: the user's pen name. **Never default to the canon author** —
   putting the source author's name on a fanfic misattributes it, and platforms remove such covers.
   If the user imitates a source cover that shows the source author, say this plainly and ask which
   name goes on top. A "по мотивам <author>" credit line is the user's call (`--series-line`).
2. **Title** — from `STORY_INTENT.md` heading or `SERIES_ARC.md`; working titles are often long
   ("Хроники Севера: чужая война"). Ask whether the series name belongs in the title or in the
   series line — not both.
3. **Number** — two numbering systems can exist: the fic's own book number and its position in the
   source's volume count (`CANON.md` may say "book 1 of the fic = volume 4 of the series"). Ask which
   one the reader should see, and the word before it (`Книга`, `Том`, `Часть`).

Copy every value verbatim into the command; the script prints the author in capitals, nothing else
is changed.

## Phase 2 — Choose the direction

Offer three with a recommendation:

| Direction | How | Cost |
|---|---|---|
| **Typographic parchment** (default; the source series' own look) | `--background parchment` + emblem | Free, seconds |
| **Illustrated** | Art generated through `illustrate`'s style, text laid over it with `--scrim` | One or more paid generations |
| **User's own image** | `--background <file>`, cover-cropped to 2:3 | Free |

**Emblem.** A single symbol from the canon (a sigil, a crest, the core, a weapon) turns a plain
cover into this series' cover. Find it in `wiki/canon/world/` and cite it; if the user shows a
source cover with a symbol, draw an SVG of the same idea at `plan/cover/emblem.svg` — plain
`stroke`/`fill` attributes, one colour, a `viewBox`, no text. Render and look at it before using it.

**Illustrated background prompt.** Write it as a ```` ```prompt ```` block in `COVER.md` with the
locked style block from `plan/illustration/STYLE.md` verbatim, and locked character blocks if a
character is shown. Composition rules the text layer depends on:

- Aspect ratio **2:3** (`--aspect-ratio 2:3`).
- **Upper third and bottom tenth kept calm and empty** — sky, wall, fog, dark cloth — for title and
  series line. Subject in the middle band. **Asking for room does not get room.** Seedream filled
  the frame with the figure both times — "keep the top third empty" (b01 r1: head at 20 % of
  height) and figure placement in percentages (r2: head at 11 %). Ask anyway, but plan for the
  **outpaint route** once pose and look are right:
  1. Shrink the liked image and centre it on a 2:3 canvas so the head lands at ~35 % and the feet
     at ~85 %; fill the border with blurred colour taken **from the image's own sky and ground
     strips** (`-crop` the top and bottom rows, stretch, `-append`, blur). Blurring the whole image
     instead leaves a dark ghost of the head in the border.
  2. Write an `illustration-edit` file whose prompt keeps **only the figure and what it holds**
     unchanged and repaints the background everywhere, behind the figure too, as one scene;
     `AVOID:` "frame, border, visible rectangle, seam, patch, blur". Asking to keep "the sharp
     central picture" unchanged (b01 r3) made Nano Banana 2 keep that rectangle pixel for pixel:
     layout right, hard seam, a castle cut off at the panel edge.
  3. Run it on an edit-capable model with the padded image as `Image 1`. The file extension
     follows the model (Nano Banana → `.png`, Seedream → `.jpg`) — `ls` before checking a round.

  4. **If a seam survives one repair edit, stop editing.** b01 r4: the second edit repainted only
     the sky inside the panel, left the soft-focus arches and paving (seam still there) and turned
     the black eyes blue-grey. Instead blur the best outpainted round (`-blur 0x7`: layout stays
     readable, the seam does not) and generate fresh on the target model with it as
     `Image 1` "blurred layout guide only … draw everything new, sharp and seamless" and the
     character sheet as `Image 2` for appearance; put the wrong eye colour in `AVOID:`. b01 r5 on Seedream: layout kept, black eyes back — **but the seam came back as scenery**: a
     bank of mist ending in a straight vertical line exactly at the old panel edge (x≈620), which
     the user caught and the review missed. After any round built from a padded or guided image,
     **crop each old panel edge by its coordinates** and look for straight lines — mist, cloud or
     wall boundaries that line up with where the panel was.
  5. **Fix a local defect on a crop, not on the whole image.** Cut a box that holds the defect and
     no face (`-crop WxH+X+Y`, a ratio the model accepts, e.g. 3:4), edit only that crop, resize
     the result back to WxH and paste it with feathered edges:
     `magick base.jpg \( fixed.png -resize WxH! \( -size WxH xc:black -fill white -draw "rectangle 12,12 W-13,H-13" -blur 0x8 \) -alpha off -compose copy_opacity -composite \) -geometry +X+Y -compose over -composite out.png`.
     The face cannot drift because the model never sees it.

  Filling the border locally (blur, mirror) looks like a picture in a frame — not usable.
- **Posture in SHOT and its opposites in AVOID.** "Stands" alone came back crouching; add
  "sitting, crouching, kneeling" to `AVOID:` when the figure must stand.
- `AVOID:` must include "text, letters, title, captions, logo, watermark, signature" — the model
  otherwise writes gibberish where the title goes.

Run `prompt_budget.py check` on it as in `illustrate`, give the user the `openrouter_image.py`
command; do not run it unless asked (it spends their money).

## Phase 3 — Compose, check, iterate

```bash
for d in .agents/scripts ~/.agents/scripts "$CLAUDE_PLUGIN_ROOT/scripts" scripts; do
  [ -f "$d/compose_cover.py" ] && SCRIPTS="$d" && break
done
python3 "$SCRIPTS/compose_cover.py" \
  --author "Псевдоним" --title "Название книги" --series "Серия" --number 1 \
  --emblem plan/cover/emblem.svg --size 1200x1800 --min-w 200 --min-h 285 --max-mb 15 \
  --out plan/cover/book-01/cover-r1.jpg
```

Useful options: `--background art.png --scrim` (illustrated), `--series-line "…"` (whole bottom
line verbatim), `--number-label Том`, `--seed N` (another parchment), `--font/--font-title` (any
TTF/OTF **with the book's alphabet** — check Cyrillic glyphs before recommending one),
`--emblem-width`, `--emblem-y`, `--no-frame`, `--ink`, `--author-y/--title-y/--title-h/--series-y`
(fractions of height — move text off a face or a spear tip). A long title wraps wherever it fits
(e.g. «Долина. Первая / зима»); put the break where the sense breaks with a literal `\n`:
`--title 'Долина.\nПервая зима'`. `--check FILE` validates without composing.

Exit `0` written and within limits; `2` written but outside a limit (fix before handing over);
`3` usage error, missing font or a tool failed. Needs `magick` (ImageMagick 7) and, for SVG
emblems, `rsvg-convert` — ImageMagick's own SVG renderer silently draws nothing for many files, and
the script stops rather than ship an empty emblem.

Each round:

1. Run the command, paste its output into `## Rounds` with the date and exact command.
   **Every new art background gets a test layout first** — compose it with placeholder text
   (`--author "Автор"`, the real title length) into the scratchpad and look at where the text
   falls on faces and hands, before the user spends another round on it or on text decisions.
2. **Look at the image** — whole, then zoomed on each text line
   (`magick <img> -crop …`): every letter correct, nothing touching the frame, emblem centred,
   text readable over the background. Also look at it **at thumbnail size**
   (`magick <img> -resize 200x285 <scratch>.png`) — that is how most readers first see it; a title
   illegible there needs a bolder font or fewer words.
3. Change only what the feedback names; next round `cover-r<N+1>.jpg`.

**Close on explicit approval** ("yes", "approve", "это финал"): copy the round to
`plan/cover/book-<NN>/cover.jpg`, verify with `cmp`, run `--check` on the copy and paste the
output; set `status: approved` and `image:` in `COVER.md`; append to `wiki/log.md`.

## Artifacts

```
plan/cover/
  emblem.svg                      # series-wide; shared by every book's cover
  book-<NN>/COVER.md              # facts, direction, prompt (if illustrated), rounds
  book-<NN>/cover-r<N>.jpg        # rounds
  book-<NN>/cover.jpg             # approved
```

`COVER.md`:

```markdown
---
type: cover
book: 1
status: draft            # draft | approved
direction: parchment     # parchment | illustrated | user-image
image:                   # book-01/cover.jpg once approved
---

# Обложка — книга 1

## Facts
| Field | Value | Source |
|---|---|---|
| Author | … | user, <date> |
| Title | … | STORY_INTENT.md |
| Series line | «…» · Книга N | user, <date> |

## Emblem
What it is, canon citation `[src: …]`, file.

## Rounds
### r1 — <date>
command, script output, what the user said, what changed.
```

Log:

```
## [YYYY-MM-DD] cover | b01 approved
   metrics: rounds=3 direction=parchment size=1200x1800 bytes=0.70MB final=plan/cover/book-01/cover.jpg
```

## Rules

- **Never let an image model render the title, author or number.** Text goes through the script.
- **Never put the canon author's name as the author** without the user's explicit decision.
- **One question at a time**, with a recommendation.
- **Never claim a cover meets the platform rule** without a fresh `--check` of that exact file,
  its output pasted (§10).
- **Never generate paid images yourself** unless the user asks.
- **Every workflow correction the user makes goes into this skill.**
