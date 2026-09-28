/*
 * Runs pages (scripts/runpages.py): one run at a time, and a table you can filter and sort.
 *
 * Every run of the benchmark is on the page, one <section data-run-panel="<id>"> each, so the page works without
 * this script (all of them, one after the other). With it:
 *   - the "Agent run" picker ([data-runsel]) shows one run and hides the rest; the choice lives in the URL
 *     (?run=<id>), so a link to a run stays a link to that run; the benchmark's default run is shown when the URL
 *     names none. On the overview its first option, "All runs" (data-run=""), shows every run's card;
 *   - each run's table ([data-rt-bar] + table.rt, one <tbody> per task) filters on its chips (tasks with at least one
 *     trial in that state, or flagged: records missing, follow-up, host silent) and sorts on its menu, a benchmark's
 *     declared metrics included (option m<k>, data-m<k> on each task, data-dir asc for a distance). The warning
 *     chips above the table ([data-rt-filter]) set the same filter and scroll to the table;
 *   - a table that fits its column keeps its header in view while the page scrolls (.rt-wrap--fit); one that does
 *     not (many columns, a narrow screen) scrolls sideways instead, where a sticky header cannot work;
 *   - tasks excluded from the benchmark (tbody[data-x], state `excluded:`) stay last, under their heading
 *     (tbody[data-rt-sep]), whatever the sort; the heading hides when none of them is shown;
 *   - a run with excluded tasks has a "Count" switch ([data-scope-switch]): the numbers of the benchmark's own tasks
 *     ([data-scope-block="bench"], the default) or with the excluded ones ([data-scope-block="all"]).
 */
