# Skill Description & Structure Audit — fanfic-skills

**Date:** 2026-10-18
**Scope:** All 15 skills under `skills/`
**Purpose:** Capture baseline state before rewriting descriptions and splitting oversized SKILL.md files. This document is the review surface — please sanity-check the trigger vocabulary and cross-deconfliction clauses before any files are touched.

---

## 1. Baseline metrics

| Skill | Lines | Bytes | Description chars | Has `references/`? |
|---|---:|---:|---:|---|
| brainstorm | 261 | 12 370 | 520 | no |
| cover | 231 | 12 871 | 528 | no |
| develop-character | 149 | 7 646 | 552 | no |
| illustrate | 445 | 29 505 | 773 | **yes** |
| ingest-source | 211 | 13 090 | 403 | no |
| naturalize | 308 | 18 437 | 577 | no |
| plan-chapters | 579 | 39 347 | 762 | no |
| plan-story | 181 | 8 757 | 397 | no |
| publish | 332 | 19 949 | 587 | **yes** |
| reconcile | 150 | 7 898 | 377 | no |
| refine-harness | 170 | 8 792 | 448 | **yes** |
| translate | 328 | 18 772 | 604 | no |
| wiki-init | 147 | 7 528 | 404 | no |
| wiki-lint | 227 | 14 861 | 355 | no |
| write-chapter | 446 | 33 032 | 375 | no |
| **Total** | **4 165** | **252 838** | **—** | 3 of 16 |

### Findings

- **3 skills exceed the 500-line guideline** that Anthropic's best-practices doc recommends: `plan-chapters` (579), `illustrate` (445 — at the edge), `write-chapter` (446 — at the edge). `naturalize` and `publish` are at 308 / 332 — borderline, candidate for split only if they grow.
- **3 skills already have `references/` folders** (`illustrate`, `publish`, `refine-harness`) but SKILL.md may still inline heavy content — needs verification.
- **Sum of description byte counts ≈ 7 700 chars** — this is the part that lives in **every system prompt** forever once skills are installed. Per Anthropic's best practices ("Each Skill has exactly one description field. The description is critical for skill selection"), this is the highest-leverage place to cut noise.
- **All current descriptions violate the "trigger-only" rule** from superpowers' `writing-skills` (lines 152–158) and from Anthropic's best-practices implicit guidance. They open with a verb describing what the skill *does* (e.g. "Generate, discuss, and cull story ideas…", "Make a book cover…", "Decompose one chapter into scene beats…"). That is workflow summary — agents may follow the description and skip the body.
- **No description mentions any other skill by name.** That is the root cause of cross-triggering. The cross-deconfliction matrix below is derived from inspecting which trigger phrases overlap.

---

## 2. Current trigger surface (extracted from all SKILL.md bodies)

These are the user-typed phrases the model currently sees as triggers, organised by skill. Phrases that appear in **multiple** skills are flagged.

| Phrase | Skills that list it as a trigger |
|---|---|
| "brainstorm" / "what if" / "ideas" | `brainstorm` |
| "I want to write a fic about" / "help me figure out what to write" / "start planning" | `plan-story` |
| "outline the story" / "plan the chapters" / "expand the plan" / "break this into chapters" / "outline book 2" | `plan-chapters` |
| "write chapter N" / "draft the next chapter" / "write the scene where X" / "continue the story" | `write-chapter` |
| "ingest chapter N" / "process this book" / "add this to canon" | `ingest-source` |
| "set up a story bible" / "start a fanfic project" / "init a canon wiki" | `wiki-init` |
| "lint the wiki" / "check the story bible" / "audit the wiki" | `wiki-lint` |
| "reconcile" / "update the wiki with the new chapter" / "promote the fanon" | `reconcile` |
| "refine" / "learn from my edits" / "tune the harness" | `refine-harness` |
| "translate chapter N" / "translate to English" | `translate` |
| "the text sounds mechanical" / "reads like AI" / "fix clumsy phrasing" / "почисти" | `naturalize` |
| "develop this character" / "flesh out X" / "who is X really" / "проработай" | `develop-character` |
| "illustrate chapter N" / "image for chapter N" | `illustrate` |
| "book cover" / "cover" / "сделай обложку" / "обложка для книги" | `cover` |
| "publish the next chapter" / "publish chapter N" | `publish` |

