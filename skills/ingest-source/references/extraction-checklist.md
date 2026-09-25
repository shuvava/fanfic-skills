# Extraction Checklist & Page Templates

Field-by-field capture list. All page bodies in `wiki_language`; all quotations untranslated.

---

## 1. Character page — `wiki/canon/characters/<name>.md`

**Required headings — the exact set, in this order, on every character page.** `wiki-lint` checks
for them by name. A heading you have nothing for gets `не установлено` beneath it, not deletion:

`## Identity` · `## Physical` · `## Personality` · `## Wants vs. Needs` · `## Backstory` ·
`## Relationships` · `## Arc state` · `## Mannerisms` · `## Would never do` · `## Contradictions` ·
`## Sources`

Extra headings beyond this set are allowed — a composite page needs its roster table, a character
may earn a page-specific section. What is not allowed is dropping one of the required headings or
renaming it away. Do not rename, merge, or substitute. A page that reorganizes these into bespoke
sections
(`## Личность/способности`, `## Dialogue`) loses whichever detail had no home in the improvised
shape — and `## Mannerisms` is the one that disappears, every time, because gestures and tells feel
like flavor next to plot facts.

**Granularity:** one page per character once canon gives them three or more facts. Below that they
may live as a row in a composite page (a family, a squad). See `../SKILL.md` §1 — the composite page
has no per-character `## Mannerisms`, so a character who outgrows a row and stays in one silently
loses everything the row has no column for.

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
The internal moral code — the lines they hold **under pressure**. Each with citation.
**Highest-value section. Populate it aggressively — but only with refusals.**
An unvoiced discomfort is Personality, not a held line; `plan-chapters` reads every row here as a
hard behavioral constraint, so a soft inference here is worse than a thin section.

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

Quote as a blockquote rather than wrapping the line in quotation marks. Wrapping imports punctuation
the source may not use, and the drafter reads these lines as the model for dialogue — it will copy
whatever marks it sees around them.

1. > <line exactly as in raw/, including the source's own dialogue marker>
   [src: ...]
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

## Mechanism
For social, political, and economic rules: **why** the rule produces the effect canon shows. Record
the cause, not only the outcome — an outcome can be staged anywhere, a mechanism says where it can
and cannot happen. Omit this heading only for rules canon states without explanation.

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

### 3a. Geography — `wiki/canon/world/<geography>.md` (derived)

```markdown
---
tier: canon
type: world
topic: <Geography and space>
derived: true
sources_ingested: [...]
---

# <Geography and space>

**Derived page.** Assembled from the topic pages; adds nothing to them. Every row carries a
citation or says `not established`. **An empty cell is a fact about the wiki, not about the
world** — never fill one with a plausible distance.

## Relation sketch
<a rough ASCII or mermaid diagram of what borders, contains, or lies beyond what>

## Places
| Place | Type | Relation to others | Distance / travel time | Source |

## Placement rules
The world's own spatial law — what may be built where, who may live how far from what.

## Units of measure
Which units of distance and time canon has actually named. If none: say so, and forbid
inventing leagues, miles, hours, or weekday names in prose.

## Gaps that would break world logic
Numbered. Each one a question planning must settle before a scene depends on it.

## Sources
```

### 3b. Constraint ledger — `wiki/canon/world/constraints.md` (derived)

```markdown
---
tier: canon
type: world
topic: <Constraint ledger>
derived: true
sources_ingested: [...]
---

# <Constraint ledger>

**Derived page.** One row per rule, aggregated from every world page. `plan-chapters` reads
this first: an outline can be checked against one table, and will not be checked against eight
prose pages.

## Hard constraints
| # | Rule | Limit / cost | Source |

## What canon does NOT establish
The silences, listed. Absence of a rule reads as permission to a drafting model — no magic
shown, no other creatures in frame, no economy. Anything here needs `reconcile` before a plot
leans on it.

## How to use this
Which severity a violation of each section earns, and the instruction to rebuild after each
ingest.

## Sources
```

Both derived pages are **regenerated, never hand-edited**. Rebuild them at the end of every ingest so
they cannot drift from the pages they summarize.

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

### The style fingerprint — counted, not described

A drafter cannot act on an adjective. "Uses ellipsis heavily" is satisfied by one ellipsis per
paragraph and by five; a chapter written against that note came out at a quarter of the source's
density and still matched the note. Record a table of **counts and literal examples**, so the
convention is checkable rather than agreeable:

```markdown
## Style fingerprint
| Feature | Source value | Literal example |
|---|---|---|
| Chapter length | ~1200 слов | — |
| Ellipsis | ~21 на 1000 слов | `Ну... Кажется... Это был не сон...` |
| Dialogue marker | `\- ` в начале строки, 99% реплик | `\- Привет, Анна.` |
| Guillemets «» | не используются (0) | — |
| Paragraph length | 1–3 предложения | — |
```

Count from the actual text — including at least chapter length in words, the frequency of every
punctuation habit that reads as a tic, and the exact literal form of the dialogue marker.
`write-chapter` is instructed to reproduce these numbers, and `wiki-lint` checks them.

### Comic register — the device *and* the delivery

If the source is funny, record **how**, concretely enough to reproduce. Humour is the first thing to
go flat in a continuation, and it goes flat in a specific, diagnosable way: the joke structure
survives and the delivery does not.

Measured on a real corpus, a generated chapter reproduced the narrator's ironic scare-quoting at 10.4
per 1000 words against the author's 10.9 — because `overview.md` had recorded that convention with
examples. The same chapter dropped exclamations by 92% and stacked terminal marks (`!..`, `?..`) by
87%, because nothing recorded those. The prose came out composed and dry where the source sputters.

```markdown
## Comic register
- **Source of humour:** ирония рассказчика к самому себе и к обстановке, не остроты персонажей
  [src: raw/ch01.md#p3, p21].
- **Signature device:** кавычки для иронической дистанции — `"сценария"`, `"спасение"`,
  `"ловушкой"`. 10 на 1000 слов [src: raw/ch01.md#p21].
- **Delivery markers:** восклицания 11.8 на 1000 слов; составные знаки `!..` `?..` 7.7 на 1000 слов;
  многоточие 20.9 на 1000 слов. **Это и есть звук голоса — без них шутка остаётся, а голос уходит.**
- **Never:** отточенные реплики-панчлайны. Юмор рождается в ремарках повествователя, а не в
  диалоге [src: ...].
```

The last line matters as much as the counts. Record where the humour *lives* — narrator's asides,
character wit, situational absurdity, understatement — because a drafter that relocates it writes
jokes the source would never make.

### Non-standard orthography — the section a model will silently repair

**Look specifically for places where the source departs from standard spelling or punctuation, and
record the deviation as a rule with its count.** This is the highest-risk item on the page: a model
drafting a continuation will "correct" the author back to the standard without ever noticing it did,
and the result reads subtly like a different writer.

Hunt for at least: hyphenation the standard requires and the author omits (or vice versa), spacing
around dashes and ellipses, apostrophes and quotation marks, capitalization of invented terms,
inconsistent transliterations, and any spelling the author repeats often enough to be deliberate.

```markdown
## Non-standard orthography
- Постфиксы -то/-нибудь пишутся БЕЗ дефиса: `какой то`, `кто то`, `что то`
  (1688 раз без дефиса против 5 с дефисом) [src: raw/ch01.md#p3, ch02.md#p17].
  **Это авторская норма. Не «исправлять».**
```

Write the count. A rule recorded with its frequency survives the next stage; a rule recorded as a
remark does not.

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
