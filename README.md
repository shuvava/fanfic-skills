# fanfic-wiki

Extract a canon wiki from a book, plan collaboratively, then write fanfiction chapters that stay
in-character, in-canon, and **in the source's language**.

## Install

Each `skills/<name>/SKILL.md` reads the shared `CONVENTIONS.md` as `../../CONVENTIONS.md` — a
markdown path, resolved from that SKILL.md's own folder. Either install method keeps it intact; do
not move `SKILL.md` files out of their `skills/<name>/` folders.

`scripts/style_fingerprint.py` is different: it runs in a shell whose working directory is **your
project root**, not the plugin, so the skills resolve it at run time against your install layout
(`.agents/scripts`, `~/.agents/scripts`, `$CLAUDE_PLUGIN_ROOT/scripts`, `scripts` — first hit wins).
See `CONVENTIONS.md` §7. Copy `scripts/` wherever you copy `skills/` and it resolves itself.

### Claude Code

```bash
git clone https://github.com/shuvava/fanfic-skills.git
```

Then, inside Claude Code:

```
/plugin marketplace add /path/to/fanfic-skills
/plugin install fanfic-wiki@fanfic-skills
```

To load it for a single non-interactive run instead:

```bash
claude --plugin-dir /path/to/fanfic-skills
```

### opencode

opencode discovers skills from `.agents/skills/<name>/SKILL.md` (project) or
`~/.agents/skills/<name>/SKILL.md` (global). Vendor the plugin so the `../../` paths resolve:

```bash
cd /path/to/your-fic-project
mkdir -p .agents
cp -R /path/to/fanfic-skills/{CONVENTIONS.md,scripts,skills} .agents/
```

opencode walks up from the cwd to the git worktree root looking for `.agents/`, so the project must
be a git repo (`git init` if not). Verify the skills loaded:

```bash
opencode debug skill | grep -E 'wiki-init|ingest-source|brainstorm|plan-story|plan-chapters|develop-character|write-chapter|reconcile|refine-harness|wiki-lint|illustrate|cover'
```

For a global install visible from every project, copy the same three into `~/.agents/` instead.

**Do not move `SKILL.md` files out of their `skills/<name>/` folders.** The `../../CONVENTIONS.md`
reference resolves to the plugin root from that exact depth — flattening the layout silently breaks
the shared conventions.

## Use it

Make a project directory and **put your source material in `raw/`**. That directory name is not a
suggestion: every skill reads the source from `raw/`, cites to it as `[src: <file>#<location>]`, and
measures the style fingerprint against `raw/*.md`. A book sitting in `source/`, `books/`, or the
project root will not be found, and `wiki-init` will copy it into `raw/` rather than read it in
place — leaving you two copies of the same book.

Plain markdown or text, **one file per chapter** if you can. That matters more than it looks: ingest
is per-chapter, citations point into whatever file you give it, and `measure` globs `raw/*.md` — so
a single file holding the whole novel produces citations into a megabyte of text and a style
fingerprint computed over chapters you have not ingested yet.

```
mkdir my-fic && cd my-fic
mkdir raw && cp ~/books/the-source/chapter-*.md raw/    # one file per chapter
git init                                                 # so a bad ingest can be reverted
claude
```

`raw/` is never edited and never translated, by any skill, ever. Everything else in the project is
generated from it.

Then talk to Claude. Skills trigger from what you say; you never type a skill name.

**1. Scaffold.** → *"Set up a story bible from the chapters in raw/."*

Builds the tree, detects the source language, writes `CANON.md`. If the source is Hungarian, the wiki
and the chapters will be Hungarian — Claude still talks to you in your language.

**2. Ingest, one chapter at a time.** → *"Ingest raw/chapter-01.md."*

Compiles that chapter into `wiki/canon/`: character pages, voice cards holding verbatim dialogue,
world rules with their costs, plot threads, and the style fingerprint. Repeat per chapter. Six to ten
chapters is usually enough to plan against.

Ask *"lint the wiki"* whenever you want a health report.

**3. Figure out what to write** (optional, and skip it if you already know) → *"Let's brainstorm the
next book"* or *"What if he ends up on the throne — how many books is that?"*

The divergent stage. You and Claude throw ideas at each other, each one gets a quick canon check as
it lands, and most of them get killed out loud with the reason recorded so they don't come back next
session. Planning several books sets a destination and a ladder of rungs to reach it — which turns
"any idea is fine" into "does this move him along it?" Lands in `plan/IDEAS.md` and
`plan/SERIES_ARC.md`. Nothing is committed here; the next step reads them as candidates.

**4. Decide what you're writing.** → *"Let's plan the story."*

A one-question-at-a-time interview, each question carrying a recommended answer so you can say "yes"
and move on. Anything the wiki can answer is looked up, never asked. Ends with `plan/STORY_INTENT.md`
once you confirm.

