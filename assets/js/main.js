/* Bratküche – kleine Helfer: Mobilmenü, Speisekarten-Filter, „Jetzt geöffnet“-Anzeige */
(function () {
  "use strict";

  document.documentElement.classList.add("js");

  /* ---------- Mobilmenü ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("hauptnavigation");

  function setMenu(open) {
    if (!toggle || !nav) return;
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
    window.matchMedia("(min-width: 881px)").addEventListener("change", function (mq) {
      if (mq.matches) setMenu(false);
    });
  }

  /* ---------- Speisekarte filtern ---------- */
  var chips = document.querySelectorAll(".chip[data-filter]");
  var grid = document.querySelector(".menu-grid");
  var groups = document.querySelectorAll(".menu-group[data-cat]");

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var filter = chip.getAttribute("data-filter");
      chips.forEach(function (c) { c.setAttribute("aria-pressed", String(c === chip)); });
      groups.forEach(function (g) {
        g.hidden = filter !== "alle" && g.getAttribute("data-cat") !== filter;
      });
      if (grid) grid.classList.toggle("is-filtered", filter !== "alle");
    });
  });

  /* ---------- Öffnungszeiten & Status ----------
     Die Zeiten werden aus der Tabelle (#zeiten) gelesen – dort anpassen.
     Gerechnet wird immer in deutscher Zeit (Europe/Berlin). */
  var DAY_NAMES = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"];

  function toMinutes(hhmm) {
    var p = String(hhmm || "").split(":");
    if (p.length !== 2) return null;
    return parseInt(p[0], 10) * 60 + parseInt(p[1], 10);
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

  var rows = document.querySelectorAll(".hours-table tr[data-day]");
  if (rows.length) {
    var schedule = {};
    rows.forEach(function (row) {
      var day = parseInt(row.getAttribute("data-day"), 10);
      var open = toMinutes(row.getAttribute("data-open"));
      var close = toMinutes(row.getAttribute("data-close"));
      schedule[day] = open !== null && close !== null
        ? { open: open, close: close, openText: row.getAttribute("data-open"), closeText: row.getAttribute("data-close") }
        : null;
    });

    var updateStatus = function () {
      var now = berlinNow();
      var today = schedule[now.day];
      var isOpen = false;
      var text;

      if (today && now.minutes >= today.open && now.minutes < today.close) {
        isOpen = true;
        text = "Jetzt geöffnet · bis " + today.closeText + " Uhr";
      } else if (today && now.minutes < today.open) {
        text = "Gerade geschlossen · öffnet heute um " + today.openText + " Uhr";
      } else {
        text = "Gerade geschlossen";
        for (var i = 1; i <= 7; i++) {
          var d = (now.day + i) % 7;
          if (schedule[d]) {
            var when = i === 1 ? "morgen" : "am " + DAY_NAMES[d];
            text = "Gerade geschlossen · öffnet " + when + " um " + schedule[d].openText + " Uhr";
            break;
          }
        }
      }

      document.querySelectorAll("[data-status]").forEach(function (el) {
        el.classList.toggle("is-open", isOpen);
        el.classList.toggle("is-closed", !isOpen);
        var t = el.querySelector(".status-text");
        if (t) t.textContent = text;
      });

      rows.forEach(function (row) {
        row.classList.toggle("is-today", parseInt(row.getAttribute("data-day"), 10) === now.day);
      });
    };

    updateStatus();
    setInterval(updateStatus, 60 * 1000);
  }

  /* ---------- Jahr in der Fußzeile ---------- */
  var year = String(new Date().getFullYear());
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = year; });
})();
