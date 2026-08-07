# Extraction Checklist & Page Templates

Field-by-field capture list. All page bodies in `wiki_language`; all quotations untranslated.

---

## 1. Character page — `wiki/canon/characters/<name>.md`

```markdown
---
tier: canon
type: character
name: <name as spelled in source>
aliases: [<all forms the source uses>]
first_seen: <src>
last_updated: <YYYY-MM-DD>
sources: <n>
---

# <Name>

## Identity
Full name, aliases, nicknames — **and who uses which form**. In languages with case systems,
diminutives, or honorifics, record which characters use which register toward this person. That
mapping is relationship data.

## Physical
Eye color, hair, height, build, scars, distinguishing features, wardrobe signatures.
(Lowest-value section; do not over-invest here.)

## Personality
Strengths · flaws · fears · values · temperament · quirks.

## Wants vs. Needs
- **External want:** what they pursue
- **Internal need:** what they actually lack
- **Defining contradiction:** the tension that generates their drama

## Backstory
Only what canon establishes. Empty is fine.

## Relationships
| With | Nature | How they behave differently | Address form used |
|---|---|---|---|

## Arc state
Where they stand at the end of ingested canon.

## Mannerisms
- Physical: gestures, posture, expressions
- Verbal: catchphrases, filler words, speech habits
- Behavioral: rituals, habits, tells under stress

## Would never do
The internal moral code — the lines they hold. Each with citation.
**Highest-value section. Populate it aggressively.**

## Contradictions
Claims from different sources that do not reconcile. Keep both.

## Sources
```

**For situations canon never showed:** do not invent. Note the closest analogous canon situation and
label the extrapolation `(inferred)`.

---

## 2. Voice card — `wiki/canon/voices/<name>.md`

```markdown
---
tier: canon
type: voice
name: <Name>
language: <source language>
lines_captured: <n>
---

# Voice: <Name>

## Verbatim canon lines
Minimum five. **Exact. Untranslated. Cited.** The spine of the card.

1. «<line exactly as in raw/>» [src: ...]
2. ...

## Vocabulary
- Register: <formal / casual / clipped / ornate>
- Average word/syllable length:
- Archaic or unusual words used:
- Words conspicuously absent:

## Language-specific markers
Populate whichever the source language has:
- **Address forms** — ты/вы, tu/vous, du/Sie, 敬語 level; who gets which, and when it shifts
- **Grammatical gender** in self-reference and in how others refer to them
- **Diminutives / augmentatives** — which they use, toward whom
- **Honorifics, titles, particles**
- **Verb aspect / tense habits** where the language marks them meaningfully
- **Dialect or regional markers** — note; never phonetically transcribe in generated prose
- **Code-switching between languages**, if the source has it

## Cultural touchpoints
References, slang, era markers, how in or out of sync with peers.

## Rhythm and syntax
Sentence length distribution. Staccato vs. flowing. Fragments. Subordinate clause habits.
Word-order habits where the language permits variation.

## Verbal tics
Maximum three.

## Code-switching (interpersonal)
| Speaking to | How the voice changes |
|---|---|

## Would never say
| Canon line | Wrong rewrite (same language) | Why they wouldn't |
|---|---|---|

## Sources
```

**The eight-step extraction method:**
1. Pull five-plus representative canon lines, verbatim, in the source language.
2. Read them aloud; note what they sound like.
3. Measure word and syllable length; count long words.
4. Flag archaic words, register markers, and cultural references.
5. Rewrite each line differently *in the same language* and articulate why the character wouldn't say
   it that way.
6. Find similar-register synonyms. If the character uses no complex words, ask why.
7. Recontextualize: what if said to a different character, or while scared, hurt, overjoyed, sick?
8. The resulting "would never say" table is what prevents drift at drafting time.

**Why translation destroys this:** register, rhythm, archaism, syntax, and address forms are the
substance of a voice card. None survive translation. A translated card describes the translator.

---

## 3. World page — `wiki/canon/world/<topic>.md`

```markdown
---
tier: canon
type: world
topic: <Topic>
---

# <Topic>

## The rule
What canon establishes.

## Limits and costs
What it cannot do. What it costs. What it breaks.
**A rule with no recorded limit is a rule the writer can cheat with.**

## How canon has used it
Instances, cited.

## Open questions
What canon has not established — listed explicitly so planning knows not to assume.

## Sources
```

Also capture across world pages: geography and travel distances · culture, customs, religion,
politics, hierarchies · history and key events · daily-life texture (food, clothing, currency, jobs,
technology level) · sensory detail · **naming conventions in the source language** (patronymics,
surnames, place-name morphology) so invented names fit.

---

## 4. Plot pages

**`wiki/canon/plot/<source>.md`** — summary · events in order · threads opened · threads closed ·
foreshadowing planted and unpaid · sources.

**`wiki/canon/plot/threads.md`** — the ledger:

| Thread | Status | First seen | Last seen | Notes |
|---|---|---|---|---|

Status: `open` / `ongoing` / `paid` / `abandoned`. Unpaid foreshadowing is the most valuable content
here — it is where a continuation earns its keep.

**`wiki/canon/plot/timeline.md`** — chronological events, in-world dates, ages, milestones,
relationship state changes.

---

## 5. Overview — `wiki/canon/overview.md`

- Premise, one sentence
- Themes; motifs and symbols
- Tone words (narrator's attitude) recorded **separately** from atmosphere (the reader's feeling)
- **POV person** and whose head(s); **tense**; narrative distance and deep-POV conventions
- Chapter and scene length; how chapters open and close; cliffhanger habits
- **Style and orthographic conventions** — invented name spellings, capitalization, dialogue
  punctuation as the source language uses it (guillemets, em-dashes, quotation marks), how thoughts,
  letters, and dreams are formatted

---

## 6. Forbidden — `wiki/canon/forbidden.md`

```markdown
# <heading in wiki_language>

- <constraint> — <reason> [src: ...]
```

Three entries on day one is fine. Value comes from it growing, not from being complete at the start.

---

## Anti-patterns

- **Filling every field.** Bibles fail when profiles become biographies of backstory nobody uses.
- **Paraphrasing or translating dialogue.** Produces generic prose. Verbatim or nothing.
- **Silently resolving contradictions.** Log both.
- **Confident synthesis from thin evidence.** If two sentences support a claim, say so.
