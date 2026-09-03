# Sending applications to a SharePoint list

Every time someone submits the employment form on takwafoods.com, a new item
appears in a SharePoint list.

Nothing here is built yet. This is the plan.

---

## How it works, in one line

The form already saves each application to a file on the server. We add one
extra step: after saving, the server also sends the application to a Power
Automate flow, and the flow creates the SharePoint list item.

    apply.html  ->  apply-submit.php  ->  file on the server  (already exists)
                                      \
                                       ->  Power Automate  ->  SharePoint list

**The file on the server stays.** It is the record of last resort. If
SharePoint, Power Automate or the internet is having a bad day, the application
is still safely on disk and nothing is lost.

---

## The rule that governs the whole design

**A failure to reach SharePoint must never fail the application.**

An applicant who has spent twenty minutes filling in nine sections must not see
an error because a Microsoft service timed out. So the SharePoint call happens
*after* the application is safely written to disk, its result is ignored, and
any failure is written to a log for you rather than shown to them.

This is not optional politeness. Without it, an outage at Microsoft becomes an
outage in your hiring.

---

## Decide this first: which route

Three ways to get data from the website into SharePoint. They differ mostly in
cost and setup effort.

### Route A — Power Automate (recommended)

The website posts to a flow. The flow writes to SharePoint.

**Good:** almost no code on the website — about fifteen lines. Everything else
is drag-and-drop. When you want to add a column later, you change the flow, not
the website. You can add email alerts, Teams messages or approvals to the same
flow with no code at all.

**Catch:** the trigger it needs — *When an HTTP request is received* — is a
**premium** Power Automate connector. It is not in the Power Automate included
with a normal Microsoft 365 business licence. You would need a Power Automate
Premium licence, or the cheaper per-flow plan.

**Check before committing:** open **make.powerautomate.com**, create a new
instant cloud flow, and search the triggers for *When an HTTP request is
received*. If it appears without a diamond or "Premium" tag, you already have
it. If it is tagged premium, that is a monthly cost.

### Route B — Microsoft Graph, direct from the website

The website talks to Microsoft's API itself and creates the list item.

**Good:** no extra licence. Uses what you already pay for.

**Catch:** real setup. An app registration in Entra ID, a client secret, and
more code on the website. The secret **expires** — 24 months at most — and when
it does, applications silently stop reaching SharePoint until someone renews
it. That is a maintenance obligation you will forget about, so it needs a
calendar reminder.

### Route C — email-triggered flow

The website already emails `info@takwafoods.com` when an application arrives.
A free flow could watch that mailbox and create the list item from the email.

**Good:** free, and no app registration.

**Catch:** to build a useful list item, the email would have to carry the whole
application — and the current design deliberately keeps applicants' personal
data out of email. It also breaks the moment someone edits the email template.

### Recommendation

**Route A if the premium connector is available or affordable.** It is by far
the easiest to live with, and the one you can maintain yourself.

**Route B if not.** Same result, no extra cost, more setup and a secret to
renew. Tell me and I will write out those steps in the same detail.

The rest of this document assumes **Route A**.

---

## The SharePoint list design

The form collects **103 fields**. A list with 103 columns would be unusable —
SharePoint's own view editor would fight you, and nobody sorts by
`cert3_expires`.

So the list gets **13 real columns**, the things you actually search, sort and
filter by, plus **one column holding the complete application** as text. You
see a clean list; you open an item to read everything.

### Columns to create

| Column name | Type | Notes |
|---|---|---|
| `Title` | Single line of text | Already exists. We put the applicant's full name here. |
| `Position` | Single line of text | What they applied for |
| `Email` | Single line of text | |
| `Mobile` | Single line of text | |
| `Nationality` | Single line of text | |
| `EmploymentType` | Single line of text | Full time, part time, etc |
| `AvailableFrom` | Single line of text | Free text on the form, so not a date column |
| `ExpectedSalary` | Single line of text | |
| `VacancyRef` | Single line of text | Which vacancy, if given |
| `HeardVia` | Single line of text | Where they saw it |
| `ReceivedUTC` | Date and Time | When it arrived |
| `Status` | Choice | New / Screening / Interview / Offer / Rejected / Withdrawn. Default **New**. |
| `FullApplication` | Multiple lines of text, **plain text** | Everything else, formatted as readable lines |

Use exactly these internal names. The flow refers to them, and renaming a
column later does not change its internal name — which causes confusing
breakage.

**Set `FullApplication` to plain text, not rich text.** Rich text mangles line
breaks and makes the content painful to read.

---

# PART 1 — Create the SharePoint list

