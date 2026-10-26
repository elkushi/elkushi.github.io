"""Builds the static portfolio from content/*.html fragments, in three languages.

Output is plain HTML ready for GitHub Pages:

    index.html, work/*.html          English, at the root
    ar/index.html, ar/work/*.html    Arabic, right to left
    ru/index.html, ru/work/*.html    Russian

Each page shares the same head, nav and footer, and carries hreflang links to
its siblings. Run: python3 tools/build.py
"""
import base64
import hashlib
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
CONTENT = SITE / "content"
ORIGIN = "https://elkushi.github.io"

EMAIL = "moustafa.elkoushy7@gmail.com"
GITHUB = "https://github.com/elkushi"
# The t.me username. No phone number: CLAUDE.md keeps that off public pages.
TELEGRAM = "Elkushi99"
TG_URL = f"https://t.me/{TELEGRAM}" if TELEGRAM else ""

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

# The work pages, in the order they appear on the home page.
# The tool logos. Inlined into every page rather than referenced as a file:
# browsers refuse cross-document <use> for SVG, and the CSP forbids it anyway.
SPRITE = (SITE / "assets" / "logos.svg").read_text(encoding="utf-8")

WORK = ["ritorica", "video-generator", "seo-audit", "research-workflow", "design-system"]

LOCALES = {
    "en": {
        "lang": "en", "rtl": False, "name": "English", "short": "EN",
        "nav": ["Work", "Skills", "Security", "Experience", "Contact"],
        "connect": "Let's connect",
        "theme": "Switch between light and dark theme",
        "lang_label": "Language", "main_nav": "Main",
        "footer": "Hand-written HTML, CSS and a little JavaScript. No framework, no tracking.",
        "font_preload": ["Outfit.woff2", "JetBrainsMono-500.woff2"],
        "titles": {
            "index.html": ("Moustafa Elkoushy · AI Product Engineer",
                           "AI product engineer. I turn bold AI ideas into real-world products, and I make the AI check its own work."),
            "work/index.html": ("All work · Moustafa Elkoushy",
                                "Every project, grouped: AI products, web development, design and security."),
            "work/ritorica.html": ("ritorica.com: rebuilt alone, and still running · Moustafa Elkoushy",
                                   "Sole designer and developer: Figma file, Django CMS build, launch, server and everything since."),
            "work/video-generator.html": ("An AI studio that makes a branded video for nothing per video · Moustafa Elkoushy",
                                          "One brief in; a finished video or image post out, in English, Arabic or Russian. Every paid API has a free or local fallback."),
            "work/seo-audit.html": ("Audits a 25-page site in under a minute, for Google and AI search · Moustafa Elkoushy",
                                    "Three scores, a to-do list ranked by impact, and code to paste in. A real run: 25 pages in 57 seconds, scored 76 out of 100."),
            "work/research-workflow.html": ("A 61-page competitor report with a source behind every claim · Moustafa Elkoushy",
                                            "Nine research agents in parallel, about 190 sources, 400+ cited claims, and a validator that blocks the rest."),
            "work/design-system.html": ("One brand system, replacing three blues and four button shapes · Moustafa Elkoushy",
                                        "The brand and UI system behind Ritorica's website, decks, emails, events and print work."),
        },
    },
    "ar": {
        "lang": "ar", "rtl": True, "name": "العربية", "short": "ع",
        "nav": ["الأعمال", "المهارات", "الأمان", "الخبرة", "تواصل"],
        "connect": "لنتواصل",
        "theme": "التبديل بين الوضع الفاتح والداكن",
        "lang_label": "اللغة", "main_nav": "القائمة الرئيسية",
        "footer": "HTML وCSS وقليل من JavaScript، مكتوبة يدويًا. بلا إطار عمل، وبلا تتبّع.",
        "font_preload": ["Cairo-arabic.woff2", "Cairo-latin.woff2"],
        "titles": {
            "index.html": ("مصطفى القوشي · مهندس منتجات ذكاء اصطناعي",
                           "مهندس منتجات ذكاء اصطناعي. أحوّل أفكار الذكاء الاصطناعي الجريئة إلى منتجات تعمل في الواقع، وأجعل النموذج يراجع عمله بنفسه."),
            "work/index.html": ("كل الأعمال · مصطفى القوشي",
                                "كل المشاريع مصنّفة: منتجات ذكاء اصطناعي، وتطوير ويب، وتصميم، وأمان."),
            "work/ritorica.html": ("ritorica.com: أعدت بناءه بمفردي، وما زال يعمل · مصطفى القوشي",
                                   "المصمّم والمطوّر الوحيد: من ملف Figma والبناء على Django CMS إلى الإطلاق والخادم وكل ما تلاهما."),
            "work/video-generator.html": ("استوديو بالذكاء الاصطناعي يُنتج فيديو بهوية العلامة دون أي تكلفة للفيديو الواحد · مصطفى القوشي",
                                          "طلب واحد يدخل، وفيديو أو منشور مصوّر جاهز يخرج، بالإنجليزية أو العربية أو الروسية. ولكل واجهة برمجية مدفوعة بديل مجاني أو محلي."),
            "work/seo-audit.html": ("يفحص موقعًا من 25 صفحة في أقل من دقيقة، لجوجل وللبحث بالذكاء الاصطناعي · مصطفى القوشي",
                                    "ثلاث نتائج، وقائمة مهام مرتّبة حسب الأثر، وكود جاهز للّصق. في تشغيل حقيقي: 25 صفحة في 57 ثانية، ونتيجة 76 من 100."),
            "work/research-workflow.html": ("تقرير منافسين من 61 صفحة، وخلف كل ادعاء مصدر · مصطفى القوشي",
                                            "تسعة وكلاء بحث بالتوازي، ونحو 190 مصدرًا، وأكثر من 400 ادعاء موثّق، ومدقّق يوقف كل ما عدا ذلك."),
            "work/design-system.html": ("نظام هوية واحد بدل ثلاث درجات من الأزرق وأربعة أشكال للأزرار · مصطفى القوشي",
                                        "نظام الهوية والواجهة الذي بُني عليه موقع Ritorica وعروضها ورسائلها البريدية وفعالياتها ومطبوعاتها."),
        },
    },
    "ru": {
        "lang": "ru", "rtl": False, "name": "Русский", "short": "RU",
        "nav": ["Работы", "Навыки", "Безопасность", "Опыт", "Контакты"],
        "connect": "Связаться",
        "theme": "Переключить светлую и тёмную тему",
        "lang_label": "Язык", "main_nav": "Главное меню",
        "footer": "HTML, CSS и немного JavaScript, написанные вручную. Без фреймворков и без трекинга.",
        "font_preload": ["Manrope-cyrillic.woff2", "Manrope-latin.woff2"],
        "titles": {
            "index.html": ("Мустафа Элькуши · AI Product Engineer",
                           "AI Product Engineer. Превращаю смелые идеи с ИИ в работающие продукты и заставляю ИИ проверять собственную работу."),
            "work/index.html": ("Все работы · Мустафа Элькуши",
                                "Все проекты по группам: ИИ-продукты, веб-разработка, дизайн и безопасность."),
            "work/ritorica.html": ("ritorica.com: пересобрал в одиночку и до сих пор веду · Мустафа Элькуши",
                                   "Единственный дизайнер и разработчик: макет в Figma, сборка на Django CMS, запуск, сервер и всё, что было после."),
            "work/video-generator.html": ("ИИ-студия, в которой брендированное видео ничего не стоит · Мустафа Элькуши",
                                          "На входе один бриф, на выходе готовое видео или пост на английском, арабском или русском. У каждого платного API есть бесплатная или локальная замена."),
            "work/seo-audit.html": ("Аудит сайта из 25 страниц меньше чем за минуту — для Google и ИИ-поиска · Мустафа Элькуши",
                                    "Три оценки, список задач по важности и готовый код для вставки. Реальный запуск: 25 страниц за 57 секунд, оценка 76 из 100."),
            "work/research-workflow.html": ("Отчёт о конкурентах на 61 страницу с источником за каждым утверждением · Мустафа Элькуши",
                                            "Девять исследовательских агентов параллельно, около 190 источников, больше 400 утверждений со ссылками и валидатор, который отсекает всё остальное."),
            "work/design-system.html": ("Одна бренд-система вместо трёх синих и четырёх форм кнопок · Мустафа Элькуши",
                                        "Бренд- и UI-система, на которой построены сайт, презентации, письма, мероприятия и печатные материалы Ritorica."),
        },
    },
}

