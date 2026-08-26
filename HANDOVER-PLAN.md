# Handover plan

Step by step, in order. Work top to bottom and tick as you go.

`README.md` is the *developer's* guide — give her that one. **This** file is
yours: the plan for getting her set up without giving away anything you should
keep.

**The split:** she edits and pushes. You deploy. She never gets cPanel, DNS,
the domain registrar or Microsoft 365. Nothing she can do will take the site
down or stop company email.

---

## Where things stand right now

Already done, on this laptop:

- [x] Full backup on the Backup Plus drive — 4.9 GB, verified
- [x] Repository restructured so the editing tools travel with the site
- [x] `.cpanel.yml` moved to the repo root and rehearsed against a test server
- [x] Two files that were leaking onto the live site fixed
- [x] `README.md` written for her
- [x] First commit made — `1f51593`, 338 files, 26 MB

Not done, because only you can do it: the GitHub account, the repo, adding
her, and re-pointing cPanel. That is the rest of this document.

**Nothing has been pushed. The live site is untouched.**

---

## Phase 1 — Create the account and the repo

- [ ] Create the company GitHub account
- [ ] Sign in to it
- [ ] Create a **new empty repository**

**Do not tick "Add a README", "Add .gitignore" or "Choose a licence."** Any of
them creates a commit on the remote that collides with yours, and the first
push is rejected with a confusing error.

- [ ] Decide private or public. **Private** is right — this repo contains the
      admin page and the application handling code. Private repos need one
      extra step in Phase 4; that is the only cost.
- [ ] Copy the repository URL

---

## Phase 2 — Push

From `~/obsidian/George/Takwa`:

```bash
git remote add origin https://github.com/COMPANY-ACCOUNT/REPO-NAME.git
git push -u origin main
```

- [ ] Push succeeds
- [ ] Open the repo on github.com and confirm you see `README.md`,
      `start.py`, and the `Takwafoods web` folder

If the push asks for a password: GitHub stopped accepting account passwords
for git. Use a **personal access token** as the password
(Settings → Developer settings → Personal access tokens), or install the
GitHub CLI and run `gh auth login`.

---

## Phase 3 — Give her access

She needs **her own free GitHub account**. Not yours.

- [ ] She creates her account and sends you the username
- [ ] Repo → **Settings → Collaborators and teams → Add people**
- [ ] Add her username, permission **Write**
- [ ] She accepts the emailed invitation

This is what lets her push without ever seeing your password, and it is
revokable in one click.

**Do not sign your GitHub account into her VS Code.** It hands her the account
itself, every commit appears to be yours, and the only way to undo it is
changing your password.

---

## Phase 4 — Re-point cPanel

cPanel is still cloned from the old repository. It must be moved to the new
one or your deploys will keep publishing the old structure.

- [ ] cPanel → **Git Version Control**
- [ ] Note the existing repo's settings, then **remove** the old entry
      (this only removes cPanel's clone — nothing on the live site is deleted)
- [ ] **Create** a new one from the new repository URL
- [ ] If the repo is private, cPanel needs credentials: generate an SSH key in
      cPanel, then add it to the repo under
      **Settings → Deploy keys → Add deploy key** (read access is enough)

- [ ] cPanel clones the repository successfully

---

## Phase 5 — Deploy once, before she starts

Do this while the only changes are yours. If something is broken, you want to
know it was already broken.

- [ ] Git Version Control → **Update from Remote**
- [ ] **Deploy HEAD Commit**
- [ ] Open **takwafoods.com** and check:
  - [ ] Home page loads and looks normal
  - [ ] Arabic version loads
  - [ ] A product page loads
  - [ ] `takwafoods.com/apply.html` loads
- [ ] Confirm the tooling files are **not** public — these should all fail:
  - [ ] `takwafoods.com/_photo-index.html`
  - [ ] `takwafoods.com/listing/_product-template.html`
  - [ ] `takwafoods.com/uploads/share/_flavora-cafe-og.jpg.bak`

If any of those three load, stop and tell me.

---

## Phase 6 — Set the admin password today

`/admin/` has **no password set**. The first person to open it sets it and
owns it — including a stranger who guesses the URL.

- [ ] Open `takwafoods.com/admin/`
- [ ] Set a strong password
- [ ] Store it in a password manager

Only a bcrypt hash is kept, in a file above the web root. **Nobody can recover
it later — not you, not me.** If it is lost, that file has to be deleted on the
server to bring the setup screen back.

---

## Phase 7 — Her setup

Send her `README.md`. She needs Python 3 and Git, then:

```bash
pip install Pillow
```

- [ ] She clones the repository in VS Code
- [ ] She runs `python3 start.py`
- [ ] She opens `http://localhost:8099` and sees the site
- [ ] She opens `/_photo-index.html` and `/_text-index-ar.html`

---

## Phase 8 — One change end to end, before you trust it

Do not consider the handover done until **she**, on her machine, has:

- [ ] Made a small visible change — a typo fix somewhere obvious
- [ ] Checked it at localhost:8099
- [ ] Checked the **Arabic** version of the same page still matches
- [ ] Committed and pushed
- [ ] Texted you

And then **you**:

- [ ] Update from Remote → Deploy HEAD Commit
- [ ] Confirmed the change is live on takwafoods.com

That last Arabic check matters more than it looks. The `-ar.html` pages are
*generated* from the English by `build_arabic.py`. Someone editing English by
hand without regenerating leaves the two languages saying different things,
with no error and no warning. It is the most likely way a newcomer quietly
damages this site.

---

## Phase 9 — Clean up, only after Phase 8 passes

- [ ] Delete `.git-OLD-archive/` from
      `Takwafoods web/takwaweb.designersidhost.com/`
- [ ] Leave the old GitHub repo alone — it holds the previous 46 commits of
      history. Archive it rather than deleting it.

---

## If it goes wrong

While she is only a collaborator, everything is reversible:

| Problem | Fix |
|---|---|
| She should not have access any more | Repo → Settings → Collaborators → remove |
| A bad change reached the live site | Deploy an earlier commit from cPanel |
| The restructure broke deploys | The old repo is untouched — re-point cPanel back to it |
| Everything is wrong | Restore from `01-site-and-scripts-COMPLETE.tar.gz` on the Backup Plus drive |

The one-way door is **transferring the repository**. Do not do it. Collaborator
access does everything transfer does, and you can undo it.

---

## What she never gets, and why

| | |
|---|---|
| **cPanel** | The server, the live files, and the job applications — real people's dates of birth, salary history and referees |
| **Cloudflare / DNS** | A wrong record here kills company email, silently, and you find out days later through bounced messages |
| **Domain registrar** | Ownership of takwafoods.com |
| **Microsoft 365** | Company email |

The MX records must never be altered. Put that in writing before anyone else
touches DNS.

---

## Things worth telling her out loud

**Never use "Discard All Changes" in VS Code.** It permanently deletes
untracked files. That is exactly how `listing/_product-template.html`
disappeared once already and broke "Add a product".

**Files starting with `_` are tools, not clutter.** `_photo-backups/` is
load-bearing — `start.py` rebuilds pages from those pristine copies.

**Pushing does not publish.** Only your click in cPanel does.