### 1.1

- [ ] Go to the SharePoint site where this should live
- [ ] If there is no suitable site, create one first: **SharePoint → Create
      site → Team site**, named something like `HR`

### 1.2

- [ ] **New → List → Blank list**
- [ ] Name it **`Job Applications`**
- [ ] Create

### 1.3 — Add the columns

For each row in the table above except `Title` (which already exists):

- [ ] Click **+ Add column**
- [ ] Choose the type from the table
- [ ] Type the name **exactly** as written
- [ ] Save

For `Status`, choose **Choice** and enter the six options, then set the default
to **New**.

### 1.4 — Tidy the default view

- [ ] Hide `FullApplication` from the main view — it is long and makes the list
      unreadable. It still shows when you open an item.
- [ ] Sort by `ReceivedUTC`, newest first

### 1.5 — Permissions

- [ ] Restrict the list to whoever should see applications

This list will contain dates of birth, salary history and referees' contact
details. Do not leave it open to everyone in the company.

---

# PART 2 — Build the flow

### 2.1

- [ ] Go to **make.powerautomate.com**
- [ ] Confirm the environment, top right, is your company tenant
- [ ] **Create → Instant cloud flow**
- [ ] Name it `Takwa website application to SharePoint`
- [ ] Choose the trigger **When an HTTP request is received**
- [ ] Create

### 2.2 — Tell the trigger what to expect

- [ ] Open the trigger
- [ ] Click **Use sample payload to generate schema**
- [ ] Paste this and click Done:

```json
{
  "full_name": "Sample Name",
  "position": "Sample Position",
  "email": "sample@example.com",
  "mobile": "+963000000000",
  "nationality": "Syrian",
  "employment_type": "Full time",
  "start_date": "Immediately",
  "expected_salary": "Negotiable",
  "vacancy_ref": "REF-1",
  "vacancy_source": "Website",
  "received_utc": "2026-01-01T00:00:00Z",
  "full_application": "Line one\nLine two",
  "shared_secret": "replace-me"
}
```

### 2.3 — Reject anything that is not from your website

The trigger URL is long and secret, but a URL is not authentication. Add a
check so a leaked URL alone cannot fill your list with rubbish.

- [ ] **+ New step → Control → Condition**
- [ ] Left side: the `shared_secret` field from the trigger
- [ ] Operator: **is equal to**
- [ ] Right side: type a long random string — make one up, 40+ characters, no
      spaces. **Write it down; you need it again in Part 3.**

Everything else goes in the **If yes** branch.

- [ ] In the **If no** branch: **Response**, status code **401**

### 2.4 — Create the item

Inside **If yes**:

- [ ] **+ Add an action → SharePoint → Create item**
- [ ] **Site Address:** the site holding your list
- [ ] **List Name:** `Job Applications`

Map the fields:

| SharePoint column | Value from the trigger |
|---|---|
| Title | `full_name` |
| Position | `position` |
| Email | `email` |
| Mobile | `mobile` |
| Nationality | `nationality` |
| EmploymentType | `employment_type` |
| AvailableFrom | `start_date` |
| ExpectedSalary | `expected_salary` |
| VacancyRef | `vacancy_ref` |
| HeardVia | `vacancy_source` |
| ReceivedUTC | `received_utc` |
| FullApplication | `full_application` |

Leave `Status` alone — the default handles it.

### 2.5 — Answer the website

Still inside **If yes**, after Create item:

- [ ] **+ Add an action → Response**
- [ ] Status code **200**

### 2.6 — Save and copy the URL

- [ ] **Save**
- [ ] Reopen the trigger. The **HTTP POST URL** now exists.
- [ ] Copy it somewhere safe

**Treat that URL like a password.** Anyone holding it can post to your flow.
Never put it in the website's HTML, never commit it to GitHub, never paste it
in a chat.

---

# PART 3 — Change the website

This is the only code change, and it goes in `apply-submit.php`.

### 3.1 — Put the secrets outside the web root

The flow URL and the shared secret must not live in the repository — it is
public, and a public repository is the one place they must never be.

- [ ] cPanel → **File Manager**
- [ ] Go to `/home/takwafood/` — the folder **containing** `public_html`
- [ ] Create a file named `takwa-sharepoint-config.php`
- [ ] Put this in it, with your real values:

```php
<?php
return [
    'url'    => 'PASTE-THE-FLOW-URL-HERE',
    'secret' => 'PASTE-THE-SHARED-SECRET-HERE',
];
```

- [ ] Set its permissions to **600**

Same folder as `takwa-admin-config.php`, and for the same reason: there is no
URL that can reach it.

