"""Generate the Arabic version of the site from the English pages.

Arabic pages are written next to their English originals with an -ar suffix
(index-ar.html, about-us-ar.html, our-brands/flavora-cafe-ar.html). Keeping
them at the same directory depth means every relative path in the page --
stylesheets, scripts, uploads/ images -- stays valid untouched. Only links
between pages are rewritten, so an Arabic visitor stays in Arabic while
clicking around.

Each generated page gets lang="ar" dir="rtl" and one extra stylesheet,
frontend/css/takwa/rtl.css, loaded after custom.css so it can flip the
directional rules without editing them.

This is a generator, not an editor: it always rebuilds from the English page,
so it can be re-run after any English edit and is safe to run twice. The
English pages themselves are touched in exactly one place -- the language
dropdown, which has to learn where the Arabic page lives.

Run:  python3 build_arabic.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import text_engine as te
from translations_ar import AR, SKIP, is_placeholder

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "Takwafoods web", "takwaweb.designersidhost.com")

# The pages that make up the real site. The blogs?search=... files are demo
# leftovers from the original scrape and are deliberately not translated.
PAGES = [
    "index.html",
    "about-us.html",
    "listings.html",
    "our-team.html",
    "blogs.html",
    "careers.html",
    "apply.html",
    "contact-us.html",
    "our-brands/flavora-cafe.html",
    "our-brands/enna.html",
]

# Detail pages, linked from the listing and blog grids above. They are built
# the same way; they are listed apart only because the grids link into them.
DETAIL_PAGES = [
    "listing/mushroom-soup.html",
    "listing/chicken-noodle-soup.html",
    "listing/broccoli-soup.html",
    "listing/vegetable-soup.html",
    "listing/three-in-one.html",
    "listing/two-in-one.html",
    "listing/pure-coffee.html",
    "listing/coffee-creamer.html",
    "listing/espresso-capsules.html",
    "blog/quality-begins-with-every-test.html",
    "blog/delivering-freshness-across-the-region.html",
    "blog/flavora-cafe-opens-its-doors.html",
    "blog/introducing-enna-soups.html",
    "career/project-manager-consultant.html",
]

ALL_PAGES = PAGES + DETAIL_PAGES

RTL_CSS = '<link href="%sfrontend/css/takwa/rtl.css" rel="stylesheet" media="screen">'
CUSTOM_CSS = re.compile(r'<link href="((?:\.\./)*)frontend/css/takwa/custom\.css"[^>]*>')

PLACEHOLDERS = {
    "Full Name": "الاسم الكامل",
    "Name ": "الاسم ",
    "Company ": "الشركة ",
    "Email": "البريد الإلكتروني",
    "Phone number": "رقم الهاتف",
    "Subject ": "الموضوع ",
    "Message": "الرسالة",
    "Address": "العنوان",
    "City": "المدينة",
    "State": "المحافظة",
    "As per passport or national ID": "كما في جواز السفر أو الهوية",
    "If you have one": "إن وُجد",
    "MM/YYYY": "شهر/سنة",
    "MM/YYYY or present": "شهر/سنة أو حتى الآن",
    "Search products...": "ابحث عن منتج...",
    "Search products": "ابحث عن منتج",
}


# Page titles are not text nodes -- the scanner skips <title> on purpose --
# so they are handled here. Most follow a "Section || Takwa" pattern; the
# section half is looked up, the Takwa half is always the brand name.
TITLE_PARTS = {
    "Takwa": "تقوى",
    "takwa": "تقوى",
    "Home Page": "الصفحة الرئيسية",
    "About Us": "من نحن",
    "Listing": "المنتجات",
    "Team": "فريقنا",
    "Our Blog": "المدونة",
    "Career": "الوظائف",
    "Contact Us": "اتصل بنا",
    "Our Brands": "علاماتنا التجارية",
}

TITLE_TAG = re.compile(r"<title>([^<]*)</title>")


def translate_title(body):
    def repl(match):
        parts = [p.strip() for p in match.group(1).split("||")]
        out = []
        for part in parts:
            unescaped = te.html.unescape(part)
            arabic = TITLE_PARTS.get(part) or AR.get(unescaped)
            out.append(arabic if arabic else part)
        return "<title>%s</title>" % " || ".join(out)

    return TITLE_TAG.sub(repl, body, count=1)



# The filter matches against each card's data-search attribute, which is
# built once from the English product record. Translating the visible text
# alone therefore left an Arabic reader searching an English haystack --
# typing قهوة found nothing. This rebuilds the attribute from the card's own
# translated name and description, keeping the English words on the end so
# that a Latin query still works on the Arabic page.
SEARCH_ATTR = re.compile(r'data-search="([^"]*)"')
CARD_NAME = re.compile(r'<h[35][^>]*>([^<]+)</h[35]>')
CARD_DESC = re.compile(r'class="short-desc"[^>]*>([^<]+)<')


def localise_search(body):
    out, last = [], 0
    for m in SEARCH_ATTR.finditer(body):
        window = body[m.end():m.end() + 1800]
        extra = []
        name = CARD_NAME.search(window)
        if name:
            extra.append(name.group(1))
        desc = CARD_DESC.search(window)
        if desc:
            extra.append(desc.group(1))
        merged = " ".join(extra + [te.html.unescape(m.group(1))])
        merged = re.sub(r"\s+", " ", merged).strip().lower()
        out.append(body[last:m.start()])
        out.append('data-search="%s"' % merged.replace('"', "&quot;"))
        last = m.end()
    out.append(body[last:])
    return "".join(out)



# ---------------------------------------------------------------- Arabic head
# The head block is generated for the English page, so without this the Arabic
# copy would declare the English URL canonical, announce en_US as its locale
# and carry an English title and description -- telling Google the two pages
# are the same one, and serving English text to Arabic searchers.
AR_TITLES = {
    "index.html": "تقوى للأغذية | التصنيع الغذائي بالتعاقد والعلامة الخاصة — سوريا",
    "about-us.html": "عن تقوى للأغذية | 30 عاماً من التصنيع الغذائي في سوريا",
    "listings.html": "منتجاتنا | قهوة فلافورا وشوربات إينا — تقوى للأغذية",
    "our-brands/flavora-cafe.html": "فلافورا كافيه | قهوة سريعة التحضير وكبسولات ومبيّض — تقوى",
    "our-brands/enna.html": "شوربات إينا | دجاج بالشعيرية، فطر، خضار وبروكلي",
    "contact-us.html": "اتصل بتقوى للأغذية | دمشق، سوريا",
    "careers.html": "الوظائف في تقوى للأغذية | انضم إلى فريقنا في دمشق",
    "blogs.html": "الأخبار والمستجدات | تقوى للأغذية",
    "our-team.html": "فريقنا وقيادتنا | تقوى للأغذية",
}

AR_DESCRIPTIONS = {
    "index.html":
        "شركة تصنيع أغذية سورية منذ عام 1996. تصنيع مشترك، وتصنيع بالعلامة الخاصة، "
        "ونكهات وخلطات بهارات مخصّصة في القهوة والألبان والأغذية.",
    "about-us.html":
        "من مورّد مواد أولية عام 1996 إلى مورّد معتمد لدى نستله وشريك تصنيع إقليمي. "
        "تعرّف على الفريق والمعايير والمصنع خلف العلامات.",
    "listings.html":
        "تصفّح مجموعة تقوى كاملة: قهوة فلافورا سريعة التحضير والكبسولات والمبيّض، "
        "وشوربات إينا بالدجاج والشعيرية والفطر والخضار والبروكلي.",
    "our-brands/flavora-cafe.html":
        "فلافورا كافيه: خلطات ثلاثة في واحد واثنان في واحد بلا سكر، وقهوة نقية، "
        "ومبيّض، وكبسولات إسبريسو برازيلية وكولومبية.",
    "our-brands/enna.html":
        "شوربات إينا مصنوعة من خضار حقيقية مزروعة محلياً ومجفّفة في منشأتنا. "
        "أربعة أنواع، جاهزة خلال دقائق.",
    "contact-us.html":
        "تحدّث إلى فريقنا عن التصنيع المشترك أو التصنيع بعلامتك الخاصة أو البيع بالجملة. "
        "الكسوة، ريف دمشق. نرد خلال 24 ساعة.",
    "careers.html":
        "وظائف شاغرة في الإنتاج والجودة والبحث والتطوير وسلسلة التوريد لدى إحدى أبرز "
        "شركات تصنيع الأغذية في سوريا.",
    "blogs.html":
        "أخبار الشركة وإطلاق المنتجات وما يجري خلف الكواليس في مصنع تقوى.",
    "our-team.html":
        "الأشخاص الذين يديرون تقوى للأغذية — القيادة والإنتاج والجودة وسلسلة التوريد "
        "والإدارة التجارية.",
}


def fix_ar_head(body, english_page, arabic_page):
    """Point the generated page's head at itself, in Arabic."""
    key = english_page.replace(os.sep, "/")
    en = "https://takwafoods.com/" + key
    ar = "https://takwafoods.com/" + arabic_page.replace(os.sep, "/")

    body = body.replace('<link rel="canonical" href="%s">' % en,
                        '<link rel="canonical" href="%s">' % ar)
    body = body.replace('<meta property="og:url" content="%s">' % en,
                        '<meta property="og:url" content="%s">' % ar)
    body = body.replace('<meta property="og:locale" content="en_US">',
                        '<meta property="og:locale" content="ar_SY">')
    body = body.replace('<meta property="og:locale:alternate" content="ar_SY">',
                        '<meta property="og:locale:alternate" content="en_US">')

    title = AR_TITLES.get(key)
    if title:
        body = TITLE_TAG.sub(lambda _: "<title>%s</title>" % title, body, count=1)
        for pat in (r'(<meta name="title" content=")[^"]*(">)',
                    r'(<meta property="og:title" content=")[^"]*(">)',
                    r'(<meta name="twitter:title" content=")[^"]*(">)'):
            body = re.sub(pat, lambda m: m.group(1) + title + m.group(2), body)

    desc = AR_DESCRIPTIONS.get(key)
    if desc:
        for pat in (r'(<meta name="description" content=")[^"]*(">)',
                    r'(<meta property="og:description" content=")[^"]*(">)',
                    r'(<meta name="twitter:description" content=")[^"]*(">)'):
            body = re.sub(pat, lambda m: m.group(1) + desc + m.group(2), body)

    body = swap_webfont(body)
    return body


