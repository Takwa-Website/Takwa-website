<?php
/* ==========================================================================
   Applications inbox.

   One card per application, newest first, with everything the applicant sent.

   ON THE PASSWORD
   ---------------
   Handled by auth.php, required below. The password is set on first visit and
   only its hash is kept, in a file above the web root. Apache Basic auth
   (cPanel > Directory Privacy) is accepted as well if it is configured, so
   the two can be layered.

   The applications are read from outside the web root, so this page is the
   only way to see them and there is no URL that serves the raw files.
   ========================================================================== */

declare(strict_types=1);

const STORE_DIR = '/takwa-applications';

/* The gate. Nothing below this line runs until a session exists: auth.php
   renders the sign-in screen and exits instead of returning. */
require __DIR__ . '/auth.php';

$store = dirname($_SERVER['DOCUMENT_ROOT']) . STORE_DIR;
$files = is_dir($store) ? glob($store . '/*.json') : [];
rsort($files);                       /* filenames start with the timestamp */

$apps = [];
foreach ($files as $path) {
    $data = json_decode((string) file_get_contents($path), true);
    if (is_array($data)) {
        $data['_file'] = basename($path);
        $apps[] = $data;
    }
}

function e(?string $v): string
{
    return htmlspecialchars((string) $v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

/* field name -> human label, in the order the form asks them */
$groups = [
    'Applicant' => [
        'full_name' => 'Full legal name', 'nationality' => 'Nationality',
        'date_of_birth' => 'Date of birth', 'mobile' => 'Mobile',
        'alt_number' => 'Alternative number', 'email' => 'Email',
        'linkedin' => 'LinkedIn / portfolio', 'address' => 'Address',
        'driving_licence' => 'Driving licence',
    ],
    'Position' => [
        'position' => 'Position', 'employment_type' => 'Employment type',
        'work_arrangement' => 'Work arrangement', 'start_date' => 'Available from',
        'notice_period' => 'Notice period', 'expected_salary' => 'Expected salary',
        'vacancy_ref' => 'Vacancy ref', 'vacancy_source' => 'Heard via',
        'previously_applied' => 'Applied before', 'previous_details' => 'Previous details',
    ],
    'Education' => [
        'edu1_institution' => 'Institution 1', 'edu1_qualification' => 'Qualification 1',
        'edu1_from' => 'From 1', 'edu1_to' => 'To 1', 'edu1_grade' => 'Grade 1',
        'edu2_institution' => 'Institution 2', 'edu2_qualification' => 'Qualification 2',
        'edu2_from' => 'From 2', 'edu2_to' => 'To 2', 'edu2_grade' => 'Grade 2',
        'edu3_institution' => 'Institution 3', 'edu3_qualification' => 'Qualification 3',
        'edu3_from' => 'From 3', 'edu3_to' => 'To 3', 'edu3_grade' => 'Grade 3',
    ],
    'Certifications' => [
        'cert1_name' => 'Certificate 1', 'cert1_body' => 'Issued by 1',
        'cert1_issued' => 'Issued 1', 'cert1_expires' => 'Expires 1', 'cert1_credential' => 'ID 1',
        'cert2_name' => 'Certificate 2', 'cert2_body' => 'Issued by 2',
        'cert2_issued' => 'Issued 2', 'cert2_expires' => 'Expires 2', 'cert2_credential' => 'ID 2',
        'cert3_name' => 'Certificate 3', 'cert3_body' => 'Issued by 3',
        'cert3_issued' => 'Issued 3', 'cert3_expires' => 'Expires 3', 'cert3_credential' => 'ID 3',
    ],
    'Employment' => [
        'job1_employer' => 'Employer 1', 'job1_title' => 'Title 1', 'job1_type' => 'Type 1',
        'job1_reporting' => 'Reported to 1', 'job1_from' => 'From 1', 'job1_to' => 'To 1',
        'job1_duties' => 'Duties 1', 'job1_salary' => 'Salary 1', 'job1_leaving' => 'Left because 1',
        'job2_employer' => 'Employer 2', 'job2_title' => 'Title 2', 'job2_type' => 'Type 2',
        'job2_reporting' => 'Reported to 2', 'job2_from' => 'From 2', 'job2_to' => 'To 2',
        'job2_duties' => 'Duties 2', 'job2_salary' => 'Salary 2', 'job2_leaving' => 'Left because 2',
        'job3_employer' => 'Employer 3', 'job3_title' => 'Title 3', 'job3_type' => 'Type 3',
        'job3_reporting' => 'Reported to 3', 'job3_from' => 'From 3', 'job3_to' => 'To 3',
        'job3_duties' => 'Duties 3', 'job3_salary' => 'Salary 3', 'job3_leaving' => 'Left because 3',
    ],
    'Skills' => [
        'skills' => 'Core skills', 'software' => 'Software & systems', 'languages' => 'Languages',
    ],
    'Additional' => [
        'why_apply' => 'Why applying', 'employment_gaps' => 'Employment gaps',
        'related_to_staff' => 'Related to staff', 'other_interests' => 'Other interests',
        'currently_employed' => 'Currently employed', 'willing_shifts' => 'Willing to work shifts',
        'relatives_here' => 'Relatives here', 'yes_details' => 'Details for any yes',
    ],
    'References' => [
        'ref1_name' => 'Referee 1', 'ref1_role' => 'Role 1', 'ref1_relationship' => 'Relationship 1',
        'ref1_email' => 'Email 1', 'ref1_phone' => 'Phone 1',
        'ref2_name' => 'Referee 2', 'ref2_role' => 'Role 2', 'ref2_relationship' => 'Relationship 2',
        'ref2_email' => 'Email 2', 'ref2_phone' => 'Phone 2',
    ],
    'Consent' => [
        'consent_processing' => 'Processing consent', 'consent_retention' => 'Retention consent',
        'declaration' => 'Declaration', 'declaration_name' => 'Signed', 'declaration_date' => 'Dated',
    ],
];
?><!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Applications — Takwa Foods</title>
<style>
:root{ color-scheme: light dark;
  --bg:#f6f7f6; --card:#fff; --line:#dfe1de; --ink:#12211f; --dim:#6b7a76;
  --accent:#2C6728; --warn:#8a5a00; }
@media (prefers-color-scheme: dark){ :root{
  --bg:#0f1614; --card:#17211f; --line:#2a3835; --ink:#e8efec; --dim:#93a5a0;
  --accent:#73ED7C; --warn:#f0c674; } }
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{position:sticky;top:0;z-index:5;background:var(--bg);
  border-bottom:1px solid var(--line);padding:16px 22px}
h1{margin:0 0 4px;font-size:19px}
.sub{color:var(--dim);font-size:13px}
input[type=search]{margin-top:12px;width:100%;max-width:420px;padding:8px 11px;
  border:1px solid var(--line);border-radius:8px;background:var(--card);
  color:var(--ink);font:inherit}
main{padding:22px;max-width:1080px;margin:0 auto}
.app{background:var(--card);border:1px solid var(--line);border-radius:14px;
  margin-bottom:16px;overflow:hidden}
.app>summary{list-style:none;cursor:pointer;padding:18px 20px;display:flex;
  flex-wrap:wrap;gap:6px 16px;align-items:baseline}
.app>summary::-webkit-details-marker{display:none}
.who{font-size:17px;font-weight:600}
.role{color:var(--accent);font-weight:600}
.when{margin-left:auto;color:var(--dim);font-size:13px}
.body{padding:0 20px 20px;border-top:1px solid var(--line)}
h2{font-size:12px;text-transform:uppercase;letter-spacing:.09em;
  color:var(--dim);margin:22px 0 10px}
dl{display:grid;grid-template-columns:minmax(150px,220px) 1fr;gap:8px 18px;margin:0}
dt{color:var(--dim);font-size:13.5px}
dd{margin:0;white-space:pre-wrap;word-break:break-word}
.empty{padding:60px 20px;text-align:center;color:var(--dim)}
.note{background:var(--card);border:1px solid var(--line);
  border-left:3px solid var(--warn);border-radius:10px;padding:13px 16px;
  margin-bottom:20px;font-size:13.5px;color:var(--dim)}
a{color:var(--accent)}
@media(max-width:640px){ dl{grid-template-columns:1fr;gap:2px 0} dt{margin-top:10px} }
</style>
</head>
<body>
<header>
  <h1>Applications</h1>
  <div class="sub"><?= count($apps) ?> received &middot; <a href="?logout=1">sign out</a></div>
  <input type="search" id="q" placeholder="Search name, position, email&hellip;">
</header>

<main>
  <div class="note">
    These records contain personal data: dates of birth, addresses, salary
    history and referees who did not themselves consent. Do not forward a card
    by email or screenshot it into a group chat. Delete applications once the
    retention period in the recruitment privacy notice has passed.
  </div>

<?php if (!$apps): ?>
  <p class="empty">No applications yet.</p>
<?php endif; ?>

<?php foreach ($apps as $a): ?>
  <details class="app" data-find="<?= e(strtolower(
      ($a['full_name'] ?? '') . ' ' . ($a['position'] ?? '') . ' ' .
      ($a['email'] ?? '') . ' ' . ($a['nationality'] ?? ''))) ?>">
    <summary>
      <span class="who"><?= e($a['full_name'] ?? 'Unnamed') ?></span>
      <span class="role"><?= e($a['position'] ?? '') ?></span>
      <span class="when"><?= e(substr((string)($a['_received'] ?? ''), 0, 10)) ?></span>
    </summary>
    <div class="body">
      <?php foreach ($groups as $title => $fields):
            $rows = array_filter($fields, fn($l, $k) => !empty($a[$k]),
                                 ARRAY_FILTER_USE_BOTH);
            if (!$rows) { continue; } ?>
        <h2><?= e($title) ?></h2>
        <dl>
          <?php foreach ($rows as $key => $label): ?>
            <dt><?= e($label) ?></dt>
            <dd><?php
                if ($key === 'email' || substr($key, -6) === '_email') {
                    echo '<a href="mailto:' . e($a[$key]) . '">' . e($a[$key]) . '</a>';
                } else {
                    echo e($a[$key]);
                } ?></dd>
          <?php endforeach; ?>
        </dl>
      <?php endforeach; ?>
    </div>
  </details>
<?php endforeach; ?>
</main>

<script>
document.getElementById('q').addEventListener('input', function () {
    var q = this.value.trim().toLowerCase();
    document.querySelectorAll('.app').forEach(function (el) {
        el.style.display = !q || el.dataset.find.indexOf(q) > -1 ? '' : 'none';
    });
});
</script>
</body>
</html>
