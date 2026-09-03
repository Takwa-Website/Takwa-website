# Request for IT — Microsoft 365 admin

**What this is for:** the careers form on takwafoods.com should create an item
in a SharePoint list each time someone applies for a job.

**Why you:** two of the steps need Global Administrator or SharePoint
Administrator rights. `gyoussef@takwafoods.com` can create the app registration
but cannot grant consent, so the work stops there.

**What already exists**

| | |
|---|---|
| Site | `https://takwafood.sharepoint.com/sites/HR-Website` |
| List | `Job Applications` |
| Site ID | `takwafood.sharepoint.com,5a68ffae-661f-4982-a16b-b336a450d2d9,fac8b71d-bdd2-40d6-ae43-5f4dc7e7acc9` |

No code has been written yet. Nothing is live. This is setup only.

---

## 1. Register an application

Entra admin centre → **Applications → App registrations → New registration**

- Name: **`Takwa Website Applications`**
- Supported account types: **Single tenant**
- Redirect URI: leave empty — this is a server-to-server integration with no
  user sign-in

From the Overview page, note the **Application (client) ID** and the
**Directory (tenant) ID**.

## 2. Create a client secret

**Certificates & secrets → New client secret**

- Description: `takwafoods.com web server`
- Expiry: longest available (24 months)

Copy the **Value** immediately — it is displayed once only.

Please also note the expiry date somewhere it will be seen. When this secret
expires the integration stops silently: the form still works and nothing
raises an alert.

## 3. Grant the permission

**API permissions → Add a permission → Microsoft Graph → Application
permissions → `Sites.Selected`**

Then **Grant admin consent**.

`Sites.Selected` is deliberate rather than `Sites.ReadWrite.All`. The secret
will live on a shared web host, and `Sites.Selected` grants nothing until step
4 scopes it to one site. If that host is ever compromised, the exposure is one
HR list rather than all of SharePoint. Please do not substitute the broader
permission.

## 4. Scope it to the one site

In **Graph Explorer** (developer.microsoft.com/graph/graph-explorer), signed in
as admin. This needs the delegated permission `Sites.FullControl.All` — grant
it on the **Modify permissions** tab if prompted.

**POST**

```
https://graph.microsoft.com/v1.0/sites/takwafood.sharepoint.com,5a68ffae-661f-4982-a16b-b336a450d2d9,fac8b71d-bdd2-40d6-ae43-5f4dc7e7acc9/permissions
```

**Body** — substitute the client ID from step 1:

```json
{
  "roles": ["write"],
  "grantedToIdentities": [
    {
      "application": {
        "id": "CLIENT-ID-FROM-STEP-1",
        "displayName": "Takwa Website Applications"
      }
    }
  ]
}
```

Expected result: **201 Created**.

## 5. Get the list ID

**GET**

```
https://graph.microsoft.com/v1.0/sites/takwafood.sharepoint.com,5a68ffae-661f-4982-a16b-b336a450d2d9,fac8b71d-bdd2-40d6-ae43-5f4dc7e7acc9/lists
```

Find the entry with `displayName` = `Job Applications` and note its `id`.

---

## What to send back

| | |
|---|---|
| Directory (tenant) ID | step 1 |
| Application (client) ID | step 1 |
| Client secret **Value** | step 2 |
| List ID | step 5 |
| Confirmation step 4 returned 201 | |

**Please send the client secret through a password manager or another secure
channel, not in an email or chat message.** It is equivalent to a password for
this integration.

---

## Scope, for the record

This grants one application **write access to one SharePoint list**. It cannot
read mail, cannot read other sites, cannot sign in as a user, and cannot act
outside `HR-Website`. It is used only by takwafoods.com's own server when an
application form is submitted.

Applications are also written to a file on the web server, outside the web
root, and read through an existing password-protected admin page. SharePoint is
an addition to that, not a replacement — so if this integration fails, no
application is lost.
