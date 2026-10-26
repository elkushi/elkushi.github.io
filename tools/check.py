"""Checks the built site before it is deployed: every local link and asset exists,
every page carries the content security policy, and the CSS still obeys the
design system (moustafa-portfolio-design-system.html, section 07 · Usage).

Rule 2 - one violet primary action per view - is not checked here: it depends on
rendered colour, and counting `.btn.primary` gives a false positive on the maroon
band, which repaints its primary button cream. Verify that one in a browser.

Run: python3 tools/check.py"""
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
errors = []
for page in sorted(SITE.glob("**/*.html")):
    if "content" in page.parts or ".git" in page.parts:
        continue
    html = page.read_text(encoding="utf-8")
    if "Content-Security-Policy" not in html:
        errors.append(f"{page.relative_to(SITE)}: no CSP")
    for ref in re.findall(r'(?:href|src|poster|srcset)="([^"]+)"', html):
        for part in ref.split(","):
            url = part.strip().split(" ")[0].split("#")[0]
            if not url or re.match(r"^(https?:|mailto:|data:)", url):
                continue
            if not (page.parent / url).resolve().exists():
                errors.append(f"{page.relative_to(SITE)}: missing {url}")

# --- design system rules ------------------------------------------------------
# Animations that loop in the background are meant to be slow; the 200-400ms band
# in rule 5 is about motion a person triggers.
AMBIENT = {"spin", "tilt", "type", "caret", "float", "drift", "pulse"}

css = (SITE / "style.css").read_text(encoding="utf-8")
blocks = re.findall(r"([^{}]*)\{([^}]*)\}", css)

for sel, body in blocks:
    sel = " ".join(sel.split())
    # Rule 3: brand-maroon is a block or a band, never a text colour.
    if re.search(r"(?<![-\w])color\s*:\s*var\(--brand-maroon\)", body):
        errors.append(f"design rule 3: {sel[:60]} sets text colour to brand-maroon")
    # Rule 4: borders use `line`, never coloured left-border accents.
    m = re.search(r"border-left\s*:([^;]*)", body)
    if m and re.search(r"--(accent|brand)-", m.group(1)):
        errors.append(f"design rule 4: {sel[:60]} has a coloured left border")
    # Rule 5: motion a person triggers lasts 200-400ms.
    for decl in re.findall(r"(transition|animation)\s*:([^;]*)", body):
        prop, val = decl
        if prop == "animation" and any(name in val for name in AMBIENT):
            continue
        for d in re.findall(r"(\d*\.?\d+)s", val):
            if not 0.2 <= float(d) <= 0.4:
                errors.append(f"design rule 5: {sel[:50]} {prop} {d}s is outside 200-400ms")

# Rule 6: the mobile gutter is space-4 (16px).
gutter = re.search(r"\.wrap\s*\{[^}]*padding:\s*0\s+var\(--space-4\)", css)
if not gutter:
    errors.append("design rule 6: .wrap no longer uses a var(--space-4) mobile gutter")

print("\n".join(errors) or "site check: OK")
sys.exit(1 if errors else 0)
