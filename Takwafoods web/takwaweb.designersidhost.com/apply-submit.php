<?php
/* ==========================================================================
   Receives an application and writes it to disk.

   Two things matter here and neither is negotiable.

   1. The applications are written OUTSIDE public_html. $STORE resolves to
      /home/takwafood/takwa-applications, a sibling of the web root, so there
      is no URL that can reach a submission file even if the admin directory
      is later misconfigured. A data store inside public_html is one bad
      .htaccess away from being a public archive of people's dates of birth
      and salary history.

   2. Nothing here trusts the browser. The form fields are whitelisted below;
      anything else posted is discarded rather than written, so a crafted POST
      cannot plant arbitrary keys in the record.

   This replaces the Web3Forms path for applications. That route sent every
   application through a US third party that stores submissions for 30 days
   and offers no data processing agreement, while the form's own privacy
   notice promised no third-party disclosure. Keeping the data on Takwa's own
   host is what makes that promise true.
   ========================================================================== */

declare(strict_types=1);

const STORE_DIR = '/takwa-applications';

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['ok' => false, 'message' => 'Method not allowed.']);
    exit;
}

/* ---------------------------------------------------------- rate limit -----
   The form has no CAPTCHA, so without this one script could post thousands of
   valid-looking applications in a minute and bury the real ones. This caps a
   single IP to a handful of submissions per hour.

   The counter lives in the system temp directory, one small file per IP. It is
   best-effort, not a fortress: it is per-server and resets if temp is cleared.
   That is the right weight for a careers form -- enough to stop casual flooding
   without a database or a dependency. */
(function () {
    $ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
    $max = 6;                 // submissions allowed
    $window = 3600;           // per this many seconds
    $file = sys_get_temp_dir() . '/takwa_rl_' . md5($ip);

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
        echo json_encode(['ok' => false,
            'message' => 'Too many submissions from this connection. '
                       . 'Please try again later, or email info@takwafoods.com.']);
        exit;
    }
    $hits[] = $now;
    @file_put_contents($file, implode(',', $hits), LOCK_EX);
})();

/* ------------------------------------------------------------- the fields --
   Whitelist, not a free-for-all. Repeating groups are expanded by index so
   edu1_institution through edu3_grade are accepted but edu9_ is not. */
$allowed = [
    'vacancy_ref', 'application_date',
    'full_name', 'nationality', 'date_of_birth', 'mobile', 'alt_number',
    'email', 'linkedin', 'driving_licence', 'address',
    'position', 'employment_type', 'work_arrangement', 'start_date',
    'notice_period', 'expected_salary', 'vacancy_source',
    'previously_applied', 'previous_details',
    'skills', 'software', 'languages',
    'why_apply', 'employment_gaps', 'related_to_staff', 'other_interests',
    'currently_employed', 'willing_shifts', 'relatives_here', 'yes_details',
    'consent_processing', 'consent_retention', 'declaration',
    'declaration_name', 'declaration_date',
];

foreach ([1, 2, 3] as $i) {
    foreach (['institution', 'qualification', 'from', 'to', 'grade'] as $k) {
        $allowed[] = "edu{$i}_{$k}";
    }
    foreach (['name', 'body', 'issued', 'expires', 'credential'] as $k) {
        $allowed[] = "cert{$i}_{$k}";
    }
    foreach (['employer', 'title', 'type', 'reporting', 'from', 'to',
              'duties', 'salary', 'leaving'] as $k) {
        $allowed[] = "job{$i}_{$k}";
    }
}
foreach ([1, 2] as $i) {
    foreach (['name', 'role', 'relationship', 'email', 'phone'] as $k) {
        $allowed[] = "ref{$i}_{$k}";
    }
}

/* Truncate without mbstring. The extension is not guaranteed on shared
   hosting -- it is absent on the development machine -- and a plain substr()
   would cut an Arabic or accented character in half and leave broken bytes in
   the record. PCRE's /u modifier gives UTF-8 awareness with no extension. */
function clip(string $value, int $max): string
{
    if (preg_match('/^.{0,' . $max . '}/us', $value, $m)) {
        return $m[0];
    }
    return substr($value, 0, $max);
}

$raw = file_get_contents('php://input');
$posted = json_decode($raw ?: '[]', true);
if (!is_array($posted)) {
    $posted = $_POST;
}

$record = [];
foreach ($allowed as $key) {
    if (!isset($posted[$key])) {
        continue;
    }
    $value = trim((string) $posted[$key]);
    if ($value !== '') {
        /* store text, never markup -- the admin page escapes on output too,
           but a value that was never markup cannot become markup later */
        $record[$key] = clip(strip_tags($value), 5000);
    }
}

/* the three that make the application meaningful */
foreach (['full_name', 'email', 'position'] as $need) {
    if (empty($record[$need])) {
        http_response_code(422);
        echo json_encode(['ok' => false, 'message' => 'Missing required details.']);
        exit;
    }
}
if (empty($record['consent_processing']) || empty($record['declaration'])) {
    http_response_code(422);
    echo json_encode(['ok' => false, 'message' => 'Consent and declaration are required.']);
    exit;
}

$record['_received']    = gmdate('c');
$record['_ip']          = $_SERVER['REMOTE_ADDR'] ?? '';
$record['_status']      = 'new';

/* ------------------------------------------------------------------ write -- */
$store = dirname($_SERVER['DOCUMENT_ROOT']) . STORE_DIR;
if (!is_dir($store) && !mkdir($store, 0700, true) && !is_dir($store)) {
    http_response_code(500);
    echo json_encode(['ok' => false, 'message' => 'Could not save the application.']);
    exit;
}

/* belt and braces: if this directory ever does end up inside a web root,
   refuse to serve anything out of it */
$guard = $store . '/.htaccess';
if (!file_exists($guard)) {
    @file_put_contents($guard, "Require all denied\n");
}

$name = gmdate('Ymd-His') . '-' . bin2hex(random_bytes(4)) . '.json';
$written = file_put_contents(
    $store . '/' . $name,
    json_encode($record, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE),
    LOCK_EX
);

if ($written === false) {
    http_response_code(500);
    echo json_encode(['ok' => false, 'message' => 'Could not save the application.']);
    exit;
}
@chmod($store . '/' . $name, 0600);

/* a short note to the office so nobody has to poll the admin page.
   The application itself is not emailed -- that would put the personal data
   back into an inbox and undo the point of storing it here. */
@mail(
    'info@takwafoods.com',
    'New application: ' . $record['position'] . ', ' . $record['full_name'],
    "A new employment application has been received.\n\n"
    . "Position: " . $record['position'] . "\n"
    . "Applicant: " . $record['full_name'] . "\n\n"
    . "Read it here: https://takwafoods.com/admin/\n",
    'From: no-reply@takwafoods.com'
);

echo json_encode(['ok' => true, 'message' => 'Application received.']);
