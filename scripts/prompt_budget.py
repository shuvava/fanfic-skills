#!/usr/bin/env python3
"""Check an image-generation prompt against a model's size budget and the locked blocks.

The `illustrate` skill writes prompts into markdown files as fenced ```prompt blocks and keeps
approved character and style text in fenced ```locked-full / ```locked-short blocks. This script
answers two questions with evidence instead of recollection:

  1. Does the prompt fit the target model?  (hard limit = rejected or truncated;
     soft limit = past this the model starts dropping details)
  2. Does every locked block the prompt claims to use appear in it byte-for-byte
     (whitespace-normalised)?  A paraphrased identity block is how a face drifts.

Usage:
  prompt_budget.py list
  prompt_budget.py check <prompt.md> --model <openrouter-id> [--locked <sheet.md> ...]
  prompt_budget.py check <prompt.md> --hard-chars 2000 --soft-words 250

Exit codes: 0 fits, 1 over the soft limit, 2 over the hard limit or a locked block is missing,
3 usage error / unknown model.

Limits are dated. Re-check vendor docs when a model is added; see
skills/illustrate/references/models.md for sources and what "unverified" means.
"""

import argparse
import re
import sys
from pathlib import Path

# prefix -> (hard_limit, unit, soft_words, max_refs, verified, alias)
# unit: "chars" | "words" | "tokens".  First (longest) matching prefix wins.
# verified=True means the hard limit comes from the vendor's own docs; False means it is the
# context length OpenRouter reports or a conservative guess, and the real cap may be lower.
MODELS = {
    "google/gemini-2.5-flash-image":      (32768,  "tokens", 300, 3,  True,  "Nano Banana"),
    "google/gemini-3-pro-image":          (65536,  "tokens", 500, 14, True,  "Nano Banana Pro"),
    "google/gemini-3.1-flash-image":      (65536,  "tokens", 500, 14, True,  "Nano Banana 2"),
    "google/gemini-3.1-flash-lite-image": (65536,  "tokens", 300, 14, False, "Nano Banana 2 Lite"),
    "openai/gpt-image":                   (32000,  "chars",  500, 16, True,  "GPT Image"),
    "openai/gpt-5":                       (32000,  "chars",  500, 16, False, "GPT-5 Image (chat)"),
    "black-forest-labs/flux.2-klein":     (32000,  "tokens", 200, 4,  False, "FLUX.2 klein"),
    "black-forest-labs/flux.2":           (32000,  "tokens", 250, 8,  True,  "FLUX.2"),
    "bytedance-seed/seedream-4.5":        (600,    "words",  300, 14, True,  "Seedream 4.5"),
    "bytedance-seed/seedream-5":          (600,    "words",  300, 14, False, "Seedream 5.0"),
    "qwen/qwen-image":                    (800,    "chars",  120, 4,  False, "Qwen-Image"),
    "recraft/recraft-v3":                 (1000,   "chars",  150, 1,  True,  "Recraft V3"),
    "recraft/recraft-v4-styles":          (10000,  "chars",  300, 10, True,  "Recraft V4 Styles"),
    "recraft/recraft-v4":                 (10000,  "chars",  300, 1,  True,  "Recraft V4/4.1"),
    "microsoft/mai-image-2.6":            (4096,   "tokens", 300, 5,  False, "MAI-Image 2.6"),
    "microsoft/mai-image":                (4096,   "tokens", 300, 1,  False, "MAI-Image 2.5"),
    "x-ai/grok-imagine":                  (4096,   "chars",  300, 3,  False, "Grok Imagine"),
    "krea/krea-2":                        (65536,  "tokens", 300, 1,  False, "Krea 2"),
    "sourceful/riverflow-v2.5-pro":       (32768,  "tokens", 300, 10, False, "Riverflow 2.5 Pro"),
    "sourceful/riverflow-v2.5":           (32768,  "tokens", 300, 4,  False, "Riverflow 2.5"),
    "sourceful/riverflow-v2-pro":         (8192,   "tokens", 300, 10, False, "Riverflow 2 Pro"),
    "sourceful/riverflow-v2":             (8192,   "tokens", 300, 4,  False, "Riverflow 2"),
    "meta/muse-image":                    (65536,  "tokens", 300, 0,  False, "Muse Image"),
}

FENCE = re.compile(r"^```([\w-]+)[^\n]*\n(.*?)^```\s*$", re.M | re.S)


def lookup(model_id):
    hits = [p for p in MODELS if model_id.startswith(p)]
    return (max(hits, key=len), MODELS[max(hits, key=len)]) if hits else (None, None)


def blocks(text, kind):
    return [body for k, body in FENCE.findall(text) if k == kind]


def norm(s):
    return " ".join(s.split())


