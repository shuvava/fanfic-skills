#!/usr/bin/env python3
"""Measure a source's style fingerprint, and check drafted prose against it.

Standard library only, no dependencies, any language.

    # during ingest — produce the tables that go into canon/overview.md
    python3 style_fingerprint.py measure raw/*.md

    # during drafting or linting — how far has a draft drifted?
    python3 style_fingerprint.py check drafts/ch07.md --against raw/*.md

Why this exists
---------------
A style note written as an adjective cannot be checked. "Uses ellipsis heavily" is
satisfied by prose carrying a quarter of the source's density, and in a real run it
was: the wiki said heavy, the source ran 21 ellipses per 1000 words, the generated
chapter ran 4.6, and nothing in the pipeline could tell. Counts can be checked.

The orthography scan matters even more. Every source has habits that depart from the
standard, and a model drafting a continuation will silently repair them — it has been
trained to. The scan finds those habits mechanically by looking for one written form
of a word dominating another, so the wiki can record "this is the author's norm, do
not correct it" before any prose is written.
"""

from __future__ import annotations

import argparse
import glob
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

# --------------------------------------------------------------------------- #

WORD_RE = re.compile(r"\w+(?:['’\-]\w+)*", re.UNICODE)
BARE_WORD_RE = re.compile(r"\w+", re.UNICODE)
HEADING_RE = re.compile(r"^#+ .*$", re.MULTILINE)
FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?…。！？])[\s\n]+")

# Punctuation habits worth counting. Anything a writer can lean on hard enough that
# its absence reads as a different author.
PUNCTUATION = {
    "ellipsis": re.compile(r"\.\.\.|…"),
    "em_dash": re.compile(r"—"),
    "en_dash": re.compile(r"–"),
    "hyphen_dash_aside": re.compile(r"\s-\s"),
    "exclamation": re.compile(r"!"),
    "question": re.compile(r"\?"),
    "semicolon": re.compile(r";"),
    "colon": re.compile(r":"),
    "parenthesis": re.compile(r"\("),
    "guillemet": re.compile(r"«"),
    "double_quote": re.compile(r"[\"“”]"),
    "single_quote": re.compile(r"[‘’](?![\w])"),
    # Comic register. Humour is not directly countable, but its delivery is, and
    # these three carry most of it in practice: a short quoted span mid-sentence is
    # almost always ironic distance rather than speech, and stacked terminal marks
    # are the sound of a narrator sputtering. Measured on a real corpus, the author
    # scare-quoted at 10 per 1000 words and a draft that reproduced the device
    # scored 10.4 while a draft that missed it scored 1.2 — a gap no reader-facing
    # note about "ironic tone" had managed to close.
    "scare_quote": re.compile(r"[\"“«][^\"“”«»\n]{1,40}[\"”»]"),
    "stacked_terminal": re.compile(r"[!?]\.\.|\.\.[!?]|[!?]{2,}"),
    "interjection_dash": re.compile(r"(?<=[а-яёa-z])\s*[-—]\s*[а-яёa-z]", re.IGNORECASE),
}

# How a line of dialogue opens. Order matters: the escaped form is checked before
# the bare one so a markdown-escaped dash is not miscounted as a plain hyphen.
DIALOGUE_MARKERS = [
    ("escaped_dash", re.compile(r"^\\-\s")),
    ("em_dash", re.compile(r"^—\s?")),
    ("en_dash", re.compile(r"^–\s?")),
    ("plain_dash", re.compile(r"^-\s")),
    ("guillemet", re.compile(r"^«")),
    ("double_quote", re.compile(r"^[\"“]")),
    ("single_quote", re.compile(r"^[‘']")),
]


def read(paths: list[Path]) -> list[tuple[Path, str]]:
    out = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        out.append((path, HEADING_RE.sub("", FRONTMATTER_RE.sub("", text))))
    return out


def words(text: str) -> list[str]:
    return BARE_WORD_RE.findall(text)


def paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def sentences(text: str) -> list[str]:
    normalised = re.sub(r"\.\.\.", "…", text)
    return [s for s in (p.strip() for p in SENTENCE_SPLIT_RE.split(normalised)) if words(s)]


# --------------------------------------------------------------------------- #
# fingerprint
# --------------------------------------------------------------------------- #


