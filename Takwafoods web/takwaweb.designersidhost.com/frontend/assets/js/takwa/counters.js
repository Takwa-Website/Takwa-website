/* ==========================================================================
   Counting statistics.

   The theme ships jquery.counterup, but it never ran: it hangs its trigger
   off a jQuery Waypoint that does not fire on these pages, so the figures
   simply sat at their final values. It also rebuilds the element's text from
   the parsed number alone, which would have dropped the "+" off "30+" the
   moment it did fire -- hence the markup keeps the digits in their own span
   and leaves the "+" outside it.

   Two deliberate choices here:

     * the step runs on setInterval, not requestAnimationFrame. rAF is
       suspended whenever the page is not being painted -- a background tab,
       an offscreen frame -- and a figure that was skipped rather than
       animated would be left showing 0.
     * a scroll and resize check backs up the IntersectionObserver, so if
       the observer is unavailable or never fires the figures still count
       once they are in view, and are shown in full if all else fails.
   ========================================================================== */
(function () {
    "use strict";

    /* 1100ms, not 1800. These are two- and three-digit figures, so a longer
       run does not read as more impressive -- it reads as the number being
       slow to settle, and the eye has finished with it well before it stops. */
    var DURATION = 1100;
    var TICK = 40;

    function ease(t) {
        /* quick off the mark, gentle into the final number */
        return 1 - Math.pow(1 - t, 3);
    }

    function format(value, template) {
        var text = String(value);
        if (template.indexOf(",") !== -1) {
            text = text.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        }
        return text;
    }

    /* A figure that is really "years since <year>" is worked out at run time
       rather than written into the page, so it gains a year on its own every
       January instead of quietly going stale. The digits in the markup are
       only the no-JS fallback. */
    function targetOf(el) {
        var since = parseInt(el.getAttribute("data-count-since"), 10);
        if (!isNaN(since)) {
            return Math.max(0, new Date().getFullYear() - since);
        }
        var template = el.getAttribute("data-count-to") || el.textContent;
        return parseInt(template.replace(/[^\d]/g, ""), 10);
    }

    /* A counter can drive artwork elsewhere in its block: the About Us panel
       grows a parsley plant in step with the figure. The eased progress is
       published as a custom property on the ancestor named by
       data-progress-scope, so the growth is CSS's business and stays in step
       with the number by construction rather than by running a second timer
       alongside it and hoping the two keep time.

       The property is deliberately absent until the count starts. The
       stylesheet falls back to a fully grown plant, which is what should be
       shown if this script never runs at all. */
    function publisher(el) {
        var selector = el.getAttribute("data-progress-scope");
        var host = selector && el.closest ? el.closest(selector) : null;
        return function (value) {
            if (host) {
                host.style.setProperty("--count-progress", value.toFixed(3));
            }
        };
    }

    function run(el) {
        if (el.getAttribute("data-counted")) { return; }
        el.setAttribute("data-counted", "1");

        var template = el.getAttribute("data-count-to") || el.textContent;
        var target = targetOf(el);
        var publish = publisher(el);
        if (isNaN(target)) { return; }

        /* honour a request for less motion: show the number, do not animate */
        if (window.matchMedia &&
            window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
            el.textContent = format(target, template);
            publish(1);
            return;
        }

        var started = Date.now();
        el.textContent = format(0, template);
        publish(0);
        var timer = setInterval(function () {
            var progress = Math.min((Date.now() - started) / DURATION, 1);
            var eased = ease(progress);
            el.textContent = format(Math.round(target * eased), template);
            publish(eased);
            if (progress >= 1) { clearInterval(timer); }
        }, TICK);
    }

    function onScreen(el) {
        var r = el.getBoundingClientRect();
        var h = window.innerHeight || document.documentElement.clientHeight;
        return r.top < h * 0.9 && r.bottom > 0;
    }

    function init() {
        var figures = [].slice.call(document.querySelectorAll(".stat-count"));
        if (!figures.length) { return; }

        function sweep() {
            var left = false;
            figures.forEach(function (el) {
                if (el.getAttribute("data-counted")) { return; }
                if (onScreen(el)) { run(el); } else { left = true; }
            });
            if (!left) {
                window.removeEventListener("scroll", sweep);
                window.removeEventListener("resize", sweep);
            }
        }

        if ("IntersectionObserver" in window) {
            var watcher = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) { return; }
                    run(entry.target);
                    watcher.unobserve(entry.target);
                });
            }, { threshold: 0.35 });
            figures.forEach(function (el) { watcher.observe(el); });
        }

        window.addEventListener("scroll", sweep, { passive: true });
        window.addEventListener("resize", sweep);
        sweep();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