# The English site is set in Fustat, and every page inherits its webfont link
# from the shared head. The Arabic pages are set in Tajawal instead, so the
# link is rewritten here rather than left to load a family the -ar stylesheet
# never uses -- otherwise each Arabic page fetches Fustat and then paints in
# Tajawal, paying for a font it does not show.
#
# Tajawal ships discrete weights and has no 600, which is the weight the
# stylesheets ask for most. CSS font matching resolves a missing 600 upward, so
# those rules land on 700; 600 is deliberately not requested rather than
# silently mapped to something else. 200 is dropped because nothing uses it.
FONT_LINK = re.compile(
    r'<link href="https://fonts\.googleapis\.com/css2\?family=Fustat[^"]*"'
    r'\s+rel="stylesheet">')
TAJAWAL = ('<link href="https://fonts.googleapis.com/css2?family=Tajawal:'
           'wght@300;400;500;700;800;900&amp;display=swap" rel="stylesheet">')


def swap_webfont(body):
    body, n = FONT_LINK.subn(TAJAWAL, body)
    if not n and "family=Tajawal" not in body:
        print("  !! no Fustat font link found; Arabic page will fall back")
    return body


PLACEHOLDER_ATTR = re.compile(r'placeholder="([^"]*)"')


def translate_placeholders(body, missing):
    """Translate placeholder attributes, matching on the trimmed value.

    These were matched as exact strings, which is brittle in a way that had
    already gone wrong: the table holds "Email" and "Phone number" while the
    markup carries placeholder="Email " and placeholder="Phone number " with a
    trailing space, so two fields on the contact form stayed in English on an
    otherwise Arabic page. Comparing trimmed values fixes those and every other
    field that picks up stray whitespace later.

    Anything with no entry is reported through the same channel as untranslated
    text, so a new field shows up as a warning rather than silently shipping
    in English.
    """
    table = {k.strip(): v for k, v in PLACEHOLDERS.items()}

    def swap(match):
        raw = match.group(1)
        key = raw.strip()
        if not key or is_placeholder(key):
            return match.group(0)
        if key not in table:
            missing.add(key)
            return match.group(0)
        return 'placeholder="%s"' % table[key].strip()

    return PLACEHOLDER_ATTR.sub(swap, body)


