import collections
import glob
import html as htmlmod
import json
import os
import re
import urllib.parse

ROOT = "/home/geogre-youssef/obsidian/George/Takwa"
SITE = os.path.join(ROOT, "Takwafoods web", "takwaweb.designersidhost.com")
OUT = os.path.join(SITE, "_photo-index.html")

with open(os.path.join(ROOT, "photo-slots.json"), encoding="utf-8") as fh:
    slot_map = {k: v for k, v in json.load(fh).items() if not k.startswith("_")}
NAME_OF = {v: k for k, v in slot_map.items()}

BACKUPS = os.path.join(ROOT, "_photo-backups")
PAGES_BACKUP = os.path.join(BACKUPS, "_pages")

# slots the user has removed from the site — still listed, so Undo stays reachable
REMOVED = set()
_manifest = os.path.join(BACKUPS, "_removed.json")
if os.path.exists(_manifest):
    try:
        with open(_manifest, encoding="utf-8") as fh:
            REMOVED = set(json.load(fh).keys())
    except Exception:
        pass


def sources_of(page):
    """Both copies of a page: the pristine backup and the live file.

    Neither on its own is complete. The product cards, the filter UI and
    anything else written at rebuild time exist only in the live file --
    listings.html mentions six images in the backup and fifteen live, which
    is why "Our Products" used to show a single header photo. Photos the
    owner has removed survive only in the backup. Reading both and merging
    means the index lists everything either of them refers to.
    """
    out = []
    backed = os.path.join(PAGES_BACKUP, page)
    if os.path.exists(backed):
        out.append(backed)
    live = os.path.join(SITE, page)
    if os.path.exists(live) and live != backed:
        out.append(live)
    return out


def every_html():
    """All HTML files, so the 'used on N pages' count tells the whole truth —
    including the language-switcher and blog copies."""
    out = []
    for dirpath, _dirs, files in os.walk(SITE):
        for f in files:
            if f.lower().endswith(".html") and not f.startswith("_photo-index"):
                out.append(os.path.relpath(os.path.join(dirpath, f), SITE))
    return sorted(out)


def true_page_count(rel):
    base = os.path.basename(rel)
    variants = {base, urllib.parse.quote(base), base.replace(" ", "%20")}
    n = 0
    for page in every_html():
        for src in sources_of(page):
            body = open(src, encoding="utf-8", errors="replace").read()
            if any(v in body for v in variants):
                n += 1
                break
    return n

KNOWN_LABELS = {
    "index.html": "Home Page",
    "about-us.html": "About Us",
    "listings.html": "Our Products",
    "our-brands/flavora-cafe.html": "Our Brand \u2014 Flavora",
    "our-brands/enna.html": "Our Brand \u2014 Enna",
    "our-team.html": "Our Team",
    "blogs.html": "Blog & Events",
    "careers.html": "Vacancies",
    "contact-us.html": "Contact Us",
}


def _title_of(rel):
    """The page's own <title>, minus the site suffix."""
    try:
        body = open(os.path.join(SITE, rel), encoding="utf-8", errors="replace").read()
    except OSError:
        return rel
    m = re.search(r"<title>(.*?)</title>", body, re.S)
    # the title is HTML, so entities are decoded before the card escapes
    # them again -- otherwise "&amp;" ends up rendered as "&amp;amp;"
    text = htmlmod.unescape(re.sub(r"\s+", " ", m.group(1)).strip()) if m else rel
    # drop the site suffix, written either as "|| Takwa" or "| Takwa Foods"
    return re.sub(r"\s*\|\|?\s*Takwa.*$", "", text, flags=re.I).strip() or rel