### 3.2 — The code

I will write this, test it, and commit it once you have decided on Route A.
The shape of it:

- Runs **after** the application is written to disk and the email is sent
- Reads the config file; if it is missing, does nothing at all and carries on
- Builds `full_application` as readable lines from all 103 fields
- Posts JSON to the flow, with a **10 second timeout**
- **Ignores the result.** Success or failure, the applicant sees the same
  "thank you"
- On failure, appends one line to a log file outside the web root so you can
  see what happened

It will use `curl` where available and fall back to a stream context where it
is not — the development machine here has no `curl` extension, and I would
rather the code not care.

### 3.3 — What does NOT change

- [ ] The application is still written to `/home/takwafood/takwa-applications`
- [ ] The `/admin/` inbox still works exactly as now
- [ ] The notification email to `info@` still goes
- [ ] The form, the five steps and the validation are untouched

SharePoint becomes an **addition**, never a replacement. If you later decide
you hate it, deleting the config file turns the whole thing off with no code
change.

---

# PART 4 — Test it

### 4.1 — Test the flow on its own, before touching the website

- [ ] In Power Automate, open the flow and click **Test → Manually**
- [ ] Send it the sample payload from 2.2, with the **real** shared secret

Use a tool that can POST — Postman, or in a terminal:

```bash
curl -X POST -H "Content-Type: application/json" -d @sample.json "THE-FLOW-URL"
```

- [ ] A new item appears in the SharePoint list
- [ ] The flow run shows green

Fix any problems here. Debugging a flow is much easier than debugging a flow
and a website at once.

### 4.2 — Test the wrong secret

- [ ] Send the same payload with a wrong `shared_secret`
- [ ] You get **401** and **no list item is created**

If an item is created anyway, the condition in 2.3 is wired wrong. Stop and fix
it — otherwise anyone who finds the URL can write to your HR list.

### 4.3 — End to end

- [ ] Submit a real application through `takwafoods.com/apply.html`, using
      obviously fake details
- [ ] The thank-you message appears
- [ ] The item appears in SharePoint within a few seconds
- [ ] The application also appears in `takwafoods.com/admin/`
- [ ] Delete the test item from SharePoint and the test file from the server

### 4.4 — Test the failure path

This is the test people skip, and it is the one that matters.

- [ ] In Power Automate, **turn the flow off**
- [ ] Submit another test application
- [ ] The applicant **still sees the thank-you message**
- [ ] It still appears in `/admin/`
- [ ] Turn the flow back on

If the applicant saw an error, the integration is wired wrong and must not go
live. A hiring form that breaks when Microsoft hiccups is worse than no
SharePoint at all.

---

# PART 5 — After it is running

- [ ] Add a note to the HR list description saying where the data comes from,
      so whoever inherits it knows
- [ ] Decide who gets notified. The flow can email or post to Teams — add it in
      the **If yes** branch, no code needed.
- [ ] Decide retention. The privacy notice on the form promises data is kept
      only for the period in your recruitment privacy notice. Applications will
      now sit in **two** places — the server and SharePoint — and both need
      clearing out when that period ends. A scheduled flow can do the
      SharePoint half.

---

## Data protection

The form tells applicants their data "is not disclosed to any third party
without your consent, save where required by law."

Putting it in SharePoint does **not** break that promise. Microsoft is your
data processor, not a third party receiving a disclosure — and their email
already runs through the same tenant, so no new company gets access.

Two things do change, and both are on you:

**The data now lives in two places.** An erasure request means deleting from
the server *and* from SharePoint. Whoever handles those requests must know
that.

**More people can see it.** The `/admin/` page is behind one password. A
SharePoint list is visible to whoever has site access, which is usually more
people than you think. Set the permissions in step 1.5 deliberately.

---

## If it stops working later

| Symptom | Likely cause |
|---|---|
| Items stopped appearing, form still works | Flow turned off, or its owner left the company. Check the run history. |
| Every run fails with 401 | Shared secret changed on one side only |
| Nothing at all, no runs recorded | The website cannot reach Microsoft. Check the log file, and whether the host blocks outbound HTTPS. |
| Items appear with fields missing | A column was renamed in SharePoint. Internal names do not follow renames — check the flow's mapping. |

The applications on the server are unaffected by all of these. `/admin/` is
always the source of truth.

---

## What I need from you to start

1. **Is the HTTP trigger premium in your tenant?** Check as described in
   Route A. That decides everything.
2. **Which SharePoint site** should the list live on?
3. **Who should be able to see it?**

Answer those and I will write the code, test it against a real flow, and commit
it.
