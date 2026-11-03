/* Die Bratküche – kleine Helfer: Mobilmenü und „Jetzt geöffnet“-Anzeige */
(function () {
  "use strict";

  document.documentElement.classList.add("js");

  /* ---------- Mobilmenü ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("hauptnavigation");

  function setMenu(open) {
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Menü schließen" : "Menü öffnen");
    nav.classList.toggle("is-open", open);
  }

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      setMenu(toggle.getAttribute("aria-expanded") !== "true");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) setMenu(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setMenu(false);
    });
    var wide = window.matchMedia("(min-width: 901px)");
    var onWide = function () { if (wide.matches) setMenu(false); };
    if (wide.addEventListener) wide.addEventListener("change", onWide);
  }

  /* ---------- Öffnungszeiten & Status ----------
     Die Zeiten stehen in der Tabelle (#zeiten) im Attribut data-hours,
     z. B. data-hours="11:00-15:00,17:00-20:00". Dort anpassen.
     Gerechnet wird immer in deutscher Zeit (Europe/Berlin). */
  var DAY_NAMES = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"];

  function toMinutes(hhmm) {
    var p = String(hhmm || "").trim().split(":");
    if (p.length !== 2) return null;
    var m = parseInt(p[0], 10) * 60 + parseInt(p[1], 10);
    return isNaN(m) ? null : m;
  }

  function parseHours(attr) {
    if (!attr) return [];
    return attr.split(",").map(function (range) {
      var parts = range.split("-");
      var open = toMinutes(parts[0]);
      var close = toMinutes(parts[1]);
      if (open === null || close === null) return null;
      return { open: open, close: close, openText: parts[0].trim(), closeText: parts[1].trim() };
    }).filter(Boolean).sort(function (a, b) { return a.open - b.open; });
  }

  function berlinNow() {
    var map = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
    try {
      var parts = new Intl.DateTimeFormat("en-GB", {
        timeZone: "Europe/Berlin",
        weekday: "short",
        hour: "2-digit",
        minute: "2-digit",
        hourCycle: "h23"
      }).formatToParts(new Date());
      var o = {};
      parts.forEach(function (p) { o[p.type] = p.value; });
      return { day: map[o.weekday], minutes: parseInt(o.hour, 10) * 60 + parseInt(o.minute, 10) };
    } catch (err) {
      var d = new Date();
      return { day: d.getDay(), minutes: d.getHours() * 60 + d.getMinutes() };
    }
  }

  function computeStatus(schedule, now) {
    var today = schedule[now.day] || [];
    var i;

    for (i = 0; i < today.length; i++) {
      if (now.minutes >= today[i].open && now.minutes < today[i].close) {
        return { state: "open", text: "Jetzt geöffnet · bis " + today[i].closeText + " Uhr" };
      }
    }
    for (i = 0; i < today.length; i++) {
      if (now.minutes < today[i].open) {
        if (i > 0) {
          return { state: "break", text: "Mittagspause · ab " + today[i].openText + " Uhr wieder offen" };
        }
        return { state: "closed", text: "Geschlossen · öffnet heute um " + today[i].openText + " Uhr" };
      }
    }
    for (i = 1; i <= 7; i++) {
      var d = (now.day + i) % 7;
      if (schedule[d] && schedule[d].length) {
        var when = i === 1 ? "morgen" : "am " + DAY_NAMES[d];
        return { state: "closed", text: "Geschlossen · öffnet " + when + " um " + schedule[d][0].openText + " Uhr" };
      }
    }
    return { state: "closed", text: "Gerade geschlossen" };
  }

  var rows = document.querySelectorAll(".hours-table tr[data-day]");
  if (rows.length) {
    var schedule = {};
    rows.forEach(function (row) {
      schedule[parseInt(row.getAttribute("data-day"), 10)] = parseHours(row.getAttribute("data-hours"));
    });

    var updateStatus = function () {
      var now = berlinNow();
      var status = computeStatus(schedule, now);

      document.querySelectorAll("[data-status]").forEach(function (el) {
        el.classList.toggle("is-open", status.state === "open");
        el.classList.toggle("is-break", status.state === "break");
        el.classList.toggle("is-closed", status.state === "closed");
        var t = el.querySelector(".status-text");
        if (t) t.textContent = status.text;
      });

      rows.forEach(function (row) {
        row.classList.toggle("is-today", parseInt(row.getAttribute("data-day"), 10) === now.day);
      });
    };

    updateStatus();
    setInterval(updateStatus, 60 * 1000);

    /* Für Tests: window.__bratkuecheStatus({ day: 1, minutes: 16 * 60 }) */
    window.__bratkuecheStatus = function (now) { return computeStatus(schedule, now); };
  }

  /* ---------- Jahr in der Fußzeile ---------- */
  var year = String(new Date().getFullYear());
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = year; });
})();
