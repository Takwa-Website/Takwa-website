<?php
/* ==========================================================================
   Minimal SMTP sender shared by apply-submit.php and contact-submit.php.

   Why not PHP's mail(): mail() hands the message to the local server, which
   then sends it to takwafoods.com's mail host (Microsoft 365) from the cPanel
   web IP. M365 treats a message From: @takwafoods.com arriving from a non-M365
   server as spoofing its own domain and drops it -- which is exactly what
   happened: the application saved, the notification never arrived.

   The fix is to submit the message THROUGH M365 with a real mailbox login, so
   it originates inside M365 and is delivered normally. This is a tiny, self-
   contained SMTP client (STARTTLS + AUTH LOGIN) so it needs no Composer or
   PHP extension beyond OpenSSL, which shared cPanel always has.

   Credentials are NOT in this file and NOT in the repo. They live in a config
   file OUTSIDE public_html that George fills on the server:
       /home/<account>/takwa-mail-config.php
   (a sibling of public_html, so no URL can ever reach it). See
   mail-config.example.php for its shape.
   ========================================================================== */

declare(strict_types=1);

/* Load the credentials file from one level above the web root. Returns null
   if it is missing or malformed, so the caller can log and degrade rather
   than fatal. */
function takwa_mail_config(): ?array
{
    $path = dirname($_SERVER['DOCUMENT_ROOT']) . '/takwa-mail-config.php';
    if (!is_file($path)) {
        return null;
    }
    $cfg = include $path;
    return is_array($cfg) ? $cfg : null;
}

/* Encode a header value as UTF-8 only when it is not plain ASCII, so ordinary
   subjects stay readable in the raw message and Arabic names still arrive
   intact. */
function takwa_mime_header(string $value): string
{
    if (preg_match('//u', $value) && !preg_match('/[^\x20-\x7E]/', $value)) {
        return $value;
    }
    return '=?UTF-8?B?' . base64_encode($value) . '?=';
}

/* Send one plain-text message to one or more recipients.
   $to may be an array or a comma-separated string.
   Returns ['ok' => bool, 'error' => string]; never throws. */
function takwa_send_mail($to, string $subject, string $body, ?string $replyTo = null): array
{
    $cfg = takwa_mail_config();
    if (!$cfg) {
        return ['ok' => false, 'error' => 'mail config missing (takwa-mail-config.php not found above public_html)'];
    }

    $recipients = is_array($to) ? $to : explode(',', $to);
    $recipients = array_values(array_filter(array_map('trim', $recipients), 'strlen'));
    if (!$recipients) {
        return ['ok' => false, 'error' => 'no recipients'];
    }

    $host      = $cfg['host']       ?? 'smtp.office365.com';
    $port      = (int) ($cfg['port'] ?? 587);
    $user      = (string) ($cfg['username'] ?? '');
    $pass      = (string) ($cfg['password'] ?? '');
    $fromEmail = (string) ($cfg['from_email'] ?? $user);
    $fromName  = (string) ($cfg['from_name'] ?? 'Takwa Foods');
    /* 'starttls' (port 587, the default) or 'ssl' / 'tls' (implicit TLS, port
       465). M365 uses STARTTLS; a cPanel mailbox usually offers either. */
    $enc = strtolower((string) ($cfg['encryption'] ?? 'starttls'));
    $implicitTls = ($enc === 'ssl' || $enc === 'tls');

    if ($user === '' || $pass === '' || $fromEmail === '') {
        return ['ok' => false, 'error' => 'mail config incomplete (username, password, from_email)'];
    }

    $errno = 0; $errstr = '';
    $fp = @fsockopen(($implicitTls ? 'ssl://' : '') . $host, $port, $errno, $errstr, 20);
    if (!$fp) {
        return ['ok' => false, 'error' => "connect failed: $errstr ($errno)"];
    }
    stream_set_timeout($fp, 20);

    $read = function () use ($fp) {
        $data = '';
        while (($line = fgets($fp, 515)) !== false) {
            $data .= $line;
            /* a multiline SMTP reply has a '-' after the code on every line
               but the last, which has a space */
            if (strlen($line) < 4 || $line[3] === ' ') { break; }
        }
        return $data;
    };
    $code = function ($reply) { return (int) substr($reply, 0, 3); };
    $cmd  = function ($line) use ($fp, $read) { fwrite($fp, $line . "\r\n"); return $read(); };

    $fail = function ($msg) use ($fp) { @fclose($fp); return ['ok' => false, 'error' => $msg]; };

    $r = $read();                       if ($code($r) !== 220) { return $fail('greeting: ' . trim($r)); }
    $ehlo = 'EHLO takwafoods.com';
    $r = $cmd($ehlo);                   if ($code($r) !== 250) { return $fail('EHLO: ' . trim($r)); }
    $r = $cmd('STARTTLS');              if ($code($r) !== 220) { return $fail('STARTTLS: ' . trim($r)); }
    if (!stream_socket_enable_crypto($fp, true, STREAM_CRYPTO_METHOD_TLS_CLIENT)) {
        return $fail('TLS negotiation failed');
    }
    $r = $cmd($ehlo);                   if ($code($r) !== 250) { return $fail('EHLO after TLS: ' . trim($r)); }
    $r = $cmd('AUTH LOGIN');            if ($code($r) !== 334) { return $fail('AUTH LOGIN: ' . trim($r)); }
    $r = $cmd(base64_encode($user));   if ($code($r) !== 334) { return $fail('username stage: ' . trim($r)); }
    $r = $cmd(base64_encode($pass));   if ($code($r) !== 235) { return $fail('authentication failed: ' . trim($r)); }
    $r = $cmd('MAIL FROM:<' . $fromEmail . '>');
    if ($code($r) !== 250) { return $fail('MAIL FROM: ' . trim($r)); }
    foreach ($recipients as $rcpt) {
        $r = $cmd('RCPT TO:<' . $rcpt . '>');
        if ($code($r) !== 250 && $code($r) !== 251) { return $fail("RCPT $rcpt: " . trim($r)); }
    }
    $r = $cmd('DATA');                  if ($code($r) !== 354) { return $fail('DATA: ' . trim($r)); }

    $headers  = 'From: ' . takwa_mime_header($fromName) . ' <' . $fromEmail . '>' . "\r\n";
    $headers .= 'To: ' . implode(', ', $recipients) . "\r\n";
    if ($replyTo !== null && $replyTo !== '') {
        $headers .= 'Reply-To: ' . str_replace(["\r", "\n"], '', $replyTo) . "\r\n";
    }
    $headers .= 'Subject: ' . takwa_mime_header($subject) . "\r\n";
    $headers .= 'MIME-Version: 1.0' . "\r\n";
    $headers .= 'Content-Type: text/plain; charset=utf-8' . "\r\n";
    $headers .= 'Content-Transfer-Encoding: 8bit' . "\r\n";
    $headers .= 'Date: ' . date('r') . "\r\n";

    /* normalise to CRLF and dot-stuff lines that begin with '.' so the body
       cannot end the DATA stage early */
    $bodyOut = str_replace("\r\n", "\n", $body);
    $bodyOut = preg_replace('/^\./m', '..', $bodyOut);
    $bodyOut = str_replace("\n", "\r\n", $bodyOut);

    fwrite($fp, $headers . "\r\n" . $bodyOut . "\r\n.\r\n");
    $r = $read();                       if ($code($r) !== 250) { return $fail('message rejected: ' . trim($r)); }
    @fwrite($fp, "QUIT\r\n");
    @fclose($fp);
    return ['ok' => true, 'error' => ''];
}
