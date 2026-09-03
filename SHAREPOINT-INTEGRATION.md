# Sending applications to a SharePoint list

Every time someone submits the employment form on takwafoods.com, a new item
appears in a SharePoint list.

Nothing here is built yet. This is the plan.

---

## How it works

    apply.html -> apply-submit.php -> file on the server   (already exists)
                                  \
                                   -> Microsoft Graph -> SharePoint list

The website talks to Microsoft directly. No Power Automate, no environment, no
premium licence, no monthly cost.

**Power Automate was the original plan and has been dropped.** Your tenant has
no Power Platform environment, and the trigger it needed was a premium
connector, so it was always going to be a monthly bill. This route uses only
what you already pay for.

---

## The rule that governs the whole design

**A failure to reach SharePoint must never fail the application.**

Someone who has spent twenty minutes on nine sections must not see an error
because Microsoft timed out. So the SharePoint call happens *after* the
application is safely written to disk, its result is ignored, and failures go
to a log for you rather than to the applicant.

Without this, an outage at Microsoft becomes an outage in your hiring.

**The file on the server stays.** `/admin/` remains the source of truth.
SharePoint is an addition, never a replacement — delete one config file and the
whole thing switches off with no code change.

---

## What you will end up with

Five values, stored in one file above the web root:

| | Where it comes from |
|---|---|
| Tenant ID | app registration |
| Client ID | app registration |
| Client secret | app registration |
| Site ID | Graph Explorer |
| List ID | Graph Explorer |

Then roughly seventy lines of PHP that I write and test.

---

# PART 1 — Create the SharePoint list

The form collects **103 fields**. A 103-column list would be unusable — nobody
sorts by `cert3_expires`. So: **13 real columns** for what you search and
filter on, plus one holding the complete application as text.

### 1.1 — The list

- [ ] Go to the SharePoint site this should live on. If there is none, create
      one: **SharePoint → Create site → Team site**, named `HR`
- [ ] **Write down the site URL.** You need it in Part 3. It looks like
      `https://takwafoods.sharepoint.com/sites/HR`
- [ ] In that site: **New → List → Blank list**
- [ ] Name it exactly **`Job Applications`**

### 1.2 — The columns

Add each of these with **+ Add column**.

| Column name | Type |
|---|---|
| `Position` | Single line of text |
| `Email` | Single line of text |
| `Mobile` | Single line of text |
| `Nationality` | Single line of text |
| `EmploymentType` | Single line of text |
| `AvailableFrom` | Single line of text |
| `ExpectedSalary` | Single line of text |
| `VacancyRef` | Single line of text |
| `HeardVia` | Single line of text |
| `ReceivedUTC` | Date and Time |
| `Status` | Choice |
| `FullApplication` | Multiple lines of text |

`Title` already exists — the applicant's name goes there.

**Type the names exactly as written, with no spaces.** SharePoint turns a space
in a column name into `_x0020_` in the internal name that Graph uses, and
renaming a column later does not change its internal name. Both cause
confusing breakage.

- [ ] For `Status`, choose **Choice** with options: New, Screening, Interview,
      Offer, Rejected, Withdrawn. Default **New**.
- [ ] For `FullApplication`, set it to **plain text**, not rich text. Rich text
      mangles line breaks.
- [ ] `AvailableFrom` is text, not a date — the form lets people type
      "Immediately" or "1 month notice".

### 1.3 — Tidy up

- [ ] Hide `FullApplication` from the default view. It is long and makes the
      list unreadable. It still shows when you open an item.
- [ ] Sort the view by `ReceivedUTC`, newest first

### 1.4 — Permissions

- [ ] Restrict the list to whoever should see applications

This will hold dates of birth, salary history and referees' contact details.
Do not leave it open to everyone in the company.

---

# PART 2 — Register the application

This creates the identity the website uses to talk to Microsoft.

### 2.1 — Create it

- [ ] Go to **https://entra.microsoft.com**
- [ ] **Applications → App registrations → New registration**
- [ ] Name: `Takwa Website Applications`
- [ ] Supported account types: **Accounts in this organizational directory
      only (Single tenant)**
- [ ] Leave Redirect URI empty — the website never signs a person in
- [ ] **Register**

### 2.2 — Copy two values

On the overview page that appears:

- [ ] **Application (client) ID** — copy it
- [ ] **Directory (tenant) ID** — copy it