(function () {
  "use strict";

  function initTabs() {
    [].forEach.call(document.querySelectorAll("[data-runsel]"), function (root) {
      if (root.getAttribute("data-ready")) return;
      root.setAttribute("data-ready", "1");
      var tabs = [].slice.call(root.querySelectorAll("[data-run]"));
      var panels = [].slice.call(document.querySelectorAll("[data-run-panel]"));
      var ids = tabs.map(function (t) { return t.getAttribute("data-run"); });
      var fallback = root.hasAttribute("data-default") ? root.getAttribute("data-default") : ids[0];

      // a renamed run's former ids (data-aliases, from `formerly:` in data/agents/) pick the run they name now
      var aliases = {};
      try { aliases = JSON.parse(root.getAttribute("data-aliases") || "{}"); } catch (e) { aliases = {}; }

      function show(id, remember) {
        if (Object.prototype.hasOwnProperty.call(aliases, id)) { id = aliases[id]; remember = true; }
        if (ids.indexOf(id) < 0) id = fallback;
        tabs.forEach(function (t) {
          var on = t.getAttribute("data-run") === id;
          t.classList.toggle("is-on", on);
          t.setAttribute("aria-current", on ? "page" : "false");
        });
        panels.forEach(function (p) { p.hidden = id !== "" && p.getAttribute("data-run-panel") !== id; });
        fitTables();
        if (remember) {
          var params = new URLSearchParams(window.location.search);
          if (id === fallback) params.delete("run"); else params.set("run", id);
          var qs = params.toString();
          window.history.replaceState(null, "", window.location.pathname + (qs ? "?" + qs : "") + window.location.hash);
        }
      }

      tabs.forEach(function (t) {
        t.addEventListener("click", function (ev) {
          ev.preventDefault();
          show(t.getAttribute("data-run"), true);
        });
      });
      root.classList.add("runsel--js");
      var asked = new URLSearchParams(window.location.search).get("run");
      show(asked === null ? fallback : asked, false);
    });
  }

  var SORTS = {
    default: function (a, b) { return num(a, "i") - num(b, "i"); },
    title: function (a, b) { return a.getAttribute("data-title").localeCompare(b.getAttribute("data-title")); },
    cost: function (a, b) { return num(b, "cost") - num(a, "cost") || num(a, "i") - num(b, "i"); },
    time: function (a, b) { return num(b, "time") - num(a, "time") || num(a, "i") - num(b, "i"); },
    // tasks without a progress value (-1) go last
    prog: function (a, b) {
      var x = num(a, "prog"), y = num(b, "prog");
      return ((x < 0) - (y < 0)) || x - y || num(a, "i") - num(b, "i");
    }
  };

  function num(el, key) { return parseFloat(el.getAttribute("data-" + key)) || 0; }

  // A declared metric (data-m<k>): best first in its own direction; tasks without a value go last.
  function metricSort(key, dir) {
    return function (a, b) {
      var x = a.getAttribute("data-" + key), y = b.getAttribute("data-" + key);
      if (x === null || y === null) return (x === null) - (y === null) || num(a, "i") - num(b, "i");
      return dir * (parseFloat(x) - parseFloat(y)) || num(a, "i") - num(b, "i");
    };
  }

  function fitTables() {
    [].forEach.call(document.querySelectorAll(".rt-wrap"), function (w) {
      var t = w.querySelector("table");
      if (!t || !w.offsetParent) return;            // hidden (another run's panel): measured when shown
      w.classList.remove("rt-wrap--fit");
      if (t.offsetWidth <= w.clientWidth + 1) w.classList.add("rt-wrap--fit");
    });
  }

  function initTables() {
    [].forEach.call(document.querySelectorAll("[data-rt-bar]"), function (bar) {
      if (bar.getAttribute("data-ready")) return;
      bar.setAttribute("data-ready", "1");
      var panel = bar.closest("[data-run-panel]") || document;
      var table = bar.nextElementSibling && bar.nextElementSibling.querySelector("table.rt");
      if (!table) return;
      var groups = [].slice.call(table.querySelectorAll("tbody.rt-group"));
      var sep = table.querySelector("tbody[data-rt-sep]");
      function isX(g) { return g.hasAttribute("data-x") ? 1 : 0; }
      var chips = [].slice.call(bar.querySelectorAll("[data-f]"));
      var sortEl = bar.querySelector("[data-rt-sort]");
      var count = bar.querySelector("[data-rt-count]");
      var state = { f: "", sort: "default" };

      function apply() {
        var shown = 0, placed = false;
        groups.forEach(function (g) {
          var hit = !state.f || (" " + g.getAttribute("data-tags") + " ").indexOf(" " + state.f + " ") >= 0;
          g.hidden = !hit;
          if (hit) shown++;
        });
        var cmp = SORTS[state.sort];
        if (!cmp && /^m\d+$/.test(state.sort)) {
          var opt = sortEl && sortEl.querySelector('option[value="' + state.sort + '"]');
          cmp = metricSort(state.sort, opt && opt.getAttribute("data-dir") === "asc" ? 1 : -1);
        }
        cmp = cmp || SORTS.default;
        groups.slice().sort(function (a, b) { return (isX(a) - isX(b)) || cmp(a, b); }).forEach(function (g) {
          if (sep && isX(g) && sep.parentNode === table && !placed) { table.appendChild(sep); placed = true; }
          table.appendChild(g);
        });
        if (sep) sep.hidden = !groups.some(function (g) { return isX(g) && !g.hidden; });
        chips.forEach(function (c) { c.classList.toggle("is-on", c.getAttribute("data-f") === state.f); });
        if (count) count.textContent = state.f ? shown + " of " + groups.length + " tasks" : "";
      }

      chips.forEach(function (c) {
        c.addEventListener("click", function () {
          var f = c.getAttribute("data-f");
          state.f = state.f === f ? "" : f;
          apply();
        });
      });
      if (sortEl) sortEl.addEventListener("change", function () { state.sort = this.value; apply(); });
      [].forEach.call(panel.querySelectorAll("[data-rt-filter]"), function (b) {
        b.addEventListener("click", function () {
          state.f = b.getAttribute("data-rt-filter");
          apply();
          bar.scrollIntoView({ behavior: "smooth", block: "start" });
        });
      });
      bar.classList.add("rt-bar--js");
    });
  }

  function initScopes() {
    [].forEach.call(document.querySelectorAll("[data-scope-switch]"), function (sw) {
      if (sw.getAttribute("data-ready")) return;
      sw.setAttribute("data-ready", "1");
      var host = sw.parentNode;        // the run's panel or card: the switch and its two blocks are its children
      var opts = [].slice.call(sw.querySelectorAll("[data-scope]"));
      function show(key) {
        opts.forEach(function (o) {
          var on = o.getAttribute("data-scope") === key;
          o.classList.toggle("is-on", on);
          o.setAttribute("aria-pressed", on ? "true" : "false");
        });
        [].forEach.call(host.querySelectorAll("[data-scope-block]"), function (b) {
          if (b.parentNode === host) b.hidden = b.getAttribute("data-scope-block") !== key;
        });
        fitTables();
      }
      opts.forEach(function (o) { o.addEventListener("click", function () { show(o.getAttribute("data-scope")); }); });
      [].forEach.call(host.querySelectorAll("[data-scope-go]"), function (b) {
        b.addEventListener("click", function () { show(b.getAttribute("data-scope-go")); });
      });
    });
  }

  function init() { initTabs(); initTables(); initScopes(); fitTables(); }

  var resizeTimer;
  window.addEventListener("resize", function () { clearTimeout(resizeTimer); resizeTimer = setTimeout(fitTables, 150); });

  if (typeof window.document$ !== "undefined") window.document$.subscribe(init);
  else if (document.readyState !== "loading") init();
  else document.addEventListener("DOMContentLoaded", init);
})();
