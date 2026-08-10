# fanfic-wiki

Extract a canon wiki from a book, plan collaboratively, then write fanfiction chapters that stay
in-character, in-canon, and **in the source's language**.

## Install

The skills reference `CONVENTIONS.md` and `scripts/style_fingerprint.py` via repo-relative paths
(`../../CONVENTIONS.md`, `../../scripts/...` from each `skills/<name>/SKILL.md`). Either install
method keeps those paths intact; do not move `SKILL.md` files out of their `skills/<name>/` folders.

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
opencode debug skill | grep -E 'wiki-init|ingest-source|plan-story|plan-chapters|write-chapter|reconcile|refine-harness|wiki-lint'
```

For a global install visible from every project, copy the same three into `~/.agents/` instead.

**Do not move `SKILL.md` files out of their `skills/<name>/` folders.** The `../../` references
resolve to the plugin root from that exact depth — flattening the layout silently breaks the shared
conventions and the style fingerprint script.

## Use it

Make a project directory and put your source material in it. Plain markdown or text, one file per
chapter if you can — smaller ingests produce sharper pages.

```
mkdir my-fic && cd my-fic
mkdir raw && cp ~/books/the-source/*.md raw/
claude
```

Then talk to Claude. Skills trigger from what you say; you never type a skill name.

**1. Scaffold.** → *"Set up a story bible from the chapters in raw/."*

Builds the tree, detects the source language, writes `CANON.md`. If the source is Hungarian, the wiki
and the chapters will be Hungarian — Claude still talks to you in your language.

**2. Ingest, one chapter at a time.** → *"Ingest raw/chapter-01.md."*

Compiles that chapter into `wiki/canon/`: character pages, voice cards holding verbatim dialogue,
world rules with their costs, plot threads, and the style fingerprint. Repeat per chapter. Six to ten
chapters is usually enough to plan against.

Ask *"lint the wiki"* whenever you want a health report.

**3. Decide what you're writing.** → *"Let's plan the story."*

A one-question-at-a-time interview, each question carrying a recommended answer so you can say "yes"
and move on. Anything the wiki can answer is looked up, never asked. Ends with `plan/STORY_INTENT.md`
once you confirm.

**4. Outline.** → *"Outline it — five chapters."*

Expands to paragraph → arc → chapter list → scene list, ratifying each layer. Then it lints the plan
against canon **before any prose exists** and reports conflicts.

**5. Write.** → *"Write chapter 1."*

Beats first — you review them, which is the cheapest place to catch a problem. Then prose, then a
canon check reporting anything it violated rather than quietly fixing it.

**6. Edit the draft yourself.** Then → *"Reconcile chapter 1."*

Routes what the chapter invented through your review, promoting what you accept into `fanon`.

**7. After a few chapters** → *"Refine the harness."*

Reads the diff between what Claude drafted and what you kept, and proposes project-local rules. You
ratify each one.

## Pipeline

```
wiki-init      → structure + language detection
ingest-source  → canon wiki pages                        [tier: canon, immutable]
plan-story     → plan/STORY_INTENT.md                    [grilling gate]
plan-chapters  → outline + conflict report               [conflict gate]
write-chapter  → beats → prose → canon check             [beat gate]
reconcile      → review inbox → fanon promotion          [review gate]
refine-harness → learn from your edits
wiki-lint      → health report
```

Four human gates. Each catches errors one stage before they become expensive.

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

## Style is measured, not described

A style note written as an adjective cannot be checked. "Uses em-dashes heavily" is satisfied at any
density — and in testing, exactly that happened: the wiki recorded the source's ellipsis habit as
"heavy", the source ran 21 ellipses per 1,000 words, the generated chapter ran 4.6, and nothing in
the pipeline could tell the difference. So the plugin ships a counter.

```bash
# during ingest — produces the tables that go into canon/overview.md
python3 scripts/style_fingerprint.py measure raw/*.md

# during drafting and linting — how far has this draft drifted?
python3 scripts/style_fingerprint.py check drafts/ch07-*.md --against raw/*.md
```

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
├── plan/                 # STORY_INTENT.md, outline.md, conflicts.md, beats/, HARNESS.md
├── drafts/               # chapters + continuity.md + snapshots/
└── wiki/
    ├── canon/            # overview, forbidden, characters, voices, world, plot
    └── fanon/            # ratified inventions + proposed/
```

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