**5. Outline.** → *"Outline it — five chapters."*

Expands to paragraph → arc → chapter list → scene list, ratifying each layer. Then it lints the plan
against canon **before any prose exists** and reports conflicts.

**6. Write.** → *"Write chapter 1."*

Beats first — you review them, which is the cheapest place to catch a problem. Then prose, then a
canon check reporting anything it violated rather than quietly fixing it.

**7. Edit the draft yourself.** Then → *"Reconcile chapter 1."*

Routes what the chapter invented through your review, promoting what you accept into `fanon`.

**8. After a few chapters** → *"Refine the harness."*

Reads the diff between what Claude drafted and what you kept, and proposes project-local rules. You
ratify each one.

## Pipeline

```
wiki-init      → structure + language detection
ingest-source  → canon wiki pages                        [tier: canon, immutable]
brainstorm     → plan/IDEAS.md + plan/SERIES_ARC.md      [no gate — candidates only]
plan-story     → plan/STORY_INTENT.md                    [grilling gate]
plan-chapters  → outline + conflict report               [conflict gate]
develop-character → character profiles + cardboard check [depth threshold, CONVENTIONS §11]
write-chapter  → beats → prose → canon check             [beat gate]
reconcile      → review inbox → fanon promotion          [review gate]
refine-harness → learn from your edits
wiki-lint      → health report
illustrate     → image prompts per chapter               [style + character lock gates]
cover          → book cover: author, title, series number [platform size check]
```

Four human gates. Each catches errors one stage before they become expensive. `brainstorm` is
deliberately not one of them — nothing it produces is committed, so there is nothing to gate.

## Three invariants

**1. `raw/` is never edited and never translated.** It is the source of truth.

**2. Everything is produced in the source's language by default.** Verbatim quotations are *never*
translated — register, rhythm, archaism, address forms, and honorifics are the substance of a voice
card, and none of them survive translation. Override per-layer in `CANON.md` (`wiki_language`,
`output_language`) and Claude will flag the lossy step.

**3. Generated fiction never becomes canon.** Four tiers, promotion upward only, by explicit user
action, never reaching canon:

| Tier | Location | Mutable |
|---|---|---|
| `canon` | `wiki/canon/` | Never |
| `fanon-established` | `wiki/fanon/` | Yes, by ratification |
| `fanon-proposed` | `wiki/fanon/proposed/` | Yes |
| `generated` | `drafts/` | Yes |

Without this wall, chapter 7 treats chapter 3's inventions as source material and canon fidelity rots.

## Ideas are candidates, not facts

`brainstorm` writes to `plan/`, never to `wiki/` — not even to `fanon/proposed/`. An idea is not a
fact about the world; it is something you might decide later, and most of them you won't. Putting
candidates in a provenance tier dilutes the entries that actually matter when a chapter is being
drafted.

Two things make the stage worth running rather than just chatting:

**A destination makes ideas judgeable.** If the series ends with him on the throne ten books out,
"what if he falls in love" stops being unanswerable. The relationship is good if it's *how* he learns
what the throne demands, or *what* he trades to reach it — and it's a detour if he ends it unchanged.
Without a destination every idea looks equally fine, which is the same as having no opinion. So
`SERIES_ARC.md` holds the destination and a ladder of rungs, where each book's end state is the next
book's start state. The destination is firm; the next two rungs are detailed; rungs 4–10 are one line
each. Ten planned books get thrown away when book 2 changes, exactly as forty planned scenes get
thrown away when chapter 3 does.

**Killed ideas stay killed.** Every kill is recorded with its reason, so the same idea doesn't come
back next session to be re-argued from scratch. The skill is told to take a position on every idea
and kill out loud, because thirty ideas met with equal enthusiasm contain no signal — the culling is
the work. A session's `kill_rate` goes in the log; a session that killed nothing didn't discriminate.

## Conflicts surface at planning time

`plan-chapters` lints the outline against canon before any prose exists:

| Severity | Condition | Behavior |
|---|---|---|
| `blocking` | Contradicts `canon` or violates `forbidden.md` | Stop and ask |
| `warning` | Contradicts `fanon-established` | Report |
| `notice` | Canon is silent | Batch report |

A blocking conflict asks one question: intentional AU divergence, or error? Intentional divergences
get recorded in `CANON.md` and stop being conflicts. Catching this at the beat stage costs a line;
catching it after drafting costs a scene.

## A series is planned one book at a time

The wiki is shared across every book; the plan and the drafts are per book. So book 2 lives in
`plan/book-02-<slug>/` and `drafts/book-02/`, chapter numbers restart at 1 in each book, and a
chapter is referred to across the project as `b02/ch03`. A project starts flat — a single book's
`plan/outline.md` — and `plan-chapters` migrates it the first time you plan a second book.

