#!/usr/bin/env python3
"""Compose a book cover locally: background + author + title + series number + optional emblem.

Written by the `cover` skill. Text is set here with a real font, never by an image model — models
misspell Cyrillic and cannot be trusted with a name. The background is either procedural aged
parchment (free, offline) or an image the user generated or supplied (`--background art.png`).

  compose_cover.py --author "Варп" --title "Ядро души" --series "Ядро души" --number 4 \
      --emblem plan/cover/emblem.svg --out plan/cover/cover-r1.jpg

  compose_cover.py --check plan/cover/cover.jpg          # validate an existing file only

Needs ImageMagick 7 (`magick`) on PATH, and `rsvg-convert` (librsvg) for SVG emblems. Nothing else outside the standard library.

The output is checked against the platform limits (--min-w/--min-h/--max-mb; defaults are the rule
the user gave: at least 200x285 px, at most 15 MB) and a report is printed.

Exit codes: 0 written and within limits, 2 written but outside a limit, 3 usage or magick error.
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SERIF = ["/System/Library/Fonts/Supplemental/Times New Roman.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
         "/usr/share/fonts/TTF/DejaVuSerif.ttf"]
SERIF_BOLD = ["/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
              "/usr/share/fonts/TTF/DejaVuSerif-Bold.ttf"]


def first_existing(paths):
    return next((p for p in paths if Path(p).is_file()), None)


def magick(*args):
    r = subprocess.run(["magick", *map(str, args)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"magick failed: {' '.join(map(str, args))[:300]}\n{r.stderr.strip()}")
    return r.stdout.strip()


def parchment(path, w, h, seed, ink, tmp):
    """Aged paper: mottled fibre, darker blotches, burnt edges, fine grain."""
    t = Path(tmp)
    magick("-size", f"{w}x{h}", "-seed", seed, "plasma:fractal", "-colorspace", "gray",
           "-blur", "0x3", "-auto-level", "-level", "20%,80%", t / "noise.png")
    magick("-size", f"{w}x{h}", "-seed", seed + 4, "plasma:fractal", "-colorspace", "gray",
           "-blur", f"0x{max(w, h) // 30}", "-auto-level", t / "blot.png")
    magick(t / "noise.png", t / "blot.png", "-compose", "multiply", "-composite", "-auto-level",
           "-level", "0%,100%,1.6", "+level-colors", "#b98d4f,#f4e2b4", t / "base.png")
    m = max(w, h) // 30
    magick("-size", f"{w}x{h}", "xc:black", "-fill", "white",
           "-draw", f"rectangle {m},{m} {w - m},{h - m}", "-blur", f"0x{max(w, h) // 20}", t / "edge.png")
    magick("-size", f"{w}x{h}", "-seed", seed + 9, "xc:", "+noise", "Random", "-colorspace", "gray",
           "-blur", "0x0.6", "-level", "40%,60%", t / "grain.png")
    magick(t / "base.png",
           "(", t / "edge.png", "+level-colors", "#5e3a12,white", ")", "-compose", "multiply", "-composite",
           "(", t / "grain.png", "+level-colors", "#e2d6bc,white", ")", "-compose", "multiply", "-composite",
           path)


def fit_background(src, path, w, h):
    """Cover-crop a supplied image to exactly w x h, centred."""
    magick(src, "-resize", f"{w}x{h}^", "-gravity", "center", "-extent", f"{w}x{h}", path)


def frame(path, w, h, ink):
    """Double rule with small corner squares, drawn in ink."""
    o, i = round(w * 0.045), round(w * 0.06)
    s, lw = round(w * 0.02), max(1, round(w * 0.003))
    draw = [f"rectangle {o},{o} {w - o},{h - o}", f"rectangle {i},{i} {w - i},{h - i}"]
    for x, y in [(o, o), (w - o, o), (o, h - o), (w - o, h - o)]:
        draw.append(f"rectangle {x - s // 2},{y - s // 2} {x + s // 2},{y + s // 2}")
    magick(path, "-fill", "none", "-stroke", ink, "-strokewidth", lw,
           *sum((["-draw", d] for d in draw), []), "-channel", "RGB", path)


def text_box(path, text, font, box_w, box_h, y, ink, w, max_pt):
    """Set text, auto-fitted into box_w x box_h, its top at vertical position y. A literal \\n in
    the text is a line break the author chose (caption: would otherwise break wherever it fits)."""
    text = text.replace("\\n", "\n")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        tile = f.name
    magick("-background", "none", "-fill", ink, "-font", font, "-size", f"{box_w}x{box_h}",
           "-gravity", "center", f"caption:{text}", tile)
    # caption: picks the largest size that fits; cap it so a short word does not fill the box
    pt = float(magick(tile, "-format", "%[caption:pointsize]", "info:") or 0)
    if max_pt and pt > max_pt:
        magick("-background", "none", "-fill", ink, "-font", font, "-pointsize", max_pt,
               "-size", f"{box_w}x", "-gravity", "center", f"caption:{text}", tile)
    magick(path, tile, "-gravity", "north", "-geometry", f"+0+{y}", "-compose", "over", "-composite", path)
    Path(tile).unlink()


def emblem(path, src, w, h, width_frac, y_frac):
    ew = round(w * width_frac)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        tile = f.name
    if Path(src).suffix.lower() == ".svg" and shutil.which("rsvg-convert"):
        # ImageMagick's built-in SVG renderer silently draws nothing for many files
        r = subprocess.run(["rsvg-convert", "-w", str(ew), "-o", tile, src], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"rsvg-convert failed on {src}\n{r.stderr.strip()}")
    else:
        magick("-background", "none", "-density", 300, src, "-resize", f"{ew}x{ew}", tile)
    if float(magick(tile, "-alpha", "extract", "-format", "%[fx:mean]", "info:")) == 0:
        sys.exit(f"emblem {src} rendered empty; install librsvg (rsvg-convert) or pass a PNG")
    eh = int(magick(tile, "-format", "%h", "info:"))
    magick(path, tile, "-gravity", "north", "-geometry", f"+0+{round(h * y_frac - eh / 2)}",
           "-compose", "over", "-composite", path)
    Path(tile).unlink()


def usage(ap, msg):
    ap.print_usage(sys.stderr)
    print(f"{ap.prog}: error: {msg}", file=sys.stderr)
    sys.exit(3)


def check(path, min_w, min_h, max_mb):
    w, h = map(int, magick(path, "-format", "%w %h", "info:").split())
    fmt = magick(path, "-format", "%m", "info:")
    size = Path(path).stat().st_size
    problems = []
    if w < min_w or h < min_h:
        problems.append(f"too small: {w}x{h} < {min_w}x{min_h}")
    if size > max_mb * 1024 * 1024:
        problems.append(f"too large: {size / 1048576:.2f} MB > {max_mb} MB")
    print(f"{path}: {fmt} {w}x{h} ratio {w / h:.3f} {size / 1048576:.2f} MB")
    print(f"limits: >= {min_w}x{min_h} px, <= {max_mb} MB -> " + ("OK" if not problems else "; ".join(problems)))
    return 0 if not problems else 2


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", metavar="FILE", help="only validate an existing cover file")
    ap.add_argument("--author")
    ap.add_argument("--title")
    ap.add_argument("--series", help="series name; with --number gives e.g. «Ядро души» · Книга 4")
    ap.add_argument("--number", help="number of this book in the series")
    ap.add_argument("--number-label", default="Книга", help="word before the number (default Книга)")
    ap.add_argument("--series-line", help="override the whole bottom line, verbatim")
    ap.add_argument("--emblem", help="SVG/PNG drawn centred between title and series line")
    ap.add_argument("--emblem-width", type=float, default=0.55, help="fraction of cover width (default 0.55)")
    ap.add_argument("--emblem-y", type=float, default=0.60, help="emblem centre, fraction of height (default 0.60)")
    ap.add_argument("--background", default="parchment", help="'parchment' or an image file (cover-cropped)")
    ap.add_argument("--no-frame", action="store_true", help="skip the double rule border")
    ap.add_argument("--scrim", action="store_true",
                    help="lighten the text zones of a busy art background so text stays readable")
    ap.add_argument("--ink", default="#1b120a", help="text/frame colour (default near-black brown)")
    ap.add_argument("--font", default=first_existing(SERIF), help="font file for author and series line")
    ap.add_argument("--font-title", default=first_existing(SERIF_BOLD), help="font file for the title")
    ap.add_argument("--author-y", type=float, default=0.10, help="top of the author line, fraction of height")
    ap.add_argument("--title-y", type=float, default=0.20, help="top of the title, fraction of height")
    ap.add_argument("--title-h", type=float, default=0.13, help="title box height, fraction of height")
    ap.add_argument("--series-y", type=float, default=0.875, help="top of the series line, fraction of height")
    ap.add_argument("--size", default="1200x1800", help="WxH in pixels (default 1200x1800, 2:3)")
    ap.add_argument("--seed", type=int, default=7, help="parchment texture seed")
    ap.add_argument("--quality", type=int, default=92, help="JPEG quality")
    ap.add_argument("--out", help="output file (.jpg or .png)")
    ap.add_argument("--min-w", type=int, default=200)
    ap.add_argument("--min-h", type=int, default=285)
    ap.add_argument("--max-mb", type=float, default=15)
    a = ap.parse_args()

    if not shutil.which("magick"):
        sys.exit("ImageMagick 7 (`magick`) not found on PATH")
    if a.check:
        sys.exit(check(a.check, a.min_w, a.min_h, a.max_mb))
    missing = [n for n in ("author", "title", "out") if not getattr(a, n)]
    if not (a.series_line or a.number):
        missing.append("number (or series-line)")
    if missing:
        usage(ap, "required: " + ", ".join("--" + m for m in missing))
    for label, f in (("--font", a.font), ("--font-title", a.font_title)):
        if not f or not Path(f).is_file():
            usage(ap, f"{label}: no font file found; pass a TTF/OTF that has the book's alphabet")

    w, h = map(int, a.size.lower().split("x"))
    series_line = a.series_line or (
        f"«{a.series}» · {a.number_label} {a.number}" if a.series else f"{a.number_label} {a.number}")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        canvas = Path(tmp) / "canvas.png"
        if a.background == "parchment":
            parchment(canvas, w, h, a.seed, a.ink, tmp)
        else:
            fit_background(a.background, canvas, w, h)
        if a.scrim:
            # soft pale bands behind the text zones; drawn on a transparent full-size layer and
            # blurred so they fade out instead of ending in a hard edge
            bands = [f"rectangle -50,{round(h * y0)} {w + 50},{round(h * y1)}"
                     for y0, y1 in ((0.08, 0.32), (0.86, 0.93))]
            magick(canvas, "(", "-size", f"{w}x{h}", "xc:none", "-fill", "rgba(244,226,180,0.6)",
                   *sum((["-draw", b] for b in bands), []), "-blur", f"0x{round(h * 0.025)}", ")",
                   "-compose", "over", "-composite", canvas)
        if not a.no_frame:
            frame(canvas, w, h, a.ink)
        tw = round(w * 0.78)
        # layout mirrors a classic typographic cover: author on top, title under it, emblem centre,
        # series and number at the foot
        text_box(canvas, a.author.upper(), a.font, tw, round(h * 0.085), round(h * a.author_y), a.ink, w,
                 round(h * 0.06))
        text_box(canvas, a.title, a.font_title, tw, round(h * a.title_h), round(h * a.title_y), a.ink, w,
                 round(h * 0.065))
        if a.emblem:
            emblem(canvas, a.emblem, w, h, a.emblem_width, a.emblem_y)
        text_box(canvas, series_line, a.font, round(w * 0.70), round(h * 0.04), round(h * a.series_y), a.ink, w,
                 round(h * 0.028))
        opts = ["-quality", a.quality, "-sampling-factor", "4:2:0", "-strip"] if out.suffix.lower() in (
            ".jpg", ".jpeg") else ["-strip"]
        magick(canvas, "-colorspace", "sRGB", *opts, out)
    sys.exit(check(out, a.min_w, a.min_h, a.max_mb))


if __name__ == "__main__":
    main()
