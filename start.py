#!/usr/bin/env python3
"""
Start the Takwa website with photo editing built in.

    python3 start.py

Then open the address it prints. Every photo has a "Change photo" button —
pick a file and it's applied straight away. Nothing else to run.
"""

import hashlib
import importlib
import importlib.util
import io
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from PIL import Image

import text_engine as te

PORT = 8099
SITE_TAIL = os.path.join("Takwafoods web", "takwaweb.designersidhost.com")

def all_pages(site):
    """Every HTML file in the site — including the language-switcher and blog
    copies, which repeat the same images and must be kept in step."""
    found = []
    for dirpath, _dirs, files in os.walk(site):
        for f in files:
            # anything starting with _ is a tool page (the photo index, the
            # Arabic text index), not part of the site
            if not f.lower().endswith(".html") or f.startswith("_"):
                continue
            found.append(os.path.relpath(os.path.join(dirpath, f), site))
    return sorted(found)


def find_site():
    here = os.path.dirname(os.path.abspath(__file__))
    for start in (here, os.getcwd()):
        d = start
        for _ in range(5):
            p = os.path.join(d, SITE_TAIL)
            if os.path.isdir(p):
                return p
            d = os.path.dirname(d)
    sys.exit("Could not find the website folder (%s)." % SITE_TAIL)


SITE = find_site()
ROOT = os.path.dirname(os.path.dirname(SITE))
BACKUPS = os.path.join(ROOT, "_photo-backups")
PAGES = all_pages(SITE)


