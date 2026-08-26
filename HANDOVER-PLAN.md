# Handover plan

Step by step, in order. Work top to bottom and tick as you go.

`README.md` is the *developer's* guide — give her that one. **This** file is
yours: the plan for getting her set up without giving away anything you should
keep.

**The split:** she edits and pushes. You deploy. She never gets cPanel, DNS,
the domain registrar or Microsoft 365. Nothing she can do will take the site
down or stop company email.

---

## Where you are now

**Done — repository is live and pushed.**

- [x] Full backup on the Backup Plus drive — 4.9 GB, verified
- [x] Repository restructured so the editing tools travel with the site
- [x] `.cpanel.yml` moved to the repo root, rehearsed against a test server
- [x] Two files that were leaking onto the live site fixed
- [x] `README.md` written for her
- [x] Company account created — **Takwa-Website**
- [x] Repository created — **Takwa-Website/Takwa-website**, set to **private**
- [x] Pushed: `dab70e4`, 339 files, in sync
- [x] Verified `website/`, `music/` and `other/` stayed out

**Next: Phase 1 below — cPanel.** The live site has NOT been deployed from the
new repository yet. Until it has, takwafoods.com is still running whatever the
old deploy left there.

---

## Why this order

Deploy before people. The site must be proven working from the new repository
*before* anyone else starts committing to it — otherwise, when something looks
wrong, you cannot tell whether it was the restructure or her first change.

So: cPanel, then verify, then bring her in.

---

## Phase 1 — Re-point cPanel

The repository is private, so cPanel cannot clone it over HTTPS. It needs an
SSH deploy key. This is the fiddliest part of the whole handover; everything
after it is easy.

### 1a. Make a key in cPanel

- [ ] cPanel → **SSH Access → Manage SSH Keys → Generate a New Key**
- [ ] Leave the **passphrase empty** — cPanel cannot type one during an
      automated clone, and a key with a passphrase will simply fail
- [ ] **Manage** the new key → **Authorize** it
- [ ] **View/Download** the *public* key and copy the whole line

### 1b. Give that key read access

- [ ] GitHub → repo → **Settings → Deploy keys → Add deploy key**
- [ ] Paste the public key, title it `cPanel`
- [ ] **Leave "Allow write access" unticked.** cPanel only ever reads.

A deploy key is scoped to this one repository. It is not an account, and it
cannot reach anything else you own — which is exactly why it is the right tool
here rather than a personal token.

### 1c. Remove the old entry

- [ ] cPanel → **Git Version Control** → the existing `TakwaFoods-Website`
      entry → **Remove**

This deletes only cPanel's own working copy. **Your live site is untouched** —
`public_html` is a separate directory that deploys copy *into*.

### 1d. Create the new one

- [ ] Git Version Control → **Create**
- [ ] Clone URL — the **SSH** form, not HTTPS:

      git@github.com:Takwa-Website/Takwa-website.git

- [ ] Repository path: something like `/home/takwafood/takwa-website`

**That path is cPanel's working copy, not the website.** It must NOT be
`public_html`. The deploy script reads from the working copy and copies into
`public_html`. Pointing it at `public_html` would put the whole repository,
including this plan, on the public internet.

- [ ] cPanel clones successfully

---

## Phase 2 — Deploy, and check it properly

This is the first time the restructured deploy runs for real. The paths
changed: cPanel now holds the whole `Takwa` folder, and `.cpanel.yml` at its
root reaches into the site subfolder through `$SRC`. I rehearsed this against
a stand-in server — 16 pages, 19 product pages, 92 uploads, no leaks — but
rehearsal is not the real thing. Check properly rather than glancing at the
home page.

- [ ] Git Version Control → **Update from Remote**
- [ ] **Deploy HEAD Commit**

### These must load

- [ ] `takwafoods.com` — home page, looks normal
- [ ] `takwafoods.com/index-ar.html` — Arabic version
- [ ] `takwafoods.com/listings.html` — products, all aligned
- [ ] any single product page
- [ ] `takwafoods.com/apply.html` — the application form
- [ ] `takwafoods.com/contact-us.html`

### These must FAIL

These three were being published and should not have been. This is how you
confirm the fix actually shipped.

- [ ] `takwafoods.com/_photo-index.html`
- [ ] `takwafoods.com/listing/_product-template.html`
- [ ] `takwafoods.com/uploads/share/_flavora-cafe-og.jpg.bak`

