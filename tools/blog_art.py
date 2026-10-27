#!/usr/bin/env python3
"""Cover art for blog posts, in the site's own colours.

Draws a 1200x630 SVG for a post and writes a dark and a light copy, the same
pair pattern as assets/pipeline-*.svg. The colours are read from style.css,
so the art follows the design tokens if they change.

Icons come from two open icon sets, downloaded once and cached in
tools/icons/ (which is never deployed):
  lucide  ISC licence  https://lucide.dev
  tabler  MIT licence  https://tabler.io/icons
Only these two are allowed: both licences permit use without asking, and their
icons are plain line art that sits well on the site.

  python3 tools/blog_art.py cover wat-framework --motif layers --icons list-checks,bot,wrench --labels "workflows/,agent,tools/"
  python3 tools/blog_art.py cover my-post --motif flow --icons globe,braces,shield-check,file-text --gate 2
  python3 tools/blog_art.py cover my-post --motif network --icons bot,search,database,mail,file-text
  python3 tools/blog_art.py icon shield-check --set tabler      # download and cache one icon

Output: assets/blog/<slug>-dark.svg and assets/blog/<slug>-light.svg.
Use them on a page with the only-dark / only-light classes.
"""
import argparse
import math
import random
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
CACHE = SITE / "tools" / "icons"
OUT = SITE / "assets" / "blog"
W, H = 1200, 630

ICON_SETS = {
    "lucide": ("https://cdn.jsdelivr.net/npm/lucide-static@0.460.0/icons/{}.svg", "Lucide, ISC licence"),
    "tabler": ("https://cdn.jsdelivr.net/npm/@tabler/icons@3.19.0/icons/outline/{}.svg", "Tabler Icons, MIT licence"),
}
# Only drawing elements survive the clean-up: no scripts, links, styles or
# foreign content can come in with a downloaded file.
SHAPES = {"path", "circle", "rect", "line", "polyline", "polygon", "ellipse"}
GEOMETRY = {"d", "cx", "cy", "r", "rx", "ry", "x", "y", "x1", "y1", "x2", "y2", "width", "height", "points"}


# --- colours ----------------------------------------------------------------

def tokens():
    """The dark and light palettes, straight from style.css."""
    css = (SITE / "style.css").read_text()
    dark = dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", re.search(r":root \{(.*?)\n\}", css, re.S).group(1)))
    light = {**dark, **dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})",
                                         re.search(r':root\[data-theme="light"\] \{(.*?)\n\}', css, re.S).group(1)))}
    def pick(t, warm, deep):
        return {"bg0": t["surface-000"], "bg1": t["surface-100"], "card": t["surface-200"], "card2": t["surface-300"],
                "ink": t["ink"], "muted": t["ink-muted"], "line": t["line"],
                "accent": t["accent-violet"], "glow": t["accent-glow"], "warm": warm, "deep": deep}
    return {"dark": pick(dark, "#e3a53c", dark["accent-glow"]),
            "light": pick(light, light.get("accent-amber", "#c46a1c"), light.get("brand-maroon", "#6b1f2a"))}


# --- icons ------------------------------------------------------------------

def icon(name, iconset="lucide"):
    """Inner shapes of one icon on a 24x24 grid, downloaded on first use."""
    if iconset not in ICON_SETS:
        sys.exit(f"unknown icon set {iconset!r}; allowed: {', '.join(ICON_SETS)}")
    if not re.fullmatch(r"[a-z0-9-]+", name):
        sys.exit(f"bad icon name {name!r}")
    cached = CACHE / iconset / f"{name}.svg"
    if not cached.exists():
        url = ICON_SETS[iconset][0].format(name)
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                raw = r.read(200_000).decode()
        except Exception as e:
            sys.exit(f"could not download {iconset}/{name} ({e}). Browse names at "
                     + ("https://lucide.dev/icons" if iconset == "lucide" else "https://tabler.io/icons"))
        cached.parent.mkdir(parents=True, exist_ok=True)
        cached.write_text(raw)
    root = ET.fromstring(re.sub(r"<!--.*?-->", "", cached.read_text(), flags=re.S))
    out = []
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag not in SHAPES or el.get("stroke") == "none":
            continue
        attrs = " ".join(f'{k}="{v}"' for k, v in el.attrib.items() if k in GEOMETRY)
        out.append(f"<{tag} {attrs}/>")
    return "".join(out)


def parse_icon(spec):
    """'bot' or 'tabler:robot'."""
    s, _, n = spec.rpartition(":")
    return icon(n, s or "lucide")


def glyph(spec, x, y, size, colour, width=2):
    """An icon centred on (x, y), drawn as line art."""
    k = size / 24
    return (f'<g transform="translate({x - size / 2:.1f} {y - size / 2:.1f}) scale({k:.3f})" fill="none" '
            f'stroke="{colour}" stroke-width="{width / k * 1.6:.2f}" stroke-linecap="round" stroke-linejoin="round">'
            f"{parse_icon(spec)}</g>")


# --- shared pieces ----------------------------------------------------------

