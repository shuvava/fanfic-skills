# Generation — running the user's key

Generation runs on the user's own key; `openrouter_image.py` sends a file's `prompt` block to the
OpenRouter Image API, attaches `--ref` images in label order, saves the result and prints any API
error in full. It spends the user's money, so who presses the button is decided by `image_autorun`:

| `image_autorun` | Who runs it |
|---|---|
| `false` (default) | The user. Give the command; run it yourself only when they ask for that round |
| `true` | You — **one generation at a time, only when nothing is waiting on the user**. Report the file and the cost the script prints, then review the image |

**Stop and ask instead of running, even with `image_autorun: true`,** when any of these holds:

- a choice is still open — the moment, a `[visual:]` decision you proposed and the user has not
  seen, a canon conflict, which of two fixes to take;
- the budget check did not exit `0`;
- it is a bake-off or a model comparison (several paid images at once) or a model other than the
  file's `model:`;
- the round would change the composition the user has not yet seen or approved — after a round the
  user has not looked at, the next run waits for them;
- three rounds have not fixed the same defect (**E9**);
- the step is a lock, an approval or closing the chapter — those are never automatic.

Automatic is for the rounds whose content the user already agreed to: the first round of a prompt
they were shown, and an edit or regeneration that carries out the fix they chose.

Never ask for the key in chat, and **never read, print or `cat` `.env`** — the key lives there.
Hand-written curl one-liners are a trap: they swallow the API's error and write the decoded `null`
as a 3-byte "image", and a pasted `@` can arrive as `＠`.

The key comes from the shell or the project's `.env` (§12).

```bash
python3 "$SCRIPTS/openrouter_image.py" plan/illustration/STYLE.md \
  --model google/gemini-3.1-flash-image openai/gpt-image-2 --out plan/illustration/refs/bakeoff
python3 "$SCRIPTS/openrouter_image.py" plan/illustration/book-01/ch05.md \
  --model google/gemini-3.1-flash-image --resolution 2K \
  --ref plan/illustration/refs/Mark-v1.png plan/illustration/refs/Anna-v1.png \
  --out plan/illustration/images/book-01 --name ch05-r1
python3 "$SCRIPTS/openrouter_image.py" plan/illustration/book-01/ch05-edit.md --block 2c \
  --model google/gemini-3.1-flash-image --resolution 2K \
  --ref plan/illustration/images/book-01/ch05-r3.png --out plan/illustration/images/book-01 --name ch05-r4
```

`--block` takes a block's label (```` ```prompt 2c ````) or its 1-based position. `--dry-run`
prints the request without sending it. Transient provider errors (429, 5xx — Seed returns 502/524
often) are retried twice, 20 s then 40 s apart (`--retries`); failed requests are not billed.

# The check — `prompt_budget.py`

```bash
for d in .agents/scripts ~/.agents/scripts "$CLAUDE_PLUGIN_ROOT/scripts" scripts; do
  [ -f "$d/prompt_budget.py" ] && SCRIPTS="$d" && break
done
python3 "$SCRIPTS/prompt_budget.py" list
python3 "$SCRIPTS/prompt_budget.py" check plan/illustration/book-01/ch05.md \
  --model google/gemini-3.1-flash-image \
  --locked plan/illustration/STYLE.md plan/illustration/characters/анна-v1.md \
           plan/illustration/world/era.md
```

It measures every `prompt` block against the model's hard and soft limits, confirms each `--locked`
sheet's full or short block appears verbatim, and that the `Image N` labels do not exceed the
references the model accepts. Exit `0` fits; `1` over the soft limit or near a token cap; `2` over
the hard limit, **a locked block missing**, or too many references; `3` unknown model or bad path.
Pass every sheet the prompt uses — a sheet left off is a sheet not checked. An **unverified** limit
is an upper bound; say so within 20% of one. Unknown model: find its limit in the vendor docs, pass
`--hard-chars`, then add it to the script's table.

# Artifacts

```
plan/illustration/
  STYLE.md
  characters/<name>-v<N>.md, <name>-v<N>-edit.md
  world/<name>-v<N>.md, era.md                     # recurring elements; the world guard
  refs/<prompt_name>-v<N>.png, <element>-v<N>.png  # approved reference images
  book-<NN>/ch<NN>.md, ch<NN>-edit.md              # flat layout: ch<NN>.md
  images/book-<NN>/ch<NN>-r<N>.png, ch<NN>.png     # rounds; the approved image (.jpg from Seedream)
```

Shared across the series, like `plan/HARNESS.md` (§8), except the per-book folders.
`plan/illustration/` is read by no other stage: nothing here is canon or fanon. The one thing
this skill writes outside it is the approved image's link line and `illustration:` key in the
chapter draft (Phase 3 step 14) — markup, not prose, and stripped by every script that measures
prose. Temporary rounds and review crops are deleted when their step closes — a lock
(Phases 1–2b) or an approved chapter image (Phase 3 step 15) — and the project is committed; only
approved images, `refs/` and the `.md` files stay.

Append to `wiki/log.md`:

```
## [YYYY-MM-DD] illustrate | style v1 locked
   metrics: rounds=4 model=google/gemini-3.1-flash-image
## [YYYY-MM-DD] illustrate | Anna v1 locked
   metrics: rounds=6 (4 gen + 2 edit) src_citations=5 visual_decisions=4 full_words=58 short_words=19
## [YYYY-MM-DD] illustrate | b01/ch05 image approved
   metrics: model=google/gemini-3.1-flash-image rounds=7 (4 gen + 2 edit + 1 local patch) refs=2 words=486 final=images/book-01/ch05.png placed=ch05-<slug>.md:27
   findings: canon/wiki gaps met on the way
```

Count metrics from the files, not from memory (§10). `rounds` is the closest thing this skill has
to a cost signal: many rounds on one feature means the wording is fighting the model.
