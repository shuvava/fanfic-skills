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
[src: chapter-04.md#Глава 4, сцена в саду]     # canon, cited to raw/
[fanon: intent#pairing-decision]                 # ratified fanon
[fanon: ch03-scene02]                            # asserted by a generated scene
(inferred)                                       # reasoned, not read
```

Citation text stays in the source language when it quotes source headings.

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

## 8. Metrics

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