def measure(prompt):
    chars = len(prompt)
    words = len(prompt.split())
    ascii_share = sum(c.isascii() for c in prompt) / max(chars, 1)
    # Rough: ~4 chars/token for English, ~2.5 for Cyrillic and other non-Latin scripts.
    tokens = round(chars / (4 if ascii_share > 0.9 else 2.5))
    return {"chars": chars, "words": words, "tokens": tokens}


def cmd_list(_):
    print(f"| {'OpenRouter id prefix':36} | {'alias':20} | {'hard limit':>14} | soft | refs | verified |")
    print(f"|{'-'*38}|{'-'*22}|{'-'*16}|------|------|----------|")
    for p, (hard, unit, soft, refs, ver, alias) in MODELS.items():
        print(f"| {p:36} | {alias:20} | {hard:>7} {unit:6} | {soft:>4} | {refs:>4} | {'yes' if ver else 'no':8} |")
    print("\nsoft = words; our judgment of where detail starts getting dropped, not a vendor number.")
    return 0


def cmd_check(a):
    path = Path(a.file)
    if not path.is_file():
        print(f"error: {path} not found", file=sys.stderr)
        return 3
    prompts = blocks(path.read_text(encoding="utf-8"), "prompt")
    if not prompts:
        print(f"error: no ```prompt block in {path}", file=sys.stderr)
        return 3

    if a.model:
        prefix, spec = lookup(a.model)
        if not spec:
            print(f"error: unknown model '{a.model}'. Run `list`, or pass --hard-chars/--soft-words.",
                  file=sys.stderr)
            return 3
        hard, unit, soft, refs, verified, alias = spec
    else:
        if not a.hard_chars:
            print("error: pass --model or --hard-chars", file=sys.stderr)
            return 3
        prefix, hard, unit, soft, refs, verified, alias = "custom", a.hard_chars, "chars", a.soft_words or 300, None, True, "custom"
    if a.soft_words:
        soft = a.soft_words

    locked = []
    for sheet in a.locked or []:
        sp = Path(sheet)
        if not sp.is_file():
            print(f"error: locked sheet {sp} not found", file=sys.stderr)
            return 3
        st = sp.read_text(encoding="utf-8")
        locked.append((sp.name, [norm(b) for b in blocks(st, "locked-full")],
                       [norm(b) for b in blocks(st, "locked-short")]))

    worst = 0
    print(f"model: {a.model or 'custom'} -> {prefix} ({alias}); hard {hard} {unit}"
          f"{'' if verified else ' (UNVERIFIED — real cap may be lower)'}; soft {soft} words"
          + (f"; max reference images {refs}" if refs is not None else ""))
    for i, p in enumerate(prompts, 1):
        m = measure(p.strip())
        used = m[unit]
        status = "OK"
        if used > hard:
            status, rc = "OVER HARD LIMIT", 2
        elif unit == "tokens" and used > 0.8 * hard:
            status, rc = "NEAR HARD LIMIT (token count is an estimate)", 1
        elif m["words"] > soft:
            status, rc = "over soft limit", 1
        else:
            rc = 0
        worst = max(worst, rc)
        print(f"\nprompt {i}: {m['chars']} chars, {m['words']} words, ~{m['tokens']} tokens (est.)")
        print(f"  budget: {used}/{hard} {unit} ({100 * used / hard:.0f}%) — {status}")
        labelled = len(set(re.findall(r"\bImage (\d+)\b", p)))
        if labelled and refs is not None:
            if labelled > refs:
                print(f"  references: {labelled} labelled, model accepts {refs} — TOO MANY")
                worst = 2
            else:
                print(f"  references: {labelled} labelled, model accepts {refs}")
        np = norm(p)
        for name, full, short in locked:
            if any(b in np for b in full):
                verdict = "full block verbatim"
            elif any(b in np for b in short):
                verdict = "short block verbatim"
            elif not full and not short:
                verdict = "MISSING: sheet has no locked-full/locked-short block"
                worst = 2
            else:
                verdict = "MISSING: neither locked block appears verbatim"
                worst = 2
            print(f"  locked {name}: {verdict}")

    print(f"\nexit {worst}")
    return worst


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="print the model budget table")
    c = sub.add_parser("check", help="check ```prompt blocks in a markdown file")
    c.add_argument("file")
    c.add_argument("--model", help="OpenRouter model id, e.g. google/gemini-3-pro-image")
    c.add_argument("--locked", nargs="*", help="character / style sheets whose locked blocks must appear")
    c.add_argument("--hard-chars", type=int, help="custom hard limit in characters (unknown model)")
    c.add_argument("--soft-words", type=int, help="override the soft limit in words")
    a = ap.parse_args()
    return cmd_list(a) if a.cmd == "list" else cmd_check(a)


if __name__ == "__main__":
    sys.exit(main())