Outlining book 2 then runs three checks book 1 never needed:

- **The start state is gated against what book 1 actually ended with**, not against what the ladder
  said it would end with. Where the drafted text and `SERIES_ARC.md` disagree, the text wins.
- **Seeds are checked both directions.** A seed the ladder says to plant in this book that no scene
  plants is `blocking` — by the time book 4 needs it, book 2 is published and the fix is either a
  rewrite or a coincidence the reader will notice.
- **The ending has to deliver this rung's end state**, because the next book's start state is already
  written against it.

Facts earlier books invented and you ratified live in `wiki/fanon/`, which is series-wide: in book 3
they are as binding as canon in practice. `drafts/continuity.md` is one file for the whole series for
the same reason — a per-book ledger is how book 3 forgets book 1.

## Style is measured, not described

A style note written as an adjective cannot be checked. "Uses em-dashes heavily" is satisfied at any
density — and in testing, exactly that happened: the wiki recorded the source's ellipsis habit as
"heavy", the source ran 21 ellipses per 1,000 words, the generated chapter ran 4.6, and nothing in
the pipeline could tell the difference. So the plugin ships a counter.

```bash
# during ingest — produces the tables that go into canon/overview.md
python3 <scripts>/style_fingerprint.py measure raw/*.md

# during drafting and linting — how far has this draft drifted?
python3 <scripts>/style_fingerprint.py check drafts/ch07-*.md --against raw/*.md
```

Run these from your project root. `<scripts>` is wherever you installed the plugin's `scripts/`
folder — `.agents/scripts` for a vendored opencode install, `$CLAUDE_PLUGIN_ROOT/scripts` under
Claude Code; the skills resolve it themselves.

Standard library only, no dependencies, no language-specific rules. `ingest-source` runs `measure`
and pastes the result; `write-chapter` runs `check` on its own draft and revises until it passes;
`wiki-lint` runs both.

`measure` produces the **style fingerprint** — measured values with literal examples:

| Feature | Source value | Literal example |
|---|---|---|
| Chapter length | ~2,400 words (range 2,050–2,780) | — |
| Sentence length | 17.2 words (sd 9.4) | — |
| Em dash | 9.1 per 1000 words | `— and he knew it —` |
| Dialogue marker `double_quote` | 98% of 412 lines | `"Not tonight."` |

`check` reports the delta on every one of them and exits non-zero if anything is out of tolerance:

```
| Feature              | Source | Draft | Delta   |
| Chapter length       |   2400 |  1810 | -25%  ⚠ |
| Em dash per 1k       |    9.1 |   2.4 | -74%  ⚠ |
| Dialogue double_quote|    98% |   96% |  -2pp   |

**2 feature(s) outside tolerance.**
```

### Orthography: what the script does, and what it refuses to do

Every source has spellings that depart from the standard, and **a drafting model will silently repair
them** — it has been trained to. So `measure` also hunts for them, two ways:

- Where the source uses *both* spellings, it reports which one dominates and by how much. Precise, and
  blind when the standard form never appears at all.
- For that blind case, it emits **candidates to adjudicate**: every hyphenated form, the frequent
  two-word sequences, and — most usefully — short tokens grouped by how many different words precede
  them, which is what a postfix particle looks like from the outside.

**The script does not decide which candidates are non-standard, and deliberately cannot.** Whether a
form needs a hyphen is a fact about the language, not about the text; shipping a dictionary would
make this work for one language and fail silently for the rest. Claude reads the candidate list, and
Claude knows the language. The script counts; the model judges. That split is what makes this work on
a Russian LitRPG and a Regency romance with the same forty lines of code.

Real output from the test corpus, where the standard form never once appears:

```
- `то` — follows 14 different words, 56 times total: `какой то`, `что то`, `какое то`, `как то`
```

Standard Russian hyphenates all four. Claude recognizes that instantly, writes the rule into
`overview.md` with its count and a do-not-correct instruction, and every later chapter keeps the
author's spelling.

## Structure

```
project/
├── CANON.md              # schema, language, divergences, preferences
├── raw/                  # immutable, untranslated
├── plan/                 # IDEAS.md, SERIES_ARC.md, HARNESS.md — series-wide
│                         #   STORY_INTENT.md, outline.md, conflicts.md, beats/ — per book,
│                         #   nested under book-<NN>-<slug>/ once there is a second book
│                         #   illustration/ — image style, locked character looks, chapter prompts
├── drafts/               # chapters + snapshots/, nested per book in a series
│                         #   continuity.md — series-wide, never per book
└── wiki/
    ├── canon/            # overview, forbidden, characters, voices, world, plot
    └── fanon/            # ratified inventions + proposed/
```

## Illustrations with the same faces

