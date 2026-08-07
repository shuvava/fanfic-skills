# fanfic-wiki

Extract a canon wiki from a book, plan collaboratively, then write fanfiction chapters that stay
in-character, in-canon, and **in the source's language**.

## Install

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

**Do not install by copying `skills/` into `.claude/skills/`.** Every skill references
`${CLAUDE_PLUGIN_ROOT}/CONVENTIONS.md`, which only resolves under plugin loading — a copied install
silently loses the shared rules on language, tiers, and citations.

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

## Style is recorded as numbers

`overview.md` carries a **style fingerprint** — measured values, not adjectives:

| Feature | Source value | Literal example |
|---|---|---|
| Chapter length | ~2,400 words | — |
| Em-dash asides | ~9 per 1,000 words | `— and he knew it —` |
| Dialogue marker | `"` … `"`, 98% of lines | `"Not tonight."` |
| Section break | `* * *`, centered | — |

Plus a **non-standard orthography** section for every place the source departs from the standard,
recorded with its count and an instruction not to "correct" it — compound adjectives the author leaves
unhyphenated, a name spelled against convention, spacing around dashes.

Both exist because a qualitative note cannot be checked. "Uses em-dashes heavily" is satisfied at any
density, and a drafting model will restore standard spelling silently unless the rule is explicit.
`write-chapter` treats these numbers as targets and reports measured against target; `wiki-lint`
flags a fingerprint written in adjectives.

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
