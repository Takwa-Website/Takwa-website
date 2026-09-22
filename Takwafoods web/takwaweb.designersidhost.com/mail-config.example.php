<?php
/* ==========================================================================
   TEMPLATE — copy this to  /home/takwafood/takwa-mail-config.php
   (ONE LEVEL ABOVE public_html, so no URL can ever reach it) and fill in the
   real values. Do NOT put real credentials in this example file, and do NOT
   commit the filled-in file — the real path is gitignored.

   ------------------------------------------------------------------ FILL 1 --
   Microsoft 365 (the chosen path). Needs a real, licensed mailbox with
   "Authenticated SMTP" enabled — see the admin steps George was given.

       'host'       => 'smtp.office365.com',
       'port'       => 587,
       'encryption' => 'starttls',
       'username'   => 'noreply@takwafoods.com',
       'password'   => 'THE-MAILBOX-PASSWORD',
       'from_email' => 'noreply@takwafoods.com',   // must equal the username
       'from_name'  => 'Takwa Foods Website',

   ------------------------------------------------------------------ FILL 2 --
   Fallback — a mailbox created in cPanel (only if the M365 path can't be
   enabled). Get host/port from cPanel → Email Accounts → Connect Devices /
   "Configure Mail Client" for that mailbox. IMPORTANT: keep the domain's
   cPanel "Email Routing" set to Remote (Exchange) so inbound mail still goes
   to Microsoft 365 — this mailbox is for OUTBOUND sending only.

       'host'       => 'mail.takwafoods.com',   // whatever cPanel shows
       'port'       => 465,
       'encryption' => 'ssl',                   // or 587 + 'starttls'
       'username'   => 'noreply@takwafoods.com',
       'password'   => 'THE-CPANEL-MAILBOX-PASSWORD',
       'from_email' => 'noreply@takwafoods.com',
       'from_name'  => 'Takwa Foods Website',

   --------------------------------------------------------------------------
   'test_key' is optional: set it to any random string to allow the browser
   test at /mail-test.php?key=THATSTRING&to=you@example.com. Leave it out and
   the web test is disabled (the command-line test still works).
   ========================================================================== */

return [
    'host'       => 'smtp.office365.com',
    'port'       => 587,
    'encryption' => 'starttls',                 // 'starttls' (587) or 'ssl' (465)
    'username'   => 'noreply@takwafoods.com',
    'password'   => 'PUT-THE-MAILBOX-PASSWORD-HERE',
    'from_email' => 'noreply@takwafoods.com',
    'from_name'  => 'Takwa Foods Website',
    // 'test_key' => 'change-me-to-a-random-string',
];