`illustrate` writes image-generation prompts for chapters — you run them on OpenRouter or anywhere
else. An image model has no memory, so a character looks the same only if the words describing them
are the same every time and, better, the same approved picture is attached as a reference. The
skill splits every prompt into what never changes and what changes per chapter:

| Layer | Locked | Where |
|---|---|---|
| Style | once per series | `plan/illustration/STYLE.md` |
| Character look | per identity version, after generate-and-revise rounds you approve | `plan/illustration/characters/<name>-v<N>.md` + reference sheet image |
| Recurring elements | per version — uniforms, props, rooms, creatures, the era guard against anachronisms | `plan/illustration/world/<name>-v<N>.md` |
| Scene | never — chosen from the chapter each time | `plan/illustration/book-<NN>/ch<NN>.md` |

Once you like a composition, the skill stops regenerating and fixes the rest with single-change
image edits, then checks the chain for drifted faces and colour. What went wrong along the way —
three hands, a standing girl in an exam where nobody stands, an examiner the size of an ant — is
kept as a checklist in `skills/illustrate/references/pitfalls.md` that every prompt is run against.

Prompt sizes differ by two orders of magnitude between models (Qwen-Image: 800 characters; Nano
Banana Pro: 65K tokens), and several truncate silently. `scripts/prompt_budget.py` checks a prompt
against the target model and confirms every locked block is present verbatim:

```bash
python3 scripts/prompt_budget.py list
python3 scripts/prompt_budget.py check plan/illustration/book-01/ch05.md \
  --model google/gemini-3.1-flash-image \
  --locked plan/illustration/STYLE.md plan/illustration/characters/лилия-v1.md
```

`scripts/openrouter_image.py` runs a prompt block on one or more OpenRouter models with your key
(`OPENROUTER_API_KEY` in the shell, or in the one `.env` at your project root — see `.env.example`
and `CONVENTIONS.md` §12; the skills make sure `.env` is gitignored before you add a key),
attaching reference images in order and printing API errors instead of saving empty files; `--block 2c` picks a labelled edit block.

Limits and sources: `skills/illustrate/references/models.md`.

## Book covers

`cover` makes one cover per book with the author, the title and the number in the series. The text
is never drawn by an image model — they misspell Cyrillic — but set by `scripts/compose_cover.py`
with a real font over a procedural aged-parchment background (free, offline) or an illustrated one
generated through `illustrate`'s locked style. An optional SVG emblem from the canon goes in the
middle. Every output is checked against the platform's upload limits:

```bash
python3 scripts/compose_cover.py --author "Псевдоним" --title "Название" --series "Серия" --number 1 \
  --emblem plan/cover/emblem.svg --min-w 200 --min-h 285 --max-mb 15 --out plan/cover/book-01/cover-r1.jpg
python3 scripts/compose_cover.py --check plan/cover/book-01/cover.jpg
```

Needs ImageMagick 7 and, for SVG emblems, `rsvg-convert` (librsvg).

## Learning from your edits

`refine-harness` closes the loop. `write-chapter` saves an untouched copy of every first draft to
`drafts/snapshots/`; the diff between that and what you actually kept is the highest-signal artifact
the project produces, and it costs nothing because you generate it anyway.

Refinement proposes changes to three targets — narrowest first:

| Target | For |
|---|---|
| `wiki/fanon/voices/<name>-notes.md` | One character's voice (most edits land here) |
| `CANON.md` preferences | Project-wide settings you'd have stated up front |
| `plan/HARNESS.md` | Cross-cutting rules for how a stage behaves |

Precedence: `CANON.md` > `HARNESS.md` > plugin defaults. A harness rule may never override a language
setting, a tier rule, or a gate — it tunes *how* a stage works, never *whether* it runs. The harness is
project-local and never written back into the plugin, so one book's habits don't leak into the next.

**You are the reward function.** Prose has no ground truth — no milestone reached, no test passing. A
system refining against its own judgment of its own output would drift confidently in whatever
direction it already leaned. So refinement proposes and you dispose; nothing is applied unratified.
Proposals need three instances across two chapters, with citations. Every run also prunes: an
accumulating harness is the failure mode, and the marginal rule is always the weakest.

`log.md` carries `metrics:` lines — `edit_rate`, `reject_rate`, `blocking_per_plan`. These are cost
signals, not quality judgments: a chapter you loved and polished heavily scores worse than one you
shrugged at. Read trends across many chapters, never a single value.

## Notes

Voice work rewards the strongest model available; ingest and lint are mechanical enough for a cheaper
one. The wiki is plain markdown in a git repo, so switch freely between operations, and `git init`
early — being able to diff and revert a bad ingest is most of the wiki's value.

No embeddings or database — at novel scale, `index.md` plus grep is enough.

Fanfiction is generally treated as transformative when non-commercial. Not legal advice; this plugin
will not generate content for commercial sale of someone else's characters.
