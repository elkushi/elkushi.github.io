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
import json
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

# Telegram is the one call to action: hero, nav, services and contact all
# open a chat, with the username written out so it works even when the click
# does not. Fragments write @@TG@@ for the link.
#
# The CV, one per language. The button only appears once the file is in
# assets/, so a missing PDF is reported at build time instead of 404ing.
CV_FILE = {"en": "cv-en.pdf", "ar": "cv-ar.pdf", "ru": "cv-ru.pdf"}
CV_LABEL = {"en": "Download CV", "ar": "تنزيل السيرة الذاتية", "ru": "Скачать резюме"}
CV_SHORT = {"en": "CV", "ar": "السيرة الذاتية", "ru": "Резюме"}

# The one inline script on the site. Its hash goes in the CSP, so the policy can
# refuse every other inline script without needing 'unsafe-inline'.
BOOT_JS = ('var d=document.documentElement;d.classList.add("js");'
           'try{var t=localStorage.getItem("theme");if(t)d.dataset.theme=t}catch(e){}')
BOOT_HASH = "sha256-" + base64.b64encode(hashlib.sha256(BOOT_JS.encode()).digest()).decode()

# Instant page changes without turning the site into a single-page app: when a
# visitor hovers a link to another page here, Chrome renders that page in the
# background, so the click shows it at once. Heavy pages are left out: the
# drone viewer (three.js) and the obby game. Browsers without speculation rules
# get a plain prefetch from reveal.js instead.
SPEC_RULES = ('{"prerender":[{"where":{"and":['
              '{"href_matches":"/*"},'
              '{"not":{"href_matches":"/alisa-obby/*"}},'
              '{"not":{"href_matches":"/*drone/*"}},'
              '{"not":{"selector_matches":"[target=_blank]"}}'
              ']},"eagerness":"moderate"}]}')
SPEC_HASH = "sha256-" + base64.b64encode(hashlib.sha256(SPEC_RULES.encode()).digest()).decode()

# default-src 'none' blocks anything not listed. Styles need 'unsafe-inline'
# because a few elements carry a style attribute; scripts do not.
CSP = (
    "default-src 'none'; "
    f"script-src 'self' '{BOOT_HASH}' 'inline-speculation-rules' '{SPEC_HASH}'; "
    "connect-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "media-src 'self'; "
    "frame-src 'self'; "
    "base-uri 'none'; "
    "form-action 'none'"
)

# The work pages, in the order they appear on the home page.
# The tool logos. Inlined into every page rather than referenced as a file:
# browsers refuse cross-document <use> for SVG, and the CSP forbids it anyway.
SPRITE = (SITE / "assets" / "logos.svg").read_text(encoding="utf-8")