### Real cross-trigger risks (the collisions that justify the rewrite)

1. **`brainstorm` ↔ `plan-story`** — both match "what should I write" and "I want to write a fic about…". User has not committed to a fic yet (`brainstorm` — divergent ideas, multiple) vs. user wants *one* fic, picked (`plan-story` — convergent interview, single decision).
2. **`plan-story` ↔ `plan-chapters`** — both match "plan", "outline", "let's plan the story". `plan-story` produces `STORY_INTENT.md`; `plan-chapters` needs that file as input. Disambiguator: does the user have an intent yet?
3. **`plan-chapters` ↔ `write-chapter`** — both match "plan", "outline", "next chapter". `plan-chapters` produces a plan; `write-chapter` consumes a plan. Hard prerequisite check.
4. **`write-chapter` ↔ `reconcile`** — `reconcile` runs automatically after `write-chapter`. Its description must say "Usually invoked by `write-chapter` finishing, not by direct user request" so the user doesn't manually trigger it.
5. **`naturalize` ↔ `translate`** — both match "chapter N", "fix prose". `naturalize` is monolingual cleanup of AI-sounding text; `translate` is cross-lingual. Disambiguator: language switch or not?
6. **`wiki-init` ↔ `ingest-source`** — both match "process this book", "set up canon". `wiki-init` runs **once** at project start, scaffolds the empty wiki; `ingest-source` runs **after** the wiki exists and adds to it.
7. **`wiki-lint` ↔ `refine-harness`** — both match "audit", "check", "review". `wiki-lint` is read-only on the **wiki**; `refine-harness` proposes changes to the **harness** (drafting rules). Different artefacts.
8. **`illustrate` ↔ `cover`** — both match "image", "art", Russian "обложка" (cover) vs no direct Russian for illustrate but "иллюстрация" sometimes used. `illustrate` = per-chapter, character-consistent; `cover` = one volume cover with title font + emblem.
9. **`cover` ↔ `publish`** — both fire on "publish book" sometimes. `cover` produces an image file; `publish` uploads text to a platform. Different artefacts entirely.
10. **`develop-character` ↔ `brainstorm`** — `develop-character` is about a named existing character; `brainstorm` is about plot-level "what if" ideas. Different objects.

### Russian-language triggers (relevant — the user is bilingual)

Found in current descriptions and bodies:

- `brainstorm` — no RU phrases yet, candidate to add
- `cover` — "обложка для книги / тома", "сделай обложку"
- `develop-character` — "проработай"
- `naturalize` — "почисти", "почисти текст"
- `publish` — (none yet in description)
- `reconcile` — (none yet)
- `translate` — (none yet)
- `write-chapter` — (none yet)
- `wiki-init` — (none yet)

**Action:** every description should include Russian equivalents where they naturally exist, since the model has to match the user's actual utterance.

---

## 3. Proposed description template

Derived from:
- Anthropic best practices, "Writing effective descriptions" — `Use when [specific triggering conditions and symptoms]`, third person.
- superpowers `writing-skills` lines 167–172 — description = triggering conditions, **never workflow summary**.
- Your choice (this conversation): maximum prescription with explicit "that's `<other-skill>`" cross-deconfliction clauses.

```yaml
description: >
  Use when ONLY when the user says <EN trigger 1>, <EN trigger 2>, <EN trigger 3>, or
  <RU trigger 1> / <RU trigger 2>. Do NOT use when <negative trigger 1> (that's <other-skill> —
  <one-line reason>) or <negative trigger 2> (that's <other-skill>). Requires <hard prerequisite
  or "no prerequisites">.
```

Optional trailing line, used **only** when the artefact name itself is a disambiguator:

