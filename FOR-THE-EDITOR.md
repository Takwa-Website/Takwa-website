# Editing the Takwa website

Everything you need, in one page. No coding.

---

## Setting up, once

You need two free programs first. Install both, then run the setup file.

### 1. Git

**https://git-scm.com/download/win**

Download, run it, click **Next** on every screen. Nothing to decide.

You will never open Git. It works quietly in the background when you press
Publish.

### 2. Python

**https://www.python.org/downloads/**

Click the big yellow **Download Python** button.

**On the first screen of the installer, tick "Add python.exe to PATH"** before
clicking Install. It is a small box at the bottom and it is easy to miss — if
setup later says Python is not installed, this box is why. You can fix it by
running the installer again and ticking it.

### 3. Run the setup file

Double-click **`setup.bat`** — the file George sent you.

It downloads the website, checks both programs, and puts a **Takwa Website
Editor** icon on your desktop. It takes a minute or two.

You only ever do this once.

---

## Every day after that

**Double-click "Takwa Website Editor" on your desktop.**

Your browser opens with the website running on your own computer. Nothing you
do here can affect the real takwafoods.com until you publish and George
deploys.

---

## What you can change

Four tools, linked from the page that opens.

| | |
|---|---|
| **Photos** | Every image on the site. Swap one and it changes everywhere it is used. |
| **Arabic text** | Every Arabic phrase beside its English original. |
| **Add a product** | Creates the product page, its card, and its Arabic version. |
| **Add news** | Creates the article, puts it at the top of Blog & Events, and makes the Arabic version. |

For news, write **one paragraph per line**.

---

## Publishing

A dark bar sits along the bottom of every editing page. It tells you how many
changes are waiting.

- **See what changed** — lists them in plain words before you send anything
- **Publish** — sends your work to George

It asks for a short note about what you changed. Anything sensible is fine:
"added September news", "new coffee photos".

**Publishing does not put anything on takwafoods.com.** It sends your work to
George. He puts it on the live site. So there is no way to accidentally publish
a mistake to the public — and equally, nothing appears online until you tell
him.

**So: publish, then message George.**

---

## Things worth knowing

**Arabic pages are made automatically, but they start in English.** When you add
a product or a news item, the Arabic version is created for you with the
English words still in it. Open the Arabic text tool afterwards and translate
it. If you skip this, the site says different things in each language.

**Never use "Discard All Changes"** if you ever open VS Code or another Git
tool. It permanently deletes work with no undo.

**Files and folders starting with `_` are part of the machinery.** They look
like clutter. They are not. Leave them alone.

**If you close the browser, the tools keep running.** Double-click the desktop
icon again to get back to them. To stop them properly, run
`takwa-tools-stop.bat` in the website folder.

---

## If something goes wrong

| What you see | What it means |
|---|---|
| "Python is not installed" | The PATH box was not ticked. Run the Python installer again and tick it. |
| "Git is not installed" | Install Git from the link above, then run setup again. |
| "GitHub would not accept it" | Sign in to GitHub when prompted, then press Publish again. Your work is safe on your computer. |
| "Someone else changed the website" | George changed something too. Your work is safe — message him rather than pressing Publish again. |
| The page will not load | Double-click the desktop icon again. |

Nothing you do in these tools can break the live website. The worst case is
that your work stays on your computer until someone helps you send it.