def minify_css(css: str) -> str:
    """Strip comments and spare whitespace. Safe for this stylesheet: no strings
    contain braces, colons or semicolons that matter."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    return css.replace(";}", "}").strip()


# The stylesheet goes inline in every page, so the first paint does not wait
# for a second request. Its url()s are written relative to /style.css, so each
# page re-points them at /assets with the right number of ../.
CSS = minify_css((SITE / "style.css").read_text(encoding="utf-8"))

WORK = ["ritorica", "video-generator", "seo-audit", "research-workflow", "design-system", "whitepapers", "drone"]

LOCALES = {
    "en": {
        "lang": "en", "rtl": False, "name": "English", "short": "EN",
        "nav": ["Work", "Services", "Skills", "Security", "Experience", "Blog", "Contact"],
        "tg": "Telegram", "arrow": "&#8599;",
        "theme": "Switch between light and dark theme",
        "lang_label": "Language", "main_nav": "Main",
        "font_preload": ["Outfit.woff2"],
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
            "work/whitepapers.html": ("Four industry guides, 87 pages, written, designed and published · Moustafa Elkoushy",
                                      "Research, writing, layout, covers, landing pages and the delivery email for four guides on business messaging, live on ritorica.com."),
            "work/drone.html": ("A drone you can take apart in the browser · Moustafa Elkoushy",
                                "An interactive 3D breakdown of how a drone fits together. Eight assemblies, generated in code, no CAD import."),
            "blog/index.html": ("Blog · Moustafa Elkoushy",
                                "Notes on building with AI: what I learn shipping AI products and workflows, written up so you can use it too."),
            "blog/wat-framework.html": ("The WAT framework: how I make Claude Code reliable · Moustafa Elkoushy",
                                        "Workflows say what to do, the Agent decides, Tools do the work. How the three layers fit together, and ten rules for using them well."),
        },
    },
    "ar": {
        "lang": "ar", "rtl": True, "name": "العربية", "short": "ع",
        "nav": ["الأعمال", "الخدمات", "المهارات", "الأمان", "الخبرة", "المدونة", "تواصل"],
        "tg": "Telegram", "arrow": "&#8598;",
        "theme": "التبديل بين الوضع الفاتح والداكن",
        "lang_label": "اللغة", "main_nav": "القائمة الرئيسية",
        "font_preload": ["Cairo-arabic.woff2", "Cairo-latin.woff2"],
        "titles": {
            "index.html": ("مصطفى القوشي · مهندس منتجات ذكاء اصطناعي",
                           "مهندس منتجات ذكاء اصطناعي. أحوّل أفكار الذكاء الاصطناعي الجريئة إلى منتجات تعمل في الواقع، وأجعل الذكاء الاصطناعي يتحقق من عمله بنفسه."),
            "work/index.html": ("كل الأعمال · مصطفى القوشي",
                                "كل المشاريع مصنّفة حسب المجال: منتجات ذكاء اصطناعي، وتطوير الويب، والتصميم، والأمان."),
            "work/ritorica.html": ("ritorica.com: أعدت بناءه بمفردي، وما زال يعمل · مصطفى القوشي",
                                   "المصمّم والمطوّر الوحيد: من ملف Figma والبناء على Django CMS إلى الإطلاق والخادم وكل ما تلاهما."),
            "work/video-generator.html": ("استوديو ذكاء اصطناعي يُنتج فيديو بهوية العلامة دون أي تكلفة للفيديو الواحد · مصطفى القوشي",
                                          "تُدخل طلبًا واحدًا، فتحصل على فيديو أو منشور مصوّر جاهز بالإنجليزية أو العربية أو الروسية. ولكل واجهة API مدفوعة بديل مجاني أو محلي."),
            "work/seo-audit.html": ("فحص موقع من 25 صفحة في أقل من دقيقة، لـ Google وللبحث بالذكاء الاصطناعي · مصطفى القوشي",
                                    "ثلاث درجات تقييم، وقائمة مهام مرتّبة حسب الأثر، وكود جاهز للّصق. في تشغيل حقيقي: 25 صفحة في 57 ثانية، بدرجة 76 من 100."),
            "work/research-workflow.html": ("تقرير عن المنافسين من 61 صفحة، لكل ادعاء فيه مصدر · مصطفى القوشي",
                                            "تسعة وكلاء بحث بالتوازي، ونحو 190 مصدرًا، وأكثر من 400 ادعاء موثّق، ومدقّق يوقف كل ما عدا ذلك."),
            "work/design-system.html": ("نظام هوية واحد يحلّ محلّ ثلاث درجات من الأزرق وأربعة أشكال للأزرار · مصطفى القوشي",
                                        "نظام الهوية والواجهة الذي بُني عليه موقع Ritorica وعروضها التقديمية ورسائل بريدها الإلكتروني وفعالياتها ومطبوعاتها."),
            "work/whitepapers.html": ("أربعة أدلة متخصصة في 87 صفحة، كتابةً وتصميمًا ونشرًا · مصطفى القوشي",
                                      "البحث والكتابة والتنسيق والأغلفة وصفحات الهبوط ورسالة البريد الإلكتروني التي تُرسل كل دليل، لأربعة أدلة عن مراسلات الأعمال منشورة على ritorica.com."),
            "work/drone.html": ("طائرة مسيّرة يمكنك تفكيكها في المتصفح · مصطفى القوشي",
                                "عرض تفاعلي ثلاثي الأبعاد يبيّن كيف تتركّب أجزاء طائرة مسيّرة. ثماني وحدات مولّدة بالكود، دون استيراد أي ملف CAD."),
            "blog/index.html": ("المدونة · مصطفى القوشي",
                                "ملاحظات عن البناء بالذكاء الاصطناعي: ما أتعلّمه أثناء بناء المنتجات ومسارات العمل، مكتوبًا لتستفيد منه أنت أيضًا."),
            "blog/wat-framework.html": ("إطار WAT: كيف أجعل Claude Code موثوقًا · مصطفى القوشي",
                                        "مسارات العمل تحدّد ما يجب فعله، والوكيل يقرّر، والأدوات تنفّذ. كيف تعمل الطبقات الثلاث معًا، وعشر قواعد لاستخدامها جيدًا."),
        },
    },
    "ru": {
        "lang": "ru", "rtl": False, "name": "Русский", "short": "RU",
        "nav": ["Работы", "Услуги", "Навыки", "Безопасность", "Опыт", "Блог", "Контакты"],
        "tg": "Telegram", "arrow": "&#8599;",
        "theme": "Переключить светлую и тёмную тему",
        "lang_label": "Язык", "main_nav": "Главное меню",
        "font_preload": ["Manrope-cyrillic.woff2", "Manrope-latin.woff2"],
        "titles": {
            "index.html": ("Мустафа Элькуши · AI Product Engineer",
                           "AI Product Engineer. Превращаю смелые ИИ-идеи в работающие продукты и заставляю ИИ проверять собственную работу."),
            "work/index.html": ("Все работы · Мустафа Элькуши",
                                "Все проекты по группам: ИИ-продукты, веб-разработка, дизайн и безопасность."),
            "work/ritorica.html": ("ritorica.com: пересобрал в одиночку и до сих пор веду · Мустафа Элькуши",
                                   "Единственный дизайнер и разработчик: макет в Figma, разработка на Django CMS, запуск, сервер и всё, что было после."),
            "work/video-generator.html": ("ИИ-студия, которая делает брендированное видео без затрат на каждый ролик · Мустафа Элькуши",
                                          "На входе один бриф, на выходе готовое видео или пост с изображением на английском, арабском или русском. У каждого платного API есть бесплатная или локальная замена."),
            "work/seo-audit.html": ("Аудит сайта из 25 страниц меньше чем за минуту — для Google и ИИ-поиска · Мустафа Элькуши",
                                    "Три оценки, список задач по степени влияния и готовый код для вставки. Реальный запуск: 25 страниц за 57 секунд, оценка 76 из 100."),
            "work/research-workflow.html": ("Отчёт о конкурентах на 61 страницу с источником за каждым утверждением · Мустафа Элькуши",
                                            "Девять исследовательских агентов параллельно, около 190 источников, больше 400 утверждений со ссылками на источники и валидатор, который отсекает всё остальное."),
            "work/design-system.html": ("Одна бренд-система вместо трёх оттенков синего и четырёх форм кнопок · Мустафа Элькуши",
                                        "Бренд- и UI-система, на которой построены сайт, презентации, письма, мероприятия и печатные материалы Ritorica."),
            "work/whitepapers.html": ("Четыре отраслевых руководства на 87 страниц: текст, дизайн и публикация · Мустафа Элькуши",
                                      "Исследование, текст, вёрстка, обложки, лендинги и письмо с доставкой для четырёх руководств по рассылкам для бизнеса, опубликованных на ritorica.com."),
            "work/drone.html": ("Дрон, который можно разобрать в браузере · Мустафа Элькуши",
                                "Интерактивная 3D-схема устройства дрона. Восемь узлов, сгенерированных кодом, без импорта из CAD."),
            "blog/index.html": ("Блог · Мустафа Элькуши",
                                "Заметки о работе с ИИ: что я узнаю, когда делаю ИИ-продукты и автоматизации, и как этим пользоваться."),
            "blog/wat-framework.html": ("WAT-фреймворк: как я делаю Claude Code надёжным · Мустафа Элькуши",
                                        "Workflows говорят, что делать, агент решает, инструменты выполняют. Как три слоя работают вместе, и десять правил, чтобы применять их правильно."),
        },
    },
}

BLOG = ["wat-framework"]

PAGE_PATHS = (["index.html", "work/index.html"] + [f"work/{w}.html" for w in WORK]
              + ["blog/index.html"] + [f"blog/{b}.html" for b in BLOG])

EXTERNAL = re.compile(r'<a href="(https?://[^"]+)"(?![^>]*target=)')


IMG = re.compile(r'<img ([^>]*?)src="((?:\.\./)*assets/)([\w-]+)\.webp"([^>]*)>')


def responsive_images(body: str) -> str:
    """Give every large image a 640px version to choose from.

    A card or a half-width screenshot shows at about 560px on a laptop, so a
    phone or laptop downloads the small file (a quarter of the bytes) and only a
    wide, sharp screen takes the full one. Runs only where NAME-640.webp exists.
    """
    def fix(m, sizes):
        pre, base, name, post = m.groups()
        attrs = pre + post
        small = SITE / "assets" / f"{name}-640.webp"
        w = re.search(r'width="(\d+)"', attrs)
        if "srcset=" in attrs or not small.exists() or not w:
            return m.group(0)
        return (f'<img {pre}src="{base}{name}.webp" srcset="{base}{name}-640.webp 640w, '
                f'{base}{name}.webp {w.group(1)}w" sizes="{sizes}"{post}>')

    half = "(min-width: 1240px) 560px, (min-width: 760px) 46vw, 100vw"
    # cards and side-by-side screenshots are half width on a laptop
    body = re.sub(r'<div class="art[^"]*">.*?</div>|<div class="shots[^"]*">.*?</div>',
                  lambda blk: IMG.sub(lambda m: fix(m, half), blk.group(0)), body, flags=re.S)
    body = re.sub(r'<figure class="bleed[^"]*">.*?</figure>',
                  lambda blk: IMG.sub(lambda m: fix(m, "(min-width: 1240px) 1200px, 100vw"), blk.group(0)), body, flags=re.S)
    return IMG.sub(lambda m: fix(m, "(min-width: 900px) 760px, 100vw"), body)


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

    body = body.replace("@@TG@@", TG_URL)
    body = external_new_tab(body)
    body = responsive_images(body)
    # Fragments write asset paths relative to the English page they were
    # authored for; re-point them at the single copy under /assets.
    body = re.sub(r'(?:\.\./)*assets/', f"{up}assets/", body)
    # The CV shows in three places: the nav, the hero and the contact section.
    has_cv = (SITE / "assets" / CV_FILE[code]).exists()
    cv_href = f"{up}assets/{CV_FILE[code]}"
    body = body.replace("@@CV@@",
                        f'<a class="btn btn-secondary" href="{cv_href}" download>'
                        f'{CV_LABEL[code]}</a>' if has_cv else "")
    nav_cv = f'<a class="cta" href="{cv_href}" download>{CV_SHORT[code]}</a>\n      ' if has_cv else ""

    css = CSS.replace('url("assets/', f'url("{up}assets/')
    # The logo sprite is only needed where the tool row is; elsewhere it is
    # 47 KB of markup for nothing.
    sprite = SPRITE + "\n" if "#logo-" in body else ""
    # Structured data on the home page, so search engines and AI tools can tell
    # who the site is about. A data block, not a script, so the CSP allows it.
    person = ""
    if page_path == "index.html":
        person = "\n<script type=\"application/ld+json\">" + json.dumps({
            "@context": "https://schema.org", "@type": "Person",
            "name": "Moustafa Elkoushy", "jobTitle": "AI Product Engineer",
            "url": f"{ORIGIN}/{rel}", "image": f"{ORIGIN}/assets/og.jpg", "email": f"mailto:{EMAIL}",
            "address": {"@type": "PostalAddress", "addressLocality": "Moscow", "addressCountry": "RU"},
            "knowsLanguage": ["ar", "en", "ru"],
            "alumniOf": {"@type": "CollegeOrUniversity", "name": "Moscow Aviation Institute"},
            "sameAs": [GITHUB, TG_URL],
        }, ensure_ascii=False) + "</script>"
    # The home page gets the drone that flies down it. The script decides on
    # the visitor's device whether three.js is worth loading at all.
    drone = f'\n<script src="{up}assets/drone-escort.js" defer></script>' if page_path == "index.html" else ""
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

    # Every nav item is a section of the home page, except the blog, which is
    # its own page and is marked current while you are reading it.
    on_blog = ' aria-current="page"' if page_path.startswith("blog/") else ""
    nav = "".join(
        f'<a href="{up}blog/index.html"{on_blog}>{label}</a>' if anchor == "blog" else
        f'<a href="{home}#{anchor}"{current if anchor == "work" else ""}>{label}</a>'
        for anchor, label in zip(["work", "services", "skills", "security", "about", "blog", "contact"], loc["nav"]))

    return f"""<!doctype html>