If any of those three load, stop and say so.

### And one to look at

- [ ] Share `takwafoods.com` into a WhatsApp chat with yourself

The preview should show the factory entrance, not the Flavora Café counter. If
it still shows the café, that is WhatsApp's cache, not a broken deploy — the
file is correct. It clears on its own, or we rename the image to force it.

---

## Phase 3 — Set the admin password today

`/admin/` has **no password set**. The first person to open it sets it and
owns it — including a stranger who guesses the URL.

- [ ] Open `takwafoods.com/admin/`
- [ ] Set a strong password
- [ ] Store it in a password manager

Only a bcrypt hash is kept, in a file above the web root. **Nobody can recover
it later — not you, not me.** If it is lost, that file has to be deleted on the
server to bring the setup screen back.

---

## Phase 4 — Bring her in

Only now, with the site proven working from the new repository.

She needs **her own free GitHub account**. Not yours.

- [ ] She creates her account and sends you the username
- [ ] Repo → **Settings → Collaborators and teams → Add people**
- [ ] Add her username, permission **Write**
- [ ] She accepts the emailed invitation

Write, not Admin. She needs to push, not to change repository settings or add
other people.

**Do not sign your GitHub account into her VS Code.** It hands her the account
itself, every commit appears to be yours, and the only way to undo it is
changing your password. Collaborator access is revokable in one click.

---

## Phase 5 — Her setup

Send her `README.md`. She needs Python 3 and Git, then:

```bash
pip install Pillow
```

- [ ] She clones the repository in VS Code
- [ ] She runs `python3 start.py`
- [ ] She opens `http://localhost:8099` and sees the site
- [ ] She opens `/_photo-index.html` and `/_text-index-ar.html`

---

## Phase 6 — One change end to end, before you trust it

Do not consider the handover done until **she**, on her machine, has:

- [ ] Made a small visible change — a typo fix somewhere obvious
- [ ] Checked it at localhost:8099
- [ ] Checked the **Arabic** version of the same page still matches
- [ ] Committed and pushed
- [ ] Texted you

And then **you**:

- [ ] Update from Remote → Deploy HEAD Commit
- [ ] Confirmed the change is live on takwafoods.com

That Arabic check matters more than it looks. The `-ar.html` pages are
*generated* from the English by `build_arabic.py`. Someone editing English by
hand without regenerating leaves the two languages saying different things,
with no error and no warning. It is the most likely way a newcomer quietly
damages this site.

---

## Phase 7 — Clean up, only after Phase 6 passes

- [ ] Delete `.git-OLD-archive/` from
      `Takwafoods web/takwaweb.designersidhost.com/`
- [ ] Leave the old GitHub repo `Georgeyoussef066/TakwaFoods-Website` alone —
      it holds the previous 46 commits of history. Archive it, do not delete it.
- [ ] Fix your git identity if you care about tidy history — commits are
      currently authored as `GeorgeYoueef066 / GeorgeYoueef066@gmail.com`,
      which is a typo and does not match your real address:

      git config --global user.name "George Youssef"
      git config --global user.email "georgeyoussef055@gmail.com"

---

## Troubleshooting

Problems actually hit while doing this, and what fixed them.

**`Repository not found` on a URL you know is right**

Two different causes, same message.

*Wrong remote.* `git remote add` only *creates*. If `origin` already exists it
errors and changes nothing, so pushes keep going to the old URL even after you
think you fixed it. Check with `git remote -v`, and change it with:

    git remote set-url origin <url>

*Wrong account.* GitHub returns 404, never 403, for a private repo your account
cannot see — it refuses to confirm the repo exists at all. Your machine uses
`credential.helper store`, which keeps **one** credential for all of
github.com, and it was authenticating as `Georgeyoussef066`. Fixed by adding
that account as a collaborator on the new repo.

To clear a stored credential and be prompted fresh:

    git credential reject <<< "protocol=https
    host=github.com
    "

Then paste a **personal access token** as the password — GitHub no longer
accepts account passwords for git. Never put a token in the remote URL; it
lands in plain text in `.git/config`.

**Two GitHub accounts on one machine**

`credential.helper store` cannot hold both. Either add one account as a
collaborator on the other's repos, or install the GitHub CLI
(`sudo apt install gh`, then `gh auth login`), which handles this properly.

**cPanel clone fails on a private repo**

HTTPS will not work. Use the SSH URL and a deploy key — Phase 1.

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
