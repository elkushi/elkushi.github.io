"""Builds the static portfolio pages from content/*.html fragments.

Each page shares the same head, nav and footer. Output is plain HTML in the
site root, ready for GitHub Pages. Run: python3 tools/build.py
"""
import base64
import hashlib
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
CONTENT = SITE / "content"

EMAIL = "moustafa.elkoushy7@gmail.com"
GITHUB = "https://github.com/elkushi"

# The one inline script on the site. Its hash goes in the CSP, so the policy can
# refuse every other inline script without needing 'unsafe-inline'.
BOOT_JS = ('var d=document.documentElement;d.classList.add("js");'
           'try{var t=localStorage.getItem("theme");if(t)d.dataset.theme=t}catch(e){}')
BOOT_HASH = "sha256-" + base64.b64encode(hashlib.sha256(BOOT_JS.encode()).digest()).decode()

# default-src 'none' blocks anything not listed. Styles need 'unsafe-inline'
# because a few elements carry a style attribute; scripts do not.
CSP = (
    "default-src 'none'; "
    f"script-src 'self' '{BOOT_HASH}'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "media-src 'self'; "
    "base-uri 'none'; "
    "form-action 'none'"
)

PAGES = {
    "index.html": ("Moustafa Elkoushy · AI Product Engineer",
                   "AI product engineer. I build AI products from design to production, and I make the AI check its own work."),
    "work/ritorica.html": ("ritorica.com: from a blank page to production · Moustafa Elkoushy",
                           "How I designed, built, deployed and secured a company website on Django CMS, alone."),
    "work/video-generator.html": ("AI video and image generator · Moustafa Elkoushy",
                                  "A Claude Code app that turns a brand kit and a topic into short videos and image posts."),
    "work/seo-audit.html": ("Website audit for Google and AI search · Moustafa Elkoushy",
                            "A web app that audits a website for Google, answer engines and AI search, and gives copy-paste fixes."),
    "work/research-workflow.html": ("A market report where every claim has a source · Moustafa Elkoushy",
                                    "A Claude Code research workflow with a validator that blocks unsourced claims and dead links."),
}


EXTERNAL = re.compile(r'<a href="(https?://[^"]+)"(?![^>]*target=)')


def external_new_tab(html: str) -> str:
    """Every link that leaves the site opens in a new tab.

    rel="noopener" stops the new page reaching back through window.opener;
    noreferrer keeps the referring URL out of the request.
    """
    return EXTERNAL.sub(r'<a href="\1" target="_blank" rel="noopener noreferrer"', html)


def page(path, title, desc, body):
    body = external_new_tab(body)
    up = "../" * path.count("/")
    current = lambda target: ' aria-current="page"' if path == target else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta name="color-scheme" content="light dark">
<meta property="og:image" content="https://elkushi.github.io/assets/portrait-900.webp">
<link rel="preload" href="{up}assets/fonts/Unbounded.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{up}assets/fonts/SpaceGrotesk.woff2" as="font" type="font/woff2" crossorigin>
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" href="{up}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{up}style.css">
<script>{BOOT_JS}</script>
</head>
<body>
<header class="nav">
  <div class="wrap">
    <a class="brand" href="{up}index.html"><img src="{up}assets/portrait-520.webp" width="30" height="30" alt=""><span>Moustafa Elkoushy</span></a>
    <nav aria-label="Main">
      <ul>
        <li><a href="{up}index.html#work"{current("index.html")}>Work</a></li>
        <li class="hide-sm"><a href="{up}index.html#security">Security</a></li>
        <li><a href="{up}index.html#about">About</a></li>
        <li><a href="{up}index.html#contact">Contact</a></li>
        <li><button class="theme-toggle" type="button" aria-label="Switch between light and dark theme"><svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg><svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button></li>
      </ul>
    </nav>
  </div>
</header>
<main>
{body}
</main>
<footer>
  <div class="wrap">
    <span>Moustafa Elkoushy · <a href="mailto:{EMAIL}">{EMAIL}</a> · <a href="{GITHUB}" target="_blank" rel="noopener noreferrer">GitHub</a></span>
    <span>Plain HTML and CSS. No framework, no tracking.</span>
  </div>
</footer>
<script src="{up}reveal.js" defer></script>
</body>
</html>
"""


if __name__ == "__main__":
    for path, (title, desc) in PAGES.items():
        src = CONTENT / path.replace("/", "__")
        out = SITE / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(path, title, desc, src.read_text(encoding="utf-8")), encoding="utf-8")
        print("built", path)