Keep them somewhere safe. Neither is secret on its own, but you need both.

### 2.3 — Create the secret

- [ ] **Certificates & secrets → Client secrets → New client secret**
- [ ] Description: `takwafoods.com web server`
- [ ] Expires: **24 months** — the longest offered
- [ ] **Add**

- [ ] Copy the **Value** column immediately

**The Value is shown once.** Navigate away and it is gone forever, and you have
to make a new one. Do not copy the "Secret ID" — that is not it.

- [ ] **Put a reminder in your calendar two months before it expires.**

When this secret expires, applications silently stop reaching SharePoint. The
form keeps working, `/admin/` keeps working, and nothing tells you. It is the
single most likely reason this breaks a year from now.

### 2.4 — Permissions

- [ ] **API permissions → Add a permission → Microsoft Graph →
      Application permissions**
- [ ] Search for and tick **`Sites.Selected`**
- [ ] **Add permissions**
- [ ] Click **Grant admin consent for <your tenant>** and confirm

**Why `Sites.Selected` and not `Sites.ReadWrite.All`:** the alternative gives
this app write access to *every* SharePoint site in the company. The secret
will be sitting on a shared web host. If that host is ever compromised, the
difference is between losing one HR list and losing everything in SharePoint.

`Sites.Selected` grants nothing by default. Part 3 gives it access to exactly
one site.

---

# PART 3 — Point the app at your site

Three lookups in Microsoft's own browser tool. No install.

- [ ] Go to **https://developer.microsoft.com/graph/graph-explorer**
- [ ] Sign in, top left, with your admin account
- [ ] Consent when prompted

### 3.1 — Find the site ID

- [ ] Method **GET**, and this URL, with your own site path:

```
https://graph.microsoft.com/v1.0/sites/takwafoods.sharepoint.com:/sites/HR
```

- [ ] **Run query**
- [ ] In the response, copy the **`id`** field

It is a long comma-separated string like
`takwafoods.sharepoint.com,8f1c…,3b7a…`. **Copy the whole thing, commas
included.**

If you get a 404, the site path is wrong. It is the part of your site URL after
`/sites/`.

### 3.2 — Grant the app access to that one site

- [ ] Method **POST**
- [ ] URL — paste your site ID where shown:

```
https://graph.microsoft.com/v1.0/sites/{SITE-ID}/permissions
```

- [ ] Request body tab, and paste this with your own client ID and app name:

```json
{
  "roles": ["write"],
  "grantedToIdentities": [{
    "application": {
      "id": "YOUR-CLIENT-ID",
      "displayName": "Takwa Website Applications"
    }
  }]
}
```

- [ ] **Run query**
- [ ] You should get **201 Created**

If it fails with "Access denied", Graph Explorer needs the consent from 2.4 to
have gone through, and your account needs to be a SharePoint admin.

### 3.3 — Find the list ID

- [ ] Method **GET**:

```
https://graph.microsoft.com/v1.0/sites/{SITE-ID}/lists
```

- [ ] **Run query**
- [ ] Find the entry whose `displayName` is `Job Applications`
- [ ] Copy its **`id`** — a plain GUID

---

# PART 4 — Put the settings on the server

The secret must not go in the repository. The repository is **public**, and a
public repository is the one place a client secret must never be.

### 4.1

- [ ] cPanel → **File Manager**
- [ ] Go to `/home/takwafood/` — the folder **containing** `public_html`
- [ ] Create a file named `takwa-sharepoint-config.php`
- [ ] Contents, with your five values:

```php
<?php
return [
    'tenant_id'     => 'PASTE-DIRECTORY-TENANT-ID',
    'client_id'     => 'PASTE-APPLICATION-CLIENT-ID',
    'client_secret' => 'PASTE-THE-SECRET-VALUE',
    'site_id'       => 'PASTE-SITE-ID-INCLUDING-COMMAS',
    'list_id'       => 'PASTE-LIST-ID',
];
```

- [ ] Set its permissions to **600**

Same folder as `takwa-admin-config.php`, for the same reason: no URL can reach
it, and no deploy overwrites it.

### 4.2 — Check the site can reach Microsoft

Some shared hosts block outbound connections. Worth knowing before we write
code that depends on it.