```yaml
  Produces <one-line artefact>. Read-only by default.
```

**Length budget:** ≤ 600 chars target, hard cap 1024. Most will land at 400–550.

**Hard rules:**

- Third person, always
- No workflow verbs at the start ("Generate", "Make", "Decompose", "Develop") — those are workflow summaries
- Every negative trigger names the skill it should defer to, so the model can see both descriptions and pick
- No mention of process steps inside the description (e.g. "Three phases: lock style…"). If a user-typed phrase is "three phases" the model will skip the body.

---

## 4. Proposed new descriptions (drafts — please review)

Each entry below is what the new frontmatter `description:` value would be. Comments in brackets explain my reasoning; they are **not** part of the final string.

### brainstorm

```
Use when ONLY when the user says "brainstorm", "what if…", "what should the next book be",
"where is this series going", "I have an idea — what if…", "give me ideas", "let's think about
future books", "придумай", "что если", "идеи для книги", or asks for many ideas at once. Do NOT
use when the user has already picked one fic to write ("I want to write a fic about X", "let's
plan the story") — that's plan-story. Do NOT use when the user names a specific existing
character to develop ("who is X really", "проработай X") — that's develop-character.
Output: plan/SERIES_ARC.md + plan/IDEAS.md. Nothing here is ever canon.
```

### cover

```
Use when ONLY when the user says "cover", "book cover", "make a cover", "обложка", "сделай
обложку", "обложка для книги", "обложка для тома", or asks for a single volume cover with
title font and optional emblem. Do NOT use when the user wants per-chapter illustrations
("illustrate chapter N", "image for chapter X") — that's illustrate. Do NOT use when the user
wants to upload or publish text ("publish the next chapter", "publish book N") — that's publish.
Produces one cover image sized to the platform's limits.
```

### develop-character

```
Use when ONLY when the user names a specific existing character and asks for depth: "develop
this character", "flesh out X", "who is X really", "what does X want", "проработай X",
"расскажи про X подробнее". Do NOT use when the user is brainstorming plot-level "what if"
ideas with no character named — that's brainstorm. Do NOT use when the user wants to write a
scene featuring an existing character — that's write-chapter. Read-only on the canon wiki.
```

### illustrate

```
Use when ONLY when the user asks for chapter-scoped image-generation prompts that must keep
the same characters recognisable across many images: "illustrate chapter N", "image for chapter
X", "make an illustration for chapter 2 of book 3", "иллюстрация к главе". Three phases:
character lock → style lock → per-chapter prompt. Do NOT use for a single book cover with title
and emblem — that's cover. Requires at least one chapter outline to exist (run plan-chapters
first if missing).
```

### ingest-source

```
Use when ONLY when the user provides source material to canonise: "ingest chapter N", "process
this book", "add this to canon", "transcribe this transcript", "this is the source", "добавь
в канон", "обработай эту главу". Adds to wiki/canon/ only — never to fanon/. Requires the
wiki to exist (run wiki-init first if it doesn't). Do NOT use when the user wants to re-read
the wiki or audit it — that's wiki-lint.
```

### naturalize

```
Use when ONLY when the user flags prose as sounding mechanical, AI-like, or non-native and
asks for cleanup in the same language: "sounds mechanical", "reads like AI", "fix clumsy
phrasing", "почисти корявые фразы", "текст механический", "проверь естественность", "почисти
текст", "звучит как ИИ", "слишком машинно". Monolingual: source stays in source language.
Strictly no meaning changes: if a passage needs meaning work, flags it without a rewrite and
tells the user to use write-chapter for that passage. Also runs internally from plan-story,
plan-chapters, and write-chapter §5 — invoke directly only when the user names this skill.
Do NOT use when the user wants cross-language translation — that's translate. Do NOT use
when the user wants to rewrite meaning, not just prose rhythm — clarify and route to
write-chapter.
```

### plan-chapters