def fingerprint(docs: list[tuple[Path, str]]) -> dict:
    joined = "\n\n".join(text for _, text in docs)
    all_words = words(joined)
    n = len(all_words) or 1
    per_1k = lambda count: round(1000.0 * count / n, 1)

    lines = [ln.strip() for _, text in docs for ln in text.splitlines() if ln.strip()]
    marker_counts = Counter()
    marker_example = {}
    for line in lines:
        for name, rx in DIALOGUE_MARKERS:
            if rx.match(line):
                marker_counts[name] += 1
                marker_example.setdefault(name, line[:60])
                break

    punctuation = {}
    for name, rx in PUNCTUATION.items():
        hits = rx.findall(joined)
        if hits:
            punctuation[name] = {
                "per_1k": per_1k(len(hits)),
                "total": len(hits),
                "example": _example_for(joined, rx),
            }

    sent_lens = [len(words(s)) for s in sentences(joined)]
    para_lens = [len(sentences(p)) for _, text in docs for p in paragraphs(text)]
    doc_lens = [len(words(text)) for _, text in docs]

    return {
        "documents": len(docs),
        "total_words": n,
        "doc_words_mean": round(statistics.mean(doc_lens)) if doc_lens else 0,
        "doc_words_range": (min(doc_lens), max(doc_lens)) if doc_lens else (0, 0),
        "sentence_words_mean": round(statistics.mean(sent_lens), 1) if sent_lens else 0,
        "sentence_words_stdev": round(statistics.stdev(sent_lens), 1) if len(sent_lens) > 1 else 0,
        "paragraph_sentences_mean": round(statistics.mean(para_lens), 1) if para_lens else 0,
        "punctuation": punctuation,
        "dialogue_markers": dict(marker_counts),
        "dialogue_marker_examples": marker_example,
        "dialogue_lines": sum(marker_counts.values()),
    }


def _example_for(text: str, rx: re.Pattern) -> str:
    match = rx.search(text)
    if not match:
        return ""
    start = max(0, match.start() - 30)
    return "…" + text[start : match.end() + 30].replace("\n", " ").strip() + "…"


# --------------------------------------------------------------------------- #
# orthography — the habits a model will silently repair
# --------------------------------------------------------------------------- #


def orthography(docs: list[tuple[Path, str]], min_total: int = 5,
                dominance: float = 0.8) -> list[dict]:
    """Words the source writes one way where another spelling is also attested.

    Works by collapsing hyphens, apostrophes and internal spaces to one key:
    `какой то`, `какой-то` and `какойто` share a key, so their counts compare
    directly. Whichever form dominates is the source's norm — and when the dominant
    form is the *unjoined* one, that is precisely what a drafting model will "fix".

    High precision, and blind in one important case: if the source never once uses
    the standard form, there is nothing to compare against and this returns nothing.
    That is why `candidates()` exists.
    """
    joined = "\n\n".join(text for _, text in docs).lower()
    tokens = WORD_RE.findall(joined)

    forms: Counter[str] = Counter(t for t in tokens if "-" in t or "'" in t or "’" in t)
    bigrams = Counter(f"{a} {b}" for a, b in zip(tokens, tokens[1:]))

    def key(form: str) -> str:
        return re.sub(r"[\s\-'’]", "", form)

    buckets: dict[str, Counter[str]] = {}
    for form, count in list(forms.items()) + list(bigrams.items()):
        buckets.setdefault(key(form), Counter())[form] = count

    findings = []
    for variants in buckets.values():
        if len(variants) < 2:
            continue
        total = sum(variants.values())
        if total < min_total:
            continue
        (top_form, top_count), *rest = variants.most_common()
        if top_count / total < dominance:
            continue  # genuinely mixed usage; not a rule
        findings.append({
            "dominant": top_form,
            "dominant_count": top_count,
            "alternatives": {f: c for f, c in rest},
            "share": round(top_count / total, 3),
            "joined": " " not in top_form,
        })

    findings.sort(key=lambda f: -f["dominant_count"])
    return findings


def candidates(docs: list[tuple[Path, str]], min_count: int = 5,
               max_second: int = 7, top: int = 30) -> dict:
    """Recall net for the case `orthography()` cannot see.

    **This function deliberately does not decide anything.** No dictionary ships
    with this script and none is wanted: whether `какой то` should carry a hyphen is
    a fact about Russian, whether `alright` should be `all right` is a fact about
    English, and the model reading this output knows both. What a script can do
    cheaply and exhaustively is count, so it hands over two lists:

      * every distinct hyphenated/apostrophised form the source uses
      * the most frequent two-word sequences ending in a short token

    One of those lists contains the source's non-standard habits. The model's job is
    to look at them and say which. That division — script counts, model judges — is
    why this works across languages without a single language-specific rule.
    """
    joined = "\n\n".join(text for _, text in docs).lower()
    tokens = WORD_RE.findall(joined)

    hyphenated = Counter(t for t in tokens if "-" in t or "'" in t or "’" in t)
    pairs = Counter(
        (a, b) for a, b in zip(tokens, tokens[1:]) if len(b) <= max_second
    )
    frequent = [
        {"form": f"{a} {b}", "count": count}
        for (a, b), count in pairs.most_common(top * 6)
        if count >= min_count
    ][:top]

    # A postfix particle attaches to many different stems, so grouping the pairs by
    # their second token makes a family visible that any single pair hides. In the
    # source this was built against, `какой то`/`что то`/`какое то` are three
    # unremarkable rows individually and one obvious rule when grouped.
    families: dict[str, list[tuple[str, int]]] = {}
    for (first, second), count in pairs.items():
        if count >= 2:
            families.setdefault(second, []).append((first, count))
    grouped = [
        {
            "second": second,
            "distinct_first": len(members),
            "total": sum(c for _, c in members),
            "examples": [f"{f} {second}" for f, _ in
                         sorted(members, key=lambda m: -m[1])[:5]],
        }
        for second, members in families.items()
        if len(members) >= 3 and sum(c for _, c in members) >= min_count * 2
    ]
    grouped.sort(key=lambda g: -g["total"])

    return {
        "hyphenated_forms": hyphenated.most_common(top),
        "frequent_pairs": frequent,
        "pair_families": grouped[:12],
    }


