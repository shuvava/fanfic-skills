# Synopsis & Annotation — Reference Material

This file holds the synopsis-check table, the synopsis writing rules, and the annotation rules. The body of `plan-chapters` references these by section.

## Synopsis Check — Layers 1–2

Before showing Layer 2, fill in the fields a publisher's synopsis form asks for, one line each, from Layers 1–2 alone. Treat the form as a test: a field you cannot fill from the layers is a hole in the story, not in the form, and here it costs one question.

| Field | Filled when | Typical hole |
|---|---|---|
| Setting | place, time and the circumstances the conflict depends on | rarely fails — canon supplies it |
| Protagonist | who, what they want, what in them stands in the way | no want: the hero only reacts, all book |
| Antagonist | a person, or opposing circumstances named concretely ("the rule that…", not "obstacles") | complications that share no source, so nothing pushes back twice |
| Inciting event | the event that makes the central question urgent | the "book starts early" check in the body |
| Climax | a scene on the page where the central conflict is decided by what the protagonist does | a result reported instead of a scene where it is decided |
| Twist | a reversal the reader did not expect that follows from something planted earlier — name where | none, or one with nothing planted: a coincidence |
| Resolution | what differs from the start state, for the protagonist and for the central conflict | the ending restates the start |
| Main intrigue | the one question the reader carries across the book; answered here or handed to the next rung | a list of subplots and no single question |

**Before calling a field a hole, read the protagonist's profile** in `wiki/fanon/proposed/characters/`. Its ratified shift section says where the change happens and what kind of change it is. Layer 2 may give that scene one clause. On a real run, a check made from the layers alone recommended a new scene for a change the profile had already placed, and the user had to be asked again. Where the profile and the intent describe the change differently, that mismatch is the finding. Fix the intent's wording; do not add a scene.

"Circumstances" as antagonist and "no twist" are legitimate answers when they are chosen. Record them as choices. In a series, a main intrigue handed forward must exist in the next rung of `SERIES_ARC.md` or as a seed there; otherwise the book ends on a question nobody plans to answer.

Show the filled table with Layer 2. A field left empty is a question for the user, like a placeholder.

## Annotation — what sells the premise

The annotation is the first text a reader sees, before any chapter. It goes up to the inciting event and no further. The climax, the twist and the ending never appear in it.

- **Check it against the reveal section of every character profile it mentions.** It is read before chapter 1, so anything scheduled for a later reveal is out.
- **Give a situation and a question, not a list of themes.** "A story about friendship and betrayal" is concept-speak, and every other book's annotation says the same thing.
- **Match the book's voice.** A first-person book often gets a first-person annotation. The voice may be the narrator's; the words must still be ones a stranger understands.
- **Keep it short.** A few hundred to a thousand characters. The platform's limit is in its `publish` adapter (`references/platforms/<platform>.md`).

## Synopsis — what retells the whole book

The synopsis retells the whole book, ending included, to someone who has never opened the series. Write it the way a person retells a book to a friend, not the way the outline is written. On a real run a synopsis assembled from outline rows was rejected whole ("not human language", "much worse than the example"), though every fact in it was right. `synopsis_check.py` found that half its sentences contained a five-word run copied from the outline.

What the good example the user supplied did, and the rejected one did not:

- **Tell it fresh, from the events.** Take from the outline *what happens and why*, then close it and write your own sentences. The outline's phrasing is shorthand for people who already know the story: paradox closers («получил допуск — и не владеет ничем, включая собственное имя»), a scene's meaning in place of the scene, a verdict at the end of every paragraph. In a synopsis these read as riddles.
- **One thread, told in steps.** Each paragraph is one step of the protagonist's story: situation → problem → what they try → what it costs → what changes. Subplots appear only where they hit that thread. Never "Meanwhile, in parallel…" — that is the outline's line structure showing through.
- **Few names.** Name the protagonist, the antagonist and the two or three people who change the plot, five or six in total. Everyone else is "a classmate", "two outcasts nobody else would take", "his brothers". A fight is told by its outcome and the protagonist's part in it, not a roll call of who struck what.
- **Explain every world word at first use, or drop it.** Before writing, list the words a stranger would not know: world terms, ranks, game jargon, creature and place names. Each one is explained in half a sentence where it first appears («ядро — источник силы внутри человека»), or replaced by a plain description («хищные цветы у воды»), or cut.
- **Name motives and feelings plainly.** «Она хочет, чтобы глава клуба её заметил», «он злится и решает отомстить». A reader follows people, not mechanisms.
- **Plain sentences.** Subject, verb, what happened, joined by «но», «поэтому», «тогда». Aim at 15–20 words; none over 30. No semicolon chains, no colon lists, no dash that ends a paragraph on an aphorism.
- **Present tense, third person.** No project apparatus: thread codes, block and chapter numbers, tiers, `[src:]`. One to two pages.

### Invented example, «Хроники Севера»

Assembled from the outline, rejected:
> Анна получает место в совете, которого добивалась, — и не владеет в нём ничем, включая собственный голос; параллельно Марк ведёт проект, о котором не говорит вслух.

Retold:
> Анну принимают в совет. Но голосовать за неё там будет Марк: её место оплатил его род. Анна злится и решает найти в совете союзников, о которых Марк не узнает.

## Mechanical check

```bash
python3 <scripts>/synopsis_check.py <book>/SYNOPSIS.md --section <synopsis heading> \
  --against <book>/outline.md <book>/STORY_INTENT.md
```

`COPIED` means a sentence carries a five-word run from the plan: rewrite it, do not reword around the run. Then read it once more with two questions only: is there a word this reader does not know, and is there a sentence you would not say aloud when retelling the book? The script cannot answer either.

## Currency

`derived_from` in the synopsis frontmatter records the outline version it was built from. When Layer 1 or 2 changes, regenerate the synopsis in the same run, and ask the user before changing an annotation already on a platform (`publish` → Book page). `wiki-lint` reports a synopsis older than its outline.
