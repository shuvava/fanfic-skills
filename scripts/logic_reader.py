#!/usr/bin/env python3
"""Logic and canon reader: a fresh-context Claude asks the questions an attentive fan would ask.

Standard library only. Run from the project root, in `write-chapter` at the beat gate (target =
the beat file) and in §5 before `naturalize` (target = the draft).

    python3 logic_reader.py prompt <target> --stage beats|draft --dir <out> [--beats <beat file>]
                                   [--check facts|breaks] [--examples <file>]
    python3 logic_reader.py add    <target> --dir <out> --reply <reply.json> [--reply <reply.json> ...]
    python3 logic_reader.py eval   <cases.json> --runs <dir> [--baseline <dir>]

`<out>` is `<book>/logic/<chapter stem>-<stage>/`, and `…-<stage>-breaks/` for `--check breaks`.

Why a separate reader
---------------------
`naturalize` and its outside readers judge sentences; they are not given the source and cannot
tell a canon slip from a true fact. Most of what a user corrects in a beat card or a first draft is
of another kind: a fact `raw/` does not support, a detail with no origin, a character who knows
what he could not, a plan with a shorter road the character would obviously take. The drafter
checks these against its own beliefs; a reader with fresh context and `raw/` at hand does not
share them.

Two checks
----------
`--check facts` (the default) asks whether claims hold: canon, cause and effect, who knows what,
invented specifics. `--check breaks` asks where the story's own logic breaks: it lists every event,
finds each one's cause (on the page, in an earlier chapter, in the character's profile) and what it
contradicts, and flags an event without a cause, against what the story showed, or decided off the
page. On one book the facts reader caught none of the user's eight objections of this kind (people
acting against what they just said they fear, a skilled character written as a supplicant, consent
given off the page): a reader hunting for false claims reads past a choice that contradicts no fact.
The breaks reader on the same chapters' beat files caught about half, and the user judged 27 of its
30 flags worth asking. A reader asked instead to imagine each character's best move caught one in
eight: it read the best move off the text it had just read.

The breaks reader gets the author's own past questions, if the project keeps them: `## Logic
examples` in `plan/HARNESS.md` (or `--examples <file>`). Run it twice: two runs share half their
flags, and the flags found once are as often right as the ones found twice.

What the reader gets
--------------------
`prompt.md`: the task, the target text, and where to look — `raw/`, `wiki/`, `drafts/continuity.md`,
the fic's earlier chapters. The reader is a subagent with file tools; it is given `prompt.md` as its
whole task and nothing of the drafting conversation. It returns a JSON array of
{quote, kind, question, evidence: [{file, quote}], certainty}; the breaks reader wraps it in an
object with its working (`traits`, `events`) beside `flags`.

What comes back
---------------
`add` keeps a flag only if its quote is an exact substring of the target, and marks each piece of
evidence verified or not by searching the cited file for the quoted words. A `canon` flag whose
evidence does not verify is kept but marked — the reader may have misremembered, exactly as the
drafter did. With several `--reply` files (runs of the same reader), flags that fall in the same
sentence are merged into one entry with every run's question. Writes `<out>/flags.json` and
`<out>/report.md`.

`eval` scores runs against a case file of real user objections (anchor quotes in the same
targets): a flag hits an objection when its quote falls in the same sentence as the anchor.
It prints recall by kind and lists unmatched flags for a human to judge — an unmatched flag is not
necessarily noise.

Exit codes: 0 ok, 1 unreadable reply, 3 usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_chapter import FRONTMATTER_RE, IMAGE_RE  # noqa: E402

KINDS = ("canon", "logic", "knows", "motive", "invented", "unneeded", "agency")

TASK = """You are a reader who knows the source canon well — you can look anything up — reading \
{what} of a fan continuation of that source. You are not an editor of style. You ask the questions \
an attentive fan asks when something does not add up, before the author's readers ask them.