```
Use when ONLY when the user wants to expand a confirmed story intent into a chapter outline:
"outline the story", "plan the chapters", "expand the plan", "break this into chapters",
"outline book 2", "составь план глав", "разбей на главы". Requires plan/STORY_INTENT.md from
plan-story. Do NOT use when no STORY_INTENT.md exists yet — that's plan-story first. Do NOT
use when the user wants to draft prose — that's write-chapter. Runs the canon conflict check
before any prose exists.
```

### plan-story

```
Use when ONLY when the user has not committed to a fic yet and wants a single one chosen:
"let's plan the story", "I want to write a fic about X", "help me figure out what to write",
"start planning", "давай придумаем фанфик", "хочу написать фанфик про…". Single convergent
interview with one question at a time. Do NOT use when the user wants many divergent ideas to
choose from later — that's brainstorm. Do NOT use when STORY_INTENT.md already exists and the
user wants chapters — that's plan-chapters. Ends with plan/STORY_INTENT.md.
```

### publish

```
Use when ONLY when the user wants to serialise the fic on a publishing platform: "publish the
next chapter", "publish chapter N", "upload chapter N", "опубликуй главу", "выложи главу".
The user confirms every publication. Do NOT use when the user wants a book cover image —
that's cover. Do NOT use when the user wants to reconcile what a chapter established against
canon — that's reconcile (and it usually runs automatically after write-chapter).
```

### reconcile

```
Use when ONLY when invoked explicitly to audit or re-audit a chapter against canon: "reconcile",
"reconcile chapter N", "update the wiki with the new chapter", "promote the fanon", "проверь
главу по канону". Usually runs automatically after write-chapter; invoke directly only to
re-audit a past chapter or to check before publishing. Do NOT use for prose drafting — that's
write-chapter. Read-only by default; user promotes each new fact.
```

### refine-harness

```
Use when ONLY when the user asks to learn from past sessions and tune the drafting harness:
"refine", "learn from my edits", "tune the harness", "why do I keep fixing the same thing",
"обучись на моих правках", "улучши процесс". Diffs the user's edits against Claude's drafts
and proposes changes to voice cards, project preferences, drafting rules. Do NOT use when the
user wants to audit the wiki — that's wiki-lint. Do NOT use when the user wants to write or
reconcile — that's write-chapter / reconcile. Every refinement is ratified by the user.
```

### translate

```
Use when ONLY when the user asks to translate the fic from one language to another:
"translate chapter N", "translate the fic", "translate to English / Russian / <lang>",
"переведи главу", "переведи на английский". Cross-lingual, paragraph-aligned. Do NOT use
when the user wants monolingual prose cleanup ("fix clumsy phrasing", "почисти") — that's
naturalize. Keeps names and terms consistent across the whole series.
```

### wiki-init

```
Use when ONLY when the user is starting a brand-new fanfic project and there is no wiki yet:
"set up a story bible", "start a fanfic project", "init a canon wiki", "I have a book in
markdown and want to write fanfic", "create the wiki", "создай вики". Runs once at project
start. Do NOT use when the wiki already exists and the user wants to add source material —
that's ingest-source. Do NOT use when the user wants to audit an existing wiki — that's
wiki-lint.
```

### wiki-lint

```
Use when ONLY when the user wants a read-only health check of the wiki: "lint the wiki",
"check the story bible", "audit the wiki", "is my wiki healthy", "проверь вики", "аудит вики".
Reports tier violations, uncited claims, contradictions, thin voice cards, language drift,
orphan pages. Do NOT use when the user wants to add source material — that's ingest-source.
Do NOT use when the user wants to tune drafting rules from past edits — that's refine-harness.
Read-only — never writes back.
```

### write-chapter

```
Use when ONLY when the user asks to draft a new chapter or scene: "write chapter N", "draft
the next chapter", "write the scene where X", "write chapter 2 of book 3", "continue the
story", "напиши главу", "напиши сцену где…". Requires a chapter outline (run plan-chapters
first if missing). Do NOT use when the user wants to outline first — that's plan-chapters.
Do NOT use when the user wants to audit an existing chapter against canon — that's reconcile.
```

---

## 5. Proposed structural splits

