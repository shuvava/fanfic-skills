# CANON.md Template

Write to project root during init. This is the schema layer — what makes Claude a disciplined
canon-keeper rather than a generic chatbot. Fill the `<>` placeholders.

---

```markdown
---
title: <title>
author: <author>
source_language: <ISO 639-1>
wiki_language: <ISO 639-1>
output_language: <ISO 639-1>
ingest_granularity: <per-chapter | per-arc | whole-book>
---

# CANON.md — Project Schema

## Language

All wiki pages, plans, and generated prose are produced in `wiki_language` / `output_language`.
Verbatim quotations from `raw/` are **never translated**, regardless of other settings.
Conversation with the user happens in whatever language the user is using.

`raw/` is never edited and never translated.

## Layers and tiers

| Tier | Location | Mutable |
|---|---|---|
| `canon` | `wiki/canon/` | Never — read-only after ingest |
| `fanon-established` | `wiki/fanon/` | Yes, by user ratification |
| `fanon-proposed` | `wiki/fanon/proposed/` | Yes |
| `generated` | `wiki/drafts/` | Yes |

Promotion moves up only, only by explicit user action, and never reaches `canon`.

## The prime directive

Every claim carries `[src: ...]` (canon), `[fanon: ...]` (invented), or `(inferred)`. A claim with
none of these is an error, not a fact.

**If the wiki has no confident answer, say so.** Never synthesize from thin evidence; never file such
an answer back. A confident fabrication that gets filed becomes a source.

Contradictions are logged under a page's `## Contradictions` heading, never silently resolved.

## Pipeline

```
ingest-source   → canon wiki pages
plan-story      → plan/STORY_INTENT.md          [grilling gate]
plan-chapters   → plan/outline.md + conflicts   [conflict gate]
write-chapter   → plan/beats/ + drafts/         [beat gate]
reconcile       → fanon promotion               [review gate]
wiki-lint       → health report
```

## Divergences

Intentional departures from canon, recorded so they are never mistaken for errors.

| Divergence | Reason | Decided |
|---|---|---|

## Preferences

<chapter length, ships, rating, POV, AU rules — recorded as they emerge>

## Log format

`## [YYYY-MM-DD] <op> | <subject>` — parseable with `grep "^## \[" log.md | tail -5`
```

---

## Page templates

All page bodies are written in `wiki_language`. Section headings may be kept in English for
machine-parseability if the user prefers — ask once during init and record the choice.

### `wiki/canon/characters/<name>.md`
```yaml
---
tier: canon
type: character
name: <name in source language>
first_seen: <src>
sources: <n>
---
```
Sections: Identity · Physical · Personality · Wants vs. Needs · Backstory · Relationships ·
Arc state · Mannerisms · **Would never do** · Contradictions · Sources

### `wiki/canon/voices/<name>.md`
```yaml
---
tier: canon
type: voice
name: <name>
language: <source language>
lines_captured: <n>
---
```
Sections: Verbatim canon lines (≥5, **untranslated**) · Vocabulary · Cultural touchpoints ·
Rhythm and syntax · Verbal tics (max 3) · Code-switching · **Would never say** · Sources

### `wiki/canon/world/<topic>.md`
Sections: The rule · **Limits and costs** · How canon has used it · Open questions · Sources

### `wiki/fanon/<...>.md`
Same shapes, but `tier: fanon-established`, `[fanon: ...]` citations, and a `## Ratified` field
recording when and by what decision the user approved it.
