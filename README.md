# fanfic-wiki

Extract a canon wiki from a book, plan collaboratively, then write fanfiction chapters that stay
in-character, in-canon, and **in the source's language**.

## Pipeline

```
wiki-init      → structure + language detection
ingest-source  → canon wiki pages                        [tier: canon, immutable]
plan-story     → plan/STORY_INTENT.md                    [grilling gate]
plan-chapters  → outline + conflict report               [conflict gate]
write-chapter  → beats → prose → canon check             [beat gate]
reconcile      → review inbox → fanon promotion          [review gate]
wiki-lint      → health report
```

Four human gates. Each catches errors one stage before they become expensive.

## Three invariants

**1. `raw/` is never edited and never translated.** It is the source of truth.

**2. Everything is produced in the source's language by default.** If the book is Russian, the wiki
and the chapters are Russian; Claude still talks to you in your language. Verbatim quotations are
*never* translated — register, rhythm, archaism, address forms, and honorifics are the substance of a
voice card, and none of them survive translation. Override per-layer in `CANON.md`
(`wiki_language`, `output_language`) and Claude will flag the lossy step.

**3. Generated fiction never becomes canon.** Four tiers, promotion upward only, by explicit user
action, never reaching canon:

| Tier | Location | Mutable |
|---|---|---|
| `canon` | `wiki/canon/` | Never |
| `fanon-established` | `wiki/fanon/` | Yes, by ratification |
| `fanon-proposed` | `wiki/fanon/proposed/` | Yes |
| `generated` | `wiki/drafts/` | Yes |

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

## Collaboration

`plan-story` runs a grilling interview: one question at a time, each with a recommended answer,
walking the decision tree in dependency order. Facts discoverable in the wiki are looked up, never
asked — only genuine authorial decisions go to you. It stops when you confirm shared understanding.

## Structure

```
project/
├── CANON.md              # schema, language, divergences, preferences
├── raw/                  # immutable, untranslated
└── wiki/
    ├── canon/            # overview, forbidden, characters, voices, world, plot
    ├── fanon/            # ratified inventions + proposed/
    ├── plan/             # STORY_INTENT.md, outline.md, conflicts.md, beats/
    └── drafts/           # chapters + continuity.md
```

## Notes

Voice work rewards the strongest model available; ingest and lint are mechanical enough for a cheaper
one. The wiki is plain markdown in a git repo, so switch freely between operations.

No embeddings or database — at novel scale, `index.md` plus grep is enough.

Fanfiction is generally treated as transformative when non-commercial. Not legal advice; this plugin
will not generate content for commercial sale of someone else's characters.

## Learning from your edits

`refine-harness` closes the loop. `write-chapter` saves an untouched copy of every first draft to
`drafts/snapshots/`; the diff between that and what you actually kept is the highest-signal artifact
the project produces, and it costs nothing because you generate it anyway.

Refinement reads edit diffs, rejected proposals, recurring conflicts, and repeat lint findings, then
proposes changes to three targets — narrowest first:

| Target | For |
|---|---|
| `wiki/fanon/voices/<name>-notes.md` | One character's voice (most edits land here) |
| `CANON.md` preferences | Project-wide settings you'd have stated up front |
| `plan/HARNESS.md` | Cross-cutting rules for how a stage behaves |

Precedence: `CANON.md` > `HARNESS.md` > plugin defaults. A harness rule may never override a language
setting, a tier rule, or a gate — it tunes *how* a stage works, never *whether* it runs. The harness is
project-local and never written back into the plugin, so one book's habits don't leak into the next.

**The user is the reward function.** Prose has no ground truth — no milestone reached, no test passing.
A system refining against its own judgment of its own output would drift confidently in whatever
direction it already leaned. So refinement proposes and you dispose; nothing is applied unratified.
Proposals need three instances across two chapters, with citations. Every run also prunes: an
accumulating harness is the failure mode, and the marginal rule is always the weakest.

`log.md` carries `metrics:` lines — `edit_rate`, `reject_rate`, `blocking_per_plan`. These are cost
signals, not quality judgments: a chapter you loved and polished heavily scores worse than one you
shrugged at. Read trends across many chapters, never a single value.
