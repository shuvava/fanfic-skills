# Image models: budgets and consistency levers

Researched 2026-09-21 against OpenRouter's `/api/v1/images/models` listing and vendor docs. Model
lineups change monthly — **re-check before trusting a row**, and add new models to
`scripts/prompt_budget.py` (the single source for the numbers; `prompt_budget.py list` prints them).

## Two limits, not one

| Limit | Meaning | What happens past it |
|---|---|---|
| **hard** | The vendor's cap on the prompt field, or the text encoder's window | Request rejected, or the tail silently truncated — usually the style section, since it comes last |
| **soft** | Where the model starts dropping details (our judgment, in words) | The image ignores whatever competed worst: a secondary character's eye colour, the second prop |

OpenRouter's `context_length` for an image model is **not** its prompt cap. Qwen-Image reports 65 536
tokens and its vendor rejects prompts over 800 characters. Where no vendor number was found, the
table uses OpenRouter's figure and marks the row **unverified** — treat it as an upper bound.

Silent truncation is the dangerous case: the image still arrives, just without the style. That is why
the prompt layout puts the shot summary and characters first and why the budget is checked, not
estimated.

## Families

| Family | OpenRouter ids | Hard limit | Refs | Notes |
|---|---|---|---|---|
| **Nano Banana** | `google/gemini-2.5-flash-image` | 32 768 tokens | 3 | First generation. Few reference slots — lock with the short blocks. |
| **Nano Banana Pro** | `google/gemini-3-pro-image` | 65 536 tokens | 14 | Reasons over the prompt before drawing. Best at multi-character scenes and at honouring labelled references ("Image 1 is Лилия"). Natural-language paragraphs beat keyword lists. |
| **Nano Banana 2** | `google/gemini-3.1-flash-image` | 65 536 tokens | 14 | Pro-grade reference handling, cheaper. Good default for chapter images. |
| **GPT Image** | `openai/gpt-image-1`, `-1-mini`, `-2`, `-2.5-*` | 32 000 chars | 16 | Vendor cap confirmed. Guidance: past a few hundred words earlier instructions fade. |
| **FLUX.2** | `black-forest-labs/flux.2-pro`, `-max`, `-flex` | 32K tokens | 8 | BFL recommends 30–80 words for most images, 80+ for complex scenes. Supports `seed`. Accepts structured (JSON-like) prompts. |
| **Seedream** | `bytedance-seed/seedream-4.5`, `-5-0-*` | 600 words | 14 | Vendor recommendation (≤600 English words / 300 Chinese chars). Supports `seed`. 5.0 limits assumed equal to 4.5. On OpenRouter (2026-09-23) 2K with 3 references failed with 524/502 from the Seed provider; 1K went through on retry — 5xx from a provider is transient, repeat the command. |
| **Qwen-Image** | `qwen/qwen-image-3`, `-3-pro` | **800 chars** | 4 | Alibaba cap for Qwen-Image; assumed for v3. Short blocks only; one or two characters per shot. |
| **Recraft** | `recraft/recraft-v3` / `-v4*` | 1 000 / 10 000 chars | 1 (Styles: 10) | Strong on illustration and vector styles. V3 is tight. |
| **MAI-Image** | `microsoft/mai-image-*` | 4 096 tokens | 1–5 | Unverified. |
| **Grok Imagine** | `x-ai/grok-imagine-*` | 4 096 chars | 3 | Unverified; 4 096 is xAI's documented video-prompt cap, used conservatively. |
| **Krea 2, Riverflow, Muse** | `krea/…`, `sourceful/…`, `meta/muse-image` | OpenRouter context | 0–10 | Unverified. Muse takes no references. |

"Refs" is the maximum `input_references` OpenRouter accepts for that model. It caps how many locked
characters can be anchored by image rather than by text alone.

## Consistency levers, strongest first

1. **Reference images** (`input_references`). An approved reference sheet of each character, passed
   with every chapter image, does more than any wording. Label them in the prompt in the same order
   they are attached: "Image 1 is Лилия, Image 2 is Нелот." Keep the style reference, if any, last.
2. **Byte-identical locked text.** The same words, in the same order, every time. A synonym ("raven"
   for "blue-black") is a different prompt, and the model draws a different person. Never paraphrase a
   locked block to save space — switch to its approved short variant instead.
3. **Distinguishing features first** inside each block: the two or three things that make this
   person recognisable at thumbnail size (a scar, hair colour and cut, build) before generic ones.
4. **Seed** (FLUX.2, Seedream, Qwen, Krea only). Useful while iterating a character sheet: keep the
   seed, change one clause, and the difference is the clause. It does **not** hold a face across
   different scenes — a new scene is a new composition regardless of seed.

## Prompt language

Most of these models were trained predominantly on English captions and follow English prompts most
reliably. Gemini, Seedream and Qwen read Russian and Chinese well; FLUX, Recraft and the smaller
models less so. Default to English and record the choice (`image_prompt_language` in `CANON.md`).

