"""Checks the built site before it is deployed: every local link and asset exists,
and every page carries the content security policy. Run: python3 tools/check.py"""
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
print("\n".join(errors) or "site check: OK")
sys.exit(1 if errors else 0)