def ar_name(page):
    """index.html -> index-ar.html, keeping any folder prefix."""
    base, ext = os.path.splitext(page)
    return base + "-ar" + ext


def translate_text(body, missing):
    """Replace every text node with its Arabic translation.

    Nodes carry absolute offsets into the source, so the replacements are
    spliced in from the end backwards and earlier offsets stay correct.
    """
    for node in reversed(te.scan(body)):
        stripped = node.text.strip()
        if not stripped or stripped in SKIP or is_placeholder(stripped):
            continue
        arabic = AR.get(stripped)
        if arabic is None:
            missing.add(stripped)
            continue
        # keep whatever whitespace surrounded the original text
        lead = node.text[: len(node.text) - len(node.text.lstrip())]
        trail = node.text[len(node.text.rstrip()) :]
        replacement = te.escape_for_html(lead + arabic + trail)
        body = body[: node.start] + replacement + body[node.end :]
    return body


def rewrite_links(body, depth):
    """Point internal page links at their Arabic counterparts."""
    known = {os.path.basename(p) for p in PAGES}
    # any href to a site page, with or without a ../ or folder prefix
    def repl(match):
        prefix, name = match.group(1), match.group(2)
        if name not in known:
            return match.group(0)
        return 'href="%s%s"' % (prefix, ar_name(name))

    body = re.sub(r'href="((?:\.\./)*(?:our-brands/)?)([a-z0-9\-]+\.html)"',
                  repl, body)

    # detail pages: listing/mushroom-soup.html, blog/..., career/...
    body = re.sub(r'href="((?:\.\./)*(?:listing|blog|career)/[a-z0-9\-]+)\.html"',
                  r'href="\1-ar.html"', body)
    return body