def frame(p, body, label, glow_at=(0.72, 0.38)):
    gx, gy = glow_at
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">
<!-- Generated by site/tools/blog_art.py. Icons: {", ".join(v[1] for v in ICON_SETS.values())}. -->
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["bg0"]}"/><stop offset="1" stop-color="{p["bg1"]}"/></linearGradient>
  <radialGradient id="glow" cx="{gx}" cy="{gy}" r="0.55"><stop offset="0" stop-color="{p["glow"]}" stop-opacity=".42"/><stop offset="1" stop-color="{p["glow"]}" stop-opacity="0"/></radialGradient>
  <radialGradient id="warm" cx="0.12" cy="0.95" r="0.5"><stop offset="0" stop-color="{p["warm"]}" stop-opacity=".18"/><stop offset="1" stop-color="{p["warm"]}" stop-opacity="0"/></radialGradient>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.3" fill="{p["line"]}"/></pattern>
  <radialGradient id="fade" cx=".5" cy=".5" r=".6"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>
  <mask id="dotmask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
</defs>
<style>
  .flow {{ animation: flow 2.4s linear infinite; }}
  .pulse {{ animation: pulse 3.2s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes flow {{ to {{ stroke-dashoffset: -40; }} }}
  @keyframes pulse {{ 50% {{ opacity: .35; }} }}
  @media (prefers-reduced-motion: reduce) {{ .flow, .pulse {{ animation: none; }} }}
</style>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#dotmask)" opacity=".7"/>
<rect width="{W}" height="{H}" fill="url(#glow)"/>
<rect width="{W}" height="{H}" fill="url(#warm)"/>
{body}
</svg>
'''


def mono(x, y, text, colour, size=18, anchor="start", weight=500):
    family = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
    return (f'<text x="{x}" y="{y}" fill="{colour}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" dominant-baseline="middle">{text}</text>')


# --- motifs -----------------------------------------------------------------

def layers(p, icons, labels, hot):
    """Stacked isometric plates: a system in layers. Good for architecture posts."""
    n = len(icons)
    w, d, thick = 400, 200, 22
    cx = 660
    gap = min(150, 420 / max(n - 1, 1))
    top = H / 2 - gap * (n - 1) / 2
    out = []
    for i in reversed(range(n)):          # bottom first, so upper plates sit on top
        cy = top + gap * i
        on = i == hot
        face = p["card2"] if on else p["card"]
        edge = p["accent"] if on else p["line"]
        L, T, R, B = (cx - w / 2, cy), (cx, cy - d / 2), (cx + w / 2, cy), (cx, cy + d / 2)
        pts = lambda *q: " ".join(f"{x:.1f},{y:.1f}" for x, y in q)
        out.append(f'<polygon points="{pts(L, B, (B[0], B[1] + thick), (L[0], L[1] + thick))}" fill="{p["bg0"]}" stroke="{edge}" stroke-width="1.5"/>')
        out.append(f'<polygon points="{pts(B, R, (R[0], R[1] + thick), (B[0], B[1] + thick))}" fill="{p["bg1"]}" stroke="{edge}" stroke-width="1.5"/>')
        out.append(f'<polygon points="{pts(L, T, R, B)}" fill="{face}" stroke="{edge}" stroke-width="{2.5 if on else 1.5}"/>')
        if on:
            out.append(f'<polygon points="{pts(L, T, R, B)}" fill="{p["glow"]}" opacity=".22" class="pulse"/>')
        # The icon lies flat on the plate: map its 24x24 grid onto the diamond.
        s = 46
        a, b, c, dd = w / (2 * s), d / (2 * s), -w / (2 * s), d / (2 * s)
        e, f = T
        out.append(f'<g transform="matrix({a:.4f} {b:.4f} {c:.4f} {dd:.4f} {e:.1f} {f:.1f}) translate({s / 2 - 12} {s / 2 - 12})" '
                   f'fill="none" stroke="{p["accent"] if on else p["ink"]}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">'
                   f"{parse_icon(icons[i])}</g>")
        if labels:
            lx = cx - w / 2 - 36
            out.append(f'<line x1="{lx + 8}" y1="{cy}" x2="{L[0] - 8}" y2="{cy}" stroke="{p["line"]}" stroke-width="1.5"/>')
            out.append(mono(lx, cy, labels[i], p["accent"] if on else p["muted"], 22, "end", 600 if on else 500))
    return "".join(out)


def flow(p, icons, labels, gate):
    """Nodes in a row, left to right, with an optional gate: a pipeline post."""
    n = len(icons)
    size, y = 132, H / 2
    span = W - 260
    xs = [130 + span * i / max(n - 1, 1) for i in range(n)]
    out = []
    for i in range(n - 1):
        x1, x2 = xs[i] + size / 2 + 10, xs[i + 1] - size / 2 - 18
        out.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{p["line"]}" stroke-width="3"/>')
        out.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{p["accent"]}" stroke-width="3" stroke-dasharray="4 16" stroke-linecap="round" class="flow"/>')
        out.append(f'<path d="M{x2} {y - 9} L{x2 + 14} {y} L{x2} {y + 9}z" fill="{p["accent"]}"/>')
    for i, x in enumerate(xs):
        on = i == gate
        r = 28
        if on:
            out.append(f'<rect x="{x - size / 2 - 14}" y="{y - size / 2 - 14}" width="{size + 28}" height="{size + 28}" rx="{r + 12}" fill="none" stroke="{p["accent"]}" stroke-width="2" stroke-dasharray="6 8" class="pulse"/>')
        out.append(f'<rect x="{x - size / 2}" y="{y - size / 2}" width="{size}" height="{size}" rx="{r}" fill="{p["card2"] if on else p["card"]}" stroke="{p["accent"] if on else p["line"]}" stroke-width="{2.5 if on else 1.5}"/>')
        out.append(glyph(icons[i], x, y, 56, p["accent"] if on else p["ink"]))
        if labels:
            out.append(mono(x, y + size / 2 + 40, labels[i], p["accent"] if on else p["muted"], 20, "middle", 600 if on else 500))
    return "".join(out)


def network(p, icons, labels, seed):
    """One agent in the middle, its tools around it: an agent post."""
    rnd = random.Random(seed)
    cx, cy = W / 2, H / 2
    k = len(icons) - 1
    # Satellites sit evenly on one wide ellipse; the seed only nudges them,
    # so two posts with the same icons still look different.
    rx, ry = 400, 205
    out = [f'<ellipse cx="{cx}" cy="{cy}" rx="{rx * f}" ry="{ry * f}" fill="none" stroke="{p["line"]}" stroke-width="1.2" opacity=".8"/>'
           for f in (.62, 1)]
    turn = rnd.uniform(0, 2 * math.pi / k)
    pts = [(cx + math.cos(t) * rx, cy + math.sin(t) * ry)
           for t in (turn + 2 * math.pi * i / k + rnd.uniform(-.12, .12) for i in range(k))]
    for x, y in pts:
        out.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{p["accent"]}" stroke-width="2.5" stroke-dasharray="4 16" stroke-linecap="round" class="flow" opacity=".85"/>')
    for i, (x, y) in enumerate(pts):
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="46" fill="{p["card"]}" stroke="{p["line"]}" stroke-width="1.5"/>')
        out.append(glyph(icons[i + 1], x, y, 40, p["ink"]))
        if labels:
            out.append(mono(x, y + 72, labels[i + 1], p["muted"], 18, "middle"))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="96" fill="{p["glow"]}" opacity=".25" class="pulse"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="74" fill="{p["card2"]}" stroke="{p["accent"]}" stroke-width="2.5"/>')
    out.append(glyph(icons[0], cx, cy, 64, p["accent"]))
    return "".join(out)


# --- commands ---------------------------------------------------------------

def cover(a):
    icons = [s.strip() for s in a.icons.split(",") if s.strip()]
    labels = [s.strip() for s in a.labels.split(",")] if a.labels else []
    if labels and len(labels) != len(icons):
        sys.exit("--labels needs one label per icon")
    if not 2 <= len(icons) <= 7:
        sys.exit("use 2 to 7 icons")
    if not re.fullmatch(r"[a-z0-9-]+", a.slug):
        sys.exit("slug: lowercase letters, digits and hyphens")
    label = a.alt or f"Cover art for {a.slug.replace('-', ' ')}"
    OUT.mkdir(parents=True, exist_ok=True)
    for theme, p in tokens().items():
        if a.motif == "layers":
            body = layers(p, icons, labels, a.hot)
        elif a.motif == "flow":
            body = flow(p, icons, labels, a.gate)
        else:
            body = network(p, icons, labels, a.seed)
        glow = (0.55, 0.5) if a.motif != "flow" else (0.5, 0.5)
        f = OUT / f"{a.slug}-{theme}.svg"
        f.write_text(frame(p, body, label.replace('"', "'"), glow))
        print(f"wrote {f.relative_to(SITE)} ({f.stat().st_size // 1024 + 1} KB)")


def fetch(a):
    icon(a.name, a.set)
    print(f"cached {a.set}/{a.name} → {(CACHE / a.set / (a.name + '.svg')).relative_to(SITE)}  ({ICON_SETS[a.set][1]})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cover", help="draw a post's cover, dark and light")
    c.add_argument("slug")
    c.add_argument("--motif", choices=["layers", "flow", "network"], default="flow")
    c.add_argument("--icons", required=True, help="comma list; 'name' is Lucide, 'tabler:name' is Tabler")
    c.add_argument("--labels", help="comma list, one short label per icon (shown in mono; keep them code-like so they work in every language)")
    c.add_argument("--hot", type=int, default=1, help="layers: which plate is highlighted (0 = top)")
    c.add_argument("--gate", type=int, default=-1, help="flow: which node is the gate (validator), -1 for none")
    c.add_argument("--seed", type=int, default=7, help="network: layout seed")
    c.add_argument("--alt", help="aria-label for the SVG")
    c.set_defaults(fn=cover)
    i = sub.add_parser("icon", help="download and cache one icon")
    i.add_argument("name")
    i.add_argument("--set", choices=list(ICON_SETS), default="lucide")
    i.set_defaults(fn=fetch)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
