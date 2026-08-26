"""Build _text-index-ar.html: every Arabic string on the site, in one editable page.

It sits beside the English text index that start.py renders at
_text-index.html, and is a separate page because the two edit different
things. That one rewrites text nodes in the English pages. This one cannot:
the -ar.html files
are generated: build_arabic.py rewrites them from the English pages on every
run, so a text edit saved into an -ar page survives only until the next build.
The Arabic that lasts lives in the translation table, and that is what this
page edits.

Strings are discovered rather than listed. Each English page is walked with the
same scanner build_arabic.py uses, through the same SKIP and is_placeholder
filters, so what appears here is exactly the set the build tries to translate --
no more, and nothing quietly left out.

A string used in more than one place is listed once, under the first page it
appears on, and says where else it is used. That is not a display convenience:
the table is keyed by the English text, so editing "Get In Touch" changes every
page carrying it, and the page has to say so before someone edits the footer
expecting to touch one page.

Anything the build could not translate is listed too, marked as missing, so the
gaps are visible instead of showing up as English on an Arabic page.

Run:  python3 rebuild-text-index.py
"""
import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import text_engine as te
import translations_ar as tr
from build_arabic import ALL_PAGES

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "Takwafoods web", "takwaweb.designersidhost.com")
OUT = os.path.join(SITE, "_text-index-ar.html")

# Friendly names, so the page reads as the site rather than as a file listing.
PAGE_NAMES = {
    "index.html": "Home",
    "about-us.html": "About Us",
    "listings.html": "Our Products",
    "our-team.html": "Our Team",
    "blogs.html": "News",
    "careers.html": "Careers",
    "contact-us.html": "Get In Touch",
    "our-brands/flavora-cafe.html": "Brand — Flavora",
    "our-brands/enna.html": "Brand — Enna",
}


def page_label(page):
    if page in PAGE_NAMES:
        return PAGE_NAMES[page]
    stem = os.path.splitext(os.path.basename(page))[0].replace("-", " ")
    folder = os.path.dirname(page)
    prefix = {"listing": "Product", "blog": "Article", "career": "Vacancy"}
    return "%s — %s" % (prefix.get(folder, folder or "Page"), stem.title())


