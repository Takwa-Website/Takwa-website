# Handover plan — every step

She edits and pushes. You deploy. She never gets cPanel, DNS, the domain
registrar or Microsoft 365.

`README.md` is her guide — send her that one. This file is yours.

**How to use this:** do it top to bottom. Every step says what to click and
what you should see afterwards. If what you see does not match, stop at that
step rather than carrying on.

---

## Already done

- [x] Full backup on the Backup Plus drive — 4.9 GB, verified
- [x] Repository restructured so the editing tools travel with the site
- [x] Company account created — **Takwa-Website**
- [x] Repository created and pushed — 339 files
- [x] `README.md` written for her

---

# PART 1 — Make the repository public

**Why:** cPanel cannot clone a private repository without an SSH key, and
cPanel's key generator will not create a usable one. Public removes the whole
problem.

**Is this safe?** Yes. `Georgeyoussef066/TakwaFoods-Website` has been public
since 2 August with the same code in it. Nothing becomes readable that was not
already readable. There are no passwords, tokens or keys in the repository —
the admin password is stored on the server as a hash, above the web root, and
never touches git.

### 1.1

- [ ] Go to **https://github.com/Takwa-Website/Takwa-website**
- [ ] If it says 404, you are signed in as the wrong account. Sign in as
      **Takwa-Website**, or open the link in a private window and sign in there.

### 1.2

- [ ] Click **Settings** — the tab on the far right of the row that starts
      Code, Issues, Pull requests
- [ ] You land on **General**

### 1.3

- [ ] Scroll to the very bottom, to the red-bordered box titled **Danger Zone**
- [ ] Find the row **Change repository visibility**
- [ ] Click **Change visibility**

### 1.4

- [ ] A dialog opens. Choose **Make public**
- [ ] Click **I want to make this repository public**
- [ ] It asks you to type the repository name to confirm. Type exactly:

      Takwa-Website/Takwa-website

- [ ] Click the final confirm button

### 1.5 — check

- [ ] The label next to the repository name at the top now reads **Public**,
      not Private
- [ ] Open a **private browsing window**, go to the repository URL, and confirm
      you can see the files while signed out

That last check is the one that matters. If a signed-out browser can see it,
so can cPanel.

---

# PART 2 — Point cPanel at the new repository

### 2.1 — Sign in

- [ ] Open cPanel and sign in
- [ ] Confirm you are on the **takwafood** account

### 2.2 — Find Git Version Control

- [ ] Use the search box at the top of cPanel and type `git`
- [ ] Click **Git™ Version Control** under the Files section

You should see one existing entry, the old `TakwaFoods-Website` repository.

### 2.3 — Read the old entry, change nothing

- [ ] Click **Manage** on the old `TakwaFoods-Website` entry
- [ ] Note its **Repository Path** and **Clone URL** — a photo on your phone is
      fine

**Look carefully at the Repository Path:**

- If it is something like `/home/takwafood/TakwaFoods-Website`, that is normal.
  Carry on.
- If it says `/home/takwafood/public_html`, **stop and say so.** That would
  mean the repository *is* the live website rather than a working copy, and the
  rest of Part 2 needs rethinking.

- [ ] Go back without changing anything

### 2.4 — Do NOT remove the old entry

Leave it exactly where it is.

cPanel allows several repositories at once, and they are independent — only the
one you click Deploy on does anything. Keeping the old entry costs nothing and
buys a free way back: if the new repository misbehaves, the old one is still
sitting there fully configured, and you deploy from it instead.

Remove it in Part 9, weeks later, once the new arrangement has proven itself.
Never as part of setting this up.

- [ ] Old entry left alone

### 2.5 — Create the new entry

- [ ] Back on the Git Version Control page, click **Create**
- [ ] Turn the **Clone a Repository** toggle **ON**

Then fill in three fields:

**Clone URL**

      https://github.com/Takwa-Website/Takwa-website.git

- [ ] Note the `.git` on the end. Include it.

**Repository Path**

      /home/takwafood/takwa-website

- [ ] **This must NOT be `public_html`.** This is cPanel's working copy. The
      deploy script reads from here and copies into `public_html`. Pointing it
      at `public_html` would publish the entire repository — including this
      plan — on the open internet.
- [ ] The folder must not already exist. If cPanel complains that it does,
      pick `/home/takwafood/takwa-website-2` instead.

**Repository Name**

      Takwa Website

- [ ] Anything readable. This is only a label in the cPanel list.

### 2.6

- [ ] Click **Create**
- [ ] Wait. Cloning 339 files takes a few seconds to a minute.

### 2.7 — check

- [ ] The new repository appears in the list
- [ ] It shows branch **main**
- [ ] It shows the last commit — the message will mention the handover

