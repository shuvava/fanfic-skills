# HANDOFF.md

Context for continuing work on the `fanfic-wiki` plugin. Written at the end of a claude.ai design
session, then revised at v0.4.0 once the design met a real book and parts of it turned out to be
wrong.

**Read this before changing anything.** The files encode *what* the plugin does; this records *why*,
including several decisions that look arbitrary until you know what they're defending against.

---

## What this is

A plugin that turns a source book into a canon wiki, plans a fanfic collaboratively against it, and
generates chapters that stay in-character and in-language. **Now measured against a real book — see
"What testing established" below before trusting any claim in this file.**

Eight skills, four human gates:

```
wiki-init      → structure + source-language detection
ingest-source  → canon wiki pages                     [tier: canon, immutable]
plan-story     → plan/STORY_INTENT.md                 [gate: grilling interview]
plan-chapters  → outline + conflict report            [gate: canon conflicts]
write-chapter  → beats → prose → canon check          [gate: beat review]
reconcile      → review inbox → fanon promotion       [gate: promotion review]
refine-harness → learn from edit diffs
wiki-lint      → health report
```

Shared rules live in `CONVENTIONS.md`. Every skill references it.

---

## Design decisions and their reasons

### 1. The canon/fanon tier wall

Four tiers: `canon` (extracted from `raw/`, **immutable**), `fanon-established` (invented, user-
ratified), `fanon-proposed`, `generated` (drafted prose). Promotion moves up only, by explicit user
action, and **never reaches canon**.

**Why:** a compiled wiki answers confidently by design. If generated prose writes back into the tier
the drafter reads as truth, chapter 7 treats chapter 3's inventions as source material, and each
chapter is conditioned on a more synthetic corpus than the last. Canon fidelity rots quietly. This is
the same self-consuming loop that degrades generative models trained on their own output, and the fan
communities solved the human version of it decades ago — it's why Wookieepedia splits Canon from
Legends and Memory Alpha quarantines Apocrypha.

**Do not "simplify" this by merging tiers.** It is the load-bearing constraint of the whole design.

### 2. Conflicts surface at planning time, not after drafting

`plan-chapters` lints the outline against canon before prose exists. `blocking` (contradicts canon or
`forbidden.md`) stops and asks one question: intentional AU divergence, or error?

**Why:** the outline is already structured facts, so checking it is cheap. Catching "she uses the
family name" at the beat stage costs one line; catching it after 3,000 words costs a scene. Intentional
divergences get recorded in `CANON.md` and stop being conflicts — AU and fix-it fic are legitimate
genres, and the system must distinguish deliberate divergence from accidental drift.

### 3. The user is the reward function

`refine-harness` learns from the diff between Claude's draft and what the user kept, but every
refinement is proposed and ratified, never applied.

**Why:** this was adapted from Karten et al., "Continual Harness" (arXiv:2605.09998, May 2026), whose
headline result is that the human can be removed from harness refinement entirely. **That part was
deliberately rejected.** Their agents play Pokémon, where ground truth exists — a milestone is reached
or it isn't. Prose has no such signal. A system refining against its own judgment of its own output
would drift confidently in whatever direction it already leaned. So the loop was kept and the human's
role inverted: they removed the human to prove it wasn't needed; here the human *is* the signal.

What was taken from the paper: refining prompt + skills + memory from past trajectory data, online,
within a run, drawing on the whole history rather than the last episode.

### 4. Source language is preserved by default

Wiki pages, plans, and prose are produced in the source's language. Conversation with the user happens
in the user's language. **Verbatim quotations are never translated, under any override.**

**Why:** voice cards are built from actual canon dialogue and measure register, rhythm, archaism,
syntax, and address forms (ты/вы, tu/vous, 敬語). None of those survive translation. A translated voice
card describes the translator, not the character. `wiki-lint` treats a translated quotation as
`critical` for this reason.

Three settings in `CANON.md` (`source_language`, `wiki_language`, `output_language`) allow per-layer
override, and Claude flags the lossy step when they diverge.

### 5. Snapshots exist so refinement has a baseline

`write-chapter` writes `drafts/snapshots/ch<NN>-v0.md` — an untouched copy of the first draft, frozen
once the user edits.

**Why:** without it there is no way to diff what Claude wrote against what the user kept, and
`refine-harness` has nothing to learn from. `wiki-lint` flags chapters missing a snapshot.

