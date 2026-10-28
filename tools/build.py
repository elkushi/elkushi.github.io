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
from html import unescape
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
CONTENT = SITE / "content"
ORIGIN = "https://elkushi.github.io"

EMAIL = "moustafa.elkoushy7@gmail.com"
GITHUB = "https://github.com/elkushi"
# The t.me username.
TELEGRAM = "Elkushi99"
TG_URL = f"https://t.me/{TELEGRAM}" if TELEGRAM else ""
# WhatsApp, on the Arabic pages only: it is how Gulf recruiters and clients
# write. His decision, 2026-10-27; every other language keeps the phone off.
WHATSAPP = "79932802066"
WA_URL = f"https://wa.me/{WHATSAPP}"
WA_SHOWN = "+7 993 280-20-66"

# One chat app is the call to action: hero, nav, services and contact all open
# a chat, with the username or number written out so it works even when the
# click does not. Telegram everywhere, except the Arabic pages, which use
# WhatsApp only (his decision, 2026-10-28). Fragments write @@TG@@ or @@WA@@.
#
# The CV, one per language. The button only appears once the file is in
# assets/, so a missing PDF is reported at build time instead of 404ing.
CV_FILE = {"en": "cv-en.pdf", "ar": "cv-ar.pdf", "ru": "cv-ru.pdf"}
CV_LABEL = {"en": "Download CV", "ar": "تنزيل السيرة الذاتية", "ru": "Скачать резюме"}
# The round button that appears near the end of a page and takes you back up.
TOP_LABEL = {"en": "Back to top", "ar": "العودة إلى الأعلى", "ru": "Наверх"}

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
# Its path data is the bulk of every page, so the numbers are cut to two
# decimals: a hundredth of a 24-unit icon drawn at 48px is a fiftieth of a pixel.


def tighten_path(d: str) -> str:
    """Shorten one path's data without changing the shape it draws.

    Paths with arcs are left alone: their flags may be written run together
    ("011"), which a plain number reader would misread as eleven.
    """
    if re.search(r"[aAeE]", d):
        return d
    out, prev = [], ""
    for tok in re.findall(r"[A-Za-z]|-?(?:\d+\.?\d*|\.\d+)", d):
        if tok.isalpha():
            out.append(tok)
            prev = tok
            continue
        n = f"{float(tok):.2f}".rstrip("0").rstrip(".")
        n = re.sub(r"^(-?)0\.", r"\1.", n)
        if n in ("-0", "", "-"):
            n = "0"
        # Two numbers need a space between them unless the second starts with
        # a minus, or with a dot after a number that already has one.
        if prev and not prev.isalpha() and not (n[0] == "-" or (n[0] == "." and "." in prev)):
            out.append(" ")
        out.append(n)
        prev = n
    return "".join(out)


SPRITE = re.sub(r'\sd="([^"]*)"', lambda m: f' d="{tighten_path(m.group(1))}"',
                (SITE / "assets" / "logos.svg").read_text(encoding="utf-8"))


def minify_css(css: str) -> str:
    """Strip comments and spare whitespace. Safe for this stylesheet: no strings
    contain braces, colons or semicolons that matter."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    # A space after a colon only ever follows a property or a media feature
    # here; no selector or string in the sheet has one.
    css = re.sub(r":\s+", ":", css)
    return css.replace(";}", "}").strip()


# Blocks whose text must reach the browser byte for byte: the inline scripts
# are allowed by the hash of their exact contents, and <pre> keeps its spaces.
KEEP = re.compile(r"<(script|style|pre|textarea)\b.*?</\1>", re.S | re.I)


def minify_html(html: str) -> str:
    """Drop comments and indentation from a built page.

    Whitespace is shortened, never removed outright: a run of spaces and
    newlines becomes one character, so text between inline tags still reads
    the same. Scripts, styles and <pre> pass through untouched.
    """
    kept = []

    def hold(m):
        kept.append(m.group(0))
        return f"\x00{len(kept) - 1}\x00"

    html = KEEP.sub(hold, html)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    html = re.sub(r"\s*\n\s*", "\n", html)
    html = re.sub(r"[ \t]{2,}", " ", html)
    return re.sub(r"\x00(\d+)\x00", lambda m: kept[int(m.group(1))], html).strip() + "\n"


# The stylesheet goes inline in every page, so the first paint does not wait
# for a second request. Its url()s are written relative to /style.css, so each
# page re-points them at /assets with the right number of ../.
CSS = minify_css((SITE / "style.css").read_text(encoding="utf-8"))

# Scripts carry a short hash of their contents in the URL. The service worker
# serves assets from its saved copy first, so without this a returning visitor
# runs last week's script for one visit after every change.
def version(*names: str) -> str:
    h = hashlib.sha256()
    for n in names:
        h.update((SITE / n).read_bytes())
    return "?v=" + h.hexdigest()[:8]

REVEAL_V = version("reveal.js")
# drone-escort.js passes its own ?v= on to the files it loads (the model, the
# scene and the worker), so one hash covers all four.
DRONE_V = version("assets/drone-escort.js", "assets/drone-model.js", "assets/drone-scene.js", "assets/drone-worker.js")

WORK = ["ritorica", "video-generator", "seo-audit", "research-workflow", "design-system", "whitepapers", "drone"]

LOCALES = {
    "en": {
        "lang": "en", "rtl": False, "name": "English", "short": "EN",
        "nav": ["Work", "Services", "Skills", "Security", "Experience", "Blog", "Contact"],
        "tg": "Telegram", "arrow": "&#8599;",
        "theme": "Switch between light and dark theme",
        "lang_label": "Language", "main_nav": "Main", "menu": "Menu",
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
            "blog/secure-vibe-coded-apps.html": ("Vibe-coded apps: how to make them secure, and how to prove it · Moustafa Elkoushy",
                                                 "The eight holes AI-built apps most often have, how to close each one, and the test that proves it. With real code from my own apps."),
            "blog/seo-geo-aeo-audit.html": ("Get found on Google and in ChatGPT: what my audit app checks · Moustafa Elkoushy",
                                            "What my free SEO, AEO and GEO audit checks, what it means for a business, and 22 fixes you can make this week."),
            "blog/ai-agents-python.html": ("AI agents: what they are, how to build one, and why Python · Moustafa Elkoushy",
                                           "What an AI agent is, a working agent in about 40 lines of Python, and the rules that keep it from going wrong."),
            "blog/php-october-2026-django-cms.html": ("PHP in October 2026: what happened, and when a Django CMS is the safer choice · Moustafa Elkoushy",
                                                      "php2shell, an exploited WordPress plugin and a self-rebuilding backdoor: what to do this week if your site runs on PHP, and when moving to Django CMS is worth it."),
        },
    },
    "ar": {
        "lang": "ar", "rtl": True, "name": "العربية", "short": "ع",
        "nav": ["الأعمال", "الخدمات", "المهارات", "الأمان", "الخبرة", "المدونة", "تواصل"],
        "tg": "Telegram", "arrow": "&#8598;",
        "theme": "التبديل بين الوضع الفاتح والداكن",
        "lang_label": "اللغة", "main_nav": "القائمة الرئيسية", "menu": "القائمة",
        "font_preload": ["Cairo-arabic.woff2", "Cairo-latin.woff2"],
        "titles": {
            "index.html": ("مصطفى القوشي · مهندس منتجات ذكاء اصطناعي",
                           "مهندس منتجات ذكاء اصطناعي. أحوّل الأفكار الجريئة في الذكاء الاصطناعي إلى منتجات تعمل في الواقع، وتتحقق من عملها بنفسها."),
            "work/index.html": ("كل الأعمال · مصطفى القوشي",
                                "كل المشاريع مصنّفة حسب المجال: منتجات ذكاء اصطناعي، وتطوير الويب، والتصميم، والأمان."),
            "work/ritorica.html": ("ritorica.com: أعدت بناءه بمفردي، وما زلت أديره · مصطفى القوشي",
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
            "blog/secure-vibe-coded-apps.html": ("تطبيقات Vibe Coding: كيف تجعلها آمنة، وكيف تثبت ذلك · مصطفى القوشي",
                                                 "الثغرات الثماني الأكثر شيوعًا في التطبيقات المبنية بالذكاء الاصطناعي، وكيف تغلق كل واحدة منها، والاختبار الذي يثبت ذلك، مع كود حقيقي من تطبيقاتي."),
            "blog/seo-geo-aeo-audit.html": ("كيف تظهر في Google وفي ChatGPT: ما يفحصه تطبيقي · مصطفى القوشي",
                                            "ما يفحصه تطبيقي المجاني لـ SEO وAEO وGEO، وما يعنيه ذلك للشركة، و22 إصلاحًا تستطيع تنفيذها هذا الأسبوع."),
            "blog/ai-agents-python.html": ("وكيل الذكاء الاصطناعي: ما هو، وكيف تبنيه، ولماذا Python · مصطفى القوشي",
                                           "ما هو وكيل الذكاء الاصطناعي بكلمات بسيطة، ووكيل يعمل في نحو 40 سطرًا من Python، وثماني قواعد تحميه من الخطأ."),
            "blog/php-october-2026-django-cms.html": ("PHP في أكتوبر 2026: ماذا حدث، ومتى يكون Django CMS الخيار الأكثر أمانًا · مصطفى القوشي",
                                                      "ثغرات PHP في أكتوبر 2026، وإضافة WordPress سمحت بتشغيل كود دون تسجيل دخول، وباب خلفي يعيد بناء نفسه. ما تفعله هذا الأسبوع، ومتى يستحق الانتقال إلى Django CMS."),
        },
    },
    "ru": {
        "lang": "ru", "rtl": False, "name": "Русский", "short": "RU",
        "nav": ["Работы", "Услуги", "Навыки", "Безопасность", "Опыт", "Блог", "Контакты"],
        "tg": "Telegram", "arrow": "&#8599;",
        "theme": "Переключить светлую и тёмную тему",
        "lang_label": "Язык", "main_nav": "Главное меню", "menu": "Меню",
        "font_preload": ["Manrope-cyrillic.woff2", "Manrope-latin.woff2"],
        "titles": {
            "index.html": ("Мустафа Элькуши · AI Product Engineer",
                           "AI Product Engineer. Довожу ИИ-идеи до работающих продуктов, в которых ИИ сам проверяет свою работу."),
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
                                      "Исследование, текст, вёрстка, обложки, лендинги и письма, с которыми приходят руководства. Четыре руководства по рассылкам для бизнеса, опубликованные на ritorica.com."),
            "work/drone.html": ("Дрон, который можно разобрать в браузере · Мустафа Элькуши",
                                "Интерактивная 3D-схема устройства дрона. Восемь узлов, сгенерированных кодом, без импорта из CAD."),
            "blog/index.html": ("Блог · Мустафа Элькуши",
                                "Заметки о работе с ИИ: что я узнаю, когда делаю ИИ-продукты и автоматизации, и как этим пользоваться."),
            "blog/wat-framework.html": ("WAT-фреймворк: как я делаю Claude Code надёжным · Мустафа Элькуши",
                                        "Workflows задают, что делать, агент принимает решения, инструменты выполняют работу. Как три слоя работают вместе — и десять правил, которые помогают применять их правильно."),
            "blog/secure-vibe-coded-apps.html": ("Приложения на вайб-кодинге: как их защитить и как это доказать · Мустафа Элькуши",
                                                 "Восемь уязвимостей, которые чаще всего встречаются в приложениях, написанных с помощью ИИ: как закрыть каждую и каким тестом это доказать. С реальным кодом из моих приложений."),
            "blog/seo-geo-aeo-audit.html": ("Как стать заметным в Google и в ChatGPT: что проверяет мой инструмент аудита · Мустафа Элькуши",
                                            "Что проверяет мой бесплатный аудит SEO, AEO и GEO, что это значит для бизнеса и 22 исправления, которые можно сделать на этой неделе."),
            "blog/ai-agents-python.html": ("ИИ-агенты: что это такое, как их делать и почему на Python · Мустафа Элькуши",
                                           "Что такое ИИ-агент и чем он отличается от чат-бота, работающий агент примерно в 40 строк на Python и восемь правил, которые не дают ему пойти не туда."),
            "blog/php-october-2026-django-cms.html": ("PHP в октябре 2026 года: что произошло и когда Django CMS — более безопасный выбор · Мустафа Элькуши",
                                                      "Срочное обновление для всех PHP-сайтов, атакованный плагин WordPress и бэкдор, который восстанавливает себя: что сделать на этой неделе и когда стоит переехать на Django CMS."),
        },
    },
}

BLOG = ["wat-framework", "secure-vibe-coded-apps", "seo-geo-aeo-audit", "ai-agents-python", "php-october-2026-django-cms"]

PAGE_PATHS = (["index.html", "work/index.html"] + [f"work/{w}.html" for w in WORK]
              + ["blog/index.html"] + [f"blog/{b}.html" for b in BLOG])

EXTERNAL = re.compile(r'<a href="(https?://[^"]+)"(?![^>]*target=)')


IMG = re.compile(r'<img ([^>]*?)src="((?:\.\./)*assets/)([\w-]+)\.webp"([^>]*)>')


def canonical(rel: str) -> str:
    """The one public URL of a page. The site serves / and /index.html alike;
    without a canonical both get indexed, cached and prerendered separately.
    Folder URLs win, because that is what people link to."""
    return f"{ORIGIN}/{rel[:-len('index.html')] if rel.endswith('index.html') else rel}"


def image_priority(body: str) -> str:
    """Load the page's main image first and every other image only when needed.

    The first image on a page that is not marked lazy is its largest early
    paint (a case study's screenshot, a post's cover), so it gets
    fetchpriority="high". A cover comes as a dark and a light copy side by
    side, so the pair gets it. Every later image is lazy and decodes off the
    main thread. An image that must load at once can say loading="eager".
    """
    imgs = list(re.finditer(r"<img\b[^>]*>", body))
    lead = next((i for i, m in enumerate(imgs) if 'loading="lazy"' not in m.group(0)), None)
    first = set()
    if lead is not None:
        first.add(lead)
        if "only-dark" in imgs[lead].group(0) and lead + 1 < len(imgs) and "only-light" in imgs[lead + 1].group(0):
            first.add(lead + 1)
    out, pos = [], 0
    for i, m in enumerate(imgs):
        tag = m.group(0)
        if i in first and "fetchpriority=" not in tag:
            tag = tag[:-1].rstrip("/").rstrip() + ' fetchpriority="high">'
        elif i not in first and "loading=" not in tag:
            tag = tag[:-1].rstrip("/").rstrip() + ' loading="lazy">'
        if i not in first and "decoding=" not in tag:
            tag = tag[:-1].rstrip("/").rstrip() + ' decoding="async">'
        out += [body[pos:m.start()], tag]
        pos = m.end()
    return "".join(out) + body[pos:]


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
    # This language's own home page. "{up}index.html" alone is the English one,
    # which sent Arabic and Russian readers to English from every nav link.
    home = f"{up}{out_path(code, 'index.html')}"

    # Service illustrations live in tools/art/ and are inlined, so their colours
    # come from the page's theme tokens.
    body = re.sub(r"@@ART:([a-z-]+)@@", lambda m: (SITE / "tools" / "art" / f"{m.group(1)}.svg").read_text().strip(), body)
    body = body.replace("@@TG@@", TG_URL).replace("@@WA@@", WA_URL).replace("@@WA_SHOWN@@", WA_SHOWN)
    body = external_new_tab(body)
    body = responsive_images(body)
    body = image_priority(body)
    # Fragments write asset paths relative to the English page they were
    # authored for; re-point them at the single copy under /assets.
    body = re.sub(r'(?:\.\./)*assets/', f"{up}assets/", body)
    # The CV shows in two places: the hero, next to GitHub, and the contact
    # section. Not in the nav: the Russian header has no room for it at 1440px.
    has_cv = (SITE / "assets" / CV_FILE[code]).exists()
    cv_href = f"{up}assets/{CV_FILE[code]}"
    body = body.replace("@@CV@@",
                        f'<a class="btn btn-secondary" href="{cv_href}" download>'
                        f'{CV_LABEL[code]}</a>' if has_cv else "")

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
            "url": canonical(rel), "image": f"{ORIGIN}/assets/og.jpg", "email": f"mailto:{EMAIL}",
            "address": {"@type": "PostalAddress", "addressLocality": "Moscow", "addressCountry": "RU"},
            "knowsLanguage": ["ar", "en", "ru"],
            "alumniOf": {"@type": "CollegeOrUniversity", "name": "Moscow Aviation Institute"},
            "sameAs": [GITHUB, TG_URL],
        }, ensure_ascii=False) + "</script>"
    # The FAQ, as structured data too, read straight from the page so the two
    # can never disagree. AI search tools quote these answers.
    faq = re.findall(r'<details class="faq-item"[^>]*>\s*<summary>(.*?)</summary>\s*'
                     r'<div class="faq-a">(.*?)</div>', body, flags=re.S)
    if faq:
        def plain(x):
            return unescape(re.sub(r"<[^>]+>", "", x)).strip()
        person += "\n<script type=\"application/ld+json\">" + json.dumps({
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": plain(q),
                            "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in faq],
        }, ensure_ascii=False) + "</script>"
    # The home page gets the drone that flies down it. The script decides on
    # the visitor's device whether three.js is worth loading at all.
    drone = f'\n<script src="{up}assets/drone-escort.js{DRONE_V}" defer></script>' if page_path == "index.html" else ""
    chat_url, chat_name = (WA_URL, "WhatsApp") if code == "ar" else (TG_URL, "Telegram")
    tg_foot = f' · <a href="{chat_url}" target="_blank" rel="noopener noreferrer">{chat_name}</a>' if chat_url else ""
    preload = "\n".join(
        f'<link rel="preload" href="{up}assets/fonts/{f}" as="font" type="font/woff2" crossorigin>'
        for f in loc["font_preload"])
    # Only point hreflang at pages that actually exist, so the tags never
    # promise a translation that has not been written yet.
    have = [c for c in LOCALES if fragment(c, page_path).exists()]
    alts = f'<link rel="canonical" href="{canonical(rel)}">\n' + "\n".join(
        f'<link rel="alternate" hreflang="{c}" href="{canonical(out_path(c, page_path))}">'
        for c in have)
    alts += f'\n<link rel="alternate" hreflang="x-default" href="{canonical(page_path)}">'

    # Language switcher: the same page in the other languages, or that
    # language's home page when this page is not translated yet.
    def target(c):
        wanted = page_path if fragment(c, page_path).exists() else "index.html"
        return f"{up}{out_path(c, wanted)}"

    switch = "".join(
        f'<a class="lang-link{" is-on" if c == code else ""}" hreflang="{c}" lang="{c}" '
        f'href="{target(c)}">{LOCALES[c]["short"]}</a>'
        for c in LOCALES)
    # The same languages, written out in full, for the phone menu.
    menu_langs = "".join(
        f'<a class="menu-lang{" is-on" if c == code else ""}" hreflang="{c}" lang="{c}" '
        f'href="{target(c)}">{LOCALES[c]["name"]}</a>'
        for c in LOCALES)

    # Every nav item is a section of the home page, except the blog, which is
    # its own page and is marked current while you are reading it.
    on_blog = ' aria-current="page"' if page_path.startswith("blog/") else ""
    nav = "".join(
        f'<a href="{up}{out_path(code, "blog/index.html")}"{on_blog}>{label}</a>' if anchor == "blog" else
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
<link rel="icon" href="{up}assets/favicon.svg?v=2" type="image/svg+xml">
<link rel="apple-touch-icon" href="{up}assets/apple-touch-icon.png">
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
      <a class="cta" href="{chat_url}" target="_blank" rel="noopener noreferrer">{chat_name} <span aria-hidden="true">{loc['arrow']}</span></a>
      <details class="menu">
        <summary class="cta"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg><span class="menu-label">{loc['menu']}</span></summary>
        <div class="menu-panel">
          <nav class="menu-links" aria-label="{loc['main_nav']}">{nav}</nav>
          <nav class="menu-langs" aria-label="{loc['lang_label']}">{menu_langs}</nav>
        </div>
      </details>
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
<a class="to-top" href="#" aria-label="{TOP_LABEL[code]}" title="{TOP_LABEL[code]}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg></a>
<script src="{up}reveal.js{REVEAL_V}" defer></script>{drone}
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
            out.write_text(minify_html(page(code, page_path, src.read_text(encoding="utf-8"))), encoding="utf-8")
            built += 1
    print(f"built {built} pages" + (f", {missing} still untranslated" if missing else ""))