If cloning fails with an authentication or "not found" error, Part 1 did not
take effect. Go back and redo step 1.5.

---

# PART 3 — Deploy

### 3.1

- [ ] Click **Manage** on the new repository
- [ ] Open the **Pull or Deploy** tab

### 3.2

- [ ] Click **Update from Remote**
- [ ] Wait for it to report success

This fetches the latest commit from GitHub into cPanel's working copy. It does
not touch the live site yet.

### 3.3

- [ ] Click **Deploy HEAD Commit**
- [ ] Wait for it to report success

**This is the moment the live site changes.** The deploy reads `.cpanel.yml`
at the repository root and copies the website into `public_html`.

### 3.4 — if it says deployment is not available

The button is greyed out or complains when `.cpanel.yml` is missing or the
repository is not on a branch. Check that step 2.7 showed branch `main`.

---

# PART 4 — Check the site properly

Do not just glance at the home page. The deploy paths changed with the
restructure, and this is the first time the new version runs for real.

### 4.1 — These must LOAD

- [ ] `takwafoods.com` — home page, looks normal
- [ ] `takwafoods.com/index-ar.html` — Arabic, reads right-to-left
- [ ] `takwafoods.com/listings.html` — products, all cards the same height
- [ ] `takwafoods.com/about-us.html` — the years counter is running
- [ ] `takwafoods.com/contact-us.html` — the WhatsApp and phone icons are
      visible against their green circles
- [ ] `takwafoods.com/apply.html` — the application form, five steps
- [ ] Any single product page from the listings

If a page 404s, note **which one** and stop.

### 4.2 — These must NOT load

Three files were being published by mistake. This is how you confirm today's
fix actually shipped. Each should give a 403 or 404.

- [ ] `takwafoods.com/_photo-index.html`
- [ ] `takwafoods.com/listing/_product-template.html`
- [ ] `takwafoods.com/uploads/share/_flavora-cafe-og.jpg.bak`

If any of those three **do** load, stop and tell me.

### 4.3 — The share picture

- [ ] Send `takwafoods.com` to yourself in a WhatsApp chat

The preview should show the **factory entrance**, not the Flavora Café counter.

If it still shows the café, that is WhatsApp's cache, **not** a broken deploy —
the file on the server is correct. It clears on its own in days. Tell me if you
want it forced immediately.

---

# PART 5 — Set the admin password

**Do this the same day.** `/admin/` has no password set, and the first person
to open it sets it. That includes a stranger who guesses the URL.

### 5.1

- [ ] Go to `takwafoods.com/admin/`
- [ ] You get a setup screen asking you to choose a password
- [ ] Choose a strong one and save it in a password manager immediately

**Only a bcrypt hash is stored**, in a file above the web root. Nobody can
recover the password later — not you, not me. If it is lost, that file has to
be deleted on the server to bring the setup screen back.

### 5.2 — check

- [ ] Open `takwafoods.com/admin/` in a private window
- [ ] It asks for the password rather than letting you in

---

# PART 6 — Bring her in

None of this is blocked by the parts above, and none of it can affect the live
site.

### 6.1 — She creates her own account

- [ ] She signs up at **github.com** with her own email
- [ ] She sends you her **username**

**Do not sign your account into her VS Code.** Collaborator access lets her
push as herself, shows her name on every commit, and you revoke it in one
click. Sharing the account cannot be undone without changing your password.

### 6.2 — You add her

- [ ] Repository → **Settings** → **Collaborators and teams** in the left
      sidebar
- [ ] Click **Add people**
- [ ] Type her username, select her from the list
- [ ] Choose role **Write** — not Admin. She needs to push, not to change
      settings or add other people.
- [ ] Click **Add**

### 6.3 — She accepts

- [ ] She gets an email invitation and clicks the link, or opens the repository
      URL and clicks **Accept invitation**
- [ ] In your Collaborators list she changes from *Pending* to a normal entry

Until she accepts, she cannot clone.

---

# PART 7 — Her setup

Send her `README.md`. This is what she does, once.

### 7.1 — Install

- [ ] **Git** — git-scm.com
- [ ] **Python 3** — python.org. On Windows, tick **"Add Python to PATH"**
      during install
- [ ] **VS Code** — code.visualstudio.com

### 7.2 — One library

In a terminal:

```bash
pip install Pillow
```

This is the only non-standard dependency. Everything else `start.py` uses ships
with Python.

### 7.3 — Clone

- [ ] Open VS Code
- [ ] **Source Control** in the left bar → **Clone Repository**
- [ ] Paste:

      https://github.com/Takwa-Website/Takwa-website.git

