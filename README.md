# Takwa Foods website

Everything needed to edit takwafoods.com: the site itself, and the tools that
maintain it.

---

## Getting set up

You need **Python 3** and **Git**. One extra library:

```bash
pip install Pillow
```

## Starting the tools

**Just double-click the launcher.** It starts the server and opens the browser.

| | |
|---|---|
| Linux | `takwa-tools.sh`, or **Takwa Website Editor** in the applications menu |
| Windows | `takwa-tools.bat` |

Running it twice is safe — it notices the server is already up and just opens
the browser.

To stop: `takwa-tools-stop.sh` on Linux, or close the minimised Python window
on Windows.

If you would rather use a terminal, `python3 start.py` from this folder does
the same thing, and `Ctrl+C` stops it.

Either way the tools are at **http://localhost:8099**. That is the whole site
running on your own machine — nothing you do there touches the live website
until someone deploys.

**The first time, it asks you to set a password.** Choose one and confirm it.
After that it asks for the password each time the tools are started.

The password is stored as a scrypt hash in `.takwa-tools-auth.json`, beside the
repository and never inside it. It is per-computer, so yours and George's are
different, and there is no way to recover a forgotten one — delete that file
and the tools offer to set a new password.

**Nothing outside your own computer can reach the tools.** The server listens
on 127.0.0.1 only, so the office wifi, a guest on the network and anyone else
simply cannot connect. The password is there for the case of an unattended
laptop.

---

## The four editing tools

All are ordinary pages served by `start.py`, and all save straight to disk.

**/_photo-index.html** — every image on the site in one place. Swap a photo and
it is replaced everywhere it appears.

**/_text-index-ar.html** — every piece of Arabic text next to its English
original. Fix a translation here rather than editing the `-ar.html` pages by
hand.

**/_add-product.html** — adds a product. Creates its page, its card on Our
Products, and its Arabic version. Pick **Enna** or **Flavora Cafe** from the
Brand list and it is listed on that brand's own page as well; leave it as
*None* and it appears under Our Products only.

**/_add-news.html** — adds a news item. Creates the article page, puts a card
at the top of Blog & Events, and makes the Arabic version. Write one paragraph
per line.

Both "add" tools generate the Arabic page from the English text, so it starts
out in English. Open the Arabic text index afterwards and translate it.

Every tool page carries the same bar along the bottom:

| | |
|---|---|
| **See what changed** | Lists what is waiting, in plain words |
| **Undo all** | Throws away everything since your last publish. Asks twice. |
| **Publish** | Sends your work to George |

**Undo all** cannot touch anything already published, and it does not delete
your saved password.

These pages start with `_`, which keeps them off the live site: the deploy
script skips them and `.htaccess` denies them.

**They only run on your machine, and that is deliberate.** They write files, so
putting them on the public server would mean a password away from someone
writing arbitrary files into the web root. Anything you publish goes out the
same way as everything else — commit, push, and George deploys.

---

## How a change reaches the live site

1. Edit locally, with the server running
2. Check it at localhost:8099 — **both languages**
3. Commit and push
4. **Tell George.** He deploys from cPanel

Pushing does not publish. The live site only changes when George clicks Deploy
in cPanel. That is deliberate — it means nothing goes public by accident.

---

## Things that will bite you

**Never use "Discard All Changes" in VS Code.** It permanently deletes
untracked files with no undo. This is exactly how `listing/_product-template.html`
was lost once already, which broke "Add a product" until it was recovered from
git history.

**Files starting with `_` are tools, not clutter.** `_photo-backups/` in
particular is load-bearing: `start.py` rebuilds pages *from* those pristine
copies. Delete it and the editing tools stop working.

**Arabic pages are generated, not written.** Every `-ar.html` file is built
from its English original by `build_arabic.py`. Edit `index.html` by hand
without regenerating and the two languages drift apart silently — no error,
just a site that says different things in each language. Use the text index.

**`start.py` reads its configuration once, at startup.** Change a config file
and you must restart the server before you see any effect.

**Restart the server after pulling.** Same reason.

---

## What is in here

| | |
|---|---|
| `Takwafoods web/takwaweb.designersidhost.com/` | the website — this is what gets deployed |
| `start.py` | dev server and editing API, port 8099 |
| `build_arabic.py` | generates every `-ar.html` page |
| `translations_ar.py` | the Arabic translation table |
| `text_engine.py` | byte-exact HTML text editing |
| `rebuild-sitemap.py` | rebuilds `sitemap.xml` from what is on disk |
| `rebuild-text-index.py` | rebuilds the Arabic review index |
| `_photo-backups/` | pristine page copies + edit manifests — do not delete |
| `.cpanel.yml` | the deploy script, read by cPanel |

Some folders are deliberately not in this repository — original photography
(3.4 GB of RAW files), the cafe playlist, and personal documents. See
`.gitignore`. None of them are needed to work on the site.

---

## Facts about this site that are not negotiable

**1996 is the founding year.** It appears in several places, including a
counter on the About page that computes years in business from it. One source
of truth.

**Do not invent claims.** Certifications, sourcing and health statements are
either already on the site or they are not. If something is not there, ask
before adding it.

**Keep the Arabic at parity.** Anything added in English gets added in Arabic.

**Nothing may reference `takwaweb.designersidhost.com`** in a URL. That is the
old staging host and the folder name is only a leftover.

**Applications contain real personal data.** Submissions from `apply.html` are
written on the server, outside the web root, and read through `/admin/`. Dates
of birth, salary history, referees. Treat accordingly.

---

## Who does what

| | |
|---|---|
| Editing, local testing, pushing | the developer |
| cPanel, deploying, DNS, email | George |

If the live site looks wrong, it is a deploy question — ask George. If
localhost looks wrong, it is an editing question.
