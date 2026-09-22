/* ==========================================================================
   Contact form delivery.

   Every "Get in Touch" form on the site -- the one on the contact page and
   the copy in the footer of every other page -- used to POST to
   takwaweb.designersidhost.com/store-contact-message. That endpoint belonged
   to the old Laravel CMS and is gone: on takwafoods.com it returned 404, so
   every message a visitor sent was lost without either side being told.

   This script takes those forms over and posts them to contact-submit.php on
   this host, which emails each message to HR@, GYoussef@ and info@ via
   authenticated SMTP. It replaces the earlier Web3Forms route, which could
   deliver to only its one registered inbox. The endpoint is root-relative so
   the footer form works the same from /blog/ or /listing/ as from the root.
   ========================================================================== */
(function () {
    "use strict";

    var ENDPOINT = "/contact-submit.php";

    /* The site is bilingual, so messages follow whichever version the
       visitor is reading. */
    var STRINGS = {
        en: {
            sending: "Sending…",
            sent: "Thank you — your message has been sent. We'll reply within 24 hours.",
            failed: "Sorry, your message could not be sent. Please email info@takwafoods.com or call +963 942002287.",
            offline: "Please email info@takwafoods.com or call +963 942002287 — we'll get straight back to you.",
            send: "Send Message",
            eFix: "Please check the highlighted fields below.",
            eRequired: "This field is required.",
            eName: "Please enter your full name.",
            eEmail: "Enter a valid email address, like name@company.com",
            ePhoneRange: "Please enter 7 to 15 digits, with an optional + country code, like +963 912 345 678.",
            ePhoneChars: "Numbers only — you may start with + for a country code.",
            eShort: "Please write a little more.",
            eMessage: "Please tell us a bit more — at least 10 characters."
        },
        ar: {
            sending: "جارٍ الإرسال…",
            sent: "شكراً لكم — تم إرسال رسالتكم، وسنرد خلال 24 ساعة.",
            failed: "نعتذر، تعذّر إرسال رسالتكم. يرجى مراسلتنا على info@takwafoods.com أو الاتصال على +963 942002287.",
            offline: "يرجى مراسلتنا على info@takwafoods.com أو الاتصال على +963 942002287 — وسنعود إليكم فوراً.",
            send: "إرسال الرسالة",
            eFix: "يرجى مراجعة الحقول المحدّدة أدناه.",
            eRequired: "هذا الحقل مطلوب.",
            eName: "يرجى إدخال اسمكم الكامل.",
            eEmail: "أدخلوا بريداً إلكترونياً صحيحاً، مثل name@company.com",
            ePhoneRange: "يرجى إدخال 7 إلى 15 رقماً، مع رمز الدولة اختيارياً، مثل +963 912 345 678.",
            ePhoneChars: "أرقام فقط — يمكنكم البدء بعلامة + لرمز الدولة.",
            eShort: "يرجى كتابة تفاصيل أكثر.",
            eMessage: "يرجى إخبارنا بالمزيد — 10 أحرف على الأقل."
        }
    };

    var t = STRINGS[document.documentElement.lang === "ar" ? "ar" : "en"];

    function statusNode(form) {
        /* the contact page ships one of these; the footer copy does not */
        var el = form.querySelector("#msgSubmit, .form-status");
        if (!el) {
            el = document.createElement("div");
            el.className = "form-status";
            form.appendChild(el);
        }
        el.className = "form-status";
        el.style.marginTop = "14px";
        el.style.fontSize = "16px";
        el.style.lineHeight = "1.6";
        return el;
    }

    function say(form, message, ok) {
        var el = statusNode(form);
        el.textContent = message;
        el.style.color = ok ? "#1a7f5a" : "#c0392b";
    }

    /* ------------------------------------------------------------------
       Field rules.

       The browser's own checks are too loose to be useful here: type="email"
       accepts "a@b" with no dot, and "required" accepts a single space. Each
       field is therefore checked properly, and the reason is written under
       the field in the reader's own language rather than in a browser bubble
       that only appears on one field at a time.
       ------------------------------------------------------------------ */
    var LETTER = /[a-zA-Z؀-ۿ]/;                  /* Latin or Arabic */

    /* Must end in a real top-level domain. Requiring "a dot somewhere after
       the @" is not enough on its own -- it lets "name@gmail." through. */
    var EMAIL = /^[^\s@]+@[^\s@.]+(\.[^\s@.]+)*\.[a-zA-Z]{2,}$/;

    /* E.164 allows up to 15 digits; 7 is the shortest national number in
       use. The form used to insist on exactly 10, which fitted a Syrian
       mobile and rejected every international buyer. */
    var PHONE_MIN = 7;
    var PHONE_MAX = 15;

    function digits(value) {
        return (value || "").replace(/\D/g, "");
    }

    /* Only digits, and a + allowed at the front for a country code. Anything
       else is dropped as it is typed, so letters cannot be entered at all
       rather than being rejected after the fact. */
    function tidyPhone(value) {
        var plus = value.charAt(0) === "+" ? "+" : "";
        /* keep the separators people type (spaces, dashes, brackets, dots),
           drop everything else, and stop accepting digits past the E.164 cap */
        var kept = "", count = 0;
        var body = value.slice(plus ? 1 : 0);
        for (var i = 0; i < body.length; i++) {
            var ch = body.charAt(i);
            if (/\d/.test(ch)) {
                if (count >= PHONE_MAX) { break; }
                count++; kept += ch;
            } else if (/[\s()\-.]/.test(ch)) {
                kept += ch;
            }
        }
        return plus + kept;
    }

    function checkPhone(value) {
        var raw = (value || "").trim();
        if (!raw) { return "required"; }
        if (/[^\d+\s()\-.]/.test(raw)) { return "chars"; }
        var n = digits(raw).length;
        return (n >= PHONE_MIN && n <= PHONE_MAX) ? null : "range";
    }

    var RULES = {
        name: function (v) {
            v = v.trim();
            if (!v) { return t.eRequired; }
            if (v.length < 2 || !LETTER.test(v)) { return t.eName; }
            return null;
        },
        email: function (v) {
            v = v.trim();
            if (!v) { return t.eRequired; }
            return EMAIL.test(v) ? null : t.eEmail;
        },
        phone: function (v) {
            var why = checkPhone(v);
            if (why === "required") { return t.eRequired; }
            if (why === "chars") { return t.ePhoneChars; }
            if (why === "range") { return t.ePhoneRange; }
            return null;
        },
        subject: function (v) {
            v = v.trim();
            if (!v) { return t.eRequired; }
            return v.length < 2 ? t.eShort : null;
        },
        company: function (v) {
            v = v.trim();
            if (!v) { return t.eRequired; }
            return v.length < 2 ? t.eShort : null;
        },
        message: function (v) {
            v = v.trim();
            if (!v) { return t.eRequired; }
            return v.length < 10 ? t.eMessage : null;
        }
    };

    function errorNode(field) {
        var el = field.parentNode.querySelector(".field-error");
        if (!el) {
            el = document.createElement("span");
            el.className = "field-error";
            el.style.cssText = "display:block;color:#c0392b;font-size:14px;" +
                               "line-height:1.5;margin-top:6px";
            field.parentNode.appendChild(el);
        }
        return el;
    }

    function clearError(field) {
        var el = field.parentNode.querySelector(".field-error");
        if (el) { el.textContent = ""; }
        field.style.borderColor = "";
    }

    function validate(form) {
        var first = null;
        Object.keys(RULES).forEach(function (name) {
            var field = form.querySelector('[name="' + name + '"]');
            if (!field) { return; }
            var problem = RULES[name](field.value);
            if (problem) {
                errorNode(field).textContent = problem;
                field.style.borderColor = "#c0392b";
                if (!first) { first = field; }
            } else {
                clearError(field);
            }
        });
        if (first) { first.focus(); }
        return !first;
    }

    function handle(form) {
        var tel = form.querySelector('[name="phone"]');
        if (tel) {
            tel.setAttribute("inputmode", "tel");
            tel.setAttribute("maxlength", "24");
            tel.addEventListener("input", function () {
                var tidy = tidyPhone(tel.value);
                if (tidy !== tel.value) {
                    var atEnd = tel.selectionStart === tel.value.length;
                    tel.value = tidy;
                    if (atEnd) { tel.setSelectionRange(tidy.length, tidy.length); }
                }
            });
        }

        /* clear a field's complaint as soon as the visitor starts fixing it */
        form.addEventListener("input", function (event) {
            if (event.target && event.target.name in RULES) {
                clearError(event.target);
            }
        });

        form.addEventListener("submit", function (event) {
            event.preventDefault();

            if (!validate(form)) {
                say(form, t.eFix, false);
                return;
            }

            var button = form.querySelector('button[type="submit"], .btn-default');
            var label = button ? button.textContent : null;
            if (button) {
                button.disabled = true;
                button.textContent = t.sending;
            }
            say(form, t.sending, true);

            var data = {};
            new FormData(form).forEach(function (value, key) {
                /* _token is a leftover Laravel CSRF field and means nothing now */
                if (key !== "_token") { data[key] = value; }
            });
            if (!data.subject) { data.subject = "New message from takwafoods.com"; }

            fetch(ENDPOINT, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(data)
            }).then(function (response) {
                return response.json();
            }).then(function (result) {
                if (result && result.success) {
                    form.reset();
                    say(form, t.sent, true);
                } else {
                    say(form, t.failed, false);
                }
            }).catch(function () {
                say(form, t.failed, false);
            }).then(function () {
                if (button) {
                    button.disabled = false;
                    button.textContent = label || t.send;
                }
            });
        });
    }

    function init() {
        var forms = document.querySelectorAll('form[action*="store-contact-message"], form[data-contact-form]');
        for (var i = 0; i < forms.length; i++) { handle(forms[i]); }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
