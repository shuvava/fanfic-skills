# Conventions

Shared rules for every skill in this plugin. When a SKILL.md says "follow the shared conventions,"
it means this file.

---

## 1. Language preservation

**Default: everything is produced in the source material's language.**

Detect the language of the material in `raw/` during `wiki-init` and record it in `CANON.md` as
`source_language`. From that point on:

| Content | Language |
|---|---|
| Wiki pages (characters, voices, world, plot) | **source language** |
| Verbatim canon quotations | **always source language, never translated** |
| Story intent, outlines, beat sheets, scene cards | **source language** |
| Generated chapter prose | **source language** |
| Conversation with the user, questions, reports, conflict warnings | user's language |

So if the book is in Russian, character pages and chapters are written in Russian while Claude talks
to the user in whatever language the user is using.

**Why this is not negotiable for voice work.** Voice cards are built from verbatim dialogue and
measure vocabulary register, syllable rhythm, archaism, and syntax. Those properties do not survive
translation — a translated voice card describes the translator's voice, not the character's. A
character page may be summarized, but quoted lines are copied exactly as they appear in `raw/`.

**Overrides.** The user can override at any level and it is recorded in `CANON.md`:

```yaml
source_language: ru
output_language: ru        # language of generated chapters
wiki_language: ru          # language of wiki pages
```

If the user says "write the fic in English" but the source is Russian, set `output_language: en`,
keep `wiki_language: ru`, and **still keep verbatim quotes in Russian** — then note in the voice card
how the register maps into the output language. Flag this explicitly to the user as a lossy step.

**Never silently switch languages.** If a skill is about to produce output in a language other than
`source_language`, say so first and confirm. Do not translate `raw/` under any circumstances.

**Mixed-language sources.** If `raw/` contains multiple languages (e.g., a Russian novel with French
dialogue), record `source_language` as the primary and preserve the code-switching in voice cards —
which characters switch, when, and to what. That is characterization data, not noise.

---

## 2. Provenance tiers

Every fact and every page carries a `tier`. This is the mechanism that stops generated fiction from
contaminating extracted canon.

| Tier | Meaning | Location | Mutable? |
|---|---|---|---|
| `canon` | Extracted from `raw/`. Cited to a source span. | `wiki/canon/` | **Never** |
| `fanon-established` | Invented for this fic, ratified by the user. | `wiki/fanon/` | Yes |
| `fanon-proposed` | Suggested by a planning stage, not yet ratified. | `wiki/fanon/proposed/` | Yes |
| `generated` | Asserted by drafted prose, not yet reviewed. | `wiki/drafts/` | Yes |

**Rules:**
- Canon tier is read-only after ingest. Nothing downstream may edit it — not planning, not drafting,
  not reconcile.
- Promotion only ever moves *up* the list and only by explicit user action:
  `generated` → `fanon-proposed` → `fanon-established`. Nothing is ever promoted to `canon`.
- Every canon fact carries `[src: <file>#<location>]`. Every fanon fact carries
  `[fanon: <decision-or-scene-that-created-it>]`. A claim with neither is an error, not a fact.
- Facts derived by reasoning rather than read directly get `(inferred)` regardless of tier.

**Statements by the source's author.** What the author says outside the published text — a letter, an
interview, a reply to the user — is **not canon**: it is unpublished, it can change, and nothing in
`raw/` supports it. Record it as `fanon-proposed` with `[author: <YYYY-MM-DD>, <channel>]`, and carry
the author's own hedges with it — «скорее всего» stays in the entry. In `brainstorm` and `plan-story`
it ranks as the strongest recommendation source, above unpaid threads, because it is the nearest thing
to the book the author would have written; the user still decides. It never enters `wiki/canon/`.

**Why the wall matters.** A compiled wiki answers confidently by design. If generated prose writes
back into the tier the drafter reads as truth, chapter 7 treats chapter 3's inventions as source
material, and canon fidelity degrades with each chapter — the same self-consuming loop that degrades
generative models trained on their own output. The tier wall is the fix, and it is cheap.