PAGE_PATHS = ["index.html", "work/index.html"] + [f"work/{w}.html" for w in WORK]

EXTERNAL = re.compile(r'<a href="(https?://[^"]+)"(?![^>]*target=)')


def external_new_tab(html: str) -> str:
    """Every link that leaves the site opens in a new tab.

    rel="noopener" stops the new page reaching back through window.opener;
    noreferrer keeps the referring URL out of the request.
    """
    return EXTERNAL.sub(r'<a href="\1" target="_blank" rel="noopener noreferrer"', html)


def out_path(code: str, page: str) -> str:
    """Where a page lands. English sits at the root; the rest under /ar, /ru."""
    return page if code == "en" else f"{code}/{page}"


def page(code: str, page_path: str, body: str) -> str:
    loc = LOCALES[code]
    title, desc = loc["titles"][page_path]
    rel = out_path(code, page_path)
    up = "../" * rel.count("/")
    dir_attr = ' dir="rtl"' if loc["rtl"] else ""
    current = ' aria-current="page"' if page_path == "index.html" else ""
    home = f"{up}index.html"

    body = external_new_tab(body)
    # Fragments write asset paths relative to the English page they were
    # authored for; re-point them at the single copy under /assets.
    body = re.sub(r'(?:\.\./)*assets/', f"{up}assets/", body)
    body = body.replace("<!--TELEGRAM-->",
                        f'<a class="btn btn-secondary" href="{TG_URL}">Telegram</a>' if TG_URL else "")

    tg_foot = f' · <a href="{TG_URL}" target="_blank" rel="noopener noreferrer">Telegram</a>' if TG_URL else ""
    preload = "\n".join(
        f'<link rel="preload" href="{up}assets/fonts/{f}" as="font" type="font/woff2" crossorigin>'
        for f in loc["font_preload"])
    # Only point hreflang at pages that actually exist, so the tags never
    # promise a translation that has not been written yet.
    have = [c for c in LOCALES if fragment(c, page_path).exists()]
    alts = "\n".join(
        f'<link rel="alternate" hreflang="{c}" href="{ORIGIN}/{out_path(c, page_path)}">'
        for c in have)
    alts += f'\n<link rel="alternate" hreflang="x-default" href="{ORIGIN}/{page_path}">'

    # Language switcher: the same page in the other languages, or that
    # language's home page when this page is not translated yet.
    def target(c):
        wanted = page_path if fragment(c, page_path).exists() else "index.html"
        return f"{up}{out_path(c, wanted)}"

    switch = "".join(
        f'<a class="lang-link{" is-on" if c == code else ""}" hreflang="{c}" lang="{c}" '
        f'href="{target(c)}">{LOCALES[c]["short"]}</a>'
        for c in LOCALES)

    nav = "".join(
        f'<a href="{home}#{anchor}"{current if anchor == "work" else ""}>{label}</a>'
        for anchor, label in zip(["work", "skills", "security", "about", "contact"], loc["nav"]))

    return f"""<!doctype html>
<html lang="{loc['lang']}"{dir_attr}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{ORIGIN}/assets/portrait-900.webp">
<meta name="color-scheme" content="dark light">
{alts}
{preload}
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" href="{up}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{up}style.css">
<script>{BOOT_JS}</script>
</head>
<body>
{SPRITE}
<header class="nav">
  <div class="wrap">
    <a class="brand" href="{home}"><span class="mark" aria-hidden="true"></span><span>Moustafa Elkoushy</span></a>
    <nav class="links" aria-label="{loc['main_nav']}">{nav}</nav>
    <div class="nav-end">
      <nav class="langs" aria-label="{loc['lang_label']}">{switch}</nav>
      <button class="theme-toggle cta" type="button" aria-label="{loc['theme']}"><svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg><svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
      <a class="cta" href="{home}#contact">{loc['connect']} <span aria-hidden="true">&#8599;</span></a>
    </div>
  </div>
</header>
<main>
{body}
</main>
<footer>
  <div class="wrap">
    <span>Moustafa Elkoushy · <a href="mailto:{EMAIL}">{EMAIL}</a> · <a href="{GITHUB}" target="_blank" rel="noopener noreferrer">GitHub</a>{tg_foot}</span>
    <span>{loc['footer']}</span>
  </div>
</footer>
<script src="{up}reveal.js" defer></script>
</body>
</html>
"""


def fragment(code: str, page_path: str) -> Path:
    """content/index.html for English, content/ar/index.html for Arabic, etc."""
    name = page_path.replace("/", "__")
    return CONTENT / name if code == "en" else CONTENT / code / name


if __name__ == "__main__":
    built = missing = 0
    for code in LOCALES:
        for page_path in PAGE_PATHS:
            src = fragment(code, page_path)
            if not src.exists():
                print(f"  skipped {code}/{page_path}: no fragment yet")
                missing += 1
                continue
            out = SITE / out_path(code, page_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(page(code, page_path, src.read_text(encoding="utf-8")), encoding="utf-8")
            built += 1
    print(f"built {built} pages" + (f", {missing} still untranslated" if missing else ""))
