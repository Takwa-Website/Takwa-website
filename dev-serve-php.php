<?php
/* ==========================================================================
   Local test router for `php -S`.

   DEVELOPMENT ONLY. This file lives outside the site folder and is never
   deployed -- .cpanel.yml copies from the site directory, not from here.

   It exists only to route directory requests to index.php, which the built-in
   server does not do on its own.

   It does NOT bypass the password. The inbox is protected by admin/auth.php,
   which is plain PHP and works here exactly as it does on the host, so the
   sign-in you test locally is the real one.

   The storage path also differs. On the host the applications sit in
   /home/takwafood/takwa-applications, a sibling of public_html. Locally
   dirname(DOCUMENT_ROOT) resolves to the folder above the site, which is
   fine -- same relationship, different absolute path.

   Run from the repository root:

       php -S 127.0.0.1:8100 -t "Takwafoods web/takwaweb.designersidhost.com" dev-serve-php.php

   Then open  http://127.0.0.1:8100/apply.html
   and        http://127.0.0.1:8100/admin/
   ========================================================================== */

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

/* directory request -> index.php */
if (substr($path, -1) === '/') {
    $candidate = rtrim($_SERVER['DOCUMENT_ROOT'], '/') . $path . 'index.php';
    if (is_file($candidate)) {
        require $candidate;
        return true;
    }
}

/* let the built-in server handle any real file it can find */
$file = rtrim($_SERVER['DOCUMENT_ROOT'], '/') . $path;
if ($path !== '/' && is_file($file)) {
    return false;
}

return false;
