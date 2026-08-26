#!/usr/bin/env python3
"""
Swap a photo on the Takwa website.

Usage:
    python3 swap-photo.py "<new photo>" "<slot>"
    python3 swap-photo.py --list
    python3 swap-photo.py --undo "<slot>"

The new photo is automatically centre-cropped, resized, and converted to match
whatever the site already expects in that slot, so you can hand it any JPG or
PNG straight off a camera or phone.

Examples:
    python3 swap-photo.py ~/Pictures/factory.jpg home-about
    python3 swap-photo.py ~/Pictures/team.jpg uploads/website-images/blog-header.webp

This script finds the website folder on its own, so it keeps working even if the
file gets moved somewhere else.
"""

import json
import os
import shutil
import sys

from PIL import Image

SITE_TAIL = os.path.join("Takwafoods web", "takwaweb.designersidhost.com")
FALLBACK_ROOT = "/home/geogre-youssef/obsidian/George/Takwa"


def find_site():
    """Locate the website folder without assuming where this script lives."""
    seen = []
    here = os.path.dirname(os.path.abspath(__file__))
    for start in (here, os.getcwd()):
        d = start
        for _ in range(5):                      # walk upward a few levels
            seen.append(os.path.join(d, SITE_TAIL))
            d = os.path.dirname(d)
    seen.append(os.path.join(FALLBACK_ROOT, SITE_TAIL))

    for path in seen:
        if os.path.isdir(path):
            return path
    sys.exit("Could not find the website folder (\"%s\").\n"
             "Run this script from inside the Takwa folder." % SITE_TAIL)


SITE = find_site()
ROOT = os.path.dirname(os.path.dirname(SITE))   # the Takwa folder
BACKUPS = os.path.join(ROOT, "_photo-backups")


def load_slots():
    """Read the shared short-name map; tolerate it having been moved too."""
    here = os.path.dirname(os.path.abspath(__file__))
    for d in (ROOT, here, os.path.join(ROOT, "other"), os.getcwd()):
        p = os.path.join(d, "photo-slots.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                return {k: v for k, v in json.load(fh).items()
                        if not k.startswith("_")}
    return {}


SLOTS = load_slots()


def resolve(slot):
    """Accept a friendly short name or a path relative to the site root."""
    if slot in SLOTS:
        return SLOTS[slot]
    candidate = slot.replace("%20", " ").lstrip("/")
    if os.path.exists(os.path.join(SITE, candidate)):
        return candidate
    sys.exit("Unknown slot: %s\nRun  python3 swap-photo.py --list  to see the options." % slot)


def flatten(im):
    """Drop transparency onto white so JPEG/WEBP output stays clean."""
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert("RGB")


def cover(im, w, h):
    """Centre-crop to the target aspect ratio, then resize — no squashing."""
    if im.width / im.height > w / h:
        new_w = int(im.height * w / h)
        x = (im.width - new_w) // 2
        im = im.crop((x, 0, x + new_w, im.height))
    else:
        new_h = int(im.width * h / w)
        y = (im.height - new_h) // 2
        im = im.crop((0, y, im.width, y + new_h))
    return im.resize((w, h), Image.LANCZOS)


def backup(rel):
    dest = os.path.join(BACKUPS, rel)
    if os.path.exists(dest):
        return                                   # keep the very first original
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(os.path.join(SITE, rel), dest)


def swap(source, slot):
    rel = resolve(slot)
    target = os.path.join(SITE, rel)
    source = os.path.expanduser(source)

    if target.lower().endswith(".mp4"):
        sys.exit("That slot is a video, not a photo. Ask Claude to swap it for you.")
    if target.lower().endswith(".svg"):
        sys.exit("That slot is an SVG icon and has to be edited by hand.")
    if not os.path.exists(source):
        sys.exit("Can't find your photo: %s" % source)

    with Image.open(target) as original:
        w, h = original.size

    backup(rel)

    with Image.open(source) as src:
        if src.width < w or src.height < h:
            print("Note: your photo (%dx%d) is smaller than the slot (%dx%d) — "
                  "it will look soft." % (src.width, src.height, w, h))
        out = cover(flatten(src), w, h)

    ext = os.path.splitext(target)[1].lower()
    opts = {"quality": 88, "method": 6} if ext == ".webp" else \
           {"quality": 88} if ext in (".jpg", ".jpeg") else {}
    out.save(target, **opts)

    print("Replaced %s  (%dx%d)" % (rel, w, h))
    print("Refresh the browser with Ctrl+Shift+R to see it.")


def undo(slot):
    rel = resolve(slot)
    saved = os.path.join(BACKUPS, rel)
    if not os.path.exists(saved):
        sys.exit("No backup stored for %s — it was never swapped with this tool." % rel)
    shutil.copy2(saved, os.path.join(SITE, rel))
    print("Restored the original %s" % rel)


def show_slots():
    if not SLOTS:
        sys.exit("photo-slots.json is missing — it should sit next to this script.")
    print("Website: %s\n" % SITE)
    for name, rel in SLOTS.items():
        path = os.path.join(SITE, rel)
        size = ""
        if os.path.exists(path) and not rel.lower().endswith((".mp4", ".svg")):
            with Image.open(path) as im:
                size = "%dx%d" % (im.width, im.height)
        elif not os.path.exists(path):
            size = "MISSING"
        print("  %-18s %-12s %s" % (name, size, rel))


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
    elif args[0] == "--list":
        show_slots()
    elif args[0] == "--undo" and len(args) == 2:
        undo(args[1])
    elif len(args) == 2:
        swap(args[0], args[1])
    else:
        sys.exit("Usage: python3 swap-photo.py \"<new photo>\" \"<slot>\"   (--help for more)")