# --------------------------------------------------------------------------- #
# reporting
# --------------------------------------------------------------------------- #


def render_measure(fp: dict, ortho: list[dict], cand: dict, limit: int) -> str:
    lo, hi = fp["doc_words_range"]
    rows = [
        "## Style fingerprint",
        "",
        "| Feature | Source value | Literal example |",
        "|---|---|---|",
        f"| Chapter length | ~{fp['doc_words_mean']} words (range {lo}–{hi}) | — |",
        f"| Sentence length | {fp['sentence_words_mean']} words (sd {fp['sentence_words_stdev']}) | — |",
        f"| Paragraph length | {fp['paragraph_sentences_mean']} sentences | — |",
    ]
    for name, data in sorted(fp["punctuation"].items(), key=lambda kv: -kv[1]["per_1k"]):
        if data["per_1k"] < 0.5:
            continue
        rows.append(f"| {name.replace('_', ' ').title()} | {data['per_1k']} per 1000 words "
                    f"({data['total']} total) | `{data['example'][:60]}` |")

    total_dialogue = fp["dialogue_lines"] or 1
    for name, count in sorted(fp["dialogue_markers"].items(), key=lambda kv: -kv[1]):
        share = round(100 * count / total_dialogue)
        example = fp["dialogue_marker_examples"].get(name, "")
        rows.append(f"| Dialogue marker `{name}` | {share}% of {fp['dialogue_lines']} lines "
                    f"| `{example}` |")

    rows += ["", "## Non-standard orthography", ""]
    if ortho:
        rows.append("Forms the source writes consistently one way, with the other spelling also "
                    "attested. **These are the author's norm. Do not 'correct' them when "
                    "drafting.**")
        rows.append("")
        for finding in ortho[:limit]:
            alts = ", ".join(f"`{f}` ×{c}" for f, c in finding["alternatives"].items())
            note = "" if finding["joined"] else " ← written unjoined; a model will join it"
            rows.append(f"- `{finding['dominant']}` ×{finding['dominant_count']} "
                        f"({finding['share']:.0%}) vs {alts}{note}")
    else:
        rows.append("No competing spellings attested — but that is *not* the same as "
                    "\"no non-standard orthography\". If the source never once uses the standard "
                    "form, there is nothing here to compare against. Read the candidates below.")

    rows += [
        "",
        "### Candidates to adjudicate",
        "",
        "**This script cannot tell you which of these are non-standard — you can.** It has no "
        "dictionary and wants none; whether a form needs a hyphen is a fact about the language, "
        "not about the text. Read each list and decide which entries depart from the standard, "
        "then record those on the page with their counts.",
        "",
        "Hyphenated and apostrophised forms used:",
        "",
    ]
    hyphenated = cand["hyphenated_forms"]
    rows.append("  " + (", ".join(f"`{f}` ×{c}" for f, c in hyphenated[:limit]) or "none") )
    rows += [
        "",
        "Frequent two-word sequences ending in a short token — check whether the standard "
        "would join any of these:",
        "",
    ]
    rows.append("  " + (", ".join(f"`{p['form']}` ×{p['count']}"
                                  for p in cand["frequent_pairs"][:limit]) or "none"))

    if cand["pair_families"]:
        rows += [
            "",
            "Short tokens that follow many different words — the signature of a postfix "
            "particle or clitic. If the standard attaches any of these, the source is not "
            "attaching it, and that is a rule worth recording:",
            "",
        ]
        for family in cand["pair_families"]:
            rows.append(f"- `{family['second']}` — follows {family['distinct_first']} different "
                        f"words, {family['total']} times total: "
                        + ", ".join(f"`{e}`" for e in family["examples"]))
    return "\n".join(rows)


