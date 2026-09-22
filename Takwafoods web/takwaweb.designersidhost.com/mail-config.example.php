<?php
/* ==========================================================================
   TEMPLATE — copy this to  /home/<your-cpanel-account>/takwa-mail-config.php
   (ONE LEVEL ABOVE public_html, so it can never be reached by a URL) and fill
   in the real values. Do NOT put real credentials in this example file and do
   NOT commit the filled-in file — the real path is gitignored.

   The values are for a Microsoft 365 mailbox with SMTP AUTH enabled. Use a
   dedicated mailbox such as noreply@takwafoods.com if you can create one;
   otherwise info@takwafoods.com works. If the mailbox has MFA, generate an
   "app password" for it and use that as the password.
   ========================================================================== */

return [
    'host'       => 'smtp.office365.com',   // M365 SMTP submission host
    'port'       => 587,                    // STARTTLS
    'username'   => 'noreply@takwafoods.com',   // the mailbox you log in as
    'password'   => 'PUT-THE-MAILBOX-OR-APP-PASSWORD-HERE',
    'from_email' => 'noreply@takwafoods.com',   // must match/allowed-for the username
    'from_name'  => 'Takwa Foods Website',
];
