/* ==========================================================================
   Employment application form.

   Posts to apply-submit.php on this host, which writes each application to a
   directory outside public_html.

   Deliberately NOT Web3Forms. That route sends the data to a US third party
   that stores submissions for 30 days and offers no data processing
   agreement, while this form's own privacy notice promises no third-party
   disclosure. Keeping the data on Takwa's own server is what makes that
   promise true.

   The form is long, so the failure modes that matter are different from a
   five-field contact form:

     * A browser's native validation bubble points at the first invalid field,
       but on a page this tall that field is often off screen and the user
       sees nothing happen. So validation is handled here: the first bad field
       is scrolled to and focused.
     * Nine sections of typing is a lot to lose. The answers are mirrored to
       sessionStorage as they are entered and restored on load, so a stray
       refresh or a back button does not empty the form. Cleared on success.
     * Empty optional fields are dropped from the payload rather than sent as
       blank keys, otherwise the email arrives as sixty lines of which fifty
       say nothing.
   ========================================================================== */
(function () {
    "use strict";

    var ENDPOINT = "apply-submit.php";
    var STORE = "takwa-application-draft";

    var form = document.getElementById("applyForm");
    if (!form) { return; }

    var status = form.querySelector(".form-status");
    var button = form.querySelector('button[type="submit"]');

    function say(message, kind) {
        if (!status) { return; }
        status.textContent = message;
        status.className = "form-status" + (kind ? " " + kind : "");
    }

    /* ------------------------------------------------------------- draft -- */
    function fields() {
        return Array.prototype.slice.call(
            form.querySelectorAll("input, select, textarea"));
    }

    function saveDraft() {
        try {
            var data = {};
            fields().forEach(function (el) {
                if (!el.name) { return; }
                data[el.name] = el.type === "checkbox" ? el.checked : el.value;
            });
            sessionStorage.setItem(STORE, JSON.stringify(data));
        } catch (e) { /* private mode, quota: a lost draft is not worth an error */ }
    }

    function restoreDraft() {
        try {
            var raw = sessionStorage.getItem(STORE);
            if (!raw) { return; }
            var data = JSON.parse(raw);
            /* rebuild any rows the draft had before restoring values, or the
               second job and third qualification quietly vanish */
            [].slice.call(form.querySelectorAll(".repeater")).forEach(function (box) {
                var kind = box.dataset.kind, max = +box.dataset.max || 3;
                for (var n = box.querySelector(".rows").children.length + 1; n <= max; n++) {
                    var probe = Object.keys(data).some(function (k) {
                        return k.indexOf(kind + n + "_") === 0 && data[k];
                    });
                    if (!probe) { break; }
                    box.querySelector(".add-row").click();
                }
            });
            fields().forEach(function (el) {
                if (!el.name || !(el.name in data)) { return; }
                if (el.type === "checkbox") { el.checked = !!data[el.name]; }
                else { el.value = data[el.name]; }
            });
            say("Your previous answers have been restored.", "note");
        } catch (e) { /* ignore a corrupt draft rather than block the form */ }
    }

    restoreDraft();
    form.addEventListener("input", saveDraft);
    form.addEventListener("change", saveDraft);


    /* ------------------------------------------------------------- steps -- */
    /* The form is five panels, one visible at a time. Splitting it is not
       decoration: as one page it measured 11,127px, twelve screens, and a form
       that long is abandoned rather than finished. */
    var panels  = [].slice.call(form.querySelectorAll(".step"));
    var crumbs  = [].slice.call(form.querySelectorAll(".stepper-item"));
    var bar     = form.querySelector(".apply-progress-bar");
    var backBtn = form.querySelector("[data-back]");
    var nextBtn = form.querySelector("[data-next]");
    var sendBtn = form.querySelector("[data-send]");
    var at = 0;

    function show(i, scroll) {
        at = Math.max(0, Math.min(panels.length - 1, i));
        panels.forEach(function (p, n) { p.classList.toggle("on", n === at); });
        crumbs.forEach(function (c, n) {
            c.classList.toggle("on", n === at);
            c.classList.toggle("done", n < at);
        });
        bar.style.width = ((at + 1) / panels.length * 100) + "%";
        backBtn.hidden = at === 0;
        nextBtn.hidden = at === panels.length - 1;
        sendBtn.hidden = at !== panels.length - 1;
        if (scroll !== false) {
            form.scrollIntoView({ block: "start", behavior: "smooth" });
        }
    }

    /* Only the fields on the current panel block moving forward. Requiring the
       whole form to validate before step two would be a wall. */
    function panelInvalid(i) {
        var all = [].slice.call(panels[i].querySelectorAll("input, select, textarea"));
        for (var k = 0; k < all.length; k++) {
            if (all[k].willValidate && !all[k].checkValidity()) { return all[k]; }
        }
        return null;
    }

    nextBtn.addEventListener("click", function () {
        var bad = panelInvalid(at);
        if (bad) { say("Please complete the highlighted field.", "error"); reveal(bad); return; }
        say("");
        show(at + 1);
    });

    backBtn.addEventListener("click", function () { say(""); show(at - 1); });

    crumbs.forEach(function (c) {
        c.addEventListener("click", function () { show(+c.dataset.go); });
    });

    show(0, false);

    /* --------------------------------------------------------- add a row -- */
    /* Education, certifications, employment and referees each start with the
       rows most people need. The rest are cloned from a <template> on request,
       which keeps 103 fields from being on screen at once. */
    form.addEventListener("click", function (event) {
        var button = event.target.closest(".add-row");
        if (!button) { return; }
        var box   = button.closest(".repeater");
        var rows  = box.querySelector(".rows");
        var count = rows.children.length;
        var max   = +box.dataset.max || 3;
        if (count >= max) { return; }

        var n = count + 1;
        var html = box.querySelector("template").innerHTML.split("__N__").join(n);
        var item = document.createElement("div");
        item.className = "row-item";
        item.dataset.row = n;
        item.innerHTML = '<span class="row-n">' + box.dataset.label + " " + n +
                         "</span>" + html;
        rows.appendChild(item);
        if (n + 1 > max) { button.hidden = true; }
        saveDraft();
    });

    /* -------------------------------------------------------- validation -- */
    function firstInvalid() {
        var all = fields();
        for (var i = 0; i < all.length; i++) {
            if (all[i].willValidate && !all[i].checkValidity()) { return all[i]; }
        }
        return null;
    }

    function reveal(el) {
        el.scrollIntoView({ block: "center", behavior: "smooth" });
        /* focus after the scroll so the browser does not fight it */
        setTimeout(function () { el.focus({ preventScroll: true }); }, 220);
        el.classList.add("invalid");
        el.addEventListener("input", function once() {
            el.classList.remove("invalid");
            el.removeEventListener("input", once);
        });
    }

    /* ------------------------------------------------------------ submit -- */
    form.addEventListener("submit", function (event) {
        event.preventDefault();

        var bad = firstInvalid();
        if (bad) {
            /* the offending field may be on a panel that is not showing, so
               open it before scrolling or the user sees nothing move */
            var owner = bad.closest(".step");
            if (owner) { show(panels.indexOf(owner)); }
            say("Please complete the highlighted field.", "error");
            reveal(bad);
            return;
        }

        var payload = {};

        fields().forEach(function (el) {
            if (!el.name) { return; }
            if (el.type === "checkbox") {
                if (el.checked) { payload[el.name] = el.value || "Yes"; }
                return;
            }
            var value = (el.value || "").trim();
            if (value) { payload[el.name] = value; }   /* skip the empties */
        });

        button.disabled = true;
        say("Sending your application…", "note");

        fetch(ENDPOINT, {
            method: "POST",
            headers: { "Content-Type": "application/json", Accept: "application/json" },
            body: JSON.stringify(payload)
        })
            .then(function (r) { return r.json(); })
            .then(function (result) {
                if (result && result.ok) {
                    try { sessionStorage.removeItem(STORE); } catch (e) {}
                    form.reset();
                    say("Thank you. Your application has been sent, and we will "
                        + "come back to you either way.", "ok");
                    form.scrollIntoView({ block: "start", behavior: "smooth" });
                } else {
                    button.disabled = false;
                    say("Something went wrong sending the form. Please email "
                        + "info@takwafoods.com instead.", "error");
                }
            })
            .catch(function () {
                button.disabled = false;
                say("Could not reach the server. Please check your connection, "
                    + "or email info@takwafoods.com.", "error");
            });
    });
})();
