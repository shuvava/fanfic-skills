# Eval Plan — Prescriptive Description Convention (v0.23.0)

## Why this matters

Per superpowers' `writing-skills` (Iron Law: NO SKILL WITHOUT A FAILING TEST FIRST), a skill
rewrite isn't validated until there's an eval set that exercises the new descriptions. The
description rewrite and body splits in PR #29 are unvalidated changes — they may improve
description-selection accuracy, but we have no measurement.

The session-log evidence I used to write the descriptions (78 sessions, 24 publish runs, Russian
trigger study) tells me how the model currently behaves. It does not tell me whether the new
descriptions make it behave correctly.

## Eval design — TDD for skills

For each of the 15 skills, three scenarios:

### 1. Trigger test (positive)
- **Input:** a user message containing a known trigger phrase (English or Russian, drawn from the
  skill's description).
- **Expected:** the model loads `skills/<name>/SKILL.md` and follows it.
- **Failure mode:** the model loads a different skill, or loads none and improvises.

### 2. Cross-deconfliction test (negative)
- **Input:** a user message containing a phrase that overlaps with 2-3 skills in the description
  surface. E.g. *"fix this paragraph"* (naturalize vs write-chapter), *"open the wiki"* (wiki-init
  vs wiki-lint vs ingest-source), *"обложка"* (cover vs publish).
- **Expected:** the model picks the right skill AND articulates why it deferred the others (i.e.
  the "Do NOT use when X — that's <skill>" clauses are doing real work).
- **Failure mode:** the model picks the wrong skill, or picks right but can't explain the
  disambiguation.

### 3. Russian trigger test
- **Input:** a user message containing ONLY a Russian phrase from the skill's description (no
  English fallback).
- **Expected:** the model picks the right skill.
- **Failure mode:** the model misses the Russian trigger and falls back to inference — which may
  or may not be right (per the 78-session study, inference is unreliable for `brainstorm`/`проработай`,
  reliable for `напиши`).

**Total:** 15 × 3 = **45 scenarios**.

## Process — RED-GREEN-REFACTOR

### Phase 1: RED (baseline)
For each scenario:
- Run with the **OLD** descriptions (in git history at `c837418`, before PR #29).
- Document the model's choice and rationale verbatim.
- This is the "watch it fail" step — we need to see what fails WITHOUT our changes before we
  can attribute improvements TO our changes.

### Phase 2: GREEN (new descriptions)
For each scenario:
- Run with the **NEW** descriptions (current state, PR #29).
- Document the model's choice and rationale.
- Compare against baseline.

### Phase 3: REFACTOR (close loopholes)
For any scenario that still fails (or shows high variance across reps):
- Identify the loophole in the description (which trigger phrase is missing, which
  negative trigger is ambiguous, which cross-deconfliction clause was ignored).
- Patch the description.
- Re-run.

## Tooling — subagent dispatches

Each scenario runs in a **fresh-context subagent** with:
- System prompt: realistic context (a loaded harness with the 15 skills' descriptions in
  the system prompt, simulating the real environment).
- User message: the trigger phrase.
- No conversation history (fresh context — that's the point).
- Subagent's task: "pick the right skill, explain your choice, then either run it or report that
  the skill is not yet invoked."

**Per-rep cost:** ~1-2K tokens (system prompt = 15 descriptions ≈ 8.8K chars + scenario + subagent
  reasoning + report). Per-scenario: 5 reps × 1-2K = ~10K tokens.
**Total:** 45 scenarios × 5 reps × 1.5K = **~340K tokens** for the full eval.

## Micro-tests first, full pressure scenarios after

Per superpowers' `writing-skills` line 577, micro-tests verify wording first (cheap, 1-2 reps),
then full pressure scenarios confirm. For descriptions:

- **Micro-test (1 rep each):** run each scenario once. Document pass/fail.
- **Variance check (5 reps each):** re-run the failing scenarios 5 times. If the failure is
  consistent, the description has a real defect. If it varies (passes some, fails others), the
  wording isn't binding.

Estimated micro-test cost: ~45 × 1.5K = **~70K tokens**. Full variance check on failures: ~10
scenarios × 5 reps × 1.5K = **~75K tokens**. Total **~150K tokens** for the full eval.

## What we measure

For each scenario, capture:
1. **Skill picked** — did the model load the right SKILL.md? (binary pass/fail)
2. **Rationale** — did the model articulate the disambiguation correctly when applicable?
3. **Variance** — across 5 reps, how stable is the choice?

Pass criteria:
- ≥ 80% of scenarios pass on first run
- ≥ 95% of failures are fixable by a description patch
- No scenario that passed with the old descriptions regresses

## What we don't measure

- Whether the model produces the right **prose** when the skill runs (that's a per-skill eval,
  not a description eval).
- Token cost — measurable in real sessions but not in this synthetic eval.
- The user's subjective experience — that comes from real sessions, not evals.

## Scope decisions

Given ~150K tokens for the full eval:

**Option A — full eval (45 scenarios × micro-test, then variance on failures):**
~150K tokens, ~30 min of subagent dispatches. Comprehensive coverage.

**Option B — micro-tests only (45 scenarios × 1 rep):**
~70K tokens, ~15 min. Identifies obvious failures; misses variance.

**Option C — high-priority subset (10 most ambiguous skills × 3 scenarios × 1 rep):**
~30K tokens, ~5 min. Covers the cross-deconfliction riskiest cases
(brainstorm / write-chapter / naturalize / reconcile / publish / cover / plan-chapters / plan-story /
illustrate / develop-character) and skips the easier ones (wiki-init, wiki-lint, ingest-source,
refine-harness — these have weaker trigger collisions).

**Recommendation: Option A.** The full eval is the deliverable that justifies the rewrite. B is
insufficient — single-rep results overstate both pass and fail rates (per superpowers line 583).
C is too narrow — the cross-deconfliction claims in the descriptions need to be tested for every
adjacent pair.

## Deliverables

1. `reports/eval-results.md` — the 45-scenario eval with baseline vs. new-skill comparisons.
2. `reports/eval-scenarios.yaml` — the structured eval set, runnable.
3. Description patches (if any failures) as a follow-up PR.

## Recommended execution order

1. Build `eval-scenarios.yaml` — 45 scenarios, each with input, expected skill, expected
   rationale, severity (blocker / nice-to-have).
2. Run Phase 1 (baseline) on the OLD descriptions. Document failures.
3. Run Phase 2 (new descriptions) on the NEW descriptions. Compare.
4. For any regression or new failure, patch the description and re-run that scenario.
5. Write `eval-results.md` with the comparison table.

The eval can be re-run any time the descriptions change — it's a regression test for the
always-loaded discovery surface.