---

## 3. Conflict severity

Used by `plan-chapters` and `wiki-lint`.

| Severity | Condition | Behavior |
|---|---|---|
| `blocking` | Plan contradicts a `canon` fact | Stop. Ask the user: intentional AU divergence, or error? |
| `warning` | Plan contradicts `fanon-established` | Report; user decides. |
| `notice` | Plan contradicts `fanon-proposed`, or asserts something canon is silent on | Report in batch. |

An intentional divergence is legitimate — AU, canon-divergence, and fix-it fic are entire genres. The
resolution is to record it in `CANON.md` under `divergences` with a reason, tag the affected fact
`fanon-divergence`, and move on. What is not acceptable is *accidental* drift.

---

## 4. Citation format

```
[src: ch04.md#Глава 4, сцена в саду]             # canon, cited raw/-relative, single-volume source
[src: book-02/ch04.md#Глава 4]                   # multi-volume source — the volume is required
[fanon: intent#pairing-decision]                 # ratified fanon
[fanon: b02/ch03-scene02]                        # asserted by a generated scene (b<NN>/ in a series)
(inferred)                                       # reasoned, not read
```

Citation text stays in the source language when it quotes source headings.

**A `[src:]` path is resolvable or it is not a citation.** It resolves against `raw/` exactly as
written, so once a source has more than one volume every citation carries the volume directory —
`ch04.md` alone is then ambiguous between volumes and points at nothing on disk.

---

## 5. Honest silence

If the wiki has no confident answer, say so. Never synthesize an answer from thin evidence, and never
file such an answer back into the wiki. An empty section reading "not established in ingested
sources" is correct and useful. Invented filler is worse than nothing, because every downstream stage
treats wiki pages as fact.

---

## 6. The harness override

`plan/HARNESS.md` is a project-local file that overrides plugin defaults. It is written by
`refine-harness` and ratified by the user. **Every skill must read it if it exists**, after reading its
own instructions and before acting.

It may contain:

```markdown
---
type: harness
revision: <n>
---

## Drafting rules
Project-specific instructions that override or extend write-chapter's defaults.

## Grilling additions
Extra questions plan-story should ask in this project, and where in the tree.

## Beat gate additions
Extra checks to run over beats before drafting.

## Reconcile bias
What to propose more or less aggressively, learned from rejections.

## Revision log
| Rev | Date | Change | Evidence |
```

