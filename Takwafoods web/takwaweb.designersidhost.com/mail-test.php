<?php
/* ==========================================================================
   Send one test email to prove the SMTP config works, without submitting a
   real form.

   Command line (safest, no exposure):
       php mail-test.php you@example.com

   Browser (only if you set 'test_key' in takwa-mail-config.php):
       https://takwafoods.com/mail-test.php?key=YOURKEY&to=you@example.com

   It reports the exact SMTP result — success, or the precise failure (auth
   rejected, connection blocked, etc.) — so a bad password or a disabled
   Authenticated SMTP shows up immediately.
   ========================================================================== */

declare(strict_types=1);

require_once __DIR__ . '/mailer.php';

$cli = (PHP_SAPI === 'cli');

if ($cli) {
    $to = $argv[1] ?? '';
    if ($to === '') {
        fwrite(STDERR, "Usage: php mail-test.php recipient@example.com\n");
        exit(2);
    }
} else {
    header('Content-Type: text/plain; charset=utf-8');
    $cfg = takwa_mail_config();
    $key = $cfg['test_key'] ?? null;
    /* No key configured, or the wrong key: refuse. This keeps a mail sender
       from being open on the web. */
    if (!$key || !isset($_GET['key']) || !hash_equals((string) $key, (string) $_GET['key'])) {
        http_response_code(403);
        echo "Forbidden. Set 'test_key' in takwa-mail-config.php and pass ?key=...&to=you@example.com,\n";
        echo "or run this from the command line: php mail-test.php you@example.com\n";
        exit;
    }
    $to = (string) ($_GET['to'] ?? '');
    if ($to === '' || !filter_var($to, FILTER_VALIDATE_EMAIL)) {
        http_response_code(400);
        echo "Add a valid ?to=you@example.com\n";
        exit;
    }
}

$result = takwa_send_mail(
    $to,
    'Takwa mail test',
    "This is a test message from takwafoods.com.\n\n"
    . "If you received it, the site can send email and the form notifications "
    . "will arrive.\n\nSent: " . date('c') . "\n"
);

if ($result['ok']) {
    echo "OK — test message sent to $to. Check that inbox (and Junk).\n";
    exit(0);
}

echo "FAILED — " . $result['error'] . "\n";
exit($cli ? 1 : 0);