def load_slots():
    for d in (ROOT, os.path.dirname(os.path.abspath(__file__)), os.path.join(ROOT, "other")):
        p = os.path.join(d, "photo-slots.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                return {k: v for k, v in json.load(fh).items() if not k.startswith("_")}
    return {}


SLOTS = load_slots()


def flatten(im):
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert("RGB")


def cover(im, w, h):
    if im.width / im.height > w / h:
        nw = int(im.height * w / h)
        im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
    else:
        nh = int(im.width * h / w)
        im = im.crop((0, (im.height - nh) // 2, im.width, (im.height - nh) // 2 + nh))
    return im.resize((w, h), Image.LANCZOS)


def apply_photo(slot, data):
    """Write uploaded bytes into a slot, matching its existing size and format."""
    if slot not in SLOTS:
        raise ValueError("Unknown photo: %s" % slot)

    rel = SLOTS[slot]
    target = os.path.join(SITE, rel)
    low = rel.lower()
    if low.endswith(".mp4"):
        raise ValueError("That one is a video, not a photo.")
    if low.endswith(".svg"):
        raise ValueError("That one is an icon that has to be edited by hand.")
    if not os.path.exists(target):
        raise ValueError("Missing on disk: %s" % rel)

    try:
        src = Image.open(io.BytesIO(data))
        src.load()
    except Exception:
        raise ValueError("That file isn't an image I can read. Try a JPG or PNG "
                         "(iPhone HEIC files need exporting first).")

    with Image.open(target) as original:
        w, h = original.size

    # keep the very first original so "Undo" always goes back to the real thing
    saved = os.path.join(BACKUPS, rel)
    if not os.path.exists(saved):
        os.makedirs(os.path.dirname(saved), exist_ok=True)
        shutil.copy2(target, saved)

    soft = src.width < w or src.height < h
    out = cover(flatten(src), w, h)
    ext = os.path.splitext(target)[1].lower()
    opts = {"quality": 88, "method": 6} if ext == ".webp" else \
           {"quality": 88} if ext in (".jpg", ".jpeg") else {}
    out.save(target, **opts)

    msg = "Updated (%dx%d)" % (w, h)
    if soft:
        msg += " — your photo was smaller than this slot, so it may look soft."
    return msg


def blank_photo(slot):
    """Replace the photo with an empty placeholder, keeping the layout intact."""
    if slot not in SLOTS:
        raise ValueError("Unknown photo: %s" % slot)
    rel = SLOTS[slot]
    target = os.path.join(SITE, rel)
    low = rel.lower()
    if low.endswith((".mp4", ".svg")):
        raise ValueError("That one isn't a photo.")

    with Image.open(target) as original:
        w, h = original.size

    saved = os.path.join(BACKUPS, rel)
    if not os.path.exists(saved):
        os.makedirs(os.path.dirname(saved), exist_ok=True)
        shutil.copy2(target, saved)

    ext = os.path.splitext(target)[1].lower()
    blank = Image.new("RGB", (w, h), (255, 255, 255))
    opts = {"quality": 88, "method": 6} if ext == ".webp" else \
           {"quality": 88} if ext in (".jpg", ".jpeg") else {}
    blank.save(target, **opts)
    return "Blanked out — the space is still there, ready for a new photo."


# ---------------------------------------------------------------- page edits

PAGES_BACKUP = os.path.join(BACKUPS, "_pages")
MANIFEST = os.path.join(BACKUPS, "_removed.json")


def read_manifest():
    if os.path.exists(MANIFEST):
        try:
            with open(MANIFEST, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            pass
    return {}


def write_manifest(data):
    os.makedirs(BACKUPS, exist_ok=True)
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def pristine_path(page):
    """The untouched copy of a page, if we've already backed one up."""
    backed = os.path.join(PAGES_BACKUP, page)
    return backed if os.path.exists(backed) else os.path.join(SITE, page)


def backup_page(page):
    """Keep the very first, untouched copy of a page so Undo always has
    something real to go back to — whether the change was a photo removal
    or a text edit."""
    backed = os.path.join(PAGES_BACKUP, page)
    if not os.path.exists(backed):
        os.makedirs(os.path.dirname(backed), exist_ok=True)
        shutil.copy2(os.path.join(SITE, page), backed)


def name_variants(rel):
    """The spellings of a filename that can appear in the HTML."""
    base = os.path.basename(rel)
    return {base, urllib.parse.quote(base), base.replace(" ", "%20")}


def strip_from_html(text, rel):
    """Delete the <img> tags and background-image rules that point at this file."""
    alts = "|".join(re.escape(v) for v in name_variants(rel))
    text = re.sub(r'<img\b[^>]*?src\s*=\s*"[^"]*(?:%s)"[^>]*?>' % alts, "", text, flags=re.I)
    text = re.sub(r'background(?:-image)?\s*:\s*url\(\s*[^)]*(?:%s)[^)]*\)\s*;?' % alts,
                  "", text, flags=re.I)
    return text


def read_html(path):
    """Read a page without touching its line endings or any odd bytes."""
    with open(path, encoding="utf-8", errors="surrogateescape", newline="") as fh:
        return fh.read()


def write_html(path, body):
    """Write it back exactly as-is — CRLF stays CRLF."""
    with open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as fh:
        fh.write(body)


def pages_using(rel):
    found = []
    for page in PAGES:
        src = pristine_path(page)
        if not os.path.exists(src):
            continue
        if any(v in read_html(src) for v in name_variants(rel)):
            found.append(page)
    return found


TEXT_EDITS_JSON = os.path.join(BACKUPS, "_text_edits.json")


def read_text_edits():
    if os.path.exists(TEXT_EDITS_JSON):
        try:
            with open(TEXT_EDITS_JSON, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            pass
    return {}


def write_text_edits(data):
    os.makedirs(BACKUPS, exist_ok=True)
    with open(TEXT_EDITS_JSON, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def rebuild_pages(pages):
    """Rewrite each page from its pristine copy, re-applying every active
    removal and then every saved text edit.

    Text edits have to be replayed here: this function restores a page from
    the pristine copy, which by definition predates them, so without this a
    photo Remove/Undo would silently wipe out text the user had saved.
    Removing an <img> or a background-image never changes how many text
    nodes a page has, so the saved positions stay valid.
    """
    manifest = read_manifest()
    edits = read_text_edits()
    for page in pages:
        body = read_html(pristine_path(page))
        for slot in manifest:
            if slot in SLOTS:
                body = strip_from_html(body, SLOTS[slot])
        full = os.path.join(SITE, page)
        write_html(full, body)

        for seq_str, text in sorted(edits.get(page, {}).items(), key=lambda kv: int(kv[0])):
            try:
                te.apply_edit(full, int(seq_str), text)
            except Exception:
                pass  # the page changed shape; skip rather than corrupt it

        # news items live in a manifest for the same reason as products: this
        # function restores from the pristine copy, which never had them, so
        # without this every rebuild would silently unpublish everything that
        # had been added.
        if page == "blogs.html":
            write_html(full, insert_news_cards(read_html(full)))

        # products live in a manifest too, so they survive the same rebuild
        if page == "listings.html":
            b = insert_product_cards(read_html(full))
            b = apply_filter_options(b)
            b = add_filter_ui(b)
            if "id='search_form'" not in b and "filter-count" in b and FILTER_JS not in b:
                b = b.replace("</body>", FILTER_JS + "\n</body>", 1)
            write_html(full, b)

    rebuild_arabic()


def rebuild_arabic():
    """Regenerate the Arabic pages from the English ones.

    The -ar.html pages are generated copies, so any rebuild above leaves them
    stale until this runs -- a photo swap or a text edit would show in English
    and not in Arabic. Failures are reported but never raised: a problem
    generating the translation must not undo an edit the user just made.
    """
    try:
        import build_arabic
        importlib.reload(build_arabic)
        missing = set()
        for page in build_arabic.ALL_PAGES:
            if os.path.exists(os.path.join(SITE, page)):
                build_arabic.build_page(page, missing)
                build_arabic.patch_english(page)
        if missing:
            print("  [arabic] %d string(s) still need a translation" % len(missing))
    except Exception as exc:
        print("  [arabic] could not rebuild: %s" % exc)


def remove_from_pages(slot):
    if slot not in SLOTS:
        raise ValueError("Unknown photo: %s" % slot)
    rel = SLOTS[slot]

    manifest = read_manifest()
    if slot in manifest:
        raise ValueError("Already removed from the page.")

    affected = pages_using(rel)
    if not affected:
        raise ValueError("This photo isn't used on any page.")

    # keep a pristine copy of every page before the first edit
    for page in affected:
        backup_page(page)

    manifest[slot] = {"pages": affected}
    write_manifest(manifest)
    rebuild_pages(affected)

    return "Removed from %d page%s. Refresh the site to see it." % (
        len(affected), "" if len(affected) == 1 else "s")


def restore_photo(slot):
    """Undo everything done to this photo: the file itself and any page removal."""
    if slot not in SLOTS:
        raise ValueError("Unknown photo: %s" % slot)
    rel = SLOTS[slot]
    done = []

    manifest = read_manifest()
    if slot in manifest:
        pages = manifest[slot].get("pages") or PAGES
        del manifest[slot]
        write_manifest(manifest)
        rebuild_pages(pages)
        done.append("put back on the page")

    saved = os.path.join(BACKUPS, rel)
    if os.path.exists(saved):
        shutil.copy2(saved, os.path.join(SITE, rel))
        done.append("original photo restored")

    # this slot is no longer showing its proposed photo
    applied = read_applied()
    if slot in applied:
        applied.discard(slot)
        write_applied(applied)

    if not done:
        raise ValueError("This one hasn't been changed yet.")
    return " and ".join(done).capitalize()


# ---------------------------------------------------------------- text edits

# Same curated page list as the photo tool — not all 46 files (many are
# search-result / language snapshots), just the real pages worth editing.
TEXT_PAGES = [
    ("index.html", "Home Page"),
    ("about-us.html", "About Us"),
    ("listings.html", "Our Products"),
    ("our-brands/flavora-cafe.html", "Our Brand — Flavora"),
    ("our-team.html", "Our Team"),
    ("blogs.html", "Blog & Events"),
    ("careers.html", "Vacancies"),
    ("contact-us.html", "Contact Us"),
]

# The home page exists three times on disk (index.html + two language-switcher
# snapshots). Editing "Home Page" in the UI should keep all three in step,
# the same way photo edits already do.
HOME_MIRRORS = ["language-switcher?lang_code=ar.html", "language-switcher?lang_code=en.html"]


def text_nodes(page):
    """(node list, was this read from the live file or does it not exist)"""
    path = os.path.join(SITE, page)
    if not os.path.exists(path):
        return [], False
    return te.scan(te.read(path)), True


def original_text_nodes(page):
    """Node list from the pristine copy, or the live one if nothing's changed yet."""
    path = pristine_path(page)
    if not os.path.exists(path):
        return []
    return te.scan(te.read(path))


def mirror_text_change(old_value, new_value):
    """Apply the same content change to the other two home-page copies, but
    only when it's unambiguous — exactly one node currently holds old_value.

    Returns {mirror_page: seq} for the ones actually changed, so the caller
    can record them and they survive a later rebuild.
    """
    changed = {}
    for mirror in HOME_MIRRORS:
        path = os.path.join(SITE, mirror)
        if not os.path.exists(path):
            continue
        nodes = te.scan(te.read(path))
        matches = [n for n in nodes if n.text == old_value]
        if len(matches) != 1:
            continue
        backup_page(mirror)
        te.apply_edit(path, matches[0].seq, new_value)
        changed[mirror] = matches[0].seq
    return changed


def apply_text_edit(page, seq, new_text):
    valid_pages = {p for p, _ in TEXT_PAGES}
    if page not in valid_pages:
        raise ValueError("Unknown page: %s" % page)
    path = os.path.join(SITE, page)
    if not os.path.exists(path):
        raise ValueError("Page not found: %s" % page)

    backup_page(page)
    try:
        old_text = te.apply_edit(path, seq, new_text)
    except ValueError as e:
        raise ValueError(str(e))

    # Remember it, so a later photo Remove/Undo (which rebuilds the page from
    # the pristine copy) replays this edit instead of throwing it away.
    edits = read_text_edits()
    edits.setdefault(page, {})[str(seq)] = new_text

    msg = "Saved."
    if page == "index.html" and old_text != new_text:
        mirrored = mirror_text_change(old_text, new_text)
        for mirror, mseq in mirrored.items():
            edits.setdefault(mirror, {})[str(mseq)] = new_text
        if mirrored:
            msg = "Saved and matched on %d other cop%s of the home page." % (
                len(mirrored), "y" if len(mirrored) == 1 else "ies")

    write_text_edits(edits)
    return msg


# ------------------------------------------------------------- Arabic text --
# The Arabic pages are generated, so they cannot be edited the way the English
# ones are: build_arabic.py rewrites every -ar.html from its English original,
# and an edit saved into one would last until the next build. The Arabic that
# lasts lives in the translation table, so the text index edits that instead
# and then regenerates the pages.
#
# Edits go to translations_ar_overrides.json rather than into the hand-written
# table, which keeps the authored translations intact and reversible.

def _overrides_path():
    import translations_ar
    return translations_ar.OVERRIDES_PATH


def read_overrides():
    try:
        with open(_overrides_path(), encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}


def write_overrides(data):
    path = _overrides_path()
    if data:
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")
    elif os.path.exists(path):
        os.remove(path)          # no overrides left: no file, nothing to explain


def reload_translations():
    """Recompute the table, then rebuild every Arabic page from it.

    translations_ar has to be reloaded rather than poked: an override replaces
    a value in AR, so the authored original is only recoverable by re-reading
    the module. rebuild_arabic() reloads build_arabic afterwards, which rebinds
    it to the fresh table.
    """
    import translations_ar
    importlib.reload(translations_ar)
    rebuild_arabic()
    try:
        # the generator's filename is hyphenated, so it cannot be imported by
        # name; load it from its path instead of shelling out to a subprocess
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "rebuild-text-index.py")
        spec = importlib.util.spec_from_file_location("rebuild_text_index", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.main()
    except Exception as e:
        print("  !! text index not regenerated: %s" % e)


def set_translation(english, arabic):
    english = (english or "").strip()
    arabic = (arabic or "").strip()
    if not english:
        raise ValueError("No English string given.")

    import translations_ar
    overrides = read_overrides()

    # saving the authored text back is a revert, not an override -- otherwise
    # the overrides file fills up with entries that change nothing
    authored = translations_ar.load_authored().get(english)
    if arabic and arabic == authored:
        overrides.pop(english, None)
    elif not arabic:
        overrides.pop(english, None)
    else:
        overrides[english] = arabic

    write_overrides(overrides)
    reload_translations()
    if not arabic:
        return "Cleared."
    return "Saved and rebuilt the Arabic pages."


def clear_translation(english):
    english = (english or "").strip()
    overrides = read_overrides()
    if english not in overrides:
        import translations_ar
        return "Nothing to revert.", translations_ar.AR.get(english, "")
    overrides.pop(english)
    write_overrides(overrides)
    reload_translations()
    import translations_ar
    return "Reverted to the original translation.", translations_ar.AR.get(english, "")


def restore_text(page, seq):
    valid_pages = {p for p, _ in TEXT_PAGES}
    if page not in valid_pages:
        raise ValueError("Unknown page: %s" % page)

    originals = original_text_nodes(page)
    original = next((n for n in originals if n.seq == seq), None)
    if original is None:
        raise ValueError("This one hasn't been changed yet.")

    live, exists = text_nodes(page)
    current = next((n for n in live if n.seq == seq), None)
    if current is None or current.text == original.text:
        raise ValueError("This one hasn't been changed yet.")

    before_value = current.text
    te.apply_edit(os.path.join(SITE, page), seq, original.text)

    mirrored = {}
    if page == "index.html":
        mirrored = mirror_text_change(before_value, original.text)

    # drop it from the saved edits so a rebuild doesn't reinstate it
    edits = read_text_edits()
    for pg in [page] + list(mirrored.keys()):
        if pg in edits:
            edits[pg].pop(str(mirrored.get(pg, seq) if pg != page else seq), None)
            if not edits[pg]:
                del edits[pg]
    write_text_edits(edits)

    return "Restored.", original.text


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ------------------------------------------------------------- products

PRODUCTS_JSON = os.path.join(BACKUPS, "_products.json")
# The demo product this used to clone was deleted from the site. A copy is
# kept as listing/_product-template.html: the underscore keeps it out of
# all_pages, the sitemap and the deploy glob, and .htaccess denies it, so it
# is a template and not a page.
PRODUCT_TEMPLATE = os.path.join("listing", "_product-template.html")


def read_products():
    if os.path.exists(PRODUCTS_JSON):
        try:
            with open(PRODUCTS_JSON, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            pass
    return []


def write_products(items):
    os.makedirs(BACKUPS, exist_ok=True)
    with open(PRODUCTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(items, fh, indent=2, ensure_ascii=False)


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "product"


def product_cards(p):
    """The two card layouts listings.html uses — grid tab and list tab.

    Each card carries its brand, category and searchable text as data
    attributes so the filters can work in the browser. The site is static,
    so there is no server to post a search to.
    """
    img, slug = _esc(p["image"]), _esc(p["slug"])
    name, short = _esc(p["name"]), _esc(p["short"])
    brand, cat = _esc(p.get("brand", "")), _esc(p.get("category", ""))
    hay = _esc(" ".join([p["name"], p.get("brand", ""), p.get("category", ""),
                         p.get("short", "")]).lower())
    data = 'data-brand="%s" data-category="%s" data-search="%s"' % (brand, cat, hay)

    grid = (
        '\n                                     <div class="col-lg-4 col-sm-6 product-cell" %s>\n'
        '                        <div class="product-container">\n'
        '                            <img src="%s">\n'
        '                            <h5 class="Prodctname">%s</h5>\n'
        '                            <p class="short-desc" style="color:#696969">%s</p>\n'
        '                            <a href="listing/%s.html" class="btn-default">More Info</a>\n'
        '                        </div>\n'
        '                    </div>\n' % (data, img, name, short, slug))
    lst = (
        '\n                                    <div class=" col-xxl-6  col-xl-12  col-lg-12  col-sm-12 product-cell" %s>\n'
        '                                        <div class="brand-car-item">\n'
        '                                            <div class="brand-car-item-img">\n'
        '                                                <img src="%s" alt="thumb">\n'
        '                                            </div>\n'
        '                                            <div class="brand-car-inner">\n'
        '                                                <a href="listing/%s.html">\n'
        '                                                    <h3>%s</h3>\n'
        '                                                </a>\n'
        '                                                <p class="short-desc" style="color:#696969">%s</p>\n'
        '                                            </div>\n'
        '                                        </div>\n'
        '                                    </div>\n' % (data, img, slug, name, short))
    return grid, lst


def build_filter_options(items):
    """Regenerate the brand and category checkboxes from the products that
    actually exist, instead of the demo list the theme shipped with."""
    def boxes(field, values):
        out = []
        for i, v in enumerate(sorted(values)):
            vid = "%s-%d" % (field, i)
            out.append(
                '\n                                                        <span class="form-check">\n'
                '                                                            <input name="%s[]" class="form-check-input" '
                'type="checkbox" id="%s" value="%s">\n'
                '                                                            <label class="form-check-label" for="%s">\n'
                '                                                                %s\n'
                '                                                            </label>\n'
                '                                                        </span>\n'
                % (field, vid, _esc(v), vid, _esc(v)))
        return "".join(out)

    brands = {p.get("brand", "").strip() for p in items if p.get("brand", "").strip()}
    cats = {p.get("category", "").strip() for p in items if p.get("category", "").strip()}
    return boxes("brands", brands), boxes("categories", cats)


def apply_filter_options(body):
    """Swap the theme's hard-coded filter lists for the real ones."""
    items = read_products()
    if not items:
        return body
    brand_html, cat_html = build_filter_options(items)
    # each list lives in its own <span class="select-Brand-box">
    parts = body.split('<span class="select-Brand-box">')
    if len(parts) < 3:
        return body
    for idx, new_inner in ((1, brand_html), (2, cat_html)):
        close = parts[idx].find("</span>\n")
        # find the matching close of the select-Brand-box wrapper
        depth, i, end = 1, 0, None
        for m in re.finditer(r"<span\b|</span>", parts[idx]):
            depth += 1 if m.group().startswith("<span") else -1
            if depth == 0:
                end = m.start()
                break
        if end is not None:
            parts[idx] = new_inner + "                                            " + parts[idx][end:]
    return '<span class="select-Brand-box">'.join(parts)


FILTER_JS = """
<script>
/* Filtering runs in the browser: the site is static files, so the original
   form (which posted to a Laravel backend that no longer exists) could never
   have worked. Ticking a box now filters instantly, with no page reload. */
(function () {
  var form = document.getElementById('search_form');
  if (!form) return;
  var cells = [].slice.call(document.querySelectorAll('.product-cell'));
  if (!cells.length) return;

  /* Two search boxes are on the page: the one in the sidebar and the wide
     one above the grid, which the template shipped wired to the dead
     backend. Both drive the same filter and mirror each other, so it
     does not matter which one a visitor types into. */
  var searches = [].slice.call(document.querySelectorAll(
        '#product-search, #outside_form_search'));
  var search = searches[0];
  var active = null;
  var countEl = document.getElementById('filter-count');

  function checked(name) {
    return [].slice.call(form.querySelectorAll('input[name="' + name + '[]"]:checked'))
             .map(function (i) { return i.value; });
  }

  function apply() {
    var brands = checked('brands');
    var cats = checked('categories');
    /* Read from whichever box was last used, not the first non-empty one:
       once the two are mirrored they both hold text, so picking the first
       meant the sidebar always won and later typing was ignored. */
    var src = active || searches[0];
    var q = (src && src.value || '').trim().toLowerCase();
    searches.forEach(function (i) { if (i !== src) { i.value = src ? src.value : ''; } });
    var shown = 0;

    cells.forEach(function (c) {
      var b = c.getAttribute('data-brand') || '';
      var k = c.getAttribute('data-category') || '';
      var hay = c.getAttribute('data-search') || '';
      var ok = (!brands.length || brands.indexOf(b) !== -1) &&
               (!cats.length   || cats.indexOf(k) !== -1) &&
               (!q             || hay.indexOf(q) !== -1);
      c.style.display = ok ? '' : 'none';
      if (ok) shown++;
    });

    // each product appears once per tab, so halve it for the human count
    var real = Math.round(shown / 2) || shown;
    if (countEl) {
      countEl.textContent = real === cells.length / 2
        ? 'Showing all ' + real + ' products'
        : 'Showing ' + real + ' of ' + Math.round(cells.length / 2) + ' products';
    }
    var empty = document.getElementById('filter-empty');
    if (empty) empty.style.display = shown ? 'none' : 'block';
  }

  form.addEventListener('change', apply);
  form.addEventListener('submit', function (e) { e.preventDefault(); apply(); });
  searches.forEach(function (i) {
    i.addEventListener('input', function () { active = i; apply(); });
  });
  var go = document.getElementById('outside_form_btn');
  if (go) go.addEventListener('click', function (e) {
    e.preventDefault();
    active = document.getElementById('outside_form_search');
    apply();
  });

  var reset = document.getElementById('filter-reset');
  if (reset) reset.addEventListener('click', function (e) {
    e.preventDefault();
    form.reset();
    active = null;
    searches.forEach(function (i) { i.value = ''; });
    apply();
  });

  apply();
})();
</script>
"""


def add_filter_ui(body):
    """Give the sidebar a working search box, a result count and a reset."""
    # a real search field in place of the hidden one the old backend used
    body = body.replace(
        '<input type="hidden" value="" name="search" id="inside_form_search">',
        '<div class="filter-search">\n'
        '                                <input type="text" id="product-search" class="form-control" '
        'placeholder="Search products...">\n'
        '                            </div>', 1)

    # the wide search box still advertised the template's car listings
    body = body.replace('placeholder="Search Car"', 'placeholder="Search products"')

    # the submit button becomes a reset — filtering is already instant
    body = body.replace(
        '<button type="submit" class="thm-btn-two">Search Here</button>',
        '<button type="button" id="filter-reset" class="thm-btn-two">Clear filters</button>', 1)

    # a count above the grid, and a message when nothing matches
    marker = '<div class="tab-content" id="pills-tabContent">'
    if marker in body and 'id="filter-count"' not in body:
        body = body.replace(
            marker,
            '<p id="filter-count" class="filter-count"></p>\n'
            '                        <p id="filter-empty" class="filter-empty" style="display:none">'
            'No products match these filters.</p>\n                        ' + marker, 1)
    return body


def insert_product_cards(body):
    """Add every saved product into both tabs of the listings page."""
    items = read_products()
    if not items:
        return body
    grid_html = "".join(product_cards(p)[0] for p in items)
    list_html = "".join(product_cards(p)[1] for p in items)

    def after(anchor, addition, text):
        i = text.find(anchor)
        if i == -1:
            return text
        j = text.find(">", i)
        return text if j == -1 else text[:j + 1] + addition + text[j + 1:]

    body = after('<div class="row g-5">', grid_html, body)
    body = after('<div class="row g-5 brand-car-two">', list_html, body)
    return body


def replace_div_contents(text, opening, new_inner):
    """Swap what's inside a <div>, matching its real closing tag.

    A non-greedy regex stops at the *first* </div>, which for a container
    holding several child divs leaves the extras orphaned and unbalances the
    page. This counts nesting instead, so the same number of tags always
    comes back out.
    """
    start = text.find(opening)
    if start == -1:
        return text
    i = start + len(opening)
    depth = 1
    for m in re.finditer(r"<div\b|</div>", text[i:]):
        depth += 1 if m.group().startswith("<div") else -1
        if depth == 0:
            close_at = i + m.start()
            return text[:start + len(opening)] + new_inner + text[close_at:]
    return text


def build_product_page(p):
    """Create the product's own page from the existing one as a template."""
    tpl_path = os.path.join(SITE, PRODUCT_TEMPLATE)
    body = read_html(tpl_path)

    body = re.sub(r"<title>.*?</title>", "<title>%s || Takwa</title>" % _esc(p["name"]),
                  body, count=1, flags=re.S)
    body = re.sub(r'(<h1 class="prductfullname">).*?(</h1>)',
                  lambda m: m.group(1) + _esc(p["name"]) + m.group(2), body, count=1, flags=re.S)
    body = re.sub(r'(<span class="pcategory">Category: <span>).*?(</span>)',
                  lambda m: m.group(1) + _esc(p["category"]) + m.group(2), body, count=1, flags=re.S)
    body = re.sub(r'(<p class="pdesc">).*?(</p>\s*<hr)',
                  lambda m: m.group(1) + " <p>" + _esc(p["full"]) + "</p> " + m.group(2),
                  body, count=1, flags=re.S)
    body = re.sub(r'(<div class="Main-pimage">\s*<img src=")[^"]*(")',
                  lambda m: m.group(1) + "../" + _esc(p["image"]) + m.group(2),
                  body, count=1, flags=re.S)

    sizes = "".join('\n                                       <div class="size">%s</div>' % _esc(s)
                    for s in p.get("sizes", []))
    body = replace_div_contents(body, '<div class="size-container">',
                                sizes + "\n                                ")
    # no flavour variants on a newly added product
    body = replace_div_contents(body, '<div class="flavor-container">', "")

    out = os.path.join(SITE, "listing", p["slug"] + ".html")
    write_html(out, body)
    return out


def add_product(data):
    name = (data.get("name") or "").strip()
    if not name:
        raise ValueError("The product needs a name.")
    short = (data.get("short") or "").strip()
    full = (data.get("full") or "").strip() or short
    category = (data.get("category") or "").strip() or "Uncategorised"
    sizes = [s.strip() for s in (data.get("sizes") or "").split(",") if s.strip()]

    items = read_products()
    slug = slugify(name)
    if any(p["slug"] == slug for p in items) or \
       os.path.exists(os.path.join(SITE, "listing", slug + ".html")):
        raise ValueError("A product with that name already exists.")

    img_data = data.get("image") or ""
    if not img_data.startswith("data:image"):
        raise ValueError("Please choose a product photo.")
    import base64
    header, b64 = img_data.split(",", 1)
    raw = base64.b64decode(b64)
    try:
        src = Image.open(io.BytesIO(raw))
        src.load()
    except Exception:
        raise ValueError("That photo couldn't be read. Try a JPG or PNG.")

    rel = "uploads/products/%s.webp" % slug
    os.makedirs(os.path.join(SITE, "uploads", "products"), exist_ok=True)
    cover(flatten(src), 555, 586).save(os.path.join(SITE, rel), quality=88, method=6)

    p = {"slug": slug, "name": name, "short": short, "full": full,
         "category": category, "sizes": sizes, "image": rel}
    items.append(p)
    write_products(items)

    build_product_page(p)
    backup_page("listings.html")
    rebuild_pages(["listings.html"])
    return "Added “%s”." % name


def delete_product(slug):
    items = read_products()
    keep = [p for p in items if p["slug"] != slug]
    if len(keep) == len(items):
        raise ValueError("No such product.")
    gone = next(p for p in items if p["slug"] == slug)
    write_products(keep)

    # the -ar twin too: it is generated, so nothing else will ever clean it up,
    # and an orphan Arabic page outlives the product it describes
    for path in (os.path.join(SITE, "listing", slug + ".html"),
                 os.path.join(SITE, "listing", slug + "-ar.html"),
                 os.path.join(SITE, gone.get("image", ""))):
        if path and os.path.exists(path) and os.path.isfile(path):
            os.remove(path)
    rebuild_pages(["listings.html"])
    return "Removed “%s”." % gone["name"]


# ----------------------------------------------------------------- news

NEWS_JSON = os.path.join(BACKUPS, "_news.json")
# Cloned from introducing-enna-soups.html, with one fix: the original's <h1>
# reads "Blog Details" and demotes the real headline to a <span> inside it,
# which the audit flagged. The template carries the headline alone, so articles
# added from here do not inherit the bug. The underscore keeps the file out of
# all_pages, the sitemap and the deploy glob, and .htaccess denies it.
NEWS_TEMPLATE = os.path.join("blog", "_news-template.html")


def read_news():
    if os.path.exists(NEWS_JSON):
        try:
            with open(NEWS_JSON, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            pass
    return []


def write_news(items):
    os.makedirs(BACKUPS, exist_ok=True)
    with open(NEWS_JSON, "w", encoding="utf-8") as fh:
        json.dump(items, fh, indent=2, ensure_ascii=False)


def news_card(n):
    """One card for the Blog & Events listing, matching the four hand-built
    ones already on the page."""
    slug, title = _esc(n["slug"]), _esc(n["title"])
    return (
        '\n                <div class="col-lg-6 col-md-6">\n'
        '                    <div class="post-item wow fadeInUp">\n'
        '                        <div class="post-item-content">\n'
        '                            <span class="blog-category">%s</span>\n'
        '                            <h2><a href="blog/%s.html">%s</a></h2>\n'
        '                            <p>%s</p>\n'
        '                            <div class="align-items-center"> <a href="blog/%s.html" class="aa" >'
        '<span class="bloglink">Read more</span><i class="fa-solid fa-chevron-right bb"></i></a></div>\n'
        '                        </div>\n'
        '                        <div class="post-featured-image">\n'
        '                            <figure>\n'
        '                                <a href="blog/%s.html" class="image-anime" data-cursor-text="View">\n'
        '                                    <img src="%s" alt="%s">\n'
        '                                </a>\n'
        '                            </figure>\n'
        '                       </div>\n'
        '                    </div>\n'
        '                </div>\n'
        % (_esc(n.get("date", "")), slug, title, _esc(n["summary"]),
           slug, slug, _esc(n["image"]), title))


def insert_news_cards(body):
    """Add every saved news item to the Blog & Events listing.

    They go in at the top of the row rather than the bottom, so the newest
    thing is the first thing read. The four original articles keep their
    order below.
    """
    items = read_news()
    if not items:
        return body
    cards = "".join(news_card(n) for n in reversed(items))
    anchor = '<div class="row alignbaseline">'
    i = body.find(anchor)
    if i == -1:
        return body
    return body[:i + len(anchor)] + cards + body[i + len(anchor):]


def build_news_page(n):
    """Create the article's own page from the template."""
    body = read_html(os.path.join(SITE, NEWS_TEMPLATE))
    title, img = _esc(n["title"]), _esc(n["image"])

    body = re.sub(r"<title>.*?</title>",
                  "<title>%s | Takwa Foods</title>" % title, body, count=1, flags=re.S)
    body = re.sub(r'(<h1 class="wow fadeInUp">).*?(</h1>)',
                  lambda m: m.group(1) + title + m.group(2), body, count=1, flags=re.S)

    # the hero, above the article body
    body = re.sub(r'(<div class="post-image">\s*<figure[^>]*>\s*<img src=")[^"]*(" alt=")[^"]*(")',
                  lambda m: m.group(1) + "../" + img + m.group(2) + title + m.group(3),
                  body, count=1, flags=re.S)

    paragraphs = "\n".join(
        "<p>%s</p>" % _esc(line.strip())
        for line in (n.get("body") or "").splitlines() if line.strip())
    body = replace_div_contents(body, '<div class="post-entry">',
                                " " + paragraphs + "\n ")

    # the share links carry the old article's slug and headline in their URLs
    body = re.sub(r'(https://takwafoods\.com/blog/)[a-z0-9\-]+', r'\g<1>' + n["slug"], body)
    for key in ("&t=", "&title=", "&text="):
        body = re.sub(re.escape(key) + r'[^"]*', key + title, body)

    out = os.path.join(SITE, "blog", n["slug"] + ".html")
    write_html(out, body)
    return out


def add_news(data):
    title = (data.get("title") or "").strip()
    if not title:
        raise ValueError("The news item needs a headline.")
    summary = (data.get("summary") or "").strip()
    if not summary:
        raise ValueError("Write a short summary — it is what shows on the listing.")
    text = (data.get("body") or "").strip() or summary
    date = (data.get("date") or "").strip()

    items = read_news()
    slug = slugify(title)
    if any(n["slug"] == slug for n in items) or \
       os.path.exists(os.path.join(SITE, "blog", slug + ".html")):
        raise ValueError("A news item with that headline already exists.")

    img_data = data.get("image") or ""
    if not img_data.startswith("data:image"):
        raise ValueError("Please choose a photo.")
    import base64
    header, b64 = img_data.split(",", 1)
    try:
        src = Image.open(io.BytesIO(base64.b64decode(b64)))
        src.load()
    except Exception:
        raise ValueError("That photo couldn't be read. Try a JPG or PNG.")

    rel = "uploads/blog/%s.webp" % slug
    os.makedirs(os.path.join(SITE, "uploads", "blog"), exist_ok=True)
    # 1026x618 matches the width/height the article template already declares
    cover(flatten(src), 1026, 618).save(os.path.join(SITE, rel), quality=88, method=6)

    n = {"slug": slug, "title": title, "summary": summary,
         "body": text, "date": date, "image": rel}
    items.append(n)
    write_news(items)

    build_news_page(n)
    backup_page("blogs.html")
    rebuild_pages(["blogs.html"])
    return "Published “%s”." % title


def delete_news(slug):
    items = read_news()
    keep = [n for n in items if n["slug"] != slug]
    if len(keep) == len(items):
        raise ValueError("No such news item.")
    gone = next(n for n in items if n["slug"] == slug)
    write_news(keep)

    # the -ar twin too: it is generated, so nothing else will ever clean it up,
    # and an orphan Arabic article outlives the news it reported
    for path in (os.path.join(SITE, "blog", slug + ".html"),
                 os.path.join(SITE, "blog", slug + "-ar.html"),
                 os.path.join(SITE, gone.get("image", ""))):
        if path and os.path.exists(path) and os.path.isfile(path):
            os.remove(path)
    rebuild_pages(["blogs.html"])
    return "Removed “%s”." % gone["title"]


# ------------------------------------------------------- photo proposals

PROPOSAL_JSON = os.path.join(ROOT, "photo-proposal.json")


def load_proposal():
    if not os.path.exists(PROPOSAL_JSON):
        return {}
    try:
        with open(PROPOSAL_JSON, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


APPLIED_JSON = os.path.join(BACKUPS, "_proposal_applied.json")


def read_applied():
    if os.path.exists(APPLIED_JSON):
        try:
            with open(APPLIED_JSON, encoding="utf-8") as fh:
                return set(json.load(fh))
        except Exception:
            pass
    return set()


def write_applied(names):
    os.makedirs(BACKUPS, exist_ok=True)
    with open(APPLIED_JSON, "w", encoding="utf-8") as fh:
        json.dump(sorted(names), fh, indent=2)


def apply_proposal(slot):
    """Put the proposed photo into a slot, reusing the normal upload path so
    the original is backed up and Undo keeps working."""
    proposal = load_proposal()
    if slot not in proposal:
        raise ValueError("No proposal for: %s" % slot)
    src = proposal[slot]["source"]
    if not os.path.exists(src):
        raise ValueError("Proposed photo is missing from disk: %s" % os.path.basename(src))
    with open(src, "rb") as fh:
        data = fh.read()
    msg = apply_photo(slot, data)
    applied = read_applied()
    applied.add(slot)
    write_applied(applied)
    return msg


def proposal_state():
    """Which proposed photos are currently applied.

    Tracked explicitly rather than inferred from "a backup exists", because a
    backup only means the slot was changed at some point — possibly by an
    unrelated edit — not that this proposal is what's live.
    """
    applied = read_applied()
    return {slot: (slot in applied) for slot in load_proposal()}


def render_proposal_index():
    proposal = load_proposal()
    applied = proposal_state()

    # group the cards under the page each photo belongs to
    order, grouped = [], {}
    for slot, info in proposal.items():
        page = info.get("page", "Other")
        if page not in grouped:
            grouped[page] = []
            order.append(page)
        grouped[page].append((slot, info))

    sections = []
    for page in order:
        cards = []
        for slot, info in grouped[page]:
            cards.append(_proposal_card(slot, info, applied.get(slot, False)))
        sections.append('<h2 class="pgroup">%s</h2><div class="pgrid">%s</div>'
                        % (_esc(page), "".join(cards)))
    return _proposal_shell("".join(sections))


def _proposal_card(slot, info, is_applied):
        rel = SLOTS.get(slot, "")
        return (
            '<div class="pcard" data-slot="%s">'
            '  <div class="phead"><code class="pslot">%s</code>'
            '    <span class="pbadge %s">%s</span></div>'
            '  <div class="ppair">'
            '    <figure><img src="/_proposal_img?slot=%s&which=current"><figcaption>on the site now</figcaption></figure>'
            '    <figure><img src="/_proposal_img?slot=%s&which=proposed"><figcaption class="new">proposed</figcaption></figure>'
            '  </div>'
            '  <p class="preason">%s</p>'
            '  <p class="psrc">from: %s</p>'
            '  <div class="pactions">'
            '    <button class="papply"%s>Use this photo</button>'
            '    <button class="pundo"%s>Put the old one back</button>'
            '  </div>'
            '  <p class="pstatus"></p>'
            '</div>' % (
                _esc(slot), _esc(slot),
                "on" if is_applied else "",
                "applied" if is_applied else "not applied",
                urllib.parse.quote(slot), urllib.parse.quote(slot),
                _esc(info.get("reason", "")), _esc(info.get("name", "")),
                " disabled" if is_applied else "",
                "" if is_applied else " disabled",
            ))


def _proposal_shell(body_html):
    doc = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Takwa — Photo Proposal</title>
<style>
 *{box-sizing:border-box}
 body{margin:0;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
      color:#1e1e1e;background:#fafaf8}
 header{background:#4c9932;color:#fff;padding:26px 32px}
 header h1{margin:0 0 6px;font-size:24px}
 header p{margin:0;opacity:.93;font-size:14px}
 .note{margin:22px 32px;padding:16px 20px;background:#fff;border:1px solid #e2e2dc;
       border-radius:10px;font-size:14px}
 .bulk{margin:0 32px 20px;display:flex;gap:10px;flex-wrap:wrap}
 .bulk button{border:1px solid #cfcfc7;background:#fff;border-radius:7px;padding:9px 16px;
              font-size:13px;font-weight:600;cursor:pointer}
 .bulk .all{background:#4c9932;color:#fff;border-color:#4c9932}
 .bulk button:hover{filter:brightness(.95)}
 .pgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(430px,1fr));gap:20px;
        margin:0 32px 40px}
 .pgroup{margin:28px 32px 14px;font-size:19px;border-bottom:2px solid #4c9932;
         padding-bottom:7px}
 .pcard{background:#fff;border:1px solid #e2e2dc;border-radius:10px;padding:14px 16px;
        display:flex;flex-direction:column}
 .phead{display:flex;align-items:center;gap:9px;margin-bottom:10px}
 .pslot{background:#eef2ea;color:#4c6b3c;padding:3px 8px;border-radius:4px;font-size:12px;font-weight:700}
 .pbadge{font-size:11px;color:#999;text-transform:uppercase;letter-spacing:.05em}
 .pbadge.on{color:#2f6b1e;font-weight:700}
 .ppair{display:grid;grid-template-columns:1fr 1fr;gap:10px}
 figure{margin:0}
 figure img{width:100%;height:180px;object-fit:cover;border-radius:7px;background:#f0f0ea;display:block}
 figcaption{font-size:11px;color:#888;margin-top:5px;text-align:center;
            text-transform:uppercase;letter-spacing:.06em}
 figcaption.new{color:#2f6b1e;font-weight:700}
 .preason{font-size:13.5px;color:#444;margin:12px 0 5px}
 .psrc{font-size:11.5px;color:#999;margin:0 0 10px}
 .pactions{margin-top:auto;display:flex;gap:8px;flex-wrap:wrap}
 .papply{background:#4c9932;color:#fff;border:none;border-radius:6px;padding:7px 14px;
         font-size:12.5px;font-weight:600;cursor:pointer}
 .papply:hover:not(:disabled){background:#3d7a28}
 .pundo{border:1px solid #cfcfc7;background:#fff;border-radius:6px;padding:7px 12px;
        font-size:12.5px;cursor:pointer;color:#666}
 .pundo:hover:not(:disabled){background:#f2f2ec}
 button:disabled{opacity:.4;cursor:default}
 .pstatus{margin:8px 0 0;font-size:11.5px;min-height:1px}
 .pstatus.ok{color:#2f6b1e}.pstatus.err{color:#b3261e}.pstatus.busy{color:#777}
 .pcard.flash{outline:2px solid #4c9932;outline-offset:-2px}
</style></head><body>
<header>
  <h1>Home Page — Photo Proposal</h1>
  <p>Try any of these on the real site, and put the old one back whenever you like.</p>
</header>
<div class="note">
  <strong>Everything here is reversible.</strong> "Use this photo" swaps it in for real, so you
  can look at the actual page. "Put the old one back" restores the original exactly &mdash;
  the very first version is kept safe, so this keeps working no matter how many times you
  switch back and forth. Nothing goes live until you sync to GitHub yourself.
</div>
<div class="bulk">
  <button class="all">Use all proposed photos</button>
  <button class="none">Put every original back</button>
</div>
@@CARDS@@

<script>
function cardOf(el){return el.closest('.pcard');}
function say(card,t,k){var s=card.querySelector('.pstatus');s.textContent=t;s.className='pstatus '+(k||'');}
function setApplied(card,on){
  card.querySelector('.papply').disabled = on;
  card.querySelector('.pundo').disabled = !on;
  var b=card.querySelector('.pbadge');
  b.textContent = on ? 'applied' : 'not applied';
  b.className = 'pbadge' + (on ? ' on' : '');
  if(on){
    var img=card.querySelector('figure img');
    img.src = img.src.split('&t=')[0] + '&t=' + Date.now();
  }
}
function refreshCurrent(card){
  var img=card.querySelector('figure img');
  var base=img.getAttribute('src').split('&t=')[0];
  img.setAttribute('src', base + '&t=' + Date.now());
}
function call(card,url){
  return fetch(url,{method:'POST'})
    .then(function(r){return r.json().then(function(j){return {ok:r.ok,j:j};});})
    .then(function(res){
      if(!res.ok||!res.j.ok) throw new Error(res.j.message||'Failed');
      say(card,res.j.message,'ok');
      card.classList.add('flash');
      setTimeout(function(){card.classList.remove('flash');},1200);
      return res.j;
    })
    .catch(function(e){ say(card, e.message||'Could not reach the server.', 'err'); throw e; });
}
document.querySelectorAll('.papply').forEach(function(b){
  b.addEventListener('click',function(){
    var card=cardOf(b); say(card,'Applying...','busy');
    call(card,'/_apply_proposal?slot='+encodeURIComponent(card.dataset.slot))
      .then(function(){ setApplied(card,true); refreshCurrent(card); }).catch(function(){});
  });
});
document.querySelectorAll('.pundo').forEach(function(b){
  b.addEventListener('click',function(){
    var card=cardOf(b); say(card,'Restoring...','busy');
    call(card,'/_undo?slot='+encodeURIComponent(card.dataset.slot))
      .then(function(){ setApplied(card,false); refreshCurrent(card); }).catch(function(){});
  });
});
document.querySelector('.bulk .all').addEventListener('click',function(){
  document.querySelectorAll('.papply:not(:disabled)').forEach(function(b){b.click();});
});
document.querySelector('.bulk .none').addEventListener('click',function(){
  document.querySelectorAll('.pundo:not(:disabled)').forEach(function(b){b.click();});
});
</script>
</body></html>"""
    return doc.replace("@@CARDS@@", body_html)


def render_text_index():
    """Build the text-editing page fresh from whatever's on disk right now —
    no separate index file to go stale, unlike the photo one."""
    sections = []
    navlinks = []

    for page, label in TEXT_PAGES:
        nodes, exists = text_nodes(page)
        if not exists:
            continue
        originals = {n.seq: n.text for n in original_text_nodes(page)}

        anchor = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
        navlinks.append('<a href="#%s">%s</a>' % (anchor, _esc(label)))

        cards = []
        for n in nodes:
            edited = n.seq in originals and originals[n.seq] != n.text
            rows = 1 if len(n.text) <= 50 else (3 if len(n.text) <= 160 else 6)
            edited_badge = '<span class="edited">edited</span>' if edited else ""
            cards.append(
                '<div class="tcard" data-page="%s" data-seq="%d">'
                '<div class="tmeta"><code class="ttag">%s</code>%s</div>'
                '<textarea rows="%d">%s</textarea>'
                '<div class="tactions">'
                '<button class="tsave">Save</button>'
                '<button class="tundo"%s>Undo</button>'
                '</div>'
                '<p class="tstatus"></p>'
                '</div>' % (
                    _esc(page), n.seq, _esc(n.tag), edited_badge, rows, _esc(n.text),
                    "" if edited else " disabled"
                )
            )

        sections.append(
            '<section id="%s"><h2>%s</h2><div class="tgrid">%s</div></section>'
            % (anchor, _esc(label), "".join(cards))
        )

    doc = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Takwa — Text Index</title>
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
  .how { margin:24px 32px; padding:18px 22px; background:#fff; border:1px solid #e2e2dc; border-radius:10px; }
  .how h3 { margin:0 0 8px; font-size:15px; }
  .how p { margin:0; font-size:14px; color:#444; }
  section { margin:0 32px 44px; }
  section h2 { font-size:19px; border-bottom:2px solid #4c9932; padding-bottom:7px; margin:0 0 18px; }
  .tgrid { display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:16px; }
  .tcard { background:#fff; border:1px solid #e2e2dc; border-radius:10px; padding:12px 14px;
           display:flex; flex-direction:column; }
  .tmeta { display:flex; align-items:center; gap:8px; margin-bottom:8px; }
  .ttag { background:#eef2ea; color:#4c6b3c; padding:2px 7px; border-radius:4px; font-size:11px; font-weight:700; }
  .edited { color:#a05a00; background:#fdf3e3; padding:2px 7px; border-radius:4px; font-size:11px; font-weight:600; }
  textarea { width:100%; font:14px/1.4 inherit; border:1px solid #cfcfc7; border-radius:6px;
             padding:8px 10px; resize:vertical; }
  textarea:focus { outline:2px solid #4c9932; outline-offset:1px; }
  .tactions { margin-top:9px; display:flex; gap:7px; }
  .tsave { background:#4c9932; color:#fff; border:none; border-radius:6px; padding:6px 14px;
           font-size:12px; font-weight:600; cursor:pointer; }
  .tsave:hover { background:#3d7a28; }
  .tundo { border:1px solid #cfcfc7; background:#fff; border-radius:6px; padding:6px 12px;
           font-size:12px; cursor:pointer; color:#666; }
  .tundo:hover:not(:disabled) { background:#f2f2ec; }
  .tundo:disabled { opacity:.4; cursor:default; }
  .tstatus { margin:7px 0 0; font-size:11.5px; min-height:1px; }
  .tstatus.ok { color:#2f6b1e; }
  .tstatus.err { color:#b3261e; }
  .tstatus.busy { color:#777; }
  .tcard.flash { outline:2px solid #4c9932; outline-offset:-2px; }
</style>
</head>
<body>
<header>
  <h1>Takwa — Text Index</h1>
  <p>Every piece of text on the site, grouped by the page it appears on.</p>
</header>
<nav>@@NAV@@</nav>

<div class="how">
  <h3>How to change text</h3>
  <p>Edit the box, click <strong>Save</strong>. Undo puts the original back. The Home
  page exists three times on disk (the site has an Arabic-language copy and an
  English-language copy) &mdash; editing it here updates all three automatically,
  as long as the text matches exactly across copies.</p>
</div>

@@SECTIONS@@

<script>
function cardOf(el) { return el.closest('.tcard'); }
function say(card, text, kind) {
  var s = card.querySelector('.tstatus');
  s.textContent = text; s.className = 'tstatus ' + (kind || '');
}
function send(card, url, body) {
  return fetch(url, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) })
    .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
    .then(function (res) {
      if (!res.ok || !res.j.ok) throw new Error(res.j.message || 'Failed');
      say(card, res.j.message, 'ok');
      card.classList.add('flash');
      setTimeout(function () { card.classList.remove('flash'); }, 1200);
      return res.j;
    })
    .catch(function (e) { say(card, e.message || 'Could not reach the server.', 'err'); throw e; });
}

document.querySelectorAll('.tsave').forEach(function (b) {
  b.addEventListener('click', function () {
    var card = cardOf(b);
    var ta = card.querySelector('textarea');
    say(card, 'Saving...', 'busy');
    send(card, '/_text_edit', { page: card.dataset.page, seq: parseInt(card.dataset.seq, 10), text: ta.value })
      .then(function () { card.querySelector('.tundo').disabled = false; })
      .catch(function () {});
  });
});

document.querySelectorAll('.tundo').forEach(function (b) {
  b.addEventListener('click', function () {
    var card = cardOf(b);
    say(card, 'Restoring...', 'busy');
    send(card, '/_text_undo', { page: card.dataset.page, seq: parseInt(card.dataset.seq, 10) })
      .then(function (j) {
        if (j.original !== undefined) card.querySelector('textarea').value = j.original;
        b.disabled = true;
      })
      .catch(function () {});
  });
});
</script>
</body>
</html>"""
    # the Arabic text lives in the translation table, not in these pages, so
    # it gets its own index; link the two so neither is a dead end
    navlinks.append('<a href="/_text-index-ar.html">Arabic text &rarr;</a>')
    return doc.replace("@@NAV@@", " ".join(navlinks)).replace("@@SECTIONS@@", "".join(sections))


def render_add_product():
    items = read_products()
    rows = "".join(
        '<tr><td><img src="/%s"></td><td><strong>%s</strong><br><span>%s</span></td>'
        '<td>%s</td><td><a href="/listing/%s.html" target="_blank">view</a></td>'
        '<td><button class="del" data-slug="%s">Remove</button></td></tr>'
        % (_esc(p["image"]), _esc(p["name"]), _esc(p.get("category", "")),
           _esc(", ".join(p.get("sizes", [])) or "—"), _esc(p["slug"]), _esc(p["slug"]))
        for p in items) or '<tr><td colspan="5" class="none">No products added yet.</td></tr>'

    return """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Takwa — Add a Product</title>
<style>
 *{box-sizing:border-box}
 body{margin:0;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
      background:#fafaf8;color:#1e1e1e}
 header{background:#4c9932;color:#fff;padding:26px 32px}
 header h1{margin:0 0 6px;font-size:24px}header p{margin:0;opacity:.93;font-size:14px}
 .wrap{margin:24px 32px 60px;max-width:1100px}
 .card{background:#fff;border:1px solid #e2e2dc;border-radius:10px;padding:22px 24px;margin-bottom:26px}
 h2{font-size:18px;margin:0 0 16px;border-bottom:2px solid #4c9932;padding-bottom:7px}
 label{display:block;font-size:13px;font-weight:600;margin:14px 0 5px}
 .hint{font-weight:400;color:#888}
 input[type=text],textarea,select{width:100%;border:1px solid #cfcfc7;border-radius:6px;
      padding:9px 11px;font:14px inherit}
 textarea{resize:vertical}
 input[type=file]{margin-top:6px;font-size:13px}
 .row2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
 button{border:none;border-radius:6px;padding:10px 20px;font-size:13.5px;font-weight:600;cursor:pointer}
 .save{background:#4c9932;color:#fff;margin-top:20px}
 .save:hover{background:#3d7a28}
 .del{background:#fff;border:1px solid #e0c0bc;color:#a33b2c;padding:6px 12px;font-size:12px}
 .del:hover{background:#fdf0ee}
 table{width:100%;border-collapse:collapse;font-size:13.5px}
 td{border-top:1px solid #eee;padding:9px 8px;vertical-align:middle}
 td img{width:54px;height:54px;object-fit:cover;border-radius:6px;background:#f0f0ea;display:block}
 td span{color:#888;font-size:12px}
 .none{color:#999;text-align:center;padding:22px}
 #status{margin-top:14px;font-size:13px;min-height:1px}
 #status.ok{color:#2f6b1e}#status.err{color:#b3261e}#status.busy{color:#777}
 #preview{max-width:150px;border-radius:8px;margin-top:10px;display:none}
</style></head><body>
<header><h1>Add a Product</h1>
<p>Creates the product's own page and adds it to Our Products automatically.</p></header>
<div class="wrap">

 <div class="card">
  <h2>New product</h2>
  <div class="row2">
   <div>
    <label>Product name</label>
    <input type="text" id="name" placeholder="e.g. Chicken Stock Powder">
    <label>Category</label>
    <input type="text" id="category" placeholder="e.g. MIXED SPICES">
    <label>Sizes available <span class="hint">(comma separated)</span></label>
    <input type="text" id="sizes" placeholder="e.g. 100g, 250g, 1kg">
    <label>Product photo</label>
    <input type="file" id="image" accept="image/*">
    <img id="preview">
   </div>
   <div>
    <label>Short description <span class="hint">(shown on the product card)</span></label>
    <textarea id="short" rows="3" placeholder="One or two lines."></textarea>
    <label>Full description <span class="hint">(shown on the product's page)</span></label>
    <textarea id="full" rows="8" placeholder="The longer description."></textarea>
   </div>
  </div>
  <button class="save" id="save">Add product</button>
  <p id="status"></p>
 </div>

 <div class="card">
  <h2>Products you've added</h2>
  <table><tbody id="list">@@ROWS@@</tbody></table>
 </div>
</div>

<script>
var imgData="";
document.getElementById('image').addEventListener('change',function(e){
  var f=e.target.files[0]; if(!f) return;
  var r=new FileReader();
  r.onload=function(){ imgData=r.result;
    var p=document.getElementById('preview'); p.src=r.result; p.style.display='block'; };
  r.readAsDataURL(f);
});
function say(t,k){var s=document.getElementById('status');s.textContent=t;s.className=k||'';}
document.getElementById('save').addEventListener('click',function(){
  var body={name:document.getElementById('name').value,
            category:document.getElementById('category').value,
            sizes:document.getElementById('sizes').value,
            short:document.getElementById('short').value,
            full:document.getElementById('full').value,
            image:imgData};
  if(!body.name.trim()){say('Give the product a name first.','err');return;}
  if(!imgData){say('Choose a product photo first.','err');return;}
  say('Adding...','busy');
  fetch('/_add_product',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify(body)})
   .then(function(r){return r.json().then(function(j){return {ok:r.ok,j:j};});})
   .then(function(res){
      if(!res.ok||!res.j.ok) throw new Error(res.j.message||'Failed');
      say(res.j.message+' Reloading...','ok');
      setTimeout(function(){location.reload();},900);
   }).catch(function(e){say(e.message,'err');});
});
document.getElementById('list').addEventListener('click',function(e){
  var b=e.target.closest('.del'); if(!b) return;
  if(!confirm('Remove this product? Its page and photo will be deleted.')) return;
  fetch('/_delete_product?slug='+encodeURIComponent(b.dataset.slug),{method:'POST'})
   .then(function(r){return r.json();})
   .then(function(j){ say(j.message||'Removed','ok'); setTimeout(function(){location.reload();},700); })
   .catch(function(){ say('Could not remove it.','err'); });
});
</script>
</body></html>""".replace("@@ROWS@@", rows)


# --------------------------------------------------------------- publishing
#
# The point of this section is that editing the website should not require
# knowing what git is. The tools already write files; these functions send
# those files to GitHub, so the whole job is "edit, then press Publish".
#
# Publishing does NOT put anything on takwafoods.com. It uploads the work to
# GitHub, where George deploys it from cPanel. Saying so plainly in the UI
# matters: someone who believes Publish means "live" will press it and then
# panic about a typo that is not actually public.

FRIENDLY_NAMES = [
    ("uploads/products/", "product photo"),
    ("uploads/blog/",     "news photo"),
    ("uploads/",          "photo"),
    ("blog/",             "news article"),
    ("listing/",          "product page"),
    ("_photo-backups/",   "internal record"),
    ("frontend/",         "styling"),
]


def _git(args, timeout=90):
    """Run git in the repository and return (ok, output).

    quotepath is off so an Arabic or accented filename comes back as itself
    rather than as \\330\\247 escapes, which would be shown to the user.
    """
    try:
        r = subprocess.run(["git", "-c", "core.quotepath=false"] + args,
                           cwd=ROOT, capture_output=True, text=True,
                           timeout=timeout)
        return r.returncode == 0, (r.stdout + r.stderr).strip()
    except FileNotFoundError:
        return False, ("Git is not installed on this computer. "
                       "Install it from git-scm.com, then restart the tools.")
    except subprocess.TimeoutExpired:
        return False, "Git took too long and was stopped."


def describe_change(path):
    """Turn a file path into something a non-technical person can check.

    Matched against the path inside the website folder, not the repository
    root: every site file is prefixed "Takwafoods web/takwaweb…/", so testing
    the start of the raw path never matches anything.
    """
    inner = path.replace("\\", "/")
    marker = "takwaweb.designersidhost.com/"
    if marker in inner:
        inner = inner.split(marker, 1)[1]

    name = os.path.basename(inner)
    for ext in (".html", ".webp", ".jpg", ".jpeg", ".png", ".json", ".css", ".js"):
        if name.endswith(ext):
            name = name[: -len(ext)]
            break
    name = name.replace("-", " ").replace("_", " ").strip() or inner

    for prefix, label in FRIENDLY_NAMES:
        if inner.startswith(prefix):
            return "%s — %s" % (label, name)
    if inner.endswith(".html") or "/" not in inner and inner != path:
        return "page — %s" % name
    return path


def git_changes():
    """What is waiting to be published.

    -z gives NUL-separated records, so a filename containing a space -- and
    this repository has "Takwafoods web" in every path -- cannot be split in
    the wrong place. Each record is two status characters, a space, then the
    path, so the path always begins at index 3.
    """
    try:
        r = subprocess.run(["git", "-c", "core.quotepath=false", "status",
                            "--porcelain", "--no-renames", "-z"],
                           cwd=ROOT, capture_output=True, timeout=90)
    except FileNotFoundError:
        return {"ok": False, "files": [],
                "message": "Git is not installed on this computer. "
                           "Install it from git-scm.com, then restart the tools."}
    except subprocess.TimeoutExpired:
        return {"ok": False, "files": [], "message": "Git took too long."}

    if r.returncode != 0:
        return {"ok": False, "files": [],
                "message": (r.stderr or b"").decode("utf-8", "replace").strip()}

    files = []
    for record in r.stdout.decode("utf-8", "replace").split("\0"):
        if len(record) < 4:
            continue
        path = record[3:]
        files.append({"path": path, "what": describe_change(path)})
    return {"ok": True, "files": files}


def git_identity():
    """Who git thinks is making the changes.

    Git refuses to commit without this, and the stock error tells people to run
    two terminal commands. The whole point of the Publish button is that there
    is no terminal, so the tools ask in the browser instead.
    """
    ok_n, name = _git(["config", "user.name"])
    ok_e, email = _git(["config", "user.email"])
    name = name.strip() if ok_n else ""
    email = email.strip() if ok_e else ""
    return {"ok": True, "set": bool(name and email), "name": name, "email": email}


def set_git_identity(name, email):
    name = (name or "").strip()
    email = (email or "").strip()
    if not name:
        raise ValueError("Please give a name.")
    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("That does not look like an email address.")
    # --global, so it is set once per computer rather than once per copy of
    # the website
    for key, value in (("user.name", name), ("user.email", email)):
        ok, out = _git(["config", "--global", key, value])
        if not ok:
            raise ValueError("Could not save that.\n\n" + out)
    return "Thanks — your changes will be signed as %s." % name


def git_publish(message):
    """Commit everything and push it to GitHub."""
    changes = git_changes()
    if not changes["ok"]:
        raise ValueError(changes["message"])
    if not changes["files"]:
        raise ValueError("Nothing has changed, so there is nothing to publish.")

    message = (message or "").strip() or "Website update"

    ok, out = _git(["add", "-A"])
    if not ok:
        raise ValueError("Could not stage the changes.\n\n" + out)

    ok, out = _git(["commit", "-m", message])
    if not ok and "nothing to commit" not in out.lower():
        # the usual cause is git never being told who is making the change
        if "please tell me who you are" in out.lower() or "user.email" in out.lower():
            raise ValueError(
                "Git does not know who you are yet. Run these two lines once, "
                "in a terminal, with your own name and email:\n\n"
                '  git config --global user.name "Your Name"\n'
                '  git config --global user.email "you@example.com"')
        raise ValueError("Could not save the changes.\n\n" + out)

    # Catch up with anything published elsewhere before sending. Without this,
    # any change made on another computer since this copy was cloned makes the
    # push bounce, and the person is left with committed work they cannot send
    # and no way forward that does not involve a terminal.
    #
    # --rebase replays this work on top of the newer history rather than making
    # a merge commit; --autostash covers anything still unstaged.
    ok, out = _git(["pull", "--rebase", "--autostash"], timeout=180)
    if not ok:
        _git(["rebase", "--abort"])          # leave the copy usable
        raise ValueError(
            "Your work is saved on this computer, but it could not be combined "
            "with a change someone else made to the same thing.\n\n"
            "Nothing is lost. Send George this message and he will sort it "
            "out.\n\n" + out)

    ok, out = _git(["push"], timeout=180)
    if not ok:
        low = out.lower()
        if "authentication" in low or "could not read" in low or "403" in low:
            raise ValueError(
                "Your work is saved on this computer, but GitHub would not "
                "accept it — it did not recognise the sign-in.\n\n"
                "Sign in to GitHub once and press Publish again. Nothing has "
                "been lost.\n\n" + out)
        if "rejected" in low or "non-fast-forward" in low or "behind" in low:
            raise ValueError(
                "Someone published something in the last few seconds, so this "
                "could not be sent. Your work is saved — press Publish again "
                "in a moment.\n\n" + out)
        raise ValueError("Saved on this computer, but could not reach GitHub."
                         "\n\n" + out)

    n = len(changes["files"])
    return "Published %d change%s. Tell George so he can put it on the website." % (
        n, "" if n == 1 else "s")


# The bar is injected into every tool page rather than living on a page of its
# own, so Publish is where the work happens and cannot be forgotten.
PUBLISH_BAR = """
<style>
 #tk-pub{position:fixed;left:0;right:0;bottom:0;z-index:99999;
   background:#20301c;color:#eaf3e6;font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
   box-shadow:0 -2px 14px rgba(0,0,0,.22);padding:11px 18px;
   display:flex;align-items:center;gap:14px;flex-wrap:wrap}
 #tk-pub b{font-weight:600}
 #tk-pub .grow{flex:1 1 auto;min-width:120px}
 #tk-pub button{border:none;border-radius:6px;padding:9px 18px;font:600 13.5px inherit;cursor:pointer}
 #tk-pub .go{background:#73ED7C;color:#12300f}
 #tk-pub .go:disabled{background:#5b6b57;color:#b9c7b5;cursor:default}
 #tk-pub .ghost{background:transparent;color:#cfe3ca;border:1px solid #4a6144}
 #tk-pub .msg{font-size:13px;opacity:.95}
 #tk-pub .msg.err{color:#ffb4a8}#tk-pub .msg.ok{color:#a8f0a4}
 #tk-list{position:fixed;left:0;right:0;bottom:52px;z-index:99998;max-height:44vh;overflow:auto;
   background:#16210f;color:#dce9d7;padding:14px 18px;display:none;
   font:13px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
   border-top:1px solid #33482c}
 #tk-list ul{margin:6px 0 0;padding-left:18px}
 body{padding-bottom:64px}
</style>
<div id="tk-list"></div>
<div id="tk-pub">
  <span class="grow"><b id="tk-count">Checking…</b>
    <span class="msg" id="tk-msg"></span></span>
  <button class="ghost" id="tk-see">See what changed</button>
  <button class="go" id="tk-go" disabled>Publish</button>
</div>
<script>
(function(){
 var count=document.getElementById('tk-count'), msg=document.getElementById('tk-msg'),
     go=document.getElementById('tk-go'), see=document.getElementById('tk-see'),
     list=document.getElementById('tk-list'), files=[];
 function say(t,k){ msg.textContent=t?(' — '+t):''; msg.className='msg'+(k?' '+k:''); }
 function refresh(){
   fetch('/_changes').then(function(r){return r.json();}).then(function(j){
     files=j.files||[];
     if(!j.ok){ count.textContent='Cannot check'; say(j.message||'','err'); return; }
     if(!files.length){ count.textContent='Nothing to publish'; go.disabled=true; return; }
     count.textContent=files.length+' change'+(files.length===1?'':'s')+' ready';
     go.disabled=false;
   }).catch(function(){ count.textContent='Cannot check'; });
 }
 see.addEventListener('click',function(){
   if(list.style.display==='block'){ list.style.display='none'; return; }
   list.innerHTML='<b>These will be sent:</b><ul>'+
     (files.length?files.map(function(f){return '<li>'+f.what+'</li>';}).join('')
                  :'<li>nothing</li>')+'</ul>';
   list.style.display='block';
 });
 function ensureIdentity(){
   return fetch('/_identity').then(function(r){return r.json();}).then(function(j){
     if(j.set) return true;
     var n=prompt('Before your first publish:\\n\\nWhat is your name? (it is recorded against your changes)');
     if(!n) return false;
     var e=prompt('And your email address?');
     if(!e) return false;
     return fetch('/_identity',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({name:n,email:e})})
       .then(function(r){return r.json().then(function(k){return {ok:r.ok,k:k};});})
       .then(function(res){ if(!res.ok||!res.k.ok) throw new Error(res.k.message||'Failed');
                            return true; });
   });
 }
 go.addEventListener('click',function(){
   var what=prompt('Briefly, what did you change?\\n\\n(This is just a note so it can be found later.)','Website update');
   if(what===null) return;
   go.disabled=true; list.style.display='none'; say('Sending…');
   ensureIdentity().then(function(okid){
    if(!okid){ say('Not sent','err'); go.disabled=false; return; }
    return fetch('/_publish',{method:'POST',headers:{'Content-Type':'application/json'},
         body:JSON.stringify({message:what})})
    .then(function(r){return r.json().then(function(j){return {ok:r.ok,j:j};});})
    .then(function(res){
       if(!res.ok||!res.j.ok) throw new Error(res.j.message||'Failed');
       count.textContent='Published'; say(res.j.message,'ok');
       setTimeout(refresh,2500);
    });
   }).catch(function(e){ alert(e.message); say('Not sent','err'); go.disabled=false; });
 });
 refresh(); setInterval(refresh,20000);
})();
</script>
"""


def with_publish_bar(html):
    if "</body>" not in html:
        return html + PUBLISH_BAR
    return html.replace("</body>", PUBLISH_BAR + "\n</body>", 1)


def render_add_news():
    items = read_news()
    rows = "".join(
        '<tr><td><img src="/%s"></td><td><strong>%s</strong><br><span>%s</span></td>'
        '<td>%s</td><td><a href="/blog/%s.html" target="_blank">view</a></td>'
        '<td><button class="del" data-slug="%s">Remove</button></td></tr>'
        % (_esc(n["image"]), _esc(n["title"]), _esc(n["summary"][:70]),
           _esc(n.get("date", "") or "—"), _esc(n["slug"]), _esc(n["slug"]))
        for n in reversed(items)) or '<tr><td colspan="5" class="none">No news added yet.</td></tr>'

    return """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Takwa — Add News</title>
<style>
 *{box-sizing:border-box}
 body{margin:0;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
      background:#fafaf8;color:#1e1e1e}
 header{background:#4c9932;color:#fff;padding:26px 32px}
 header h1{margin:0 0 6px;font-size:24px}header p{margin:0;opacity:.93;font-size:14px}
 .wrap{margin:24px 32px 60px;max-width:1100px}
 .card{background:#fff;border:1px solid #e2e2dc;border-radius:10px;padding:22px 24px;margin-bottom:26px}
 h2{font-size:18px;margin:0 0 16px;border-bottom:2px solid #4c9932;padding-bottom:7px}
 label{display:block;font-size:13px;font-weight:600;margin:14px 0 5px}
 .hint{font-weight:400;color:#888}
 input[type=text],textarea{width:100%;border:1px solid #cfcfc7;border-radius:6px;
      padding:9px 11px;font:14px inherit}
 textarea{resize:vertical}
 input[type=file]{margin-top:6px;font-size:13px}
 .row2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
 button{border:none;border-radius:6px;padding:10px 20px;font-size:13.5px;font-weight:600;cursor:pointer}
 .save{background:#4c9932;color:#fff;margin-top:20px}
 .save:hover{background:#3d7a28}
 .del{background:#fff;border:1px solid #e0c0bc;color:#a33b2c;padding:6px 12px;font-size:12px}
 .del:hover{background:#fdf0ee}
 table{width:100%;border-collapse:collapse;font-size:13.5px}
 td{border-top:1px solid #eee;padding:9px 8px;vertical-align:middle}
 td img{width:78px;height:47px;object-fit:cover;border-radius:5px;background:#f0f0ea;display:block}
 td span{color:#888;font-size:12px}
 .none{color:#999;text-align:center;padding:22px}
 #status{margin-top:14px;font-size:13px;min-height:1px}
 #status.ok{color:#2f6b1e}#status.err{color:#b3261e}#status.busy{color:#777}
 #preview{max-width:230px;border-radius:8px;margin-top:10px;display:none}
 .note{background:#f4f8f2;border-left:3px solid #4c9932;padding:11px 14px;
       font-size:13px;color:#4a5a45;margin:0 0 20px;border-radius:0 6px 6px 0}
</style></head><body>
<header><h1>Add News</h1>
<p>Creates the article's own page and puts it at the top of Blog &amp; Events.</p></header>
<div class="wrap">

 <p class="note">The Arabic version is generated automatically, but it starts as
 the English text. Open the Arabic text index afterwards to translate it.</p>

 <div class="card">
  <h2>New news item</h2>
  <div class="row2">
   <div>
    <label>Headline</label>
    <input type="text" id="title" placeholder="e.g. Takwa Opens New Production Line">
    <label>Date <span class="hint">(shown on the card, optional)</span></label>
    <input type="text" id="date" placeholder="e.g. September 2026">
    <label>Photo</label>
    <input type="file" id="image" accept="image/*">
    <img id="preview">
   </div>
   <div>
    <label>Summary <span class="hint">(one or two lines, shown on the listing)</span></label>
    <textarea id="summary" rows="3"></textarea>
    <label>Article <span class="hint">(one paragraph per line)</span></label>
    <textarea id="body" rows="11" placeholder="Leave a blank line between paragraphs if you like — each line becomes its own paragraph."></textarea>
   </div>
  </div>
  <button class="save" id="save">Publish news item</button>
  <p id="status"></p>
 </div>

 <div class="card">
  <h2>News you've added</h2>
  <table><tbody id="list">@@ROWS@@</tbody></table>
 </div>
</div>

<script>
var imgData="";
document.getElementById('image').addEventListener('change',function(e){
  var f=e.target.files[0]; if(!f) return;
  var r=new FileReader();
  r.onload=function(){ imgData=r.result;
    var p=document.getElementById('preview'); p.src=r.result; p.style.display='block'; };
  r.readAsDataURL(f);
});
function say(t,k){var s=document.getElementById('status');s.textContent=t;s.className=k||'';}
document.getElementById('save').addEventListener('click',function(){
  var body={title:document.getElementById('title').value,
            date:document.getElementById('date').value,
            summary:document.getElementById('summary').value,
            body:document.getElementById('body').value,
            image:imgData};
  if(!body.title.trim()){say('Give the news item a headline first.','err');return;}
  if(!body.summary.trim()){say('Write a short summary — it is what shows on the listing.','err');return;}
  if(!imgData){say('Choose a photo first.','err');return;}
  say('Publishing...','busy');
  fetch('/_add_news',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify(body)})
   .then(function(r){return r.json().then(function(j){return {ok:r.ok,j:j};});})
   .then(function(res){
      if(!res.ok||!res.j.ok) throw new Error(res.j.message||'Failed');
      say(res.j.message+' Reloading...','ok');
      setTimeout(function(){location.reload();},900);
   }).catch(function(e){say(e.message,'err');});
});
document.getElementById('list').addEventListener('click',function(e){
  var b=e.target.closest('.del'); if(!b) return;
  if(!confirm('Remove this news item? Its page and photo will be deleted.')) return;
  fetch('/_delete_news?slug='+encodeURIComponent(b.dataset.slug),{method:'POST'})
   .then(function(r){return r.json();})
   .then(function(j){ say(j.message||'Removed','ok'); setTimeout(function(){location.reload();},700); })
   .catch(function(){ say('Could not remove it.','err'); });
});
</script>
</body></html>""".replace("@@ROWS@@", rows)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=SITE, **kw)

    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet

    def _json(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        # never cache, so a changed photo shows up on refresh
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        if path == "/_state":
            # what the page needs to show current state without being regenerated
            return self._json(200, {"ok": True, "removed": sorted(read_manifest().keys())})

        if path == "/_changes":
            return self._json(200, git_changes())

        if path == "/_identity":
            return self._json(200, git_identity())

        # The tool pages are static files on disk. Serving them through here
        # rather than letting SimpleHTTPRequestHandler do it is what puts the
        # Publish bar on every one of them, including ones added later.
        if re.fullmatch(r"/_[a-z0-9\-]+\.html", path):
            disk = os.path.join(SITE, path.lstrip("/"))
            if os.path.exists(disk):
                body = with_publish_bar(read_html(disk)).encode("utf-8", "replace")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
                return

        if path == "/_add-news.html":
            body = with_publish_bar(render_add_news()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/_add-product.html":
            body = with_publish_bar(render_add_product()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/_team-preview.html":
            p = os.path.join(ROOT, "photo-proposal", "team-preview.html")
            if not os.path.exists(p):
                return self._json(404, {"ok": False, "message": "no team preview built yet"})
            body = open(p, encoding="utf-8").read().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/_photo-proposal.html":
            body = render_proposal_index().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/_proposal_img":
            # serves both sides of the comparison: what's on the site now, and
            # the proposed photo cropped exactly as applying it would produce
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            slot = (q.get("slot") or [""])[0]
            which = (q.get("which") or ["current"])[0]
            proposal = load_proposal()
            rel = SLOTS.get(slot)
            if not rel or slot not in proposal:
                return self._json(404, {"ok": False, "message": "unknown slot"})
            try:
                live = os.path.join(SITE, rel)
                with Image.open(live) as original:
                    w, h = original.size
                if which == "proposed":
                    with Image.open(proposal[slot]["source"]) as src:
                        src.load()
                        im = cover(flatten(src), w, h)
                else:
                    with Image.open(live) as cur:
                        cur.load()
                        im = flatten(cur)
                buf = io.BytesIO()
                im.save(buf, format="JPEG", quality=88)
                data = buf.getvalue()
            except Exception as e:
                return self._json(500, {"ok": False, "message": str(e)})
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        if path == "/_text-index.html":
            body = render_text_index().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/.well-known/appspecific/com.chrome.devtools.json":
            # Lets Chrome DevTools edit these files directly: Sources -> Workspace
            # shows the folder and offers to connect it. Once connected, changes
            # made in the Styles pane are written straight to the .css file.
            uuid = hashlib.md5(SITE.encode()).hexdigest()
            return self._json(200, {"workspace": {"root": SITE, "uuid": uuid}})

        return super().do_GET()

    def _json_body(self):
        """Read the whole request before deciding anything about it.

        Rejecting on Content-Length alone left the browser still sending, so
        it saw a broken pipe instead of the error message. A product photo
        base64-encodes to several MB, so the old 2MB ceiling was too low as
        well.
        """
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            raise ValueError("Nothing was sent.")
        if length > 40 * 1024 * 1024:
            # still drain it, so the client gets a real answer
            remaining = length
            while remaining > 0:
                chunk = self.rfile.read(min(65536, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
            raise ValueError("That photo is too large — please use one under about 25 MB.")

        raw = b""
        while len(raw) < length:
            chunk = self.rfile.read(min(65536, length - len(raw)))
            if not chunk:
                break
            raw += chunk
        return json.loads(raw.decode("utf-8"))

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        slot = (query.get("slot") or [""])[0]

        try:
            if parsed.path == "/_identity":
                b = self._json_body()
                return self._json(200, {"ok": True,
                    "message": set_git_identity(b.get("name", ""), b.get("email", ""))})

            if parsed.path == "/_publish":
                body = self._json_body()
                return self._json(200, {"ok": True,
                                        "message": git_publish(body.get("message", ""))})

            if parsed.path == "/_add_news":
                return self._json(200, {"ok": True, "message": add_news(self._json_body())})

            if parsed.path == "/_delete_news":
                slug = (query.get("slug") or [""])[0]
                return self._json(200, {"ok": True, "message": delete_news(slug)})

            if parsed.path == "/_add_product":
                return self._json(200, {"ok": True, "message": add_product(self._json_body())})

            if parsed.path == "/_delete_product":
                slug = (query.get("slug") or [""])[0]
                return self._json(200, {"ok": True, "message": delete_product(slug)})

            if parsed.path == "/_text_edit":
                body = self._json_body()
                msg = apply_text_edit(body.get("page", ""), int(body.get("seq", -1)), body.get("text", ""))
                return self._json(200, {"ok": True, "message": msg})

            if parsed.path == "/_ar_edit":
                body = self._json_body()
                msg = set_translation(body.get("english", ""), body.get("arabic", ""))
                return self._json(200, {"ok": True, "message": msg})

            if parsed.path == "/_ar_reset":
                body = self._json_body()
                msg, arabic = clear_translation(body.get("english", ""))
                return self._json(200, {"ok": True, "message": msg, "arabic": arabic})

            if parsed.path == "/_text_undo":
                body = self._json_body()
                msg, original = restore_text(body.get("page", ""), int(body.get("seq", -1)))
                return self._json(200, {"ok": True, "message": msg, "original": original})

            if parsed.path == "/_undo":
                return self._json(200, {"ok": True, "message": restore_photo(slot)})

            if parsed.path == "/_apply_proposal":
                return self._json(200, {"ok": True, "message": apply_proposal(slot)})

            if parsed.path == "/_blank":
                return self._json(200, {"ok": True, "message": blank_photo(slot)})

            if parsed.path == "/_remove":
                return self._json(200, {"ok": True, "message": remove_from_pages(slot)})

            if parsed.path == "/_upload":
                length = int(self.headers.get("Content-Length") or 0)
                if length <= 0:
                    raise ValueError("No file received.")
                if length > 60 * 1024 * 1024:
                    raise ValueError("That file is over 60 MB — too big.")
                return self._json(200, {"ok": True,
                                        "message": apply_photo(slot, self.rfile.read(length))})
        except ValueError as e:
            return self._json(400, {"ok": False, "message": str(e)})
        except Exception as e:
            return self._json(500, {"ok": False, "message": "Something went wrong: %s" % e})

        self._json(404, {"ok": False, "message": "Not found"})


def lan_ip():
    """The address other devices on the Wi-Fi can reach, ignoring VPN and Docker."""
    try:
        import subprocess
        out = subprocess.run(["ip", "-4", "-o", "addr", "show"],
                             capture_output=True, text=True, timeout=3).stdout
        candidates = []
        for line in out.splitlines():
            parts = line.split()
            if len(parts) < 4:
                continue
            iface, addr = parts[1], parts[3].split("/")[0]
            if iface == "lo" or iface.startswith(("docker", "br-", "veth", "proton", "tun", "wg")):
                continue
            candidates.append((iface, addr))
        # prefer wireless/ethernet interfaces on a normal home subnet
        for iface, addr in candidates:
            if addr.startswith("192.168."):
                return addr
        if candidates:
            return candidates[0][1]
    except Exception:
        pass

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("192.168.1.1", 1))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    if not SLOTS:
        sys.exit("photo-slots.json is missing — it should sit next to this script.")

    # make sure the photo index is up to date before serving
    gen = os.path.join(ROOT, "rebuild-photo-index.py")
    if os.path.exists(gen):
        os.system('python3 "%s" > /dev/null 2>&1' % gen)

    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print("\n  Takwa website is running.\n")
    print("  Edit photos here:   http://localhost:%d/_photo-index.html" % PORT)
    print("  Edit text here:     http://localhost:%d/_text-index.html" % PORT)
    print("  Edit Arabic text:   http://localhost:%d/_text-index-ar.html" % PORT)
    print("  Photo proposal:     http://localhost:%d/_photo-proposal.html" % PORT)
    print("  Add a product:      http://localhost:%d/_add-product.html" % PORT)
    print("  Add news:           http://localhost:%d/_add-news.html" % PORT)
    print("  From another device: http://%s:%d/_photo-index.html" % (lan_ip(), PORT))
    print("                   or: http://%s:%d/_text-index.html" % (lan_ip(), PORT))
    print("\n  See the site itself: http://localhost:%d/\n" % PORT)
    print("  Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.\n")
