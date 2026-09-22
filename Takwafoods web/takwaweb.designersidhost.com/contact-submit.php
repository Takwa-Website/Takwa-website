<?php
/* ==========================================================================
   Receives a "Get in Touch" contact message and emails it.

   Why this exists rather than Web3Forms: the requirement is that every
   message reaches BOTH HR@takwafoods.com and GYoussef@takwafoods.com. A free
   Web3Forms key delivers only to the single inbox it is registered to
   (info@), and adding recipients needs access to that Web3Forms account,
   which is not available here. A tiny PHP handler on the same host -- the
   same pattern as apply-submit.php -- delivers to as many addresses as we
   like and keeps the message on Takwa's own infrastructure.

   Unlike an application this holds no sensitive personal-data record, so it
   is emailed rather than written to disk.
   ========================================================================== */

declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');

/* Where every contact message must go. info@ is kept so the existing inbox
   still receives them; the two required addresses are added. */
const RECIPIENTS = 'HR@takwafoods.com, GYoussef@takwafoods.com, info@takwafoods.com';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed.']);
    exit;
}

/* ---------------------------------------------------------- rate limit -----
   Same lightweight per-IP cap as the application form: one small file per IP
   in the system temp dir, best-effort, no database. Stops casual flooding of
   the inbox without a CAPTCHA. */
(function () {
    $ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
    $max = 8;
    $window = 3600;
    $file = sys_get_temp_dir() . '/takwa_contact_rl_' . md5($ip);
    $now = time();
    $hits = [];
    if (is_readable($file)) {
        $hits = array_filter(
            array_map('intval', explode(',', (string) file_get_contents($file))),
            function ($t) use ($now, $window) { return $t > $now - $window; }
        );
    }
    if (count($hits) >= $max) {
        http_response_code(429);
        echo json_encode(['success' => false,
            'message' => 'Too many messages from this connection. Please try '
                       . 'again later, or email info@takwafoods.com.']);
        exit;
    }
    $hits[] = $now;
    @file_put_contents($file, implode(',', $hits), LOCK_EX);
})();

/* Accept a JSON body (what contact-form.js sends) or a plain form POST. */
$raw = file_get_contents('php://input');
$posted = json_decode($raw ?: '[]', true);
if (!is_array($posted)) {
    $posted = $_POST;
}

/* Honeypot: the form ships a hidden "botcheck" checkbox. A human never sees
   it; a bot that fills every field ticks it. If it is set, answer success and
   drop the message silently, exactly as Web3Forms did. */
if (!empty($posted['botcheck'])) {
    echo json_encode(['success' => true, 'message' => 'Message received.']);
    exit;
}

function field(array $src, string $key, int $max = 5000): string
{
    $v = isset($src[$key]) ? trim((string) $src[$key]) : '';
    $v = strip_tags($v);
    if (preg_match('/^.{0,' . $max . '}/us', $v, $m)) {
        $v = $m[0];
    }
    return $v;
}

$name    = field($posted, 'name', 200);
$email   = field($posted, 'email', 250);
$phone   = field($posted, 'phone', 60);
$company = field($posted, 'subject', 250);   /* the "Company" box is name=subject */
$message = field($posted, 'message', 5000);

/* The template pre-fills the textarea with the literal word "Message"; treat
   that as empty so an untouched box is not sent as if it were content. */
if (strcasecmp($message, 'Message') === 0) {
    $message = '';
}

if ($name === '' || $email === '' || $message === ''
    || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(422);
    echo json_encode(['success' => false, 'message' => 'Missing or invalid details.']);
    exit;
}

$body = "New message from the takwafoods.com contact form.\n\n"
      . "Name:    $name\n"
      . "Email:   $email\n"
      . "Phone:   " . ($phone !== '' ? $phone : '-') . "\n"
      . "Company: " . ($company !== '' ? $company : '-') . "\n\n"
      . "Message:\n$message\n";

/* Reply-To is the visitor so a reply goes straight back to them; From is a
   no-reply on our own domain so the message passes SPF/DKIM for takwafoods.com
   rather than being sent "as" a stranger's address (which fails and bounces). */
$headers = "From: no-reply@takwafoods.com\r\n"
         . 'Reply-To: ' . str_replace(["\r", "\n"], '', $email) . "\r\n"
         . "Content-Type: text/plain; charset=utf-8\r\n";

$sent = @mail(RECIPIENTS, 'Website contact: ' . $name, $body, $headers);

if (!$sent) {
    http_response_code(500);
    echo json_encode(['success' => false,
        'message' => 'Could not send your message. Please email info@takwafoods.com.']);
    exit;
}

echo json_encode(['success' => true, 'message' => 'Message sent.']);