- [ ] Choose a folder
- [ ] Sign in to GitHub when prompted — **as herself**
- [ ] Open the cloned folder

### 7.4 — Run it

In VS Code's terminal, from the project folder:

```bash
python3 start.py
```

On Windows that may be `python start.py`.

- [ ] Open **http://localhost:8099**
- [ ] The site loads

Stop the server with `Ctrl+C`.

### 7.5 — The two tools

- [ ] **http://localhost:8099/_photo-index.html** — every image on the site.
      Swap one and it changes everywhere it appears.
- [ ] **http://localhost:8099/_text-index-ar.html** — every Arabic string next
      to its English original.

---

# PART 8 — Her first change, all the way through

Do not consider the handover done until you have watched one change travel the
whole path.

### 8.1 — Her

- [ ] Fix a typo somewhere obvious
- [ ] Check it at localhost:8099
- [ ] **Check the Arabic version of the same page still matches**
- [ ] VS Code → Source Control → write a message → **Commit** → **Sync**
- [ ] Text you

### 8.2 — You

- [ ] cPanel → Git Version Control → **Manage** → **Update from Remote**
- [ ] **Deploy HEAD Commit**
- [ ] Open the page on takwafoods.com and confirm the change is there

### Why the Arabic check matters

Every `-ar.html` page is **generated** from its English original by
`build_arabic.py`. Editing English by hand without regenerating leaves the two
languages saying different things — no error, no warning, just a site that
contradicts itself. It is the quietest way this site can break, and the most
likely mistake for someone new.

---

# PART 9 — Clean up, only after Part 8 passes

- [ ] Remove the old cPanel Git entry — only now, with the new one proven. Its
      only purpose was to be your way back, and you no longer need one.
- [ ] Delete `.git-OLD-archive/` from
      `Takwafoods web/takwaweb.designersidhost.com/`
- [ ] Leave the old repository `Georgeyoussef066/TakwaFoods-Website` alone. It
      holds the previous 46 commits of history. **Archive** it, do not delete.
- [ ] Fix your git identity — commits are currently authored as
      `GeorgeYoueef066 / GeorgeYoueef066@gmail.com`, which is a typo:

      git config --global user.name "George Youssef"
      git config --global user.email "georgeyoussef055@gmail.com"

---

# If something goes wrong

| Problem | Fix |
|---|---|
| She should not have access any more | Settings → Collaborators → remove |
| A bad change went live | cPanel → deploy an earlier commit |
| The new repository broke deploys | The old cPanel entry is still there — open it and deploy from it instead |
| Everything is wrong | Restore `01-site-and-scripts-COMPLETE.tar.gz` from the Backup Plus drive |

Never **transfer** the repository to her. Collaborator access does the same job
and undoes in one click; a transfer cannot be reversed without her cooperation.

---

# What she never gets, and why

| | |
|---|---|
| **cPanel** | The server, and the job applications — real people's dates of birth, salary history, referees |
| **Cloudflare / DNS** | A wrong record kills company email silently; you find out days later through bounced messages |
| **Domain registrar** | Ownership of takwafoods.com |
| **Microsoft 365** | Company email |

The MX records must never be altered.

---

# Tell her these three things

**Never use "Discard All Changes" in VS Code.** It permanently deletes
untracked files with no undo. That is how `listing/_product-template.html` was
lost once already, which broke "Add a product" until it was recovered from git
history.

**Files starting with `_` are tools, not clutter.** `_photo-backups/` is
load-bearing — `start.py` rebuilds pages from those pristine copies. Delete it
and the editing tools stop working.

**Pushing does not publish.** The live site only changes when you click Deploy
in cPanel.

---

# Errors already hit, so you recognise them

**`Repository not found` on a URL you know is correct.** Two different causes,
same message.

*Wrong remote.* `git remote add` only **creates**. If `origin` already exists
it errors and changes nothing, so pushes keep going to the old URL even after
you think you fixed it. Check with `git remote -v`. Change it with:

      git remote set-url origin <url>

*Wrong account.* GitHub answers 404, never 403, for a private repository your
credential cannot see — it refuses to confirm the repository exists at all.
This machine uses `credential.helper store`, which keeps one credential for all
of github.com, and it was authenticating as `Georgeyoussef066`.

**Two GitHub accounts on one machine.** `credential.helper store` cannot hold
both. Either add one account as a collaborator on the other's repositories, or
install the GitHub CLI (`sudo apt install gh`, then `gh auth login`), which
handles multiple accounts properly.

**cPanel's SSH key form refuses an empty passphrase.** It demands one, and a
passphrase makes the key useless for automated deploys. This is why the plan
uses a public repository instead. If you ever need a private one, the way round
is cPanel's Terminal and `ssh-keygen` — ask me then.
