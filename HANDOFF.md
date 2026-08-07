# HANDOFF.md

Context for continuing work on the `fanfic-wiki` plugin. Written at the end of a claude.ai design
session; the plugin itself is complete at v0.3.0.

**Read this before changing anything.** The files encode *what* the plugin does; this records *why*,
including several decisions that look arbitrary until you know what they're defending against.

---

## What this is

A plugin that turns a source book into a canon wiki, plans a fanfic collaboratively against it, and
generates chapters that stay in-character and in-language.

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

---

## Known gaps / possible next work

- **No git integration.** The wiki benefits enormously from being versioned (diff and revert a bad
  ingest), but nothing automates it. `wiki-init` only suggests `git init`.
- **Entity resolution is naive.** Character name matching across aliases, epithets, patronymics, and
  case forms is left to the model. Fandoms with heavy epithet use will strain it.
- **`edit_rate` is unvalidated.** It's a cost proxy, not a quality measure — a chapter the user loved
  and polished heavily scores worse than one they shrugged at. `refine-harness` is instructed to say
  so plainly if the metric isn't falling rather than invent reasons it's working. Whether it correlates
  with anything useful is untested.
- **Never run end-to-end.** The plugin was designed but not exercised against a real book. Expect the
  first real ingest to reveal template mismatches.
- **`ingest-source` deliberately ignores `HARNESS.md`** — canon extraction shouldn't be shaped by
  stylistic preferences. Keep it that way.

---

## Working agreements from the session

- Research before building. Each major addition (extraction schema, planning pipeline, refinement loop)
  followed a research pass rather than being invented.
- Skills are instructions, not code. They tell Claude what to do and, importantly, what *not* to do —
  most rules in these files are prohibitions, and the prohibitions are the valuable part.
- Prefer the narrowest target. Voice note before project preference before harness rule.
- Honest silence over confident filler. "Not established in ingested sources" is a correct entry;
  invented backstory is worse than none, because every downstream stage treats wiki pages as fact.