def collect():
    """Every translatable string, in page order, with where it is used."""
    first_seen = {}
    used_on = {}
    order = []

    for page in ALL_PAGES:
        path = os.path.join(SITE, page)
        if not os.path.exists(path):
            continue
        body = te.read(path)
        for node in te.scan(body):
            text = node.text.strip()
            if not text or text in tr.SKIP or tr.is_placeholder(text):
                continue
            used_on.setdefault(text, [])
            if page not in used_on[text]:
                used_on[text].append(page)
            if text not in first_seen:
                first_seen[text] = page
                order.append(text)

    groups = {}
    for text in order:
        groups.setdefault(first_seen[text], []).append(text)

    sections = []
    for page in ALL_PAGES:
        if page not in groups:
            continue
        entries = []
        for text in groups[page]:
            entries.append({
                "en": text,
                "ar": tr.AR.get(text, ""),
                "missing": text not in tr.AR,
                "overridden": text in tr.OVERRIDES,
                "also": [page_label(p) for p in used_on[text] if p != page],
            })
        sections.append({"page": page, "label": page_label(page),
                         "entries": entries})
    return sections


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Arabic text — Takwa</title>
<style>
:root{ color-scheme: light dark;
  --bg:#f6f7f6; --card:#fff; --line:#dfe1de; --ink:#12211f; --dim:#6b7a76;
  --accent:#2C6728; --warn:#8a5a00; --warnbg:#fff6e0; --ok:#e8f5e9; }
@media (prefers-color-scheme: dark){ :root{
  --bg:#0f1614; --card:#17211f; --line:#2a3835; --ink:#e8efec; --dim:#93a5a0;
  --accent:#73ED7C; --warn:#f0c674; --warnbg:#2e2612; --ok:#16301c; } }
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{position:sticky;top:0;z-index:5;background:var(--bg);
  border-bottom:1px solid var(--line);padding:16px 22px}
h1{margin:0 0 4px;font-size:19px}
.sub{color:var(--dim);font-size:13px}
.tools{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
input[type=search],select{padding:8px 11px;border:1px solid var(--line);
  border-radius:8px;background:var(--card);color:var(--ink);font:inherit}
input[type=search]{flex:1;min-width:220px}
main{padding:22px;max-width:1080px;margin:0 auto}
section{margin-bottom:30px}
h2{font-size:14px;text-transform:uppercase;letter-spacing:.09em;
  color:var(--dim);margin:0 0 10px}
.row{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:14px 16px;margin-bottom:10px}
.row.missing{border-color:var(--warn);background:var(--warnbg)}
.en{font-size:14px;color:var(--dim);margin-bottom:9px;white-space:pre-wrap;
  word-break:break-word}
textarea{width:100%;min-height:46px;padding:10px 12px;border-radius:9px;
  border:1px solid var(--line);background:var(--bg);color:var(--ink);
  font:16px/1.75 "Tajawal","Noto Kufi Arabic","Segoe UI",Tahoma,sans-serif;
  direction:rtl;text-align:right;resize:vertical}
textarea:focus{outline:2px solid var(--accent);outline-offset:1px}
.foot{display:flex;gap:9px;align-items:center;margin-top:9px;flex-wrap:wrap}
button{padding:7px 15px;border-radius:8px;border:1px solid var(--line);
  background:var(--card);color:var(--ink);font:inherit;cursor:pointer}
button.save{background:var(--accent);border-color:var(--accent);color:#fff;
  font-weight:600}
button[disabled]{opacity:.45;cursor:default}
.tag{font-size:12px;color:var(--dim)}
.tag.edited{color:var(--accent);font-weight:600}
.tag.warn{color:var(--warn);font-weight:600}
#toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%);
  background:#12211f;color:#fff;padding:11px 20px;border-radius:9px;
  opacity:0;transition:opacity .2s;pointer-events:none;z-index:9}
#toast.on{opacity:1}
.xlink{font-size:13px;font-weight:400;color:var(--accent);text-decoration:none;margin-left:12px}
.xlink:hover{text-decoration:underline}
.note{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--accent);
  border-radius:10px;padding:13px 16px;margin-bottom:22px;font-size:13.5px;color:var(--dim)}
</style>
</head>
<body>
<header>
  <h1>Arabic text <a class="xlink" href="/_text-index.html">English text &rarr;</a></h1>
  <div class="sub" id="count"></div>
  <div class="tools">
    <input type="search" id="q" placeholder="Search English or Arabic…">
    <select id="filter">
      <option value="all">All strings</option>
      <option value="missing">Not translated</option>
      <option value="edited">Edited here</option>
      <option value="shared">Used on more than one page</option>
    </select>
  </div>
</header>
<main>
  <div class="note">
    Editing here changes the <strong>translation table</strong>, not the Arabic
    pages &mdash; those are regenerated from English on every build, so an edit
    made in the page itself would not survive. Saving rewrites every Arabic page
    that uses the string, which is why a string shared across pages says so.
    Page titles, meta descriptions and form placeholders live in
    <code>build_arabic.py</code> and are not listed here.
  </div>
  <div id="body"></div>
</main>
<div id="toast"></div>
<script type="application/json" id="data">__DATA__</script>
<script>
(function(){
  var DATA = JSON.parse(document.getElementById('data').textContent);
  var host = document.getElementById('body');
  var toastEl = document.getElementById('toast'), timer;

  function toast(msg){
    toastEl.textContent = msg; toastEl.classList.add('on');
    clearTimeout(timer); timer = setTimeout(function(){
      toastEl.classList.remove('on'); }, 2600);
  }

  function row(entry){
    var el = document.createElement('div');
    el.className = 'row' + (entry.missing ? ' missing' : '');
    el.dataset.en = entry.en.toLowerCase();
    el.dataset.ar = (entry.ar || '').toLowerCase();
    el.dataset.missing = entry.missing ? '1' : '';
    el.dataset.shared = entry.also.length ? '1' : '';
    el.dataset.edited = entry.overridden ? '1' : '';

    var en = document.createElement('div');
    en.className = 'en'; en.textContent = entry.en;
    el.appendChild(en);

    var ta = document.createElement('textarea');
    ta.value = entry.ar; ta.rows = Math.min(6, Math.ceil(entry.en.length / 70) + 1);
    el.appendChild(ta);

    var foot = document.createElement('div'); foot.className = 'foot';
    var save = document.createElement('button');
    save.className = 'save'; save.textContent = 'Save'; save.disabled = true;
    foot.appendChild(save);

    var reset = document.createElement('button');
    reset.textContent = 'Revert'; reset.disabled = !entry.overridden;
    foot.appendChild(reset);

    var state = document.createElement('span');
    state.className = 'tag';
    function mark(){
      if (el.dataset.missing) { state.className = 'tag warn';
        state.textContent = 'not translated'; }
      else if (el.dataset.edited) { state.className = 'tag edited';
        state.textContent = 'edited here'; }
      else { state.className = 'tag'; state.textContent = ''; }
    }
    mark();
    foot.appendChild(state);

    if (entry.also.length){
      var also = document.createElement('span');
      also.className = 'tag';
      also.textContent = 'also on ' + entry.also.join(', ');
      foot.appendChild(also);
    }
    el.appendChild(foot);

    var original = entry.ar;
    ta.addEventListener('input', function(){
      save.disabled = (ta.value === original);
    });

    function post(url, payload, done){
      save.disabled = true; reset.disabled = true;
      fetch(url, {method:'POST', headers:{'Content-Type':'application/json'},
                  body: JSON.stringify(payload)})
        .then(function(r){ return r.json(); })
        .then(function(d){
          toast(d.message || (d.ok ? 'Saved.' : 'Failed.'));
          if (d.ok) done(d);
          else { save.disabled = false; }
        })
        .catch(function(e){ toast('Could not reach the server.');
                            save.disabled = false; });
    }

    save.addEventListener('click', function(){
      post('/_ar_edit', {english: entry.en, arabic: ta.value}, function(){
        original = ta.value;
        el.dataset.edited = '1'; el.dataset.missing = '';
        el.classList.remove('missing');
        reset.disabled = false; mark();
      });
    });

    reset.addEventListener('click', function(){
      post('/_ar_reset', {english: entry.en}, function(d){
        ta.value = d.arabic || '';
        original = ta.value;
        el.dataset.edited = '';
        el.dataset.missing = d.arabic ? '' : '1';
        el.classList.toggle('missing', !d.arabic);
        reset.disabled = true; save.disabled = true; mark();
      });
    });

    return el;
  }

  var total = 0, missing = 0;
  DATA.forEach(function(sec){
    var s = document.createElement('section');
    var h = document.createElement('h2');
    h.textContent = sec.label + '  ·  ' + sec.entries.length;
    s.appendChild(h);
    sec.entries.forEach(function(e){
      total++; if (e.missing) missing++;
      s.appendChild(row(e));
    });
    host.appendChild(s);
  });
  document.getElementById('count').textContent =
    total + ' strings across ' + DATA.length + ' pages' +
    (missing ? '  ·  ' + missing + ' not translated' : '  ·  all translated');

  function apply(){
    var q = document.getElementById('q').value.trim().toLowerCase();
    var f = document.getElementById('filter').value;
    document.querySelectorAll('section').forEach(function(sec){
      var shown = 0;
      sec.querySelectorAll('.row').forEach(function(r){
        var hit = !q || r.dataset.en.indexOf(q) > -1 || r.dataset.ar.indexOf(q) > -1;
        if (hit && f === 'missing') hit = !!r.dataset.missing;
        if (hit && f === 'edited')  hit = !!r.dataset.edited;
        if (hit && f === 'shared')  hit = !!r.dataset.shared;
        r.style.display = hit ? '' : 'none';
        if (hit) shown++;
      });
      sec.style.display = shown ? '' : 'none';
    });
  }
  document.getElementById('q').addEventListener('input', apply);
  document.getElementById('filter').addEventListener('change', apply);
})();
</script>
</body>
</html>
"""


def main():
    sections = collect()
    blob = json.dumps(sections, ensure_ascii=False)
    # the JSON sits inside a <script> block, so the only sequence that could
    # end it early has to be broken up
    blob = blob.replace("</", "<\\/")
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(PAGE.replace("__DATA__", blob))

    strings = sum(len(s["entries"]) for s in sections)
    gaps = sum(1 for s in sections for e in s["entries"] if e["missing"])
    shared = sum(1 for s in sections for e in s["entries"] if e["also"])
    print("  wrote %s" % os.path.relpath(OUT, ROOT))
    print("  %d strings across %d pages" % (strings, len(sections)))
    print("  %d shared between pages, %d untranslated, %d edited here"
          % (shared, gaps, len(tr.OVERRIDES)))


if __name__ == "__main__":
    main()