<html lang="{loc['lang']}"{dir_attr}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{ORIGIN}/assets/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">{person}
<meta name="color-scheme" content="dark light">
{alts}
{preload}
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" href="{up}assets/favicon.svg" type="image/svg+xml">
<style>{css}</style>
<script>{BOOT_JS}</script>
<script type="speculationrules">{SPEC_RULES}</script>
</head>
<body>
{sprite}<header class="nav">
  <div class="wrap">
    <a class="brand" href="{home}"><span class="mark" aria-hidden="true"></span><span>Moustafa Elkoushy</span></a>
    <nav class="links" aria-label="{loc['main_nav']}">{nav}</nav>
    <div class="nav-end">
      <nav class="langs" aria-label="{loc['lang_label']}">{switch}</nav>
      <button class="theme-toggle cta" type="button" aria-label="{loc['theme']}"><svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg><svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
      {nav_cv}<a class="cta" href="{TG_URL}" target="_blank" rel="noopener noreferrer">{loc['tg']} <span aria-hidden="true">{loc['arrow']}</span></a>
    </div>
  </div>
  <div class="progress" aria-hidden="true"><span></span></div>
</header>
<main>
{body}
</main>
<footer>
  <div class="wrap">
    <span>Moustafa Elkoushy · <a href="mailto:{EMAIL}">{EMAIL}</a> · <a href="{GITHUB}" target="_blank" rel="noopener noreferrer">GitHub</a>{tg_foot}</span>
  </div>
</footer>
<script src="{up}reveal.js" defer></script>{drone}
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