### 6. The harness is project-local

Refinements go to `plan/HARNESS.md`, `CANON.md`, or fanon voice notes — never into the plugin's own
SKILL.md files.

**Why:** one book's habits must not leak into the next. Precedence is `CANON.md` > `HARNESS.md` >
plugin defaults, and a harness rule may never override a language setting, a tier rule, or a gate — it
tunes *how* a stage works, never *whether* it runs.

### 7. Refinement prunes as well as adds

Every `refine-harness` run proposes removals. Proposals need three instances across two chapters, with
citations, capped at five per run.

**Why:** an accumulating harness is the real failure mode. The marginal rule is always the weakest, and
a rule set nobody reads is worse than none.

### 8. Voice extraction is verbatim, with an inversion step

Voice cards store at least five actual canon lines, then a "would never say" table built by rewriting
those lines wrong and articulating why.

**Why:** knowing what a character wouldn't say is what prevents drift at drafting time. Paraphrased
voice notes produce generic prose. This came out of researching what pro novelists, TV showrunners,
and experienced fanfic writers independently converge on — the `## Would never do` section on
character pages is the same idea and was consistently named the highest-value, most-skipped item.

### 9. Planning stops at four layers

`plan-chapters` expands to paragraph → arc synopsis → chapter list → scene list. Beat decomposition
happens in `write-chapter`, one chapter at a time.

**Why:** beating out forty scenes in advance is work thrown away when chapter 3 changes. Randy
Ingermanson dropped his own Snowflake step 9 for the same reason.

### 10. Style is recorded as counts, because adjectives cannot be checked

`overview.md` carries a `## Style fingerprint` table of measured values and a
`## Non-standard orthography` section listing every departure from the standard with its frequency.
`scripts/style_fingerprint.py` produces both and checks drafts against them.

**Why:** this was added in v0.4.0 after measurement, not by design. See the next section.

---

## What testing established (v0.4.0)

The plugin was run against a real Russian novel: six chapters ingested, two held out and generated,
output compared against what the author actually wrote. Full write-up lives outside this repo in the
test project's `results/JOURNAL.md`; the load-bearing conclusions are here.

**The central finding: recorded transfers, unrecorded is lost.**

Raw source text in a context window teaches style implicitly — a model that sees `какой то` a hundred
times copies it. **The wiki summarises, and summarising is what strips a fingerprint out.** With two
chapters ingested (raw text still in context) generated prose scored 1.00 on hyphen fidelity; with six
chapters ingested (wiki large, raw text pushed out) it scored 0.00 and wrote standard Russian
throughout. *The plugin got worse as it got more of what it asks for.*

Worse: a control with no plugin at all, the source simply pasted into the prompt, beat the v0.3.0
pipeline on every style axis at 3% of the cost. Recording the fingerprint explicitly fixed this —
generated chapters now score below the author's own chapter-to-chapter variation — but the lesson
generalises past style. **Anything the wiki does not write down, the pipeline loses.**

Confirmed three times independently: orthography (the hyphen rule), punctuation density (ellipsis),
and comic delivery. On that last one, v0.3.0 reproduced the narrator's ironic scare-quoting to within
4% — because `overview.md` happened to record that convention with examples — while dropping his
exclamations by 92% and stacked `!..` marks by 87%, which it recorded nowhere. Structurally funny,
tonally flat.

**Design decisions that survived contact:** the tier wall held; honest silence held under real
pressure (voice cards repeatedly wrote *«Не установлено — недостаточно материала»* rather than
inventing); extraction quality was high and correctly cited throughout.

## What a real reader established (v0.5.0 → v0.6.0)

The first three chapters of a continuation, drafted with v0.5.0 on the same Russian series, were read
by **the source's own author**. Every chapter passed the style fingerprint. His verdict still landed on
three defects the pipeline had no check for:

1. **A re-staged scene.** «Экзамен и вступительный экзамен прямо один в один.» The beat card had told
   the drafter to fill the exam's format from the canon entrance exam — the bored examiner, the sheets,
   the "right answers", the narrator noticing the windows. Measured afterwards, the chapter shared
   **0%** of its 4-word sequences with the canon exam. The copying was of the scene's *shape*.