def render_check(draft_fp: dict, source_fp: dict) -> tuple[str, int]:
    rows = ["| Feature | Source | Draft | Delta |", "|---|---|---|---|"]
    problems = 0

    def compare(label: str, source_value: float, draft_value: float, tolerance: float) -> None:
        nonlocal problems
        if not source_value:
            return
        delta = (draft_value - source_value) / source_value
        flag = ""
        if abs(delta) > tolerance:
            flag = "  ⚠"
            problems += 1
        rows.append(f"| {label} | {source_value} | {draft_value} | {delta:+.0%}{flag} |")

    compare("Chapter length (words)", source_fp["doc_words_mean"],
            draft_fp["doc_words_mean"], 0.20)
    compare("Sentence length", source_fp["sentence_words_mean"],
            draft_fp["sentence_words_mean"], 0.25)
    compare("Paragraph length", source_fp["paragraph_sentences_mean"],
            draft_fp["paragraph_sentences_mean"], 0.35)

    for name, data in source_fp["punctuation"].items():
        if data["per_1k"] < 1.0:
            continue
        # A habit the source leans on hard needs a tighter band than an incidental one.
        # A flat ±35% let the worst real drift through: the source ran 21 ellipses per
        # 1000 words, the draft ran 14.8, and the check passed at -30% while that single
        # feature was the largest deviation in the chapter. Anything at 10+ per 1000
        # words is a signature of the voice, and losing a fifth of it is audible.
        tolerance = 0.15 if data["per_1k"] >= 10.0 else 0.35
        compare(f"{name} per 1k", data["per_1k"],
                draft_fp["punctuation"].get(name, {}).get("per_1k", 0.0), tolerance)

    source_total = source_fp["dialogue_lines"] or 1
    draft_total = draft_fp["dialogue_lines"] or 1
    for name, count in source_fp["dialogue_markers"].items():
        source_share = round(100 * count / source_total)
        draft_share = round(100 * draft_fp["dialogue_markers"].get(name, 0) / draft_total)
        if source_share < 10:
            continue
        flag = ""
        if abs(draft_share - source_share) > 20:
            flag = "  ⚠"
            problems += 1
        rows.append(f"| Dialogue `{name}` | {source_share}% | {draft_share}% | "
                    f"{draft_share - source_share:+d}pp{flag} |")

    return "\n".join(rows), problems


def check_orthography(draft: str, ortho: list[dict], limit: int) -> tuple[str, int]:
    """Did the draft reproduce the source's spellings, or repair them?"""
    lowered = draft.lower()
    rows = ["| Source norm | In draft | Repaired form in draft |", "|---|---|---|"]
    problems = 0
    for finding in ortho[:limit]:
        norm = finding["dominant"]
        kept = lowered.count(norm)
        repaired = sum(lowered.count(alt) for alt in finding["alternatives"])
        if kept == 0 and repaired == 0:
            continue
        flag = "  ⚠" if repaired > kept else ""
        if repaired > kept:
            problems += 1
        rows.append(f"| `{norm}` | ×{kept} | ×{repaired}{flag} |")
    if len(rows) == 2:
        return "No tracked orthographic forms appeared in the draft.", 0
    return "\n".join(rows), problems


# --------------------------------------------------------------------------- #


def expand(patterns: list[str]) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        matches = [Path(p) for p in glob.glob(pattern)]
        paths.extend(matches or ([Path(pattern)] if Path(pattern).exists() else []))
    if not paths:
        sys.exit(f"no files matched: {' '.join(patterns)}")
    return sorted(paths)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("measure", help="produce the overview.md tables from source files")
    m.add_argument("files", nargs="+")
    m.add_argument("--limit", type=int, default=15, help="max orthography findings to print")

    c = sub.add_parser("check", help="compare a draft against the source fingerprint")
    c.add_argument("draft")
    c.add_argument("--against", nargs="+", required=True)
    c.add_argument("--limit", type=int, default=15)

    args = ap.parse_args()

    if args.cmd == "measure":
        docs = read(expand(args.files))
        print(render_measure(fingerprint(docs), orthography(docs), candidates(docs), args.limit))
        return

    source_docs = read(expand(args.against))
    draft_docs = read(expand([args.draft]))
    source_fp, draft_fp = fingerprint(source_docs), fingerprint(draft_docs)
    ortho = orthography(source_docs)

    table, style_problems = render_check(draft_fp, source_fp)
    ortho_table, ortho_problems = check_orthography(draft_docs[0][1], ortho, args.limit)

    print("## Style fingerprint drift\n")
    print(table)
    print("\n## Orthography\n")
    print(ortho_table)
    total = style_problems + ortho_problems
    print(f"\n**{total} feature(s) outside tolerance.**"
          if total else "\n**Draft matches the source fingerprint.**")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