# The two dropdown entries are matched on their link text, not their href.
# Matching the href would only work on a pristine page: once this script has
# pointed "English" at index.html, the link rewriting above cannot tell it
# apart from any other link to the home page and turns it into index-ar.html,
# stranding the reader in Arabic. The label is the one part that does not
# move, so keying on it makes the rewrite self-correcting on every re-run.
DROPDOWN_ITEM = re.compile(
    r'(<a class="dropdown-item"[^>]*?href=")[^"]*("[^>]*>\s*(English|Arabic)\s*</a>)')
LANG_TOGGLE = re.compile(r'(<a class="[^"]*lang-toggle"[^>]*?href=")[^"]*(")')


# The button itself carries a bare text node -- "English" -- between the globe
# and the chevron. It names the language you are reading, so on an Arabic page
# it has to say العربية, and its link has to lead back to English.
TOGGLE_LABEL = re.compile(
    r'(<a class="[^"]*lang-toggle".*?</span>)\s*(?:English|العربية)\s*(<span class="btn-arrow">)',
    re.S)


def rewrite_language_switcher(body, english_page, arabic_page, depth, is_arabic=False):
    """Make the header dropdown switch between this page's two languages.

    Both pages sit in the same folder, so the targets are bare filenames.
    """
    targets = {"English": os.path.basename(english_page),
               "Arabic": os.path.basename(arabic_page)}
    body = DROPDOWN_ITEM.sub(
        lambda m: m.group(1) + targets[m.group(3)] + m.group(2), body)

    # the toggle shows the current language and leads to the other one
    label = "العربية" if is_arabic else "English"
    goes_to = targets["English"] if is_arabic else targets["Arabic"]
    body = LANG_TOGGLE.sub(lambda m: m.group(1) + goes_to + m.group(2), body)
    return TOGGLE_LABEL.sub(lambda m: m.group(1) + " " + label + " " + m.group(2), body)


def build_page(page, missing):
    src = os.path.join(SITE, page)
    depth = page.count("/")
    body = te.read(src)

    arabic = ar_name(page)
    # link rewriting has to run first: it turns index.html into index-ar.html
    # everywhere, which would otherwise swallow the "English" entry the
    # switcher writes a moment later and strand the reader in Arabic.
    body = rewrite_links(body, depth)
    body = rewrite_language_switcher(body, page, arabic, depth, is_arabic=True)
    body = translate_text(body, missing)
    body = translate_title(body)
    body = fix_ar_head(body, page, arabic)
    body = localise_search(body)

    body = body.replace('<html lang="en">', '<html lang="ar" dir="rtl">', 1)

    match = CUSTOM_CSS.search(body)
    if match and "takwa/rtl.css" not in body:
        link = RTL_CSS % match.group(1)
        body = body[: match.end()] + "\n    " + link + body[match.end() :]

    body = translate_placeholders(body, missing)

    te.write(os.path.join(SITE, arabic), body)
    return arabic


def patch_english(page):
    """Teach the English page's dropdown where its Arabic twin lives."""
    src = os.path.join(SITE, page)
    depth = page.count("/")
    body = te.read(src)
    before = body
    body = rewrite_language_switcher(body, page, ar_name(page), depth)
    if body != before:
        te.write(src, body)
        return True
    return False


def main():
    missing = set()
    for page in ALL_PAGES:
        if not os.path.exists(os.path.join(SITE, page)):
            print("  ! missing English page: %s" % page)
            continue
        out = build_page(page, missing)
        patched = patch_english(page)
        print("  %-30s -> %-34s %s" % (page, out,
                                       "(switcher wired)" if patched else ""))

    if missing:
        print("\n  %d strings have no Arabic translation yet:" % len(missing))
        for text in sorted(missing):
            print("      %s" % (text[:90] + ("..." if len(text) > 90 else "")))
    else:
        print("\n  every string translated")


if __name__ == "__main__":
    main()