**Text that should appear inside the image** — a sign, a book title, a system window in a LitRPG —
stays in the source language, verbatim, in quotation marks. Gemini Pro and GPT Image render Cyrillic
reliably; FLUX and Seedream often do not, so avoid in-image text on those.

## Soft limits are real — evidence

2026-09-23, the same three chapter moments on Seedream 5.0 Pro: at ~490 words (≈160 % of its
300-word soft limit) it lost posture, orientation, relative height and the script rule in two of
three chapters; at ≤300 words it kept scene and identity in all three on the first generation.
Nano Banana 2 on the same ≤300-word prompts still lost scene geometry (poked the wrong boy) and
hair colour — so shortening is not a cure for every model. Write to the target model's soft limit;
treat any prompt over it as a draft, not a test of the model.

## Pricing

Prices move; fetch them live rather than trusting a table:

```bash
for m in google/gemini-3.1-flash-image openai/gpt-image-2 bytedance-seed/seedream-5-0-pro; do
  curl -s "https://openrouter.ai/api/v1/images/models/$m/endpoints" |
    python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["id"], json.dumps(d["endpoints"][0]["pricing"]))'
done
```

Units differ: `image` (flat), `megapixel` (FLUX.2 — a 2K image is ~4 MP), `token` (Gemini, OpenAI —
multiply by the vendor's tokens-per-image for the resolution and quality). Snapshot 2026-09-21:

| Model | Per image | Refs | Seed | AA Elo |
|---|---|---|---|---|
| Nano Banana 2 | $0.067 1K · $0.101 2K · $0.151 4K | 14 | — | 1122 |
| Nano Banana 2 Lite | ~$0.034 | 14 | — | 1091 |
| Nano Banana Pro | $0.134 1K/2K · $0.24 4K | 14 | — | 1100 |
| GPT Image 2 | $0.006 low · $0.053 medium · $0.211 high (1024²) | 16 | — | 1171 (high) |
| GPT Image 2.5 Flare / Sunburst | same token rates; ~$0.21 at max | 16 | — | 1188 / 1182 |
| Grok Imagine 2.0 | $0.04–0.08 | 3 | — | 1154 |
| MAI-Image-2.6 | ~$0.039 | 5 | — | 1147 |
| Seedream 5.0 Pro | $0.045 · $0.09 high-res (+$0.003 per reference image, billed 2026-09-23) | 14 | yes | 1078 |
| Qwen-Image 3 / 3 Pro | $0.03 / $0.04–0.075 | 4 | yes | 1076 / 1088 |
| FLUX.2 pro / max | $0.03 / $0.07 per MP | 8 | yes | — |
| Recraft V4.1 | $0.035 | 1 | — | — |

AA Elo is the Artificial Analysis text-to-image arena — overall preference, no style categories.

## Request shape (OpenRouter Image API)

```json
POST https://openrouter.ai/api/v1/images
{
  "model": "google/gemini-3.1-flash-image",
  "prompt": "<the ```prompt block>",
  "aspect_ratio": "3:2",
  "resolution": "2K",
  "input_references": [
    {"type": "image_url", "image_url": {"url": "data:image/png;base64,<Лилия v1 sheet>"}},
    {"type": "image_url", "image_url": {"url": "data:image/png;base64,<Нелот v1 sheet>"}}
  ]
}
```

`seed` only where the model lists it. **No image model on OpenRouter exposes `negative_prompt` or a
`style` parameter** (checked 2026-09-21 across the whole `/api/v1/images/models` listing; Nano Banana 2
takes only `aspect_ratio`, `input_references`, `n`, `resolution`). Style is a labelled section of the
prompt; exclusions go into its `AVOID:` line as short "no X" phrases. Recraft's styles are separate
model ids, not a parameter.

## Sources

- OpenRouter image generation guide — https://openrouter.ai/docs/guides/overview/multimodal/image-generation
- OpenRouter model listing — `GET https://openrouter.ai/api/v1/images/models`
- BFL FLUX.2 prompting guide — https://docs.bfl.ml/guides/prompting_guide_flux2
- BytePlus Seedream 4.0–4.5 prompt guide — https://docs.byteplus.com/en/docs/ModelArk/1829186
- Alibaba Qwen-Image API — https://www.alibabacloud.com/help/en/model-studio/qwen-image-api
- Recraft API appendix — https://www.recraft.ai/docs/api-reference/appendix
- OpenAI image API reference — https://developers.openai.com/api/reference/resources/images/methods/generate
- Nano Banana 2 pricing — https://openrouter.ai/google/gemini-3.1-flash-image
- GPT Image 2 pricing — https://wavespeed.ai/blog/posts/gpt-image-2-pricing-2026/
- Artificial Analysis leaderboard — https://artificialanalysis.ai/image/leaderboard/text-to-image
- Google Nano Banana prompting guide — https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana
