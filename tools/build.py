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
# A phone number for the Russian clinics page (ru/clinics/) only: clinic owners
# are often older and prefer a normal call to a chat. Moustafa asked for a call
# button there on 2026-11-04, but has not yet said which number to show, so it
# stays empty and the button is left out. Set both to publish it, e.g.
# PHONE = "+79932802066" and PHONE_SHOWN = "+7 993 280-20-66". Fragments write @@CALL@@.
PHONE = ""
PHONE_SHOWN = ""
# Yandex Webmaster ownership code (webmaster.yandex.ru → add the site → "Meta tag").
# Russian clinic owners search on Yandex, so the site has to be in Webmaster to be
# indexed fast, get a region and show up for «сайт для стоматологии». Empty until
# Moustafa sends the code; the tag is left out while it is empty.
YANDEX_VERIFICATION = ""

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

# The theme switch's two icons: the header button and, on a phone, the one in
# the menu. style.css shows the one for the action the button performs.
SUN_MOON = ('<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
            '<svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>')

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
    f"script-src 'self' '{BOOT_HASH}' 'inline-speculation-rules' '{SPEC_HASH}' https://www.googletagmanager.com; "
    # Google Analytics (assets/analytics.js): the hosts Google lists for GA4.
    "connect-src 'self' https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: https://*.google-analytics.com https://*.googletagmanager.com; "
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
ANALYTICS_V = version("assets/analytics.js")
# drone-escort.js passes its own ?v= on to the files it loads (the model, the
# scene and the worker), so one hash covers all four.
DRONE_V = version("assets/drone-escort.js", "assets/drone-model.js", "assets/drone-scene.js", "assets/drone-worker.js")

WORK = ["ritorica", "video-generator", "seo-audit", "talon", "research-workflow", "design-system", "whitepapers", "drone"]

LOCALES = {
    "en": {
        "lang": "en", "rtl": False, "name": "English", "short": "EN",
        "home_name": "Moustafa Elkoushy", "city": "Moscow",
        "service_type": "Website, online booking and patient bot for private clinics",
        "service_audience": "Private dental and medical clinics",
        "service_items": ["Phone-first clinic website", "Online booking", "Telegram and MAX bot with appointment reminders",
                          "Review collection on Yandex Maps and 2GIS", "Analytics", "Design and print"],
        "nav": ["Work", "Services", "Skills", "Security", "Experience", "Blog", "Contact"],
        "tg": "Telegram", "arrow": "&#8599;",
        "theme": "Switch between light and dark theme", "theme_short": "Light / dark theme",
        "lang_label": "Language", "main_nav": "Main", "menu": "Menu",
        "font_preload": ["Outfit.woff2"],
        "titles": {
            "index.html": ("Moustafa Elkoushy · AI Product Engineer",
                           "AI product engineer in Moscow. I build AI automation, websites and online booking for businesses and clinics, and AI that checks its own work."),
            "work/index.html": ("All work · Moustafa Elkoushy",
                                "Every project, grouped: AI products, web development, design and security."),
            "work/ritorica.html": ("ritorica.com: rebuilt alone, and still running · Moustafa Elkoushy",
                                   "Sole designer and developer: Figma file, Django CMS build, launch, server and everything since."),
            "work/video-generator.html": ("An AI studio that makes a branded video for nothing per video · Moustafa Elkoushy",
                                          "One brief in; a finished video or image post out, in English, Arabic or Russian. Every paid API has a free or local fallback."),
            "work/seo-audit.html": ("Audits a 25-page site in under a minute, for Google and AI search · Moustafa Elkoushy",
                                    "Three scores, a to-do list ranked by impact, and code to paste in. A real run: 25 pages in 57 seconds, scored 76 out of 100."),
            "work/talon.html": ("A monitor that tells you what broke on your website · Moustafa Elkoushy",
                                "Eight read-only checks - redirects, robots.txt, sitemaps, pages, certificates, DNS, content and headers - in one Telegram message a day. Open source, 64 tests."),
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
            "clinics/index.html": ("Website, online booking and a clinic bot for private clinics · Moustafa Elkoushy",
                                   "A done-for-you package for private clinics: a phone-first website, online booking, a messenger bot with reminders, reviews, analytics and design. A free concept for your clinic."),
            "blog/maps-ranking-google-yandex.html": ("Get higher on Google Maps and Yandex Maps: what decides the order, and the photos that help · Moustafa Elkoushy",
                                                     "What Google and Yandex say decides the order on the map, the photos a card needs, honest reviews, and a 15-minute check, with examples from about 40 Moscow clinics."),
            "blog/ui-ux-from-zero.html": ('UI/UX from zero: how to start a new project with design thinking · Moustafa Elkoushy',
                                          'The order I use from an empty folder to a tested first version: research, the problem, ideas, user flow, wireframes, UI rules with numbers and a 5-person test, with a sketch for every step.'),
            "blog/b2b-vs-b2c-ux.html": ("B2B vs B2C in UI/UX: what changes when the buyer isn't the user · Moustafa Elkoushy",
                                        'Who decides, who reads your page, two different journeys, landing pages and product screens compared, research and metrics, with a real clinic example from both sides.'),
            "blog/php-october-2026-django-cms.html": ("PHP in October 2026: what happened, and when a Django CMS is the safer choice · Moustafa Elkoushy",
                                                      "php2shell, an exploited WordPress plugin and a self-rebuilding backdoor: what to do this week if your site runs on PHP, and when moving to Django CMS is worth it."),
            "404.html": ("Page not found · Moustafa Elkoushy",
                         "This page doesn't exist. Links to the home page, the work and the blog."),
        },
    },
    "ar": {
        "lang": "ar", "rtl": True, "name": "العربية", "short": "ع",
        "home_name": "مصطفى القوشي", "city": "Moscow",
        "service_type": "موقع وحجز إلكتروني وروبوت محادثة للعيادات الخاصة",
        "service_audience": "عيادات الأسنان والعيادات الطبية الخاصة",
        "service_items": ["موقع عيادة مصمَّم للهاتف", "حجز إلكتروني", "روبوت محادثة مع تذكير بالمواعيد",
                          "جمع التقييمات", "التحليلات", "التصميم والمطبوعات"],
        "nav": ["الأعمال", "الخدمات", "المهارات", "الأمان", "الخبرة", "المدونة", "تواصل"],
        "tg": "Telegram", "arrow": "&#8598;",
        "theme": "التبديل بين الوضع الفاتح والداكن", "theme_short": "الوضع الفاتح / الداكن",
        "lang_label": "اللغة", "main_nav": "القائمة الرئيسية", "menu": "القائمة",
        "font_preload": ["Cairo-arabic.woff2", "Cairo-latin.woff2"],
        "titles": {
            "index.html": ("مصطفى القوشي · مهندس منتجات ذكاء اصطناعي",
                           "مهندس منتجات ذكاء اصطناعي في موسكو. أبني أتمتة بالذكاء الاصطناعي ومواقع وحجزًا إلكترونيًا للشركات والعيادات، مع ذكاء اصطناعي يتحقق من عمله بنفسه."),
            "work/index.html": ("كل الأعمال · مصطفى القوشي",
                                "كل المشاريع مصنّفة حسب المجال: منتجات ذكاء اصطناعي، وتطوير الويب، والتصميم، والأمان."),
            "work/ritorica.html": ("ritorica.com: أعدت بناءه بمفردي، وما زلت أديره · مصطفى القوشي",
                                   "المصمّم والمطوّر الوحيد: من ملف Figma والبناء على Django CMS إلى الإطلاق والخادم وكل ما تلاهما."),
            "work/video-generator.html": ("استوديو ذكاء اصطناعي يُنتج فيديو بهوية العلامة دون أي تكلفة للفيديو الواحد · مصطفى القوشي",
                                          "تُدخل طلبًا واحدًا، فتحصل على فيديو أو منشور مصوّر جاهز بالإنجليزية أو العربية أو الروسية. ولكل واجهة API مدفوعة بديل مجاني أو محلي."),
            "work/seo-audit.html": ("فحص موقع من 25 صفحة في أقل من دقيقة، لـ Google وللبحث بالذكاء الاصطناعي · مصطفى القوشي",
                                    "ثلاث درجات تقييم، وقائمة مهام مرتّبة حسب الأثر، وكود جاهز للّصق. في تشغيل حقيقي: 25 صفحة في 57 ثانية، بدرجة 76 من 100."),
            "work/talon.html": ("أداة مراقبة تخبرك بما تعطّل في موقعك · مصطفى القوشي",
                                "ثماني فحوصات للقراءة فقط — التحويلات وrobots.txt وخريطة الموقع والصفحات والشهادات وDNS والمحتوى والترويسات — في رسالة واحدة على Telegram كل يوم. مفتوحة المصدر، و64 اختبارًا."),
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
            "clinics/index.html": ("موقع وحجز إلكتروني وروبوت محادثة للعيادات الخاصة · مصطفى القوشي",
                                   "حل متكامل للعيادات الخاصة: موقع مصمَّم للهاتف، وحجز إلكتروني، وروبوت على WhatsApp أو Telegram مع تذكير بالمواعيد، وتقييمات، وتحليلات، وتصميم. تصوّر مجاني لعيادتك."),
            "blog/maps-ranking-google-yandex.html": ("كيف ترتفع في خرائط Google وخرائط Yandex: ما الذي يحدّد الترتيب، وأي صور تساعد · مصطفى القوشي",
                                                     "ما تقوله Google وYandex عن ترتيب النتائج على الخريطة، والصور التي تحتاجها البطاقة، والمراجعات النزيهة، وفحص في 15 دقيقة، مع أمثلة من نحو 40 عيادة في موسكو."),
            "blog/ui-ux-from-zero.html": ('UI/UX من الصفر: كيف تبدأ مشروعًا جديدًا بالتفكير التصميمي · مصطفى القوشي',
                                          'الترتيب الذي أتبعه من مجلد فارغ إلى نسخة أولى مُختبَرة: البحث، والمشكلة، والأفكار، ومسار المستخدم، والمخططات، وقواعد الواجهة بالأرقام، واختبار مع 5 أشخاص، مع رسم لكل خطوة.'),
            "blog/b2b-vs-b2c-ux.html": ('B2B وB2C في UI/UX: ما الذي يتغير عندما لا يكون المشتري هو المستخدم · مصطفى القوشي',
                                        'مَن يقرر، ومَن يقرأ صفحتك، ورحلتان مختلفتان، ومقارنة صفحات الهبوط وشاشات المنتج، والبحث والمقاييس، مع مثال حقيقي لعيادة من الجانبين.'),
            "blog/php-october-2026-django-cms.html": ("PHP في أكتوبر 2026: ماذا حدث، ومتى يكون Django CMS الخيار الأكثر أمانًا · مصطفى القوشي",
                                                      "ثغرات PHP في أكتوبر 2026، وإضافة WordPress سمحت بتشغيل كود دون تسجيل دخول، وباب خلفي يعيد بناء نفسه. ما تفعله هذا الأسبوع، ومتى يستحق الانتقال إلى Django CMS."),
        },
    },
    "ru": {
        "lang": "ru", "rtl": False, "name": "Русский", "short": "RU",
        "home_name": "Мустафа Элькуши", "city": "Москва",
        "service_type": "Создание сайта и онлайн-записи для стоматологии и частной клиники",
        "service_audience": "Частные стоматологии и клиники",
        "service_items": ["Сайт для стоматологии и клиники под телефон", "Онлайн-запись пациентов",
                          "Бот в Telegram и MAX с напоминаниями о приёме", "Сбор отзывов на Яндекс Картах и 2ГИС",
                          "Яндекс Метрика и аналитика", "Дизайн и полиграфия для клиники"],
        "nav": ["Работы", "Услуги", "Навыки", "Безопасность", "Опыт", "Блог", "Контакты"],
        "tg": "Telegram", "arrow": "&#8599;",
        "theme": "Переключить светлую и тёмную тему", "theme_short": "Светлая / тёмная тема",
        "lang_label": "Язык", "main_nav": "Главное меню", "menu": "Меню",
        "font_preload": ["Manrope-cyrillic.woff2", "Manrope-latin.woff2"],
        "titles": {
            "index.html": ("Мустафа Элькуши · AI Product Engineer",
                           "AI Product Engineer в Москве. Делаю ИИ-автоматизацию, сайты и онлайн-запись для бизнеса и частных клиник. ИИ в моих продуктах сам проверяет свою работу."),
            "work/index.html": ("Все работы · Мустафа Элькуши",
                                "Все проекты по группам: ИИ-продукты, веб-разработка, дизайн и безопасность."),
            "work/ritorica.html": ("ritorica.com: пересобрал в одиночку и до сих пор веду · Мустафа Элькуши",
                                   "Единственный дизайнер и разработчик: макет в Figma, разработка на Django CMS, запуск, сервер и всё, что было после."),
            "work/video-generator.html": ("ИИ-студия, которая делает брендированное видео без затрат на каждый ролик · Мустафа Элькуши",
                                          "На входе один бриф, на выходе готовое видео или пост с изображением на английском, арабском или русском. У каждого платного API есть бесплатная или локальная замена."),
            "work/seo-audit.html": ("Аудит сайта из 25 страниц меньше чем за минуту — для Google и ИИ-поиска · Мустафа Элькуши",
                                    "Три оценки, список задач по степени влияния и готовый код для вставки. Реальный запуск: 25 страниц за 57 секунд, оценка 76 из 100."),
            "work/talon.html": ("Монитор, который сообщает, что сломалось на сайте · Мустафа Элькуши",
                                "Восемь проверок только на чтение — редиректы, robots.txt, карта сайта, страницы, сертификаты, DNS, контент и заголовки — одним сообщением в Telegram в день. Открытый код, 64 теста."),
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
            "clinics/index.html": ("Сайт для стоматологии и клиники с онлайн-записью · Москва",
                                   "Сайт для стоматологии и частной клиники в Москве: онлайн-запись, бот в Telegram и MAX с напоминаниями, отзывы на Картах. Бесплатный концепт."),
            "blog/maps-ranking-google-yandex.html": ("Как подняться выше в Яндекс Картах и Google Картах: что решает порядок и какие фото помогают · Мустафа Элькуши",
                                                     "Что Яндекс и Google говорят о порядке на картах, какие фото нужны карточке, честные отзывы и проверка за 15 минут. С примерами из примерно 40 московских клиник."),
            "blog/ui-ux-from-zero.html": ('UI/UX с нуля: как начать новый проект с дизайн-мышлением · Мустафа Элькуши',
                                          'Порядок от пустой папки до проверенной первой версии: исследование, проблема, идеи, пользовательский путь, вайрфреймы, правила UI с цифрами и тест на 5 людях. Со схемой к каждому шагу.'),
            "blog/b2b-vs-b2c-ux.html": ('B2B и B2C в UI/UX: что меняется, когда покупатель не пользователь · Мустафа Элькуши',
                                        'Кто решает, кто читает вашу страницу, два разных пути к покупке, сравнение лендингов и экранов продукта, исследование и метрики, с примером клиники с обеих сторон.'),
            "blog/php-october-2026-django-cms.html": ("PHP в октябре 2026 года: что произошло и когда Django CMS — более безопасный выбор · Мустафа Элькуши",
                                                      "Срочное обновление для всех PHP-сайтов, атакованный плагин WordPress и бэкдор, который восстанавливает себя: что сделать на этой неделе и когда стоит переехать на Django CMS."),
        },
    },
}

BLOG = ["wat-framework", "secure-vibe-coded-apps", "seo-geo-aeo-audit", "ai-agents-python", "php-october-2026-django-cms",
        "maps-ranking-google-yandex", "ui-ux-from-zero", "b2b-vs-b2c-ux"]

PAGE_PATHS = (["index.html", "work/index.html"] + [f"work/{w}.html" for w in WORK]
              + ["blog/index.html"] + [f"blog/{b}.html" for b in BLOG]
              # The clinics offer: Russian first (Moscow clinics), English and
              # Arabic since 2026-11-07. Pages without a fragment in a language
              # are skipped for that language.
              + ["clinics/index.html"])

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


def line_icon(name: str) -> str:
    """One Lucide icon from tools/icons/lucide/ (cached by blog_art.py), inline.

    Only drawing elements are kept, the same clean-up blog_art.py does, so a
    cached file cannot bring a script or a link into a page.
    """
    raw = (SITE / "tools" / "icons" / "lucide" / f"{name}.svg").read_text()
    shapes = re.findall(r"<(?:path|circle|rect|line|polyline|polygon|ellipse)\b[^>]*?/?>", re.sub(r"<!--.*?-->", "", raw, flags=re.S))
    clean = "".join(re.sub(r"\s(?!(?:d|cx|cy|r|rx|ry|x|y|x1|y1|x2|y2|width|height|points)=)[\w:-]+=\"[^\"]*\"", "", t).rstrip("/>").rstrip() + "/>"
                    for t in shapes)
    return ('<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{clean}</svg>')