Per Anthropic best-practices "Keep SKILL.md body under 500 lines for optimal performance".

| Skill | Current lines | Recommended split |
|---|---:|---|
| `plan-chapters` | 579 | Move per-check rubric + format examples to `references/conflict-checks.md`. Move series-expansion (book 2+) details to `references/series-expansion.md`. SKILL.md keeps the 7 rules inline (short) + 1-line links. |
| `write-chapter` | 446 | Move the canonical-check verification rubric to `references/canon-check.md`. Move the beat-sheet template to `references/scene-beats.md`. SKILL.md keeps the 3-phase flow + inputs + 1-line links. |
| `illustrate` | 445 | Move per-prompt pitfalls to `references/pitfalls.md` (already exists per README line 356 — verify it's referenced from SKILL.md). Move style-card template to `references/style-card.md`, character-card template to `references/character-card.md`. SKILL.md keeps the 3-phase overview. |
| `publish` | 332 | Already has `references/`. **Verify**: SKILL.md should only link, not duplicate platform-specific export details. Move per-platform details to `references/<platform>.md`. |
| `refine-harness` | 170 | Already has `references/`. **Verify** SKILL.md only links and that references are one level deep (Anthropic "Avoid deeply nested references" rule). |
| `naturalize` | 308 | Borderline. Don't split now; if "concept-speak in plans" guidance grows, split to `references/concept-speak.md`. |
| `translate` | 328 | Borderline. Don't split now; if a glossary workflow is added, split to `references/glossary.md`. |
| All others | <300 | No split. |

**One-level-deep rule:** SKILL.md → `references/*.md` only. No `references/foo.md` → `references/bar.md` chains. Current nested references (if any) to be flattened during the split pass.

---

## 6. Estimated token savings

This is a back-of-envelope. Real number depends on what loads per session.

- **Description tokens (always-loaded):** current ~7 700 chars total across 15 descriptions → ~1 925 tokens. New ~600 chars average × 15 = ~9 000 chars → ~2 250 tokens. **Slightly more bytes in descriptions** because of cross-deconfliction clauses — that's the explicit cost of maximum prescription. Net: +17% in the always-loaded zone, but with a much higher signal/noise ratio so the model picks correctly more often, which reduces wasted body loads downstream.
- **Body tokens (loaded only when triggered):** plan-chapters 39 KB → ~22 KB estimated (−45%), write-chapter 33 KB → ~20 KB (−40%), illustrate 30 KB → ~18 KB (−40%), publish 20 KB → ~13 KB (−35%). Total estimated body reduction: ~50 KB ≈ ~12 500 tokens saved per triggered skill.
- **Net effect:** ~12 K fewer tokens per chapter-drafting session (since 2–3 of these trigger in sequence), at the cost of ~500 more tokens in every system prompt. Worth it.

---

## 7. Open questions before I touch any files

1. **`reconcile` automatic vs manual** — confirmed: auto-invoked after `write-chapter`, but user can invoke manually too. The new description reflects that. Confirm wording is right.
2. **Russian triggers** — I've added Russian equivalents where they exist in current SKILL.md bodies. Are there user phrases I'm missing? Specifically for `brainstorm`, `publish`, `reconcile`, `translate`, `write-chapter`, `wiki-init` I had nothing to copy and guessed. **Please correct any of these.**
3. **`naturalize` boundary with `write-chapter`** — `naturalize` currently says "doesn't touch the author's jokes or the meaning". There's an edge: if the user wants meaning changes, is it `write-chapter` (redraft) or `naturalize` (tune)? I made `naturalize` clarify "monolingual prose rhythm only, not meaning" — confirm or correct.
4. **Skill names** — currently `cover`, `publish`, `translate` are nouns, not gerunds. Per Anthropic best practices, gerund form is recommended ("making covers", "publishing chapters", "translating chapters"). Should I rename? It changes frontmatter `name:` so it ripples to any cross-skill references. **Decision needed before edits.**

---

## 8. Suggested execution order

1. Get answers to the 4 questions above.
2. Rewrite all 15 descriptions in one pass.
3. Split `plan-chapters`, `write-chapter`, `illustrate`, `publish` SKILL.md bodies. Audit existing `references/` in `publish` and `refine-harness` for one-level-deep rule.
4. Re-measure byte counts. Write this report's "after" section.
5. Update README to mention the prescriptive description convention.

Each step ends with a diff you can review before the next starts.

---

## 9. Addendum — subagent-mode decision matrix

Added after session-log analysis (2026-10-18). Sources:
- `~/.claude/projects/-Users-geek-dev-fafic-yadro-dushi/67fd5195-a990-4125-992c-cd07ac34ec4a.jsonl` (S1, 32 min)
- `~/.claude/projects/-Users-geek-dev-fanfic-skills--claude-worktrees-unruffled-margulis-103ad4/9a8aec84-be43-45dd-b06c-23041ff66d3d.jsonl` (S2, 10 min)
- `~/.claude/projects/-Users-geek-dev-fanfic-skills--claude-worktrees-infallible-montalcini-2d1d1a/0fffc11d-8fec-47d8-85da-5dfbcb2d61e2.jsonl` (S3, 45 sec)

### Mode rules

**Inline** — skill runs in the main session. Use when:
- The user is likely to ask follow-up questions or iterate (write-chapter, develop-character, plan-chapters).
- The skill is itself an interactive interview (plan-story, brainstorm).
- The skill needs per-step user confirmation (publish — though this is borderline, see below).
- The conversation IS the output state.

**Subagent** — skill runs in a fresh-context subagent. Use when:
- The output is bounded (a structured table, a file, a URL).
- The user evaluates the output as a whole, not by iterating on it.
- Loss of context between subagent and main session does not break the user's workflow.

**Mixed** — parts run inline, parts in subagent. Use when:
- The skill has an interactive phase (style lock, character lock) that needs user approval, followed by an autonomous generation phase.

### Final mode assignments

| Skill | Mode | Reason | Natural persistent state |
|---|---|---|---|
| `brainstorm` | inline | Divergent riff with user | n/a — conversation |
| `plan-story` | inline | Interview loop | n/a — conversation |
| `plan-chapters` | inline | Q&A loop (9 questions observed in S1) | n/a — conversation |
| `write-chapter` | inline | User iterates on draft + asks "why" | n/a — conversation |
| `develop-character` | inline | User often iterates on profile | the profile file |
| `publish` | **subagent** | Verified across 24 publish runs in 23 sessions: 71% fire-and-forget, 17% brief acknowledgement, 0% mid-publish interruptions. 4% of runs had a printed text question (gate check) — handled by subagent internally. | publication log + platform URL |
| `illustrate` | mixed | Phase 1-2 inline (style + character lock), Phase 3 subagent (per-chapter prompt) | `plan/illustration/book-<NN>/ch<NN>.md` |
| `naturalize` | subagent | Sound eval vs original, short targeted follow-ups | cleaned chapter file + diff log |
| `translate` | subagent | Translation eval vs source | `translations/<chapter>.md` + `translations/glossary.md` |
| `reconcile` | subagent | Discrete accept/reject per row | `wiki/fanon/proposed/` + `drafts/continuity.md` row |
| `ingest-source` | subagent | One-shot read + write | `wiki/canon/` pages |
| `wiki-init` | subagent | One-time scaffolding | `wiki/` scaffold |
| `wiki-lint` | subagent | Read-only audit | `wiki/lint-reports/<date>.md` |
| `refine-harness` | subagent | Proposes, user ratifies | `plan/HARNESS.md` proposed-changes section |
| `cover` | subagent | One-shot, user judges by image | the image file |

### Revised token-savings estimate

**Verified publish workflow** (24 runs, 23 sessions): 71% fire-and-forget, 17% brief ack, 0% mid-run interruptions, 4% printed text question (handled internally). Confirms publish = subagent.

Per chapter lifecycle (write → reconcile → naturalize → translate → publish):

| Stage | Mode | Tokens added to main session |
|---|---|---|
| `write-chapter` | inline | ~6-10 K (canon context + draft + report) |
| `reconcile` | subagent | ~1 K (review table) instead of ~5-7 K |
| `naturalize` | subagent | ~1 K (cleaned text) instead of ~4-5 K |
| `translate` | subagent | ~1 K (translation) instead of ~6-8 K |
| `publish` | subagent | ~1 K (URL + log) instead of ~2 K |

**Original (over-aggressive) estimate:** 35 K → 6 K (5-6× reduction). **Incorrect** because it assumed write-chapter could go subagent.
**Revised:** ~22 K → ~5 K (4-5× reduction). Still substantial, primarily on the back-half of the lifecycle.

### Skill-body changes required for subagent mode

Each subagent-mode SKILL.md body needs:

1. **A `## Mode` indicator** at the top, just under the title (not in frontmatter, which is `name` + `description` only per spec):
   ```markdown
   ## Mode
   Subagent. Produces <one-line summary of the output>.
   ```

2. **A `## Persistent state` section** listing exactly what files / log entries / outputs the skill writes. This is the compressed output the main session remembers — no separate "session note" file.
   ```markdown
   ## Persistent state
   - `<path>` — <what it contains>
   - `<log entry>` — <what it records>
   ```

3. **A `## Inputs required` section** so the parent session knows what context to provide before spawning:
   ```markdown
   ## Inputs required
   - The chapter text at `<path>`
   - The current `wiki/canon/` (or just the relevant subset, named explicitly)
   - `plan/HARNESS.md` if it exists
   ```

4. **A `## Skip-if-loaded rule`** for inline-mode skills. Conditional on no ingest / edit / reconcile / publish since last read, to avoid stale-context bugs.

### Skip-if-loaded rule (for inline-mode skills)

Inline skills that load canon context should follow this pattern:

```markdown
## Skip-if-loaded
Before reading these files, check whether they were already loaded in the current session
and no ingest / edit / reconcile / publish has happened since:

- `wiki/canon/overview.md`
- `wiki/canon/forbidden.md`
- `wiki/canon/characters/<each relevant>.md`
- `wiki/canon/voices/<each with dialogue>.md`
- `wiki/canon/world/<each relevant>.md`
- `drafts/continuity.md`
- `CANON.md`

If all of them are in context and no `ingest-source`, `reconcile`, or `plan/HARNESS.md` edit
has happened since they were loaded, **do not re-read**. Re-using context is cheaper than
re-reading, and the staleness check is conservative.

If any of them is missing, or any of the staleness triggers fires, read fresh.
```

Estimated savings per chapter pipeline: ~3-5 K tokens (the wiki context re-read is the biggest single cost after the initial draft).

### Russian trigger gap

Initial pass on 3 sessions found zero Russian triggers → wrongly concluded Russian triggers in descriptions are decorative.

After comprehensive search across **78 main session jsonls (509 MB, 193,919 lines)** in `~/.claude/projects/-Users-geek-dev-fanfic-skills*` and `-Users-geek-dev-fafic-yadro-dushi`:

- **49 sessions contained real Russian trigger phrases.** 135 trigger events total.
- **`Skill` tool used exactly once** across 78 sessions — Claude loads SKILL.md via plain `Read` or `Bash cat` instead.
- **The mechanism is inference, not description matching.** Claude maps Russian intent to skill names via training, then navigates `.agents/skills/<name>/SKILL.md` by path. Description text was not visible to Claude in any analyzed turn.

| Russian phrase | Skill loaded | Reliability |
|---|---|---|
| `«опубликуй главу N»` | publish | **85%** |
| `«напиши главу N»` | write-chapter | **83%** |
| `«пиши»` (alone) | write-chapter | 22% (mostly conversational) |
| `«проверь»` | mostly nothing | 6% (fact-checking, not skill) |
| `«что если»`, `«придумай»`, `«идеи»`, `«проработай»` | brainstorm | **0%** ← real gap |
| `«переведи»`, `«обложка»`, `«почисти»`, `«составь план»` | n/a | User never actually types these |

**The real coverage gap is `brainstorm`.** User types `«что если»` and `«придумай»` 6+ times across the corpus; `brainstorm` never loads. The phrasing is too vague for reliable inference. **Adding Russian to its description would close this.**

**Current description coverage (Russian triggers):**

| Skill | Has Russian triggers in description? |
|---|---|
| `publish`, `cover`, `naturalize`, `develop-character`, `translate`, `plan-chapters` | ✅ yes |
| `write-chapter`, `brainstorm`, `reconcile`, `refine-harness`, `wiki-init`, `wiki-lint`, `plan-story`, `illustrate`, `ingest-source` | ❌ no |

### Revised Q2 decision

Add minimal Russian hints to the 9 skills that lack them, focused on phrases the user actually types. Specific additions:

| Skill | Add to description |
|---|---|
| `write-chapter` | `"напиши главу"`, `"напиши следующую главу"` |
| `brainstorm` | `"давай придумаем"`, `"идеи"`, `"что если"` (closes the 0% gap) |
| `reconcile` | `"сверь главу"`, `"проверь главу по канону"` (per Q1-B) |
| `plan-story` | `"давай придумаем фанфик"`, `"хочу написать фанфик про…"` |
| `refine-harness` | `"обучись на моих правках"`, `"улучши процесс"` |
| `wiki-init` | `"создай вики"` |
| `wiki-lint` | `"проверь вики"`, `"аудит вики"` |
| `illustrate` | `"иллюстрация к главе"` |
| `ingest-source` | `"добавь в канон"`, `"обработай эту главу"` |

Don't add Russian to skills that already have it (the evidence shows they work).

Don't add deep Russian to bodies — bodies load only after inference has already routed correctly, so marginal value is small.

**Total byte cost:** ~30 bytes × 9 skills ≈ 270 bytes. Negligible.

### Why this is "defensive" not "primary"

Adding Russian triggers to descriptions is **defensive against inference failure**, not the primary mechanism. The primary mechanism is the model's LLM inference. But:
- For short Russian phrases (`«напиши»`), inference is 83% reliable. Russian in description pushes this higher.
- For ambiguous Russian phrases (`«что если»`), inference is 0% reliable. Russian in description is the difference between triggering and not triggering.
- For already-clear phrases (`«опубликуй»`), Russian in description is redundant but doesn't hurt.

The descriptions help **most where inference is weakest**.

---

## 10. Updated audit status

| Question | Status |
|---|---|
| Q1-A: `reconcile` framing | ✅ settled — pipeline-first |
| Q1-B: `reconcile` trigger surface | ✅ settled — keep `«reconcile»`, `«reconcile chapter N»`, `«re-audit chapter N»`, add `«проверь главу по канону»`, `«сверь главу»`; drop the two pipeline-summary triggers |
| Q1-C: `refine-harness` cross-mention in reconcile | ✅ settled — keep it out; handoff is via prose in reconcile's report, not via description |
| Q-A (handoff-convention prose) | ✅ settled — yes, add to bodies |
| Q-B (path conventions in descriptions) | ✅ settled — yes, surface as secondary trigger |
| Subagent matrix | ✅ settled — 5 inline, 10 subagent, 1 mixed (publish moved to subagent after user confirmation) |
| Persistent-state approach | ✅ settled — each skill's existing output is its persistent state, no new universal file |
| Skip-if-loaded | ✅ settled — add to inline skills, with staleness check |
| Russian triggers | ✅ settled — add to 9 skills that lack them; ~270 bytes total cost |
| Q3-A: naturalize "no meaning change" rule | ✅ settled — strict, current body rule |
| Q3-B: naturalize on meaning-change passage | ✅ settled — flag-and-redirect, current body rule |
| Q3-C: write-chapter mention of naturalize | ✅ settled — silent; description stays focused |
| Q4: rename to gerunds | ✅ settled — keep current names (Option 2) |
