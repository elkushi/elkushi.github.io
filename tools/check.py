"""Checks the built site before it is deployed.

Three things: every local link and asset exists, every page carries the content
security policy, and the CSS and markup still obey the design system
(moustafa-portfolio-design-system.html, section 07 · Usage).

Rule 1 — at most one phrase of a headline in accent-violet-text — is not
checked here; it needs a human eye on the rendered page.

Run: python3 tools/check.py
"""
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
errors = []

PAGES = [p for p in sorted(SITE.glob("**/*.html"))
         if "content" not in p.parts and ".git" not in p.parts]

for page in PAGES:
    html = page.read_text(encoding="utf-8")
    rel = page.relative_to(SITE)
    if "Content-Security-Policy" not in html:
        errors.append(f"{rel}: no CSP")
    for ref in re.findall(r'(?:href|src|poster|srcset)="([^"]+)"', html):
        for part in ref.split(","):
            url = part.strip().split(" ")[0].split("#")[0].split("?")[0]
            if not url or re.match(r"^(https?:|mailto:|data:)", url):
                continue
            if not (page.parent / url).resolve().exists():
                errors.append(f"{rel}: missing {url}")

    # Rule 2: accent-violet fills the one primary action of a view. A view is
    # the hero or one section: the home page has one in each of those two.
    for view in re.split(r"<(?=section\b|header class=\"hero)", html):
        primaries = len(re.findall(r'class="[^"]*\bbtn-primary\b', view))
        if primaries > 1:
            errors.append(f"design rule 2: {rel} has {primaries} btn-primary in one view; a view gets one")

css = (SITE / "style.css").read_text(encoding="utf-8")
blocks = re.findall(r"([^{}]*)\{([^}]*)\}", css)

# Animations that loop in the background are meant to be slow. The 200-400ms
# band in rule 5 is about motion a person triggers.
AMBIENT = {"spin", "sway", "float", "drift", "pulse"}

for sel, body in blocks:
    sel = " ".join(sel.split())
    # Rule 2 again: the solid accent never carries text.
    if re.search(r"(?<![-\w])color\s*:\s*var\(--accent-violet\)", body):
        errors.append(f"design rule 2: {sel[:60]} sets text colour to accent-violet")
    # Rule 3: borders use `line`, never coloured left-border accents.
    m = re.search(r"border-left\s*:([^;]*)", body)
    if m and re.search(r"--(accent|brand)-", m.group(1)):
        errors.append(f"design rule 3: {sel[:60]} has a coloured left border")
    # Rule 5: motion a person triggers lasts 200-400ms.
    for prop, val in re.findall(r"(transition|animation)\s*:([^;]*)", body):
        if prop == "animation" and any(name in val for name in AMBIENT):
            continue
        for d in re.findall(r"(\d*\.?\d+)s", val):
            if not 0.2 <= float(d) <= 0.4:
                errors.append(f"design rule 5: {sel[:50]} {prop} {d}s is outside 200-400ms")

# Rule 4: buttons, nav pills and badges are pills.
for name in (".btn ", ".badge ", ".cta "):
    m = re.search(re.escape(name) + r"\{[^}]*\}", css)
    if m and "--radius-pill" not in m.group(0):
        errors.append(f"design rule 4: {name.strip()} is not radius-pill")

# Rule 5: the mobile gutter is space-4 (16px), and reduced motion is handled.
if not re.search(r"\.wrap\s*\{[^}]*padding:\s*0\s+var\(--space-4\)", css):
    errors.append("design rule 5: .wrap no longer uses a var(--space-4) mobile gutter")
if "prefers-reduced-motion: reduce" not in css:
    errors.append("design rule 5: no prefers-reduced-motion block")

print("\n".join(errors) or f"site check: OK ({len(PAGES)} pages)")
sys.exit(1 if errors else 0)