- [ ] In cPanel → Terminal, if you have it:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://graph.microsoft.com/v1.0/
```

Anything other than `000` means outbound HTTPS works. If you have no Terminal,
tell me and I will write a one-page test script instead.

---

# PART 5 — The code

I write this once you have finished Parts 1 to 4. Shape of it:

- Runs **after** the application is written to disk and the email is sent
- Reads the config; if the file is missing, does nothing at all and carries on
- Gets a token from
  `login.microsoftonline.com/{tenant}/oauth2/v2.0/token` using
  `client_credentials` and scope `https://graph.microsoft.com/.default`
- POSTs to
  `graph.microsoft.com/v1.0/sites/{site}/lists/{list}/items`
- Builds `FullApplication` as readable lines from all 103 fields
- **10 second timeout**, result **ignored**
- Failures append one line to a log outside the web root

It will use `curl` where available and fall back to a stream context where it
is not — the development machine here has no `curl` extension and I would
rather the code not care.

### What does not change

- [ ] Applications still written to `/home/takwafood/takwa-applications`
- [ ] `/admin/` still works exactly as now
- [ ] The notification email to `info@` still goes
- [ ] The form, its five steps and its validation are untouched

---

# PART 6 — Test

### 6.1 — Before touching the website

I will give you a small script that reads the config and creates one test item.
Run it first. Debugging the Microsoft side alone is far easier than debugging
it together with the website.

- [ ] Test item appears in the SharePoint list

Common failures at this point:

| Error | Meaning |
|---|---|
| `invalid_client` | Wrong secret, or you copied the Secret ID instead of the Value |
| `403 accessDenied` | Part 3.2 did not take — the app has no access to the site |
| `404 itemNotFound` | Site ID or list ID wrong |
| `400` naming a field | A column name does not match, often a space turned into `_x0020_` |

### 6.2 — End to end

- [ ] Submit a real application at `takwafoods.com/apply.html` with obviously
      fake details
- [ ] The thank-you message appears
- [ ] The item appears in SharePoint within a few seconds
- [ ] It also appears in `takwafoods.com/admin/`
- [ ] Delete the test item and the test file afterwards

### 6.3 — Test the failure path

The test people skip, and the one that matters.

- [ ] Temporarily rename `takwa-sharepoint-config.php` to break the connection
- [ ] Submit another test application
- [ ] The applicant **still sees the thank-you message**
- [ ] It still appears in `/admin/`
- [ ] Rename the file back

If the applicant saw an error, it does not go live. A hiring form that breaks
when Microsoft hiccups is worse than no SharePoint at all.

---

# PART 7 — After it is running

- [ ] **Calendar reminder for the secret**, two months before its 24-month
      expiry. This is the one thing that will definitely break eventually.
- [ ] Note in the list description where the data comes from, so whoever
      inherits it knows
- [ ] Decide retention. Applications now live in **two** places — the server
      and SharePoint — and both need clearing when the period in your
      recruitment privacy notice ends.

---

## Data protection

The form tells applicants their data "is not disclosed to any third party
without your consent, save where required by law."

SharePoint does **not** break that promise. Microsoft is your data processor,
not a third party receiving a disclosure, and your email already runs through
the same tenant. No new company gets access.

Two things do change, and both are on you:

**The data lives in two places.** An erasure request means deleting from the
server *and* from SharePoint. Whoever handles those requests must know.

**More people can see it.** `/admin/` is behind one password. A SharePoint list
is visible to everyone with site access, usually more people than you think.
Set the permissions in 1.4 deliberately.

---

## If it stops working later

| Symptom | Likely cause |
|---|---|
| Items stopped appearing, form still fine | **The client secret expired.** Check this first — it is the most likely cause by a wide margin. |
| `403` in the log | Site permission from 3.2 was removed, or the app registration was deleted |
| Nothing in the log at all | The website cannot reach Microsoft — host blocking outbound HTTPS |
| Items appear with fields missing | A column was renamed in SharePoint. Internal names do not follow renames. |

None of these affect the applications on the server. `/admin/` is always the
source of truth, which is the entire point of keeping it.

---

## What I need from you

Work through Parts 1 to 4, then send me:

1. Confirmation the list exists with those exact column names
2. That Part 3.2 returned **201**
3. The result of the outbound check in 4.2

**Do not send me the client secret.** It goes in the file on the server and
nowhere else. I never need to see it — the code reads it from disk.
