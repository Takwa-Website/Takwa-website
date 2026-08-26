"use strict";

/* ==========================================================================
   Theme helpers.

   Rewritten during the site audit. What was here before came from the
   purchased template and targeted a page structure this site does not have:
   of the eleven selectors it touched, only .menu-bg exists anywhere. The
   dead parts are listed at the bottom of this file so nobody re-adds them
   looking for behaviour that was never wired up.
   ========================================================================== */

/* AOS was being re-initialised on every scroll event:

       $(window).on("scroll", function () { AOS.init(); });

   AOS.init() re-queries the DOM and recalculates the offset of every animated
   element. Bound to scroll, that ran dozens of times a second for the whole
   life of the page. It only ever needed to run once. */
if (window.AOS) {
    AOS.init({ once: true });
}

(function ($) {
    "use strict";

    /* Header background once the page has moved off the top.
       Throttled through requestAnimationFrame so the class is written at most
       once per frame rather than once per scroll event. */
    var menuBg = $(".menu-bg");

    if (menuBg.length) {
        var ticking = false;

        $(window).on("scroll", function () {
            if (ticking) { return; }
            ticking = true;

            window.requestAnimationFrame(function () {
                menuBg.toggleClass("nav-bg", $(window).scrollTop() > 150);
                ticking = false;
            });
        });
    }
})(jQuery);

/* ---------------------------------------------------------------------------
   Removed, and why. Every selector below matches nothing on any page of this
   site, verified across all 55 documents:

     .formbold-form-wrapper / .formbold-action-btn
         chatboxToogleHandler() dereferenced both at the top level. They were
         always null, so the function threw if anything had ever called it.
     #nav-opn-btn / #nav-cls-btn / #offcanvas-nav
         openNav() and closeNav() were defined but never bound to anything.
     .back-to-top          - no such element; the theme uses a[href="#top"],
                             which function.js already handles.
     .shafull-container    - called $.fn.shuffle, a plugin this site never loads.
     .next-prev-btn, .dashboard-btn
     .my-video-links       - `new VenoBox({selector: ".my-video-links"})` ran at
                             the top level against zero elements. VenoBox itself
                             is no longer loaded at all: it registered against the
                             first of two jQuery copies and was wiped when the
                             second replaced window.jQuery.

   The old file also declared `var scrolling` twice inside the same function.
   --------------------------------------------------------------------------- */