2. **Collage.** «Программа достала куски текста из разных частей прошлых книг и скомпоновала их.»
   `Canon deps` were being used as ingredients, not constraints.
3. **No plot.** «Сюжет без сюжета.» Three setup chapters in a row — cramming, exam, conversation —
   with the inciting event planned for much later.

**The lesson generalises the earlier one.** Recorded transfers, unrecorded is lost — and the same holds
for *what a scene must not be*. Style had counts; scene novelty and plot motion had nothing, so they
were lost. v0.6.0 records them: `Precedent` / `What is new` / `Event` on the beat card with a swap
test, "canon is constraints, not ingredients" in drafting, and event / early-start / fold checks in
`plan-chapters`. Lexical overlap is the wrong instrument — it read 0% on the scene the author called
identical — so the checks are structural and read by the model, not a script.

**What the author valued:** finding inconsistencies and digging forgotten details out of earlier
books — the wiki and the conflict lint, not the prose.

**Author statements are now a source class** (`CONVENTIONS.md` §2): recorded as `fanon-proposed` with
`[author: ...]`, strongest recommendation in `brainstorm`/`plan-story`, never canon.

None of the v0.6.0 checks has been validated yet — the chapters that prompted them are the test.

## Characters as people, not scenery (v0.7.0)

The same user, rebuilding the book 1 plan, named the next failure before any chapter showed it:
secondary characters risk becoming **scenery for the protagonist**. The pipeline recorded how a
character *sounds* (voice cards) and what they *would never do*, but nothing required a character to
*want* anything of their own — so nothing did.

v0.7.0 adds `develop-character` and a depth threshold (`CONVENTIONS.md` §11): a character with a line,
two or more scenes, or agency in a scene gets a profile — own story, want / need / wound, stakes not
routed through the protagonist, off-page life, shift, reveal schedule — and a **cardboard check** run
against the scene list, not the profile. Missing profile: `warning` in `plan-chapters`, `blocking` in
`write-chapter`. Untested at the time of writing; the book 1 cast is its first run.

---

## Known gaps / possible next work

- **Plot fidelity is unsolved.** Style is now inside the author's band; content is not. Generated
  chapters score at or below what a *random wrong chapter of the same novel* scores against the
  target, even when handed a synopsis of the real events. One candidate fix — requiring every
  scene-card character to be named in narration — moved entity overlap from 0.0 to 0.40 and was
  discarded by a metric bug. It has not been re-tested. A real reader has since confirmed the gap from the other side: chapters inside
  the style band read as «сюжет без сюжета» and as a re-staged canon scene (see above).
- **Validated on one book.** One corpus, one author, one language, n=1 per condition. Nothing here
  should be trusted to generalise until it is run against a second source.
- **Entity resolution is naive.** Character name matching across aliases, epithets, patronymics, and
  case forms is left to the model. This is now the *suspected cause* of the plot-fidelity gap rather
  than a theoretical concern.
- **No git integration.** The wiki benefits enormously from being versioned (diff and revert a bad
  ingest), but nothing automates it. `wiki-init` only suggests `git init`.
- **`edit_rate` is unvalidated.** It's a cost proxy, not a quality measure — a chapter the user loved
  and polished heavily scores worse than one they shrugged at. `refine-harness` is instructed to say
  so plainly if the metric isn't falling rather than invent reasons it's working. Whether it correlates
  with anything useful is untested. `reconcile` and `refine-harness` remain **entirely untested** —
  both need real user edits, which an automated run cannot supply.
- **`ingest-source` deliberately ignores `HARNESS.md`** — canon extraction shouldn't be shaped by
  stylistic preferences. Keep it that way.
- **An ingest stage can fail silently**, leaving a wiki with a chapter missing while every later stage
  runs happily and produces plausible output. Nothing in the plugin detects this; the test harness had
  to. Worth surfacing in `wiki-lint`.

---

## Working agreements from the session

- Research before building. Each major addition (extraction schema, planning pipeline, refinement loop)
  followed a research pass rather than being invented.
- Skills are instructions, not code. They tell Claude what to do and, importantly, what *not* to do —
  most rules in these files are prohibitions, and the prohibitions are the valuable part.
- Prefer the narrowest target. Voice note before project preference before harness rule.
- Honest silence over confident filler. "Not established in ingested sources" is a correct entry;
  invented backstory is worse than none, because every downstream stage treats wiki pages as fact.