**Precedence:** `CANON.md` (user's explicit settings) > `plan/HARNESS.md` (learned refinements) >
plugin defaults. A harness rule may never override a language setting, a tier rule, or a gate. It
tunes *how* a stage works, never *whether* it runs.

**Scope:** the harness is project-local. It is never written back into the plugin's own SKILL.md
files — one book's habits must not leak into the next.

---

## 7. Locating the plugin's own files

Two different anchors are in play, and confusing them is the most common way these skills break:

| Reference | Resolved relative to |
|---|---|
| Markdown links inside a SKILL.md (`../../CONVENTIONS.md`) | that SKILL.md's own directory |
| **Paths in bash commands** (`python3 .../style_fingerprint.py`) | **the cwd — the project root** |

A bash command must therefore **never** use `../../scripts/...`; from the project root that escapes
the project entirely. Skills write the script as `<scripts>/style_fingerprint.py` and resolve
`<scripts>` at run time, first hit wins:

| Install | `<scripts>` |
|---|---|
| opencode, project-vendored | `.agents/scripts` |
| opencode, global | `~/.agents/scripts` |
| Claude Code plugin | `"$CLAUDE_PLUGIN_ROOT/scripts"` |
| Running inside a clone of the plugin repo | `scripts` |

```bash
for d in .agents/scripts ~/.agents/scripts "$CLAUDE_PLUGIN_ROOT/scripts" scripts; do
  [ -f "$d/style_fingerprint.py" ] && SCRIPTS="$d" && break
done
```

`raw/`, `wiki/`, `plan/`, and `drafts/` are always project-root-relative, in both markdown and bash.

---

## 8. Book scope

A project holds either one work or a series. **The wiki is shared across the whole series; the plan
and the drafts are per book.** Canon extracted from the source does not change because the fic moved
to its second book, but an outline, a conflict report, a beat sheet and a chapter file all belong to
exactly one book.

**Two independent book axes. Do not conflate them.**

| Axis | What it counts | Where | Numbered by |
|---|---|---|---|
| **source book** | volumes of the material being ingested | `raw/` | the source series' own numbering |
| **fic book** | volumes of the fic being written | `plan/`, `drafts/` | the `SERIES_ARC.md` ladder |

A five-volume source can be the input to a one-book fic, and a three-book fic can be built out of
volume 2 alone. `raw/book-03/` and `plan/book-03-<slug>/` have nothing to do with each other.

### Source books in `raw/`

One directory per volume as soon as there is more than one: `raw/book-<NN>/ch<NN>.md`, plus that
volume's `_meta.md`, which is where the volume's title and author live. A single-volume source stays
flat at `raw/ch<NN>.md`.

**No slug in the directory name.** It is carried by every `[src:]` in the wiki — thousands of them in
a real project — and a title that reads fine once reads as noise at that count. The plan and drafts
directories do carry a slug, because a working title is the only way to tell two unwritten books
apart at a glance; a source volume already has `_meta.md` to consult.

Chapter numbers follow the volume, so a second volume restarts at `ch01.md` and **collides with the
first volume's in a flat `raw/`** — which is the whole reason for the directory. Migrate before
ingesting volume 2, never after: citations written flat all have to be rewritten anyway, and doing it
while only one volume exists is a mechanical rename instead of a disambiguation.

Citations are `raw/`-relative and carry the volume when there is one — see §4.

### Fic books in `plan/` and `drafts/`

| Layout | When | Paths |
|---|---|---|
| **flat** | one book, one-shot, or no `plan/SERIES_ARC.md` | `plan/STORY_INTENT.md`, `plan/outline.md`, `plan/conflicts.md`, `plan/beats/ch<NN>.md`, `drafts/ch<NN>-<slug>.md`, `drafts/snapshots/ch<NN>-v0.md` |
| **series** | `plan/SERIES_ARC.md` has more than one rung, or the user says it is a series | `plan/book-<NN>-<slug>/{STORY_INTENT.md,outline.md,conflicts.md,beats/ch<NN>.md}`, `drafts/book-<NN>/ch<NN>-<slug>.md`, `drafts/book-<NN>/snapshots/ch<NN>-v0.md` |

Shared in both layouts, never per book: `CANON.md`, `wiki/`, `plan/HARNESS.md`, `plan/IDEAS.md`,
`plan/SERIES_ARC.md`, `drafts/continuity.md`.

`<NN>` is zero-padded and matches the `Book` column of the `SERIES_ARC.md` ladder. `<slug>` is the
book's working title, kebab-case, in `wiki_language`'s script transliterated to ASCII if needed.

**Which book am I in.** `CANON.md` records it:

```yaml
layout: series          # or: flat
current_book: 2         # series only
```

Resolve in this order: `CANON.md` `current_book` → the highest-numbered `plan/book-*/` whose outline
has undrafted chapters → ask. **Never guess from the highest-numbered directory alone** — a finished
book 2 and an unstarted book 3 look the same on disk.

**Chapter numbers restart at 1 in each book.** A chapter is identified across the project as
`b<NN>/ch<NN>` — `b02/ch03`. Cite it that way in `continuity.md`, `log.md`, and any cross-book
reference; a bare `ch03` in a series project is ambiguous and will eventually be read as the wrong
chapter.

**Migrating flat → series** happens the first time a second book is planned, or — for `raw/` — before
a second source volume is ingested. Move, do not copy:

```bash
mkdir -p raw/book-01
git mv raw/ch*.md raw/_meta.md raw/book-01/

mkdir -p plan/book-01-<slug> drafts/book-01
git mv plan/STORY_INTENT.md plan/outline.md plan/conflicts.md plan/beats plan/book-01-<slug>/
git mv drafts/ch*.md drafts/snapshots drafts/book-01/
```

Moving `raw/` files is not editing them — the bytes are untouched, which is what the invariant
protects. Rewrite every `[src:]` citation in the same commit; a citation pointing at a path that no
longer exists is worse than a coarse one, because `wiki-lint` cannot tell it from a typo.

Then set `layout: series` in `CANON.md` and say what moved. Leaving book 1 flat while book 2 is
nested means every later skill has to handle both shapes for the rest of the project's life.

---

## 9. Metrics

Every operation appends a metrics line to `wiki/log.md` so refinement has something to measure. Cost
signals, not quality judgments.

```
## [YYYY-MM-DD] write | ch07 <title>
   metrics: words=3120 beats=4 blocking=0 warnings=2

## [YYYY-MM-DD] reconcile | ch07 — 6 accepted, 4 rejected, 0 canon conflicts
   metrics: proposed=10 accepted=6 rejected=4 reject_rate=0.40

## [YYYY-MM-DD] refine-harness | rev 3 — 2 refinements ratified
   metrics: edit_rate=0.14 reject_rate=0.31 blocking_per_plan=0.5
```

`edit_rate` is the fraction of drafted words the user changed — the closest thing this system has to a
cost signal, analogous to button-press cost in an agent benchmark. It is a proxy for effort, **not a
measure of quality**: a chapter the user loves and polishes heavily scores worse than a mediocre one
they ignore. Use it to detect trends across many chapters, never to judge a single one.

---

## 10. Completion claims

**No completion claim without fresh verification evidence.**

Every skill here ends by reporting what it did. That report is an assertion about the state of the
project on disk, made by the same model that just wrote that state — the worst available witness.
Before claiming anything is done, checked, clean, updated, or consistent, run the gate:

1. **Identify** the command or read that would prove the claim false if it were false.
2. **Run** it, freshly and in full. Not a remembered result from earlier in the session.
3. **Read** the whole output, exit code included.
4. **Verify** that the output supports *this* claim and not an adjacent one.
5. **Then** assert — and say what the evidence was.

What proves what, in this pipeline:

| Claim | Evidence that proves it |
|---|---|
| "the draft is canon-clean" | a re-read of every `[src:]` page the beats declared as deps — not recollection of them |
| "style fingerprint passes" | a fresh `style_fingerprint.py check` run, its exit code observed, its table pasted |
| "the wiki was updated" | a re-read of the written files, after writing them |
| "N assertions accepted" | the accepted entries present in `wiki/fanon/`, counted there |
| "no tier violations" | a fresh grep over `wiki/canon/` for `[fanon:` and for `drafts/`-derived provenance |
| "the seed is planted" | the scene that plants it, quoted from the outline |
| "citations resolve" | the paths tested against `raw/` as literal paths |

**Mismatched evidence is the common failure, not missing evidence.** A passing fingerprint says
nothing about voice. A clean conflict lint says nothing about whether the beats were delivered. Name
which check you ran and which claim it carries; where a claim has no check behind it, report the
claim as unverified rather than quietly dropping the qualifier.

Red flags in your own output — each one means the gate was skipped:

- a hedge standing in for evidence: "should be", "seems", "looks consistent", "probably fine"
- satisfaction before output: "Done!", "All set", "Great — chapter complete"
- a count with no source: "6 accepted" when nothing was re-read to arrive at six
- trusting an earlier turn: the file may have changed since; re-read it

**The spirit, not the letter.** Rewording a claim to avoid the word "verified" does not exempt it.
Honest silence (§5) applies to your own work as much as to the wiki: *unchecked* is a legitimate and
useful thing to report, and it is always better than a confident guess.
