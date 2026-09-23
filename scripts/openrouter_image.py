#!/usr/bin/env python3
"""Generate images on OpenRouter from a ```prompt block written by the `illustrate` skill.

Run by the user, with their own key — the skill writes prompts, it does not spend money.

  export OPENROUTER_API_KEY=sk-or-...
  openrouter_image.py plan/illustration/STYLE.md \
      --model google/gemini-3.1-flash-image openai/gpt-image-2 \
      --out plan/illustration/refs/bakeoff --resolution 1K

  openrouter_image.py plan/illustration/book-01/ch05.md --model google/gemini-3.1-flash-image \
      --ref plan/illustration/refs/Felix-v1.png plan/illustration/refs/Lilia-v1.png

Several --model values run the same prompt on each (a bake-off). --ref files are attached in the
order given, which must match the "Image N is ..." labels in the prompt. Errors from the API are
printed in full; nothing is written for a failed request.

Exit codes: 0 all succeeded, 1 at least one request failed, 3 usage error.
"""

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://openrouter.ai/api/v1/images"
# Provider-side failures that pass on a plain retry (Seed returned 502/524 three times in one
# evening, 2026-09-23). Failed requests are not billed.
TRANSIENT = {429, 500, 502, 503, 504, 520, 522, 524}
FENCE = re.compile(r"^```prompt([^\n]*)\n(.*?)^```\s*$", re.M | re.S)


def data_url(path):
    mime = mimetypes.guess_type(path)[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="markdown file holding a ```prompt block")
    ap.add_argument("--block", default="1",
                    help="which ```prompt block: its label (```prompt 2c) or its 1-based position (default 1)")
    ap.add_argument("--model", nargs="+", required=True)
    ap.add_argument("--ref", nargs="*", default=[], help="reference images, in label order")
    ap.add_argument("--aspect-ratio", default="3:2")
    ap.add_argument("--resolution", default="1K")
    ap.add_argument("--seed", type=int, help="only for models that list seed support")
    ap.add_argument("--out", default=None, help="output dir (default: next to the file, refs/)")
    ap.add_argument("--name", default=None, help="file name stem (default: the model id)")
    ap.add_argument("--dry-run", action="store_true", help="print the request, send nothing")
    ap.add_argument("--retries", type=int, default=2,
                    help="retries on transient provider errors (429, 5xx), 20s then 40s apart (default 2)")
    a = ap.parse_args()

    blocks = [(label.strip(), body) for label, body in FENCE.findall(Path(a.file).read_text(encoding="utf-8"))]
    # A label never shifts when blocks are inserted above it; a position does.
    hits = [body for label, body in blocks if label and label == a.block]
    if len(hits) > 1:
        print(f"error: {a.file} has {len(hits)} ```prompt blocks labelled '{a.block}'", file=sys.stderr)
        return 3
    if not hits and a.block.isdigit() and 1 <= int(a.block) <= len(blocks):
        hits = [blocks[int(a.block) - 1][1]]
    if not hits:
        labels = ", ".join(l for l, _ in blocks if l) or "none"
        print(f"error: {a.file} has {len(blocks)} ```prompt block(s) (labels: {labels}); "
              f"no block '{a.block}'", file=sys.stderr)
        return 3
    prompt = hits[0].strip()
    for r in a.ref:
        if not Path(r).is_file():
            print(f"error: reference image {r} not found", file=sys.stderr)
            return 3
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key and not a.dry_run:
        print("error: OPENROUTER_API_KEY is not set in this shell", file=sys.stderr)
        return 3

    out = Path(a.out) if a.out else Path(a.file).parent / "refs"
    out.mkdir(parents=True, exist_ok=True)
    refs = [{"type": "image_url", "image_url": {"url": data_url(r)}} for r in a.ref]

    failed = 0
    for model in a.model:
        body = {"model": model, "prompt": prompt, "aspect_ratio": a.aspect_ratio, "resolution": a.resolution}
        if refs:
            body["input_references"] = refs
        if a.seed is not None:
            body["seed"] = a.seed
        if a.dry_run:
            shown = dict(body, input_references=[f"<{r}>" for r in a.ref]) if refs else body
            print(json.dumps(shown, ensure_ascii=False, indent=1))
            continue
        req = urllib.request.Request(API, data=json.dumps(body).encode(), method="POST", headers={
            "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        result, error = None, None
        for attempt in range(a.retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=300) as resp:
                    result = json.load(resp)
                break
            except urllib.error.HTTPError as e:
                error = f"HTTP {e.code} {e.read().decode(errors='replace')[:800]}"
                transient = e.code in TRANSIENT
            except (urllib.error.URLError, TimeoutError) as e:
                error = str(getattr(e, "reason", e))
                transient = True
            if not transient or attempt == a.retries:
                break
            wait = 20 * 2 ** attempt
            print(f"RETRY {model}: {error[:120]} — again in {wait}s ({attempt + 1}/{a.retries})")
            time.sleep(wait)
        if result is None:
            print(f"FAIL {model}: {error}")
            failed += 1
            continue
        items = result.get("data") or []
        if not items or not items[0].get("b64_json"):
            print(f"FAIL {model}: no image in response: {json.dumps(result)[:800]}")
            failed += 1
            continue
        ext = (items[0].get("media_type") or "image/png").split("/")[-1].replace("jpeg", "jpg")
        stem = a.name or model.replace("/", "_")
        dest = out / f"{stem}.{ext}"
        dest.write_bytes(base64.b64decode(items[0]["b64_json"]))
        cost = (result.get("usage") or {}).get("cost")
        print(f"OK   {model}: {dest} ({dest.stat().st_size // 1024} KB)" + (f", ${cost}" if cost is not None else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
