#!/usr/bin/env python3
"""Find the words and short phrases drafts overuse relative to the source — model habits.

Standard library only, any language. Optional: `pymorphy3` for Russian lemmas and parts of
speech, used automatically when installed and the text is Cyrillic.

    python3 overused_patterns.py --drafts drafts/ch*.md --against raw/ch*.md [--top 40]

Why this exists
---------------
A model drafting in someone's voice keeps habits of its own. Measured on a real Russian run,
Opus used «ровно» 105× more often than the source author, «только вот» 75×, «не потому,
что…» 34× — nothing a style fingerprint counts, and nothing a reader names until shown the
list. Counting is cheap; guessing is not.

Method: weighted log-odds with an informative Dirichlet prior (Monroe, Colaresi & Quinn 2008,
"Fightin' Words") over word n-grams (1–3). The z-score says how confidently the drafts use a
pattern more than the source, shrunk toward the pooled rate so a pattern seen three times
cannot top the list by accident.

Topic words are the trap: drafts set at an exam overuse "exam" for reasons that are not
style. Two filters keep manner and drop subject:
- with pymorphy3 (Russian): keep function words — conjunctions, particles, prepositions,
  adverbs, pronouns — and phrases of 3+ words built around them;
- otherwise: dispersion — a habit shows up in most drafts, a topic word clusters in a few.
Capitalised words that do not open a sentence are treated as names and dropped.

The output is a list for the user to confirm, not a ban list: a pattern the author also
uses is fine where the author would use it.
"""

from __future__ import annotations

import argparse
import glob
import math
import re
import sys
from collections import Counter
from pathlib import Path

WORD_RE = re.compile(r"\w+(?:-\w+)*", re.UNICODE)
SENT_RE = re.compile(r"(?<=[.!?…。！？])\s+")
FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
HEADING_RE = re.compile(r"^#+ .*$", re.MULTILINE)
# Illustration links placed by place_illustration.py — markup, not prose.
IMAGE_RE = re.compile(r"\n*^!\[[^\]\n]*\]\([^)\n]*\)[ \t]*$", re.MULTILINE)
FUNCTION_POS = {"CONJ", "PRCL", "PREP", "ADVB", "NPRO", "PRED", "INTJ", "COMP", "GRND"}
MIN_DRAFT_WORDS = 3000

try:  # optional: Russian morphology
    import pymorphy3  # type: ignore
    _MORPH = pymorphy3.MorphAnalyzer()
except Exception:  # noqa: BLE001 — absent or broken: fall back to surface forms
    _MORPH = None
_cache: dict[str, tuple[str, str | None, bool]] = {}


def analyse(w: str, cyrillic: bool) -> tuple[str, str | None, bool]:
    """(lemma, part of speech, is a name); surface form when no morphology applies."""
    if not (_MORPH and cyrillic):
        return w, None, False
    if w not in _cache:
        p = _MORPH.parse(w)[0]
        _cache[w] = (p.normal_form, p.tag.POS,
                     any(t in p.tag for t in ("Name", "Surn", "Patr", "Geox", "Orgn")))
    return _cache[w]


def read(patterns: list[str]) -> list[tuple[str, str]]:
    paths = sorted({p for pat in patterns for p in glob.glob(pat)})
    if not paths:
        sys.exit(f"no files matched: {' '.join(patterns)}")
    out = []
    for p in paths:
        t = Path(p).read_text(encoding="utf-8")
        out.append((p, IMAGE_RE.sub("", HEADING_RE.sub("", FRONTMATTER_RE.sub("", t)))))
    return out


def capitalised_words(texts: list[str]) -> set[str]:
    """Words written capitalised in most of their mid-sentence uses — names, in any language.
    Needed because a name that opens a sentence looks like any other word there."""
    up, total = Counter(), Counter()
    for t in texts:
        for sent in SENT_RE.split(t):
            for i, m in enumerate(WORD_RE.finditer(sent)):
                if i == 0:
                    continue
                w = m.group()
                total[w.lower()] += 1
                if w[0].isupper():
                    up[w.lower()] += 1
    return {w for w, n in total.items() if n >= 2 and up[w] / n > 0.5}


NAMES: set[str] = set()


