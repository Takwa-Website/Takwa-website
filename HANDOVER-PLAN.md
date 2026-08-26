# Handover plan

She edits and pushes. You deploy. That is the whole arrangement.

She never gets cPanel, DNS, the domain registrar or Microsoft 365. Nothing she
can do will take the site down or stop company email.

`README.md` is her guide — send her that one. This file is yours.

---

## Already done

- [x] Full backup on the Backup Plus drive — 4.9 GB, verified
- [x] Repository restructured so the editing tools travel with the site
- [x] Company account created — **Takwa-Website**
- [x] Repository created and pushed — 339 files
- [x] `README.md` written for her

**Three steps left.** They are all clicks.

---

## Step 1 — Make the repository public

GitHub → repo → **Settings → General → Danger Zone → Change visibility →
Public**.

This is the step that removes SSH keys, the Terminal and deploy keys from this
plan entirely. A public repository clones over plain HTTPS, which is what
cPanel already knows how to do.

**This is not a downgrade.** `Georgeyoussef066/TakwaFoods-Website` has been
public since 2 August with exactly the same code in it. Nothing becomes
readable that was not already readable. There are no passwords, tokens or keys
in the repository — the admin password lives on the server as a hash, above the
web root, and never touches git.

If you ever want it private later, it is the same menu. It makes the cPanel
side harder, which is the only reason it is not the default here.

- [ ] Repository is public

---

## Step 2 — Point cPanel at the new repository

- [ ] cPanel → **Git Version Control**
- [ ] Remove the old `TakwaFoods-Website` entry

      This deletes only cPanel's own working copy. Your live site is
      untouched — public_html is a separate directory that deploys copy into.

- [ ] **Create**, with this clone URL:

      https://github.com/Takwa-Website/Takwa-website.git

- [ ] Repository path: `/home/takwafood/takwa-website`

      This is cPanel's working copy, NOT the website. It must not be
      public_html. The deploy reads from the working copy and copies into
      public_html.

- [ ] It clones successfully

---

## Step 3 — Deploy and check

- [ ] **Update from Remote**
- [ ] **Deploy HEAD Commit**

### Should load

- [ ] `takwafoods.com`
- [ ] `takwafoods.com/index-ar.html` — Arabic
- [ ] `takwafoods.com/listings.html` — products
- [ ] `takwafoods.com/apply.html`

### Should NOT load

These three were being published by mistake. Confirming they are dead is how
you know today's fix actually shipped.

- [ ] `takwafoods.com/_photo-index.html`
- [ ] `takwafoods.com/listing/_product-template.html`
- [ ] `takwafoods.com/uploads/share/_flavora-cafe-og.jpg.bak`

If any of those three load, stop and say so.

---

## That is the handover done

Everything below is the rest of the week, not blockers.

---

## Bring her in

Any time. She does not need cPanel, so none of the above blocks her.

- [ ] She creates her own free GitHub account and sends you the username
- [ ] Repo → **Settings → Collaborators → Add people** → **Write**
- [ ] She accepts the emailed invitation

**Do not sign your GitHub account into her VS Code.** Collaborator access lets
her push as herself and you revoke it in one click. Sharing the account cannot
be undone without changing your password.

### What she does

Send her `README.md`. She needs Python 3 and Git, then:

```bash
pip install Pillow
python3 start.py
```

Then `http://localhost:8099`. Exactly what you do.

---

## Set the admin password

`/admin/` has **no password set**. The first person to open it sets it and
owns it — including a stranger who guesses the URL.

- [ ] Open `takwafoods.com/admin/`, set a strong password, save it in a
      password manager

Only a bcrypt hash is stored, above the web root. **Nobody can recover it
later — not you, not me.**

---

## Her first change, end to end

Before you trust the arrangement, watch one change go all the way through:

- [ ] She fixes a typo, checks it at localhost:8099
- [ ] She checks the **Arabic** version of that page still matches
- [ ] She commits, pushes, texts you
- [ ] You Update from Remote → Deploy HEAD Commit
- [ ] It is live

The Arabic check matters. Every `-ar.html` page is *generated* from the English
by `build_arabic.py`. Editing English by hand without regenerating leaves the
two languages saying different things, with no error. It is the quietest way
this site can break.

---

## Clean up afterwards

- [ ] Delete `.git-OLD-archive/` from
      `Takwafoods web/takwaweb.designersidhost.com/`
- [ ] Leave the old repo `Georgeyoussef066/TakwaFoods-Website` alone — it holds
      the previous 46 commits. Archive it, do not delete it.
- [ ] Fix your git identity, currently a typo:

      git config --global user.name "George Youssef"
      git config --global user.email "georgeyoussef055@gmail.com"

---

## If it goes wrong

| Problem | Fix |
|---|---|
| She should not have access | Settings → Collaborators → remove |
| A bad change went live | Deploy an earlier commit from cPanel |
| The new repo broke deploys | The old repo is untouched — point cPanel back at it |
| Everything is wrong | Restore `01-site-and-scripts-COMPLETE.tar.gz` from the Backup Plus drive |

Never **transfer** the repository. Collaborator access does the same job and
undoes in one click; a transfer cannot be reversed without the other person's
cooperation.

---

## What she never gets, and why

| | |
|---|---|
| **cPanel** | The server, and the job applications — real people's dates of birth, salary history, referees |
| **Cloudflare / DNS** | A wrong record kills company email silently; you find out days later through bounces |
| **Domain registrar** | Ownership of takwafoods.com |
| **Microsoft 365** | Company email |

The MX records must never be altered.

---

## Tell her these three things

**Never use "Discard All Changes" in VS Code.** It permanently deletes
untracked files. That is how `listing/_product-template.html` was lost once
already, which broke "Add a product".

**Files starting with `_` are tools, not clutter.** `_photo-backups/` is
load-bearing — `start.py` rebuilds pages from those pristine copies.

**Pushing does not publish.** Only your click in cPanel does.

---

## Appendix — errors already hit, so you recognise them

**`Repository not found` on a URL you know is correct.** Two causes.

*Wrong remote.* `git remote add` only creates. If `origin` already exists it
errors and changes nothing, so pushes keep going to the old URL. Check with
`git remote -v`; change it with `git remote set-url origin <url>`.

*Wrong account.* GitHub answers 404, never 403, for a private repo your
credential cannot see. This machine uses `credential.helper store`, which keeps
one credential for all of github.com and was authenticating as
`Georgeyoussef066`.

**Two GitHub accounts on one machine.** `credential.helper store` cannot hold
both. Add one account as a collaborator on the other's repos, or install the
GitHub CLI (`sudo apt install gh`, then `gh auth login`).