def out_path(code: str, page: str) -> str:
    """Where a page lands. English sits at the root; the rest under /ar, /ru."""
    return page if code == "en" else f"{code}/{page}"


def page(code: str, page_path: str, body: str) -> str:
    loc = LOCALES[code]
    title, desc = loc["titles"][page_path]
    rel = out_path(code, page_path)
    # GitHub Pages serves 404.html for a missing address at any depth, so its
    # links and assets start from the site root instead of counting ../.
    up = "/" if page_path == "404.html" else "../" * rel.count("/")
    dir_attr = ' dir="rtl"' if loc["rtl"] else ""
    # This language's own home page. "{up}index.html" alone is the English one,
    # which sent Arabic and Russian readers to English from every nav link.
    home = f"{up}{out_path(code, 'index.html')}"

    # Service illustrations live in tools/art/ and are inlined, so their colours
    # come from the page's theme tokens.
    body = re.sub(r"@@ART:([a-z-]+)@@", lambda m: (SITE / "tools" / "art" / f"{m.group(1)}.svg").read_text().strip(), body)
    # Small line icons inside a post (the maps post's card mock-ups and photo
    # list): @@ICON:name@@ inlines a cached Lucide icon in the text colour.
    body = re.sub(r"@@ICON:([a-z0-9-]+)@@", lambda m: line_icon(m.group(1)), body)
    call = (f'<a class="btn btn-secondary btn-lg" href="tel:{PHONE}">Позвонить: {PHONE_SHOWN}</a>'
            if PHONE and PHONE_SHOWN else "")
    body = body.replace("@@CALL@@", call)
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
    # Structured data, so search engines and AI tools can tell who the site is
    # about, where a page sits and what is offered. Data blocks, not scripts, so
    # the CSP allows them. One Person with a fixed @id that every page points to.
    ld = []
    me = {"@id": f"{ORIGIN}/#person"}
    page_name = title.split(" · ")[0]
    if page_path == "index.html":
        ld.append({
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "Person", "@id": f"{ORIGIN}/#person",
                 "name": "Moustafa Elkoushy", "alternateName": ["Мустафа Элькуши", "مصطفى القوشي"],
                 "jobTitle": "AI Product Engineer",
                 "url": f"{ORIGIN}/", "image": f"{ORIGIN}/assets/og.jpg", "email": f"mailto:{EMAIL}",
                 "address": {"@type": "PostalAddress", "addressLocality": "Moscow", "addressCountry": "RU"},
                 "knowsLanguage": ["ar", "en", "ru"],
                 "alumniOf": {"@type": "CollegeOrUniversity", "name": "Moscow Aviation Institute"},
                 "sameAs": [GITHUB, TG_URL]},
                {"@type": "WebSite", "@id": f"{ORIGIN}/#website", "url": f"{ORIGIN}/",
                 "name": "Moustafa Elkoushy", "inLanguage": ["en", "ar", "ru"], "publisher": me},
            ],
        })
    elif page_path != "404.html":
        # Home › section › page, in this page's language.
        crumbs = [(loc["home_name"], canonical(out_path(code, "index.html")))]
        section = page_path.split("/")[0]
        if section in ("work", "blog") and not page_path.endswith("index.html"):
            crumbs.append((loc["titles"][f"{section}/index.html"][0].split(" · ")[0],
                           canonical(out_path(code, f"{section}/index.html"))))
        crumbs.append((page_name, canonical(rel)))
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList",
                   "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u}
                                       for i, (n, u) in enumerate(crumbs)]})
    if page_path == "clinics/index.html":
        # The clinic offer as a Service: what it is, who provides it, where.
        # No prices: the clinics pages never show them.
        ld.append({"@context": "https://schema.org", "@type": "Service",
                   "name": page_name, "description": desc, "url": canonical(rel),
                   "serviceType": loc["service_type"], "provider": me,
                   "areaServed": {"@type": "City", "name": loc["city"]},
                   "audience": {"@type": "BusinessAudience", "name": loc["service_audience"]},
                   "availableLanguage": loc["lang"],
                   "hasOfferCatalog": {"@type": "OfferCatalog", "name": page_name,
                                       "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": n}}
                                                           for n in loc["service_items"]]}})
    if page_path.startswith("blog/") and not page_path.endswith("index.html"):
        slug = page_path[len("blog/"):-len(".html")]
        ld.append({"@context": "https://schema.org", "@type": "BlogPosting",
                   "headline": page_name, "description": desc, "url": canonical(rel),
                   "mainEntityOfPage": canonical(rel), "inLanguage": loc["lang"],
                   "image": f"{ORIGIN}/assets/og.jpg", "author": me, "publisher": me,
                   "isPartOf": {"@id": f"{ORIGIN}/#website"},
                   "about": slug.replace("-", " ")})
    person = "".join("\n<script type=\"application/ld+json\">" + json.dumps(d, ensure_ascii=False) + "</script>" for d in ld)
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
    # x-default is the English page; a page with no English version (the
    # Russian-only clinics page) points it at the first language it has.
    alts += f'\n<link rel="alternate" hreflang="x-default" href="{canonical(out_path(have[0] if have and "en" not in have else "en", page_path))}">'
    if page_path == "404.html":
        alts = '<meta name="robots" content="noindex">'

    # Language switcher: the same page in the other languages, or that
    # language's home page when this page is not translated yet.
    def target(c):
        wanted = page_path if fragment(c, page_path).exists() and page_path != "404.html" else "index.html"
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

    # Every nav item is a section of the home page, except Work and the blog,
    # which are their own pages and are marked current while you are on them.
    # Work goes straight to the full project list: test users who landed on the
    # home section first did not find the rest (2026-11-04).
    on_blog = ' aria-current="page"' if page_path.startswith("blog/") else ""
    on_work = ' aria-current="page"' if page_path.startswith("work/") else ""
    nav = "".join(
        f'<a href="{up}{out_path(code, "blog/index.html")}"{on_blog}>{label}</a>' if anchor == "blog" else
        f'<a href="{up}{out_path(code, "work/index.html")}"{on_work}>{label}</a>' if anchor == "work" else
        f'<a href="{home}#{anchor}">{label}</a>'
        for anchor, label in zip(["work", "services", "skills", "security", "about", "blog", "contact"], loc["nav"]))

    og_type = "article" if page_path.startswith("blog/") and not page_path.endswith("index.html") else "website"
    og_locale = {"en": "en_US", "ar": "ar_AR", "ru": "ru_RU"}.get(code, "en_US")
    yandex = f'\n<meta name="yandex-verification" content="{YANDEX_VERIFICATION}">' if YANDEX_VERIFICATION else ""
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
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{canonical(rel)}">
<meta property="og:site_name" content="{loc['home_name']}">
<meta property="og:locale" content="{og_locale}">
<meta name="twitter:card" content="summary_large_image">{person}
<meta name="color-scheme" content="dark light">
{alts}
{preload}
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="google-site-verification" content="3JFS0vJ_Erxu6fGrwpnXT0jaC41ccL5C2abv1gQSxvk"><!-- Search Console: keep, or the site loses verification -->{yandex}
<link rel="icon" href="{up}assets/favicon.svg?v=2" type="image/svg+xml">
<link rel="apple-touch-icon" href="{up}assets/apple-touch-icon.png">
<style>{css}</style>
<script>{BOOT_JS}</script>
<script type="speculationrules">{SPEC_RULES}</script>
</head>
<body>
{sprite}<header class="nav">
  <div class="wrap">
    <a class="brand" href="{home}"><span class="mark" aria-hidden="true"></span><span class="brand-name">Moustafa Elkoushy</span></a>
    <nav class="links" aria-label="{loc['main_nav']}">{nav}</nav>
    <div class="nav-end">
      <nav class="langs" aria-label="{loc['lang_label']}">{switch}</nav>
      <button class="theme-toggle cta" type="button" aria-label="{loc['theme']}">{SUN_MOON}</button>
      <a class="cta" href="{chat_url}" target="_blank" rel="noopener noreferrer">{chat_name} <span aria-hidden="true">{loc['arrow']}</span></a>
      <details class="menu">
        <summary class="cta"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg><span class="menu-label">{loc['menu']}</span></summary>
        <div class="menu-panel">
          <nav class="menu-links" aria-label="{loc['main_nav']}">{nav}</nav>
          <nav class="menu-langs" aria-label="{loc['lang_label']}">{menu_langs}</nav>
          <button class="theme-toggle menu-theme" type="button" aria-label="{loc['theme']}">{SUN_MOON}<span>{loc['theme_short']}</span></button>
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
<script src="{up}reveal.js{REVEAL_V}" defer></script>
<script src="{up}assets/analytics.js{ANALYTICS_V}" defer></script>{drone}
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

    # The not-found page. Kept out of PAGE_PATHS, so it gets no translations,
    # no hreflang and no sitemap entry; the fragment has a line in each language.
    (SITE / "404.html").write_text(minify_html(page("en", "404.html", fragment("en", "404.html").read_text(encoding="utf-8"))), encoding="utf-8")

    # sitemap.xml: every built page, with its translations, so Google finds the
    # whole site from one file. robots.txt points to it.
    urls = []
    for code in LOCALES:
        for page_path in PAGE_PATHS:
            if not fragment(code, page_path).exists():
                continue
            have = [c for c in LOCALES if fragment(c, page_path).exists()]
            alts = "".join(
                f'\n    <xhtml:link rel="alternate" hreflang="{c}" href="{canonical(out_path(c, page_path))}"/>'
                for c in have)
            urls.append(f"  <url>\n    <loc>{canonical(out_path(code, page_path))}</loc>{alts}\n  </url>")
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
    print(f"sitemap: {len(urls)} pages")