def grams(text: str, cyrillic: bool, n_max: int = 3) -> tuple[list[tuple[str, ...]], int]:
    out, words = [], 0
    for sent in SENT_RE.split(text):
        toks: list[str | None] = []
        for i, m in enumerate(WORD_RE.finditer(sent)):
            w = m.group()
            if w.isdigit():
                toks.append(None)
                continue
            words += 1
            lemma, _, is_name = analyse(w.lower(), cyrillic)
            toks.append(None if (i > 0 and w[0].isupper()) or is_name or w.lower() in NAMES else lemma)
        for n in range(1, n_max + 1):
            for i in range(len(toks) - n + 1):
                g = toks[i:i + n]
                if None not in g:
                    out.append(tuple(g))  # type: ignore[arg-type]
    return out, words


def log_odds(a: Counter, b: Counter, scale: float = 10000.0) -> dict[tuple, float]:
    na, nb = sum(a.values()), sum(b.values())
    pooled = a + b
    n0 = sum(pooled.values())
    out = {}
    for g, pc in pooled.items():
        ag = scale * pc / n0
        ya, yb = a.get(g, 0), b.get(g, 0)
        la = math.log((ya + ag) / (na + scale - ya - ag))
        lb = math.log((yb + ag) / (nb + scale - yb - ag))
        out[g] = (la - lb) / math.sqrt(1 / (ya + ag) + 1 / (yb + ag))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--drafts", nargs="+", required=True, help="generated chapters")
    ap.add_argument("--against", nargs="+", required=True, help="source chapters (the ingested span)")
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--min-count", type=int, default=4)
    ap.add_argument("--min-z", type=float, default=3.0)
    args = ap.parse_args()

    drafts, source = read(args.drafts), read(args.against)
    cyr = sum(len(re.findall(r"[А-Яа-яЁё]", t)) for _, t in source) > 0.3 * sum(len(t) for _, t in source)
    morph_on = bool(_MORPH and cyr)
    NAMES.update(capitalised_words([t for _, t in drafts + source]))

    dc: Counter = Counter()
    per_doc: list[set] = []
    dw = 0
    for _, t in drafts:
        g, w = grams(t, cyr)
        dc.update(g)
        per_doc.append(set(g))
        dw += w
    if dw < MIN_DRAFT_WORDS:
        print(f"only {dw} words of drafts — need {MIN_DRAFT_WORDS}+ for rates that mean anything. Skipping.")
        return
    sc: Counter = Counter()
    sw = 0
    for _, t in source:
        g, w = grams(t, cyr)
        sc.update(g)
        sw += w

    def manner(g: tuple) -> bool:
        if morph_on:
            pos = [analyse(x, True)[1] for x in g]
            if all(p in FUNCTION_POS for p in pos):
                return True
            return len(g) >= 3 and any(p in FUNCTION_POS for p in pos) and sum(p == "NOUN" for p in pos) <= 1
        spread = sum(1 for s in per_doc if g in s) / max(1, len(per_doc))
        return spread >= 0.5 or len(per_doc) < 3

    z = log_odds(dc, sc)
    rows = sorted(((g, s) for g, s in z.items()
                   if s >= args.min_z and dc[g] >= args.min_count and manner(g)), key=lambda t: -t[1])
    listed: list[tuple] = []
    for g, s in rows:  # drop a pattern nearly always seen inside a longer listed one
        if any(len(h) > len(g) and " ".join(g) in " ".join(h) and dc[h] >= 0.8 * dc[g] for h, _ in listed):
            continue
        listed.append((g, s))
        if len(listed) >= args.top:
            break

    print(f"drafts: {dw} words in {len(drafts)} files; source: {sw} words in {len(source)} files; "
          f"{'lemmas + parts of speech (pymorphy3)' if morph_on else 'surface forms + dispersion filter'}\n")
    print("| # | pattern | z | drafts /10k | source /10k | ratio |")
    print("|---|---|---|---|---|---|")
    for i, (g, s) in enumerate(listed, 1):
        rd, rs = 1e4 * dc[g] / dw, 1e4 * sc.get(g, 0) / sw
        ratio = "∞" if rs == 0 else f"{rd / rs:.0f}×" if rd / rs >= 10 else f"{rd / rs:.1f}×"
        print(f"| {i} | {' '.join(g)} | {s:.1f} | {rd:.1f} | {rs:.1f} | {ratio} |")
    if not listed:
        print("(nothing above the threshold)")


if __name__ == "__main__":
    main()