def discover_pages():
    """Every real English page, most important first.

    Replaces a hard-coded list of nine. The Arabic pages are generated copies
    that reuse the same image files, so listing them too would show every
    photo twice.
    """
    main, products, articles, vacancies = [], [], [], []
    for path in sorted(glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(path, SITE).replace(os.sep, "/")
        base = os.path.basename(rel)
        if base.startswith(("_photo-index", "blogs?", "language-switcher")):
            continue
        if rel.endswith("-ar.html"):
            continue
        if rel in KNOWN_LABELS:
            continue
        if rel.startswith("listing/"):
            products.append((rel, "Product \u2014 " + _title_of(rel)))
        elif rel.startswith("blog/"):
            articles.append((rel, "Article \u2014 " + _title_of(rel)))
        elif rel.startswith("career/"):
            vacancies.append((rel, "Vacancy \u2014 " + _title_of(rel)))
        else:
            main.append((rel, _title_of(rel)))
    known = [(r, l) for r, l in KNOWN_LABELS.items()
             if os.path.exists(os.path.join(SITE, r))]
    return known + main + products + articles + vacancies


PAGE_LABELS = discover_pages()

PATTERN = re.compile(
    r'(?:src=|background-image:\s*url\(|background:\s*url\()["\']?'
    r'([^"\'\)>\s]+\.(?:png|jpe?g|webp|mp4|svg))', re.I)

per_page = collections.OrderedDict()
used_on = collections.defaultdict(set)

for page, label in PAGE_LABELS:
    seen = []
    for path in sources_of(page):
        src = open(path, encoding="utf-8", errors="replace").read()
        for m in PATTERN.finditer(src):
            ref = m.group(1)
            if ref.startswith("http") or "/js/" in ref:
                continue
            rel = urllib.parse.unquote(ref.replace("../", ""))
            if rel not in seen:
                seen.append(rel)
            used_on[rel].add(label)
    per_page[label] = seen

SHARED = {slot_map[k] for k in
          ("logo", "logo-footer", "watermark", "footer-1", "footer-2", "footer-3")}


def dims(rel):
    p = os.path.join(SITE, rel)
    if rel.lower().endswith((".mp4", ".svg")) or not os.path.exists(p):
        return ""
    try:
        from PIL import Image
        with Image.open(p) as im:
            return "%d&times;%d" % (im.width, im.height)
    except Exception:
        return ""


def card(rel):
    name = NAME_OF.get(rel, "")
    url = urllib.parse.quote(rel)
    others = sorted(used_on.get(rel, []))
    warn = ""
    if len(others) > 1:
        warn = ('<p class="warn">Also on %s. Changing it changes all of them.</p>'
                % htmlmod.escape(", ".join(others)))

    low = rel.lower()
    if low.endswith(".mp4"):
        media = '<video src="%s" muted loop playsinline class="thumb"></video>' % url
        note = '<p class="warn">Video &mdash; the tool can\'t swap this one.</p>'
    elif low.endswith(".svg"):
        media = '<img src="%s" loading="lazy" class="thumb" alt="">' % url
        note = '<p class="warn">SVG icon &mdash; the tool can\'t swap this one.</p>'
    else:
        media = '<img src="%s" loading="lazy" class="thumb" alt="">' % url
        note = ""

    swappable = not low.endswith((".mp4", ".svg"))
    esc = htmlmod.escape(name, quote=True)
    if swappable:
        action = ('<label class="pick">Change photo'
                  '<input type="file" accept="image/*" data-slot="%s" hidden></label>'
                  '<button class="undo" data-slot="%s" title="Put everything back">Undo</button>'
                  '<button class="rm" data-slot="%s" data-pages="%s" '
                  'title="Take the image out of the page completely">Remove</button>'
                  '<button class="blank" data-slot="%s" '
                  'title="Empty the photo but keep the space">Blank</button>'
                  % (esc, esc, esc, true_page_count(rel) or 1, esc))
    else:
        action = ""

    removed_badge = ('<p class="removed">Removed from the page — press Undo to bring it back.</p>'
                     if name in REMOVED else "")

    return """
    <figure class="card" data-slot="%s">
      <div class="thumbwrap">%s</div>
      <figcaption>
        <code class="slot">%s</code>
        <p class="dims">%s</p>
        <p class="path">%s</p>
        %s%s%s
        <div class="actions">%s</div>
        <p class="status"></p>
      </figcaption>
    </figure>""" % (htmlmod.escape(name, quote=True), media, htmlmod.escape(name),
                    dims(rel), htmlmod.escape(rel), warn, note, removed_badge, action)


def anchor(label):
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


sections, navlinks = [], []
for label, refs in per_page.items():
    unique = [r for r in refs if r not in SHARED]
    if not unique:
        continue
    sections.append('<section id="%s"><h2>%s</h2><div class="grid">%s</div></section>'
                    % (anchor(label), htmlmod.escape(label), "\n".join(card(r) for r in unique)))
    navlinks.append('<a href="#%s">%s</a>' % (anchor(label), htmlmod.escape(label)))

shared_cards = "\n".join(card(r) for r in sorted(SHARED) if os.path.exists(os.path.join(SITE, r)))
sections.append('<section id="shared"><h2>Logo &amp; Footer '
                '<span class="sub">(appears on every page)</span></h2>'
                '<div class="grid">%s</div></section>' % shared_cards)
navlinks.append('<a href="#shared">Logo &amp; Footer</a>')

doc = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Takwa — Photo Index</title>
<style>
  * { box-sizing: border-box; }
  body { margin:0; font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
         color:#1e1e1e; background:#fafaf8; }
  header { background:#4c9932; color:#fff; padding:28px 32px; }
  header h1 { margin:0 0 6px; font-size:26px; }
  header p { margin:0; opacity:.92; font-size:14px; }
  nav { position:sticky; top:0; background:#fff; border-bottom:1px solid #e2e2dc; padding:12px 32px;
        display:flex; flex-wrap:wrap; gap:14px; z-index:5; }
  nav a { color:#3d7a28; text-decoration:none; font-size:13px; font-weight:600; }
  nav a:hover { text-decoration:underline; }
  .how { margin:24px 32px; padding:18px 22px; background:#fff; border:1px solid #e2e2dc;
         border-radius:10px; }
  .how h3 { margin:0 0 10px; font-size:15px; }
  .how pre { background:#f4f4f0; padding:12px 14px; border-radius:7px; overflow-x:auto;
             margin:8px 0; font-size:13px; }
  .how ol { margin:8px 0 0 18px; padding:0; }
  .how li { margin-bottom:6px; }
  .hint { display:block; color:#777; font-size:12.5px; margin-top:3px; }
  section { margin:0 32px 44px; }
  section h2 { font-size:19px; border-bottom:2px solid #4c9932; padding-bottom:7px; margin:0 0 18px; }
  .sub { font-weight:400; font-size:13px; color:#777; }
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(215px,1fr)); gap:18px; }
  .card { margin:0; background:#fff; border:1px solid #e2e2dc; border-radius:10px;
          overflow:hidden; display:flex; flex-direction:column; }
  .thumbwrap { height:150px; background:#f0f0ea; display:flex; align-items:center;
               justify-content:center; overflow:hidden; }
  .thumb { max-width:100%; max-height:100%; object-fit:contain; }
  figcaption { padding:11px 13px; font-size:12px; flex:1; display:flex; flex-direction:column; }
  .slot { display:inline-block; background:#e8f4e2; color:#2f6b1e; padding:2px 7px;
          border-radius:4px; font-size:12px; font-weight:700; align-self:flex-start;
          user-select:all; cursor:pointer; }
  .noslot { color:#999; font-style:italic; font-size:12px; }
  .dims { margin:6px 0 3px; color:#666; }
  .path { margin:0 0 8px; color:#999; word-break:break-all; font-size:11px;
          user-select:all; cursor:text; }
  .warn { margin:0 0 8px; color:#a05a00; background:#fdf3e3; padding:6px 8px;
          border-radius:5px; font-size:11px; }
  .actions { margin-top:auto; display:flex; gap:6px; align-items:center; flex-wrap:wrap; }
  .rm, .blank { border:1px solid #e0c0bc; background:#fff; border-radius:6px; padding:6px 10px;
                font-size:12px; cursor:pointer; color:#a33b2c; }
  .rm:hover, .blank:hover { background:#fdf0ee; }
  .removed { margin:0 0 8px; color:#a33b2c; background:#fdf0ee; padding:6px 8px;
             border-radius:5px; font-size:11px; font-weight:600; }
  .card.is-removed .thumbwrap { opacity:.28; filter:grayscale(1); }
  .card.is-removed { border-color:#e0c0bc; }
  .card.is-removed .rm { display:none; }
  .pick { background:#4c9932; color:#fff; border-radius:6px; padding:6px 12px; font-size:12px;
          font-weight:600; cursor:pointer; display:inline-block; }
  .pick:hover { background:#3d7a28; }
  .undo { border:1px solid #cfcfc7; background:#fff; border-radius:6px; padding:6px 10px;
          font-size:12px; cursor:pointer; color:#666; }
  .undo:hover { background:#f2f2ec; }
  .status { margin:8px 0 0; font-size:11.5px; min-height:1px; }
  .status.ok { color:#2f6b1e; }
  .status.err { color:#b3261e; }
  .status.busy { color:#777; }
  .card.flash { outline:2px solid #4c9932; outline-offset:-2px; }
</style>
</head>
<body>
<header>
  <h1>Takwa — Photo Index</h1>
  <p>Every image on the site, grouped by the page it appears on.</p>
</header>
<nav>@@NAV@@</nav>

<div class="how">
  <h3>How to change a photo</h3>
  <p style="margin:0;font-size:14px;">Find the photo below, click <strong>Change photo</strong>,
  and pick a picture from your computer. That's it &mdash; it's applied straight away.</p>
  <p class="hint" style="margin-top:8px;">Your photo is cropped and resized automatically, so any
  JPG or PNG works. To see the change on the real site, open it and press
  <strong>Ctrl+Shift+R</strong>.</p>
  <p class="hint"><strong>Remove</strong> takes the image out of the page completely and the
  layout closes up. <strong>Blank</strong> empties the photo but keeps the space, ready for a
  replacement. <strong>Undo</strong> reverses any of these &mdash; nothing here is permanent.</p>
</div>

@@SECTIONS@@

<script>
function cardOf(el) { return el.closest('.card'); }

// Show/hide the "removed from the page" state without rebuilding the file.
function markRemoved(card, isRemoved) {
  card.classList.toggle('is-removed', isRemoved);
  var badge = card.querySelector('.removed');
  if (isRemoved && !badge) {
    badge = document.createElement('p');
    badge.className = 'removed';
    badge.textContent = 'Removed from the page — press Undo to bring it back.';
    card.querySelector('.actions').before(badge);
  } else if (!isRemoved && badge) {
    badge.remove();
  }
}

// Ask the server what's currently removed, so a refresh shows the truth.
fetch('/_state')
  .then(function (r) { return r.json(); })
  .then(function (s) {
    (s.removed || []).forEach(function (slot) {
      var card = document.querySelector('.card[data-slot="' + slot + '"]');
      if (card) markRemoved(card, true);
    });
  })
  .catch(function () { /* server not running — leave the page as generated */ });

function say(card, text, kind) {
  var s = card.querySelector('.status');
  s.textContent = text;
  s.className = 'status ' + (kind || '');
}

function refreshThumb(card) {
  var img = card.querySelector('.thumb');
  if (!img) return;
  var base = img.getAttribute('src').split('?')[0];
  img.setAttribute('src', base + '?t=' + Date.now());
}

function send(card, url, body) {
  return fetch(url, body ? { method: 'POST', body: body } : { method: 'POST' })
    .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
    .then(function (res) {
      if (!res.ok || !res.j.ok) throw new Error(res.j.message || 'Failed');
      say(card, res.j.message, 'ok');
      refreshThumb(card);
      card.classList.add('flash');
      setTimeout(function () { card.classList.remove('flash'); }, 1500);
    })
    .catch(function (e) {
      say(card, e.message || 'Could not reach the server — is start.py still running?', 'err');
    });
}

document.querySelectorAll('input[type=file]').forEach(function (input) {
  input.addEventListener('change', function () {
    var file = input.files && input.files[0];
    if (!file) return;
    var card = cardOf(input);
    say(card, 'Uploading ' + file.name + '...', 'busy');
    send(card, '/_upload?slot=' + encodeURIComponent(input.dataset.slot), file)
      .then(function () { input.value = ''; });
  });
});

document.querySelectorAll('.undo').forEach(function (b) {
  b.addEventListener('click', function () {
    var card = cardOf(b);
    say(card, 'Restoring...', 'busy');
    send(card, '/_undo?slot=' + encodeURIComponent(b.dataset.slot), null)
      .then(function () { markRemoved(card, false); });
  });
});

// Take the image out of the page entirely (the layout closes up).
document.querySelectorAll('.rm').forEach(function (b) {
  b.addEventListener('click', function () {
    var n = parseInt(b.dataset.pages, 10) || 1;
    var where = n > 1 ? n + ' pages' : 'the page';
    if (!confirm('Remove "' + b.dataset.slot + '" from ' + where + '?\\n\\n' +
                 'The image disappears completely and the layout closes up.\\n' +
                 'You can put it back with Undo.')) return;
    var card = cardOf(b);
    say(card, 'Removing...', 'busy');
    send(card, '/_remove?slot=' + encodeURIComponent(b.dataset.slot), null)
      .then(function () { markRemoved(card, true); });
  });
});

// Empty the photo but leave the space exactly as it is.
document.querySelectorAll('.blank').forEach(function (b) {
  b.addEventListener('click', function () {
    if (!confirm('Blank out "' + b.dataset.slot + '"?\\n\\n' +
                 'The photo becomes empty white, but the space stays the same size.\\n' +
                 'You can put it back with Undo.')) return;
    var card = cardOf(b);
    say(card, 'Blanking...', 'busy');
    send(card, '/_blank?slot=' + encodeURIComponent(b.dataset.slot), null);
  });
});
</script>
</body>
</html>""".replace("@@NAV@@", " ".join(navlinks)).replace("@@SECTIONS@@", "".join(sections))

def check_script(text):
    """Catch unterminated JS string literals before they reach the browser.

    The script is embedded in a Python string, so a bare \\n escapes at build
    time and silently breaks every button on the page. Fail loudly instead.
    """
    body = re.search(r"<script>(.*?)</script>", text, re.S)
    if not body:
        raise SystemExit("BUILD FAILED: no <script> block generated")

    for lineno, line in enumerate(body.group(1).splitlines(), 1):
        stripped = re.sub(r"\\.", "", line)          # drop escaped chars
        stripped = re.sub(r"//.*", "", stripped)     # drop line comments
        if stripped.count("'") % 2 or stripped.count('"') % 2:
            raise SystemExit(
                "BUILD FAILED: unterminated string in the page script, line %d:\n  %s"
                % (lineno, line.strip()))


check_script(doc)
open(OUT, "w", encoding="utf-8").write(doc)
print("wrote", OUT)
print("cards:", doc.count('class="card"'))
print("named:", doc.count('class="slot"'), " unnamed:", doc.count('class="noslot"'))
print("script: syntax check passed")