Look for six kinds of trouble:
- canon: a fact about the world, a character or past events that the source contradicts or does \
not support. Look it up; quote the line. A hedge in the source ("примерно", "по слухам", \
"кажется") that became a flat fact counts.
- logic: cause and effect do not hold. Someone does what their situation makes impossible or \
pointless (a guard who slept through the theft \
describes the thief's face); an action has no purpose; a conclusion does not \
follow; an object behaves unlike its material.
- knows: someone knows what they could not have learned on the page or in canon; the world knows \
the hero's private discovery; locals use the narrator's words for things.
- motive: a character acts against their recorded character or interest, or takes a long road when \
an obvious short one exists (bribes a clerk for a date posted on \
the public board); a clever character is \
written as naive.
- invented: a specific — a number, a price, a fee, a custom, an institution, a name — that neither \
the source nor the wiki nor the fic's earlier chapters give. Ask where it came from.
- unneeded: a sentence that explains what the story does not need explained.

How to work:
1. Read the target. List to yourself every claim about how the world works and every specific.
2. For each, search before judging: `{raw}` (the source; grep word stems in the source's language, \
several spellings), `wiki/canon/`, `wiki/fanon/`, `drafts/continuity.md`, and the fic's earlier \
chapters under `{drafts}`. The fic's earlier chapters are canon for this fic. A claim that is \
supported is not a flag. A citation in the target ([src: …]) is a claim too: open it and check \
that the line says what the target says it says.
3. For each character's choice, ask what they want and whether a simpler way was open to them.
4. Keep only what you would put to the author as a question.
{extra}
Do NOT flag: word choice, rhythm, clumsy phrasing, punctuation, jokes that fall flat, the \
narrator's ironic pomposity. Another reader handles those.

Ten precise flags beat thirty doubtful ones. At most 20. Write `question` in the target's \
language, the way a reader would ask it aloud: «зачем…, если можно…?», «откуда он знает…?», \
«в каноне иначе: …». Evidence quotes are copied character for character from the file they cite; \
give the file path relative to the project root.

Answer with a JSON array only, nothing before or after:
[{{"quote": "<exact quote from the target, 3-25 words>",
   "kind": "canon|logic|knows|motive|invented|unneeded",
   "question": "<the question, one or two lines>",
   "evidence": [{{"file": "<path>", "quote": "<exact words from that file>"}}],
   "certainty": "high|medium"}}]
`evidence` may be empty for logic, motive and unneeded. The quote must match the target \
character for character."""

BREAKS = """You are a reader who keeps asking "why?" — you can look anything up — reading {what} of a \
fan continuation of a source. You are not an editor of style, and you do not judge whether the \
characters chose well. You look for places where the story's logic breaks: something happens \
without a cause, or contradicts what the story already showed.

How to work:
0. People first. For every named character who acts in the target, open their profile and voice \
card under `wiki/` (search by name) and copy, word for word, the lines that say how they act: \
manner, methods, rules they keep, what they never do. These go into your answer as `traits`; \
every event of theirs is checked against them.
1. Go through the target from the first line to the last and list every event: each action, \
decision, refusal, agreement, silence kept, attack, offer, and each conclusion the narrator \
draws — and each thing someone conspicuously does NOT do or say. One event per entry, in order, \
the opening scene as carefully as the last.
2. For each event, find its cause: why does this person do this, here, now? The cause must be on \
the page, or plain from an earlier chapter under `{drafts}`, the character's profile and voice \
card under `wiki/`, `drafts/continuity.md`, or the source under `{raw}`. Look it up; do not \
supply a cause the text does not give. "The plot needs it" is not a cause. When the cause is a goal \
("he does it because he wants X"), ask once more: why does he want X — is that on the page too?
3. For each event, look for what it contradicts:
   - what the same person said, feared or showed earlier in the scene or the chapter (a man who \
won't drink from a cup a sick man touched shakes the sick man's hand);
   - who the person is: their profile, their voice card, how the source and earlier chapters show \
them behaving (a proud duelist who never asks for help begs a stranger for it);
   - a reason the narrator gave before, or the stakes as they stand now (he gives an old reason \
that the new situation has undone);
   - what is at hand: the obvious means the scene itself put in front of them, ignored.
4. Mark an event that matters to the story but happens off the page — a consent, a refusal, a \
change of mind reported in a line — so the reader never sees the person decide.
5. Flag the event when its cause is missing, when it contradicts something, or when it happens \
off the page. A contradiction stays a flag when the narrator notices it or makes a joke of it: \
readers stop laughing and ask why the person did it. Flag a break even when the author chose it on \
purpose — say so in the question; the author decides whether to keep it. Not a flag: a flaw the \
character's profile records and the text shows. When an event contradicts an earlier chapter, say \
which side looks wrong: the earlier chapter may be the one to fix.
{extra}
Keep only what you would put to the author as a question. At most 15 flags, and never fewer \
than 5: if fewer breaks are clear, add the events whose cause is weakest, certainty medium. Put the quote on the \
sentence where the event happens. Write `question` in the target's language, the way a reader \
asks it aloud: «почему он…?», «но ведь она сама только что…», «а когда они это решили?» — and name \
what is missing or what it contradicts.

Answer with one JSON object only, nothing before or after:
{{"traits": [{{"who": "<character>", "file": "<profile path>", "lines": ["<copied line>", "..."]}}],
 "events": [{{"n": 1, "scene": "<scene>", "who": "<actor>", "event": "<what happens>",
   "cause": "<the cause, or 'none'>", "cause_from": "<page | file path | none>",
   "contradicts": "<what it contradicts, or empty>"}}],
 "flags": [{{"quote": "<exact quote from the target, 3-25 words>",
   "kind": "agency",
   "question": "<the question, one to three lines>",
   "evidence": [{{"file": "<path>", "quote": "<exact words from that file>"}}],
   "certainty": "high|medium"}}]}}
`evidence` holds what the event contradicts or where a cause should have been (a profile line, an \
earlier chapter); it may be empty when the scene itself shows it. The quote must match the target \
character for character."""

EXTRA = {
    "beats": "The target is a beat file: a short retelling, questions for the author with \
recommended answers, and one card per scene with its canon and fanon dependencies. Recommended \
answers and dependencies are claims to check like any other.\n",
    "outline": "The target is a piece of the book's plan: a retelling of a part or of the whole book, \
chapter rows (event, what changes, precedent) and scene rows (goal, conflict, outcome), or a planner's \
proposal with its reasons. A row compresses a chapter into a line; do not flag brevity, flag what the line \
says happens and why. Every decision, agreement, refusal, attack, request or plan in it needs a cause the \
plan gives (here, in another row, in the character's profile) or the source shows. A row that leaves a \
decision to a later chapter is a flag when no row shows that decision being made. Chapters already \
written are under `{drafts}`: what they show is fact for this fic.\n",
    "draft": "The target is a drafted chapter. Its beat file{beats} records what the drafter meant \
and what the author already decided; a decision recorded there is not a flag unless canon \
contradicts it.\n",
}


def usage(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(3)


def norm(s: str) -> str:
    # markdown emphasis is dropped: a plan is full of **bold**, and readers quote the words without it
    s = re.sub(r"[*`]", "", s.replace("ё", "е").replace("Ё", "Е"))
    return re.sub(r"\s+", " ", s).strip()


def body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if m:
        text = text[m.end():]
    return "\n".join(l for l in text.splitlines() if not IMAGE_RE.match(l.strip())).strip()


def raw_dir() -> str:
    return "raw/" if Path("raw").is_dir() else "<source directory>"


def harness_examples() -> str:
    """`## Logic examples` from plan/HARNESS.md, without its heading; empty if absent."""
    h = Path("plan/HARNESS.md")
    if not h.is_file():
        return ""
    m = re.search(r"^## Logic examples[^\n]*\n(.*?)(?=^## |\Z)", h.read_text(encoding="utf-8"), re.M | re.S)
    return m.group(1) if m else ""


def cmd_prompt(a) -> int:
    parent = a.target.parent.parent if a.target.parent.name == "snapshots" else a.target.parent
    drafts = f"{parent}/" if a.stage == "draft" else "drafts/"
    beats = f" (`{a.beats}`)" if a.beats else ""
    what = {"beats": "a beat card for one chapter", "draft": "one drafted chapter",
            "outline": "a piece of the plan"}[a.stage]
    task = {"facts": TASK, "breaks": BREAKS}[a.check].format(what=what, raw=raw_dir(), drafts=drafts,
                       extra=EXTRA[a.stage].format(beats=beats, drafts=drafts))
    examples = a.examples.read_text(encoding="utf-8") if a.examples else harness_examples()
    if a.check == "breaks" and examples.strip():
        task += ("\n\nThe author's own questions on earlier chapters — the kind of break this author "
                 "catches. Ask questions like these:\n\n" + examples.strip())
    a.dir.mkdir(parents=True, exist_ok=True)
    p = a.dir / "prompt.md"
    p.write_text(f"{task}\n\n---\n\n# TARGET: {a.target}\n\n{body(a.target)}\n", encoding="utf-8")
    print(f"wrote {p}: give it to a fresh-context subagent with file tools, as its whole task; "
          f"save its JSON reply as {a.dir / 'reply.json'} and run `add`")
    return 0


def parse(reply: str) -> list[dict]:
    m = re.search(r"\{.*\}", reply, re.S)
    if m and reply.lstrip().startswith("{"):
        # breaks check: {"traits": [...], "events": [...], "flags": [...]}; the rest is the reader's working
        try:
            reply = json.dumps(json.loads(m.group(0)).get("flags", []))
        except json.JSONDecodeError:
            pass
    m = re.search(r"\[.*\]", reply, re.S)
    if not m:
        raise ValueError("no JSON array in the reply")
    return [i for i in json.loads(m.group(0)) if isinstance(i, dict) and isinstance(i.get("quote"), str)]


def verify(ev: dict) -> bool:
    f, q = Path(str(ev.get("file", "")).split("#")[0]), norm(str(ev.get("quote", "")))
    if not q or not f.is_file():
        return False
    return q in norm(f.read_text(encoding="utf-8"))


def cmd_add(a) -> int:
    flat = norm(body(a.target))
    kept, by_sentence, returned, inexact = [], {}, 0, 0
    for run, reply in enumerate(a.reply, 1):
        try:
            flags = parse(reply.read_text(encoding="utf-8"))
        except (ValueError, json.JSONDecodeError) as e:
            print(f"unreadable reply {reply} ({e})", file=sys.stderr)
            return 1
        returned += len(flags)
        for f in flags:
            at = locate(flat, f["quote"])
            if not at:
                inexact += 1
                continue
            key = sentence_span(flat, *at)
            if key in by_sentence:  # the same sentence flagged again (another run, or a long plan row): one entry
                first = by_sentence[key]
                first["runs"] = sorted(set(first["runs"]) | {run})
                if f.get("question") and f["question"] != first.get("question"):
                    first.setdefault("also", []).append(f["question"])
                continue
            f["kind"] = f.get("kind") if f.get("kind") in KINDS else "logic"
            f["evidence"] = [dict(e, verified=verify(e)) for e in f.get("evidence") or [] if isinstance(e, dict)]
            f["unverified"] = f["kind"] == "canon" and not any(e["verified"] for e in f["evidence"])
            f["runs"] = [run]
            by_sentence[key] = f
            kept.append(f)
    rec = {"target": str(a.target), "runs": len(a.reply), "returned": returned,
           "dropped_inexact": inexact, "flags": kept}
    (a.dir / "flags.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    out = [f"# Logic reader — {a.target}\n\n{len(kept)} flag(s) from {len(a.reply)} run(s), "
           f"{inexact} dropped as inexact quotes.\n"]
    for k, f in enumerate(kept, 1):
        mark = " — evidence not found in the cited file" if f["unverified"] else ""
        both = f" (runs {', '.join(map(str, f['runs']))})" if len(a.reply) > 1 else ""
        out.append(f"\n## {k}. [{f['kind']}] «{f['quote']}»{mark}{both}\n\n{f.get('question', '')}\n")
        for q in f.get("also", []):
            out.append(f"\n{q}\n")
        for e in f["evidence"]:
            out.append(f"\n- {'✓' if e['verified'] else '✗'} `{e.get('file')}`: «{e.get('quote')}»")
        out.append("\n")
    (a.dir / "report.md").write_text("".join(out), encoding="utf-8")
    unver = sum(f["unverified"] for f in kept)
    print(f"wrote {a.dir / 'report.md'}: {len(kept)} flag(s) from {len(a.reply)} run(s), {inexact} inexact "
          f"dropped, {unver} canon flag(s) with unverified evidence")
    return 0


def sentence_span(flat: str, i: int, j: int) -> tuple[int, int]:
    """Widen [i, j) to the sentence (or markdown line) around it."""
    s = max(flat.rfind(c, 0, i) for c in ".!?…\n") + 1
    ends = [k for k in (flat.find(c, j) for c in ".!?…\n") if k >= 0]
    return s, (min(ends) + 1 if ends else len(flat))


def locate(flat: str, quote: str) -> tuple[int, int] | None:
    q = norm(quote)
    i = flat.find(q)
    return (i, i + len(q)) if q and i >= 0 else None


def hits(flat: str, anchor: str, quotes: list[str]) -> list[int]:
    a = locate(flat, anchor)
    if not a:
        return []
    s, e = sentence_span(flat, *a)
    out = []
    for n, q in enumerate(quotes):
        b = locate(flat, q)
        if b and b[0] < e and b[1] > s:
            out.append(n)
    return out


def cmd_eval(a) -> int:
    cases = json.loads(a.cases.read_text(encoding="utf-8"))["cases"]
    total, found, base_found = {}, {}, {}
    unmatched_all = 0
    flags_all = 0
    lines = []
    for c in cases:
        run = a.runs / c["id"]
        tgt = run / "target.md"
        rec_p = run / "flags.json"
        if not tgt.is_file() or not rec_p.is_file():
            lines.append(f"\n{c['id']}: no run ({run})")
            continue
        # anchors and flags are located in the same text the reader saw
        flat = norm(tgt.read_text(encoding="utf-8"))
        flags = json.loads(rec_p.read_text(encoding="utf-8"))["flags"]
        quotes = [f["quote"] for f in flags]
        base_quotes = []
        if a.baseline and (a.baseline / f"{c['id']}.json").is_file():
            base_quotes = json.loads((a.baseline / f"{c['id']}.json").read_text(encoding="utf-8"))
        matched = set()
        flags_all += len(flags)
        lines.append(f"\n## {c['id']} — {len(flags)} flag(s)")
        for it in c["items"]:
            k = it["kind"]
            total[k] = total.get(k, 0) + 1
            # a beat file states one problem in several places (summary, card): any of them counts
            anchors = it["anchor"] if isinstance(it["anchor"], list) else [it["anchor"]]
            if not any(locate(flat, x) for x in anchors):
                lines.append(f"  ! {it['id']}: anchor not in target")
                continue
            h = sorted({n for x in anchors for n in hits(flat, x, quotes)})
            bh = [n for x in anchors for n in hits(flat, x, base_quotes)]
            matched.update(h)
            if h:
                found[k] = found.get(k, 0) + 1
            if bh:
                base_found[k] = base_found.get(k, 0) + 1
            mark = "HIT " if h else "miss"
            lines.append(f"  {mark} {it['id']} [{k}] «{anchors[0]}»" + ("  (baseline hit)" if bh else ""))
            for n in h:
                lines.append(f"       ↳ [{flags[n]['kind']}] {flags[n].get('question', '')}")
        rest = [f for n, f in enumerate(flags) if n not in matched]
        unmatched_all += len(rest)
        for f in rest:
            lines.append(f"  ?    [{f['kind']}] «{f['quote']}» — {f.get('question', '')}")
    n_total, n_found, n_base = sum(total.values()), sum(found.values()), sum(base_found.values())
    print(f"recall {n_found}/{n_total}" + (f" (baseline {n_base}/{n_total})" if a.baseline else "")
          + f"; flags {flags_all}, unmatched {unmatched_all} (judge by hand)")
    for k in list(KINDS) + sorted(set(total) - set(KINDS)):
        if k in total:
            b = f", baseline {base_found.get(k, 0)}" if a.baseline else ""
            print(f"  {k:9} {found.get(k, 0)}/{total[k]}{b}")
    print("\n".join(lines))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prompt")
    p.add_argument("target", type=Path)
    p.add_argument("--stage", choices=("beats", "draft", "outline"), required=True)
    p.add_argument("--dir", type=Path, required=True, help="<book>/logic/<stem>-<stage>/")
    p.add_argument("--beats", type=Path, help="draft stage: the chapter's beat file")
    p.add_argument("--examples", type=Path,
                   help="breaks: the author's past logic questions (default: ## Logic examples in plan/HARNESS.md)")
    p.add_argument("--check", choices=("facts", "breaks"), default="facts",
                   help="facts: canon and logic (default); breaks: events without a cause, against what "
                        "the story showed, or decided off the page")
    p = sub.add_parser("add")
    p.add_argument("target", type=Path)
    p.add_argument("--dir", type=Path, required=True)
    p.add_argument("--reply", type=Path, required=True, action="append",
                   help="the subagent's JSON reply; repeat for several runs, merged by sentence")
    p = sub.add_parser("eval")
    p.add_argument("cases", type=Path)
    p.add_argument("--runs", type=Path, required=True, help="one dir per case id: target.md, flags.json")
    p.add_argument("--baseline", type=Path, help="<case id>.json: list of quotes the old pipeline flagged")
    a = ap.parse_args()
    if a.cmd in ("prompt", "add") and not a.target.is_file():
        usage(f"no such file: {a.target}")
    return {"prompt": cmd_prompt, "add": cmd_add, "eval": cmd_eval}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
