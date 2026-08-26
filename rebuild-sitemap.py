"""Regenerate sitemap.xml from the pages that actually exist on disk.

The first sitemap was written by hand, so it rotted as soon as pages were
deleted: it was listing seventeen URLs that no longer exist -- the demo product,
the placeholder vacancy and the template's car articles -- and a search engine
following it at launch would have collected seventeen 404s.

Pages are discovered rather than listed, so this stays correct as the site
changes. Each English page is paired with its -ar twin and both carry the same
pair of hreflang alternates, which is what tells a search engine they are the
same page in two languages rather than duplicates competing with each other.

Priorities keep the scheme the hand-written file used: the homepage at 1.0,
top-level pages at 0.8, detail pages in blog/ career/ listing/ our-brands/ at
0.6. lastmod comes from the file's own modification date.
"""
import datetime
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "Takwafoods web", "takwaweb.designersidhost.com")
BASE = "https://takwafoods.com/"
OUT = os.path.join(SITE, "sitemap.xml")

SKIP_DIRS = {"frontend", "global", "uploads", "_photo-backups"}
DETAIL_DIRS = {"blog", "career", "listing", "our-brands"}

# Pages deliberately kept out of the sitemap. Empty at the moment: the careers
# section was in here while it was hidden, and is back in the site now that the
# page has been rebuilt. Anything listed here should also carry a noindex, or
# the two are saying different things to a crawler.
HIDDEN = set()


def discover():
    """Every English page, relative to the site root, forward slashes."""
    found = []
    for root, dirs, files in os.walk(SITE):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if not name.endswith(".html"):
                continue
            if name.endswith("-ar.html") or name.startswith("_"):
                continue
            rel = os.path.relpath(os.path.join(root, name), SITE).replace(os.sep, "/")
            if rel in HIDDEN:
                continue
            found.append(rel)
    return sorted(found)


def priority(path):
    if path == "index.html":
        return "1.0"
    return "0.6" if path.split("/")[0] in DETAIL_DIRS else "0.8"


def lastmod(path):
    p = os.path.join(SITE, path)
    return datetime.date.fromtimestamp(os.path.getmtime(p)).isoformat()


def entry(loc, en, ar, mod, pri):
    return (
        "  <url>\n"
        "    <loc>%s%s</loc>\n"
        '    <xhtml:link rel="alternate" hreflang="en" href="%s%s"/>\n'
        '    <xhtml:link rel="alternate" hreflang="ar" href="%s%s"/>\n'
        "    <lastmod>%s</lastmod>\n"
        "    <priority>%s</priority>\n"
        "  </url>\n" % (BASE, loc, BASE, en, BASE, ar, mod, pri))


def main():
    pages = discover()
    out = ['<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n']

    listed = paired = 0
    for en in pages:
        ar = en[:-len(".html")] + "-ar.html"
        has_ar = os.path.exists(os.path.join(SITE, ar))
        pri = priority(en)
        out.append(entry(en, en, ar if has_ar else en, lastmod(en), pri))
        listed += 1
        if has_ar:
            out.append(entry(ar, en, ar, lastmod(ar), pri))
            listed += 1
            paired += 1
        else:
            print("  !! no Arabic twin for %s" % en)

    out.append("</urlset>\n")
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(out))

    print("  %d urls (%d English + %d Arabic) written to sitemap.xml"
          % (listed, len(pages), paired))


if __name__ == "__main__":
    main()
