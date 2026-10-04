/*
 * Task list: browse, filter, watch demos at speed, and edit tags in place.
 *
 * Resource budget is the design constraint. 100 rows × a <video> element each
 * is far too much for the browser, and it was also what made the first paint
 * slow. Two mechanisms keep it cheap:
 *
 *   1. Rows render in chunks. The first chunk paints immediately; the rest
 *      append as a sentinel scrolls into view.
 *   2. A row shows a poster <img> until it is near the viewport, at which
 *      point it is upgraded to a real <video preload="none"> — controls and
 *      scrubbing, but no bytes fetched until play. Rows that scroll far away
 *      revert to the poster, unless they are playing.
 *
 * Net effect: a handful of media elements alive at a time, no matter how long
 * the list is.
 *
 * Editing is single-user and local by design: the page talks to a small edit
 * daemon on localhost (scripts/editd.py). When it is not running, the site is
 * simply read-only.
 */

(function () {
  "use strict";

  var FACETS = ["scene", "room", "status", "runstate", "difficulty", "capability", "domain"];
  var SPEED_KEY = "rb-speed";
  var CHUNK = 12;          // rows painted per batch
  var NEAR = "600px";      // how early to upgrade a poster to a video

  var STATUSES = ["keep", "drop", "needs-review", "pending"];
  var DIFFICULTIES = ["unrated", "easy", "medium", "hard", "extreme"];

  // The run the pills, the Run state filter and the default order are about: one of the benchmark's runs
  // (state/runs/<benchmark>.yml), picked in the task list's Run menu; its default run until then.
  var RUN = "";
  function runOf(t) { return (t.runs && t.runs[RUN]) || null; }

  // Where editing lives, according to the page itself.
  //
  // `make edit` runs mkdocs on an internal port behind a front door that also
  // serves /api/*. Land on the internal port — an old tab, a URL mkdocs printed
  // — and /api/health is a 404, so editing is off with no way to tell that from
  // a published read-only site. `site_url` cannot tell it apart either, because
  // `mkdocs serve` overwrites that with its own dev address — so the Makefile
  // passes the front door in as RB_FRONT_URL and scripts/hooks.py writes it into
  // every page. The page therefore knows the address that works even while it is
  // being served from the one that does not. Absent in a published build.
  function frontDoor() {
    var meta = document.querySelector('meta[name="rb-front"]');
    if (!meta || !meta.content) return "";
    try {
      var url = new URL(meta.content, window.location.href);
      return url.origin === window.location.origin ? "" : url.origin;
    } catch (e) { return ""; }
  }

  var wrongDoor = "";

  // The public site (scripts/sitemode.py writes <meta name="rb-public">) is read-only: no Edit button, and no probe
  // for the local edit daemon, which only exists under `make edit`.
  var PUBLIC = !!document.querySelector('meta[name="rb-public"]');

  function esc(v) {
    return String(v == null ? "" : v)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function matches(t, s) {
    if (s.scene && t.scene !== s.scene) return false;
    if (s.room && t.rooms.indexOf(s.room) === -1) return false;
    if (s.status && t.status !== s.status) return false;
    if (s.difficulty && t.difficulty !== s.difficulty) return false;
    if (s.capability && t.capIds.indexOf(s.capability) === -1) return false;
    if (s.domain && t.capIds.indexOf(s.domain) === -1) return false;
    if (s.runstate && ((t.runTags || {})[RUN] || []).indexOf(s.runstate) === -1) return false;
    if (s.q) {
      var hay = (t.title + " " + t.instruction + " " + t.id).toLowerCase();
      if (hay.indexOf(s.q) === -1) return false;
    }
    return true;
  }

  // Default order (user, 2026-09-25), key by key, computed at build time for every run (scripts/runview.py
  // default_rank): 0. tasks excluded from the benchmark (state `excluded:`) last; 1. whether it runs: in the run on
  // show -> not built for it -> removed (a benchmark without a run: keep -> undecided -> drop); 2. more modes
  // finished first; 3. more modes running first; 4. difficulty, easy -> extreme; then A-Z.
  function orderOf(t) { return (t.order && (t.order[RUN] || t.order[""])) || []; }
  var SORTS = {
    review: function (a, b) {
      var x = orderOf(a), y = orderOf(b);
      for (var i = 0; i < Math.max(x.length, y.length); i++) {
        if ((x[i] || 0) !== (y[i] || 0)) return (x[i] || 0) - (y[i] || 0);
      }
      return a.title.localeCompare(b.title);
    },
    title: function (a, b) { return a.title.localeCompare(b.title); },
    "duration-asc": function (a, b) { return a.duration - b.duration; },
    "duration-desc": function (a, b) { return b.duration - a.duration; },
    // The run on show: what needs a look first (stalled, errors, running), removed tasks last.
    run: function (a, b) {
      return (((a.runRank || {})[RUN] || 0) - ((b.runRank || {})[RUN] || 0)) || a.title.localeCompare(b.title);
    }
  };

  function fmtMinutes(ms) {
    var m = Math.max(0, Math.round(ms / 60000));
    return m >= 60 ? Math.floor(m / 60) + "h " + String(m % 60).padStart(2, "0") + "m" : m + "m";
  }

  // One pill per mode of the run on show (scripts/import_runs.py), plus the log check.
  // A running pill counts its minutes from the trial's start, so it stays right between rebuilds.
  function runHtml(t) {
    var run = runOf(t);
    if (!run) return "";
    if (!run.in) {
      return run.removed
        ? '<span class="rpill rpill--removed" title="' + esc(run.reason) + '">removed</span>'
        : '<span class="rpill rpill--outside" title="' + esc(run.reason) + '">not in run</span>';
    }
    return run.modes.map(function (m) {
      var since = m.active && m.started
        ? ' <span data-since>' + fmtMinutes(Date.now() - Date.parse(m.started)) + "</span>" : "";
      var logs = m.logs === "n/a" ? "" :
        '<i class="rpill__logs rpill__logs--' + esc(m.logs) + '" title="' +
        esc(m.logs === "ok" ? "logs saved so far: complete" : "missing: " + m.missing.join(", ")) + '">' +
        (m.logs === "ok" ? "logs ✓" : "logs !") + "</i>";
      var tag = m.log ? "a" : "span";
      return "<" + tag + ' class="rpill rpill--' + esc(m.state) + '"' + (m.log ? ' href="' + esc(m.log) + '"' : "") +
        (since ? ' data-started="' + esc(m.started) + '"' : "") + ' title="' + esc(m.title) + '"><b>' +
        esc(m.short) + "</b>" + esc(m.label) + since + logs + "</" + tag + ">";
    }).join("");
  }

  function fmtDuration(s) {
    if (!s) return "—";
    return Math.floor(s / 60) + "m " + String(s % 60).padStart(2, "0") + "s";
  }

  /* ---------------------------------------------------------------- markup */

  function posterHtml(t) {
    if (!t.src && t.watch) {
      // The public build links this benchmark's demos to the video upstream publishes (scripts/sitemode.py).
      return '<div class="row__missing row__missing--watch">' +
        (t.poster ? '<img src="' + esc(t.poster) + '" alt="" loading="lazy">' : "") +
        '<a href="' + esc(t.watch) + '" target="_blank" rel="noopener">Watch the official demo &#8599;</a></div>';
    }
    if (!t.src) {
      var why = t.published
        ? "demo not downloaded<code>make demos</code>"
        : "no upstream video<code>scene shown</code>";
      // With no video upstream the still IS the content, so show it at full
      // strength with the caption on a strip, rather than dimmed behind text.
      var cls = !t.published && t.poster ? "row__missing row__missing--scene" : "row__missing";
      return '<div class="' + cls + '">' +
        (t.poster ? '<img src="' + esc(t.poster) + '" alt="" loading="lazy">' : "") +
        "<span>" + why + "</span></div>";
    }
    return '<img class="row__poster" src="' + esc(t.poster) + '" alt="" loading="lazy">' +
      '<button class="row__play" type="button" aria-label="Play demo: ' + esc(t.title) + '"></button>';
  }

  function rowHtml(t) {
    // The display tags: Capability first, then Task Domain (the server sends them in that order); the group colours
    // the chip.
    var labels = t.caps.length
      ? t.caps.map(function (c, i) {
          var g = (t.capGroups || [])[i];
          return '<span class="chip' + (g ? " chip--" + esc(g) : "") + '">' + esc(c) + "</span>";
        }).join("")
      : '<span class="chip chip--gap">untagged</span>';

    var facts = [t.roomLabel || "—", t.scene, fmtDuration(t.duration)];
    if (t.owner) facts.push("@" + t.owner);

    var run = runOf(t);
    var out = run && !run.in && run.removed;     // removed tasks read grey; ones not built yet do not
    // Excluded from the final benchmark (state `excluded:`, the owner's call): grey, last, its own label; its runs stay.
    var excl = t.excluded;
    return '<article class="row row--' + esc(t.status) + (out ? " row--out" : "") + (excl ? " row--excluded" : "") +
        '" data-id="' + esc(t.id) + '">' +
      '<div class="row__main">' +
        '<div class="row__head">' +
          '<a class="row__title" href="' + esc(t.url) + '">' + esc(t.title) + "</a>" +
          (excl ? '<span class="pill pill--excluded" title="' + esc("Excluded from the benchmark: " + excl) +
            '">excluded</span>' : "") +
          '<span class="pill pill--' + esc(t.status) + '">' + esc(t.status) + "</span>" +
          (t.difficulty && t.difficulty !== "unrated"
            ? '<span class="pill pill--d-' + esc(t.difficulty) + '">' + esc(t.difficulty) + "</span>"
            : "") +
          runHtml(t) +
        "</div>" +
        (excl ? '<p class="row__out row__excl">Excluded from the benchmark: ' + esc(excl) + "</p>" : "") +
        (run && !run.in
          ? '<p class="row__out">' + (out ? "Removed from this run: " : "Not in this run: ") +
            esc(run.reason) + "</p>"
          : "") +
        '<p class="row__text">' +
          (t.instruction ? esc(t.instruction) : "<em>No instruction published upstream.</em>") +
        "</p>" +
        '<div class="row__labels">' + labels + "</div>" +
        '<div class="row__foot">' + facts.map(esc).join(" &middot; ") +
          '<span class="row__actions">' +
            (PUBLIC ? "" : '<button class="row__edit" type="button" data-edit>Edit</button>') +
            '<a class="row__more" href="' + esc(t.url) + '">Open task &rarr;</a>' +
          "</span>" +
        "</div>" +
      "</div>" +
      '<div class="row__media" data-media style="aspect-ratio:' +
        esc(t.aspect || "1 / 1") + '">' + posterHtml(t) + "</div>" +
      "</article>";
  }

  /* ------------------------------------------------------------------ init */

  function init() {
    var root = document.querySelector("[data-tasklist]");
    var data = document.getElementById("tl-data");
    if (!root || !data) return;

    var tasks, runsMeta = [];
    try { tasks = JSON.parse(data.textContent); } catch (e) { return; }
    try { runsMeta = JSON.parse((document.getElementById("tl-runs") || {}).textContent || "[]"); } catch (e) { /* none */ }
    var runSel = root.querySelector('[data-role="run"]');
    var byId = {};
    tasks.forEach(function (t) { byId[t.id] = t; });

    var rows = root.querySelector('[data-role="rows"]');
    var count = root.querySelector('[data-role="count"]');
    var empty = root.querySelector('[data-role="empty"]');
    var search = root.querySelector('[data-role="search"]');
    var sortEl = root.querySelector('[data-role="sort"]');
    var reset = root.querySelector('[data-role="reset"]');
    var searchGo = root.querySelector('[data-role="search-go"]');
    var speedBtns = [].slice.call(root.querySelectorAll("[data-speed]"));
    var selects = {};
    FACETS.forEach(function (f) { selects[f] = root.querySelector('[data-facet="' + f + '"]'); });

    var speed = 2;
    try {
      var saved = parseFloat(window.localStorage.getItem(SPEED_KEY));
      if (saved > 0) speed = saved;
    } catch (e) { /* private mode */ }

    var state = { q: "", sort: "review" };
    FACETS.forEach(function (f) { state[f] = ""; });

    var params = new URLSearchParams(window.location.search);
    var defaultRun = runsMeta.length ? runsMeta[0].id : "";
    RUN = defaultRun;
    if (params.get("run") && runsMeta.some(function (r) { return r.id === params.get("run"); })) RUN = params.get("run");
    if (runSel) runSel.value = RUN;
    fillRunStates();
    FACETS.forEach(function (f) {
      var v = params.get(f);
      if (v && selects[f]) { state[f] = v; selects[f].value = v; }
    });
    if (params.get("q")) { state.q = params.get("q").toLowerCase(); search.value = params.get("q"); }
    if (params.get("sort") && SORTS[params.get("sort")]) state.sort = params.get("sort");
    sortEl.value = state.sort;

    // The Run state filter lists the states of the run on show.
    function fillRunStates() {
      var sel = selects.runstate, meta = runsMeta.filter(function (r) { return r.id === RUN; })[0];
      if (!sel || !meta) return;
      var label = sel.options.length ? sel.options[0].textContent : "Run state: any";
      sel.innerHTML = '<option value="">' + esc(label) + "</option>" + meta.values.map(function (v) {
        return '<option value="' + esc(v[0]) + '">' + esc(v[1]) + "</option>";
      }).join("");
      if (state.runstate && !meta.values.some(function (v) { return v[0] === state.runstate; })) state.runstate = "";
      sel.value = state.runstate || "";
    }

    function syncUrl() {
      var next = new URLSearchParams();
      if (RUN && RUN !== defaultRun) next.set("run", RUN);
      FACETS.forEach(function (f) { if (state[f]) next.set(f, state[f]); });
      if (state.q) next.set("q", state.q);
      if (state.sort !== "review") next.set("sort", state.sort);
      var qs = next.toString();
      window.history.replaceState(null, "",
        window.location.pathname + (qs ? "?" + qs : "") + window.location.hash);
    }

    /* ------------------------------------------------- media, lazily mounted */

    var playing = null;

    function toPoster(media) {
      var t = byId[media.closest(".row").getAttribute("data-id")];
      if (!t || !t.src) return;
      if (playing === media) playing = null;
      media.innerHTML = posterHtml(t);
      media.removeAttribute("data-live");
    }

    function toVideo(media, autoplay) {
      var t = byId[media.closest(".row").getAttribute("data-id")];
      if (!t || !t.src || media.getAttribute("data-live")) return null;
      media.innerHTML = '<video class="row__video" preload="none" controls playsinline' +
        (t.poster ? ' poster="' + esc(t.poster) + '"' : "") +
        ' src="' + esc(t.src) + '"></video>';
      media.setAttribute("data-live", "1");
      var v = media.querySelector("video");
      v.playbackRate = speed;
      if (autoplay) { playing = media; v.play().catch(function () { /* blocked */ }); }
      return v;
    }

    // Upgrade near-viewport rows to real players; retire far ones.
    var io = null;
    if ("IntersectionObserver" in window) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            toVideo(e.target, false);
          } else if (e.target !== playing) {
            toPoster(e.target);
          }
        });
      }, { rootMargin: NEAR + " 0px" });
    }

    function observeMedia(scope) {
      if (!io) return;
      [].forEach.call(scope.querySelectorAll("[data-media]"), function (m) { io.observe(m); });
    }

    /* -------------------------------------------------- chunked row painting */

    var visible = [];
    var painted = 0;
    var sentinel = document.createElement("div");
    sentinel.className = "tl__sentinel";
    var sentinelIO = null;

    function paintMore() {
      if (painted >= visible.length) {
        if (sentinel.parentNode) sentinel.parentNode.removeChild(sentinel);
        return;
      }
      var slice = visible.slice(painted, painted + CHUNK);
      painted += slice.length;
      var frag = document.createElement("div");
      frag.innerHTML = slice.map(rowHtml).join("");
      while (frag.firstChild) rows.insertBefore(frag.firstChild, sentinel);
      observeMedia(rows);
      showEditButtons();
      if (painted < visible.length) {
        rows.appendChild(sentinel);
      } else if (sentinel.parentNode) {
        sentinel.parentNode.removeChild(sentinel);
      }
    }

    if ("IntersectionObserver" in window) {
      sentinelIO = new IntersectionObserver(function (entries) {
        if (entries.some(function (e) { return e.isIntersecting; })) paintMore();
      }, { rootMargin: "800px 0px" });
      sentinelIO.observe(sentinel);
    }

    function render() {
      if (io) [].forEach.call(rows.querySelectorAll("[data-media]"), function (m) { io.unobserve(m); });
      playing = null;
      visible = tasks.filter(function (t) { return matches(t, state); });
      visible.sort(SORTS[state.sort] || SORTS.review);

      rows.innerHTML = "";
      painted = 0;
      rows.appendChild(sentinel);
      paintMore();
      if (!sentinelIO && painted < visible.length) {
        while (painted < visible.length) paintMore();   // no IO: just paint all
      }

      empty.hidden = visible.length !== 0;
      var untagged = visible.filter(function (t) { return !t.caps.length; }).length;
      var missing = visible.filter(function (t) { return !t.src && t.published && !t.watch; }).length;
      var linked = visible.filter(function (t) { return !t.src && t.watch; }).length;
      var novideo = visible.filter(function (t) { return !t.src && !t.published; }).length;
      // Tasks excluded from the benchmark are counted apart ("82 of 82 tasks + 9 excluded"), their runs included.
      var nx = tasks.filter(function (t) { return t.excluded; }).length;
      var vx = visible.filter(function (t) { return t.excluded; }).length;
      var parts = [(visible.length - vx) + " of " + (tasks.length - nx) + " tasks" +
        (nx ? " + " + (vx === nx ? nx : vx + " of " + nx) + " excluded" : "")];
      if (untagged) parts.push(untagged + " untagged");
      if (missing) parts.push(missing + " demos not downloaded");
      if (linked) parts.push(linked + " demos link to the official videos");
      if (novideo) parts.push(novideo + " without an upstream video");
      var runs = [];
      // trials we stopped (state/runs/ `stopped:`), do not count (`not_counted:`) or withdrew (`withdrawn:`) count in
      // no statistic
      visible.forEach(function (t) {
        var r = runOf(t);
        if (r && r.in) runs = runs.concat(r.modes.filter(function (m) {
          return m.state !== "stopped" && m.state !== "uncounted" && m.state !== "withdrawn";
        }));
      });
      if (runs.length) {
        var n = function (f) { return runs.filter(f).length; };
        var xr = visible.some(function (t) { var r = runOf(t); return t.excluded && r && r.in; });
        parts.push("run" + (xr ? " (excluded tasks included)" : "") + ": " +
          n(function (m) { return m.state === "success" || m.state === "failed" || m.state === "error"; }) +
          "/" + runs.length + " trials done (" + n(function (m) { return m.state === "success"; }) + " ✓), " +
          n(function (m) { return m.active; }) + " running");
      }
      var removed = visible.filter(function (t) { var r = runOf(t); return r && !r.in && r.removed; }).length;
      var outside = visible.filter(function (t) { var r = runOf(t); return r && !r.in && !r.removed; }).length;
      if (outside) parts.push(outside + " not in the run");
      if (removed) parts.push(removed + " removed");
      count.textContent = parts.join(" · ");
      paintSpeed();
      syncUrl();
    }

    function paintSpeed() {
      speedBtns.forEach(function (b) {
        b.classList.toggle("is-on", parseFloat(b.getAttribute("data-speed")) === speed);
      });
      [].forEach.call(rows.querySelectorAll("video"), function (v) { v.playbackRate = speed; });
    }

    /* --------------------------------------------------------------- events */

    rows.addEventListener("click", function (ev) {
      var play = ev.target.closest && ev.target.closest(".row__play");
      if (play) {
        ev.preventDefault();
        var media = play.closest("[data-media]");
        if (playing && playing !== media) toPoster(playing);
        toVideo(media, true);
        return;
      }
      var edit = ev.target.closest && ev.target.closest("[data-edit]");
      if (edit) {
        ev.preventDefault();
        if (!editEnabled) {
          if (wrongDoor) {
            window.location.href = wrongDoor + window.location.pathname + window.location.search;
            return;
          }
          edit.textContent = "run `make edit`";
          setTimeout(function () { edit.textContent = "Edit"; }, 2200);
          return;
        }
        openEditor(edit.closest(".row"));
      }
    });

    rows.addEventListener("play", function (ev) {
      var v = ev.target;
      if (!v || v.tagName !== "VIDEO") return;
      v.playbackRate = speed;
      playing = v.closest("[data-media]");
      [].forEach.call(rows.querySelectorAll("video"), function (o) {
        if (o !== v && !o.paused) o.pause();
      });
    }, true);

    speedBtns.forEach(function (b) {
      b.addEventListener("click", function () {
        speed = parseFloat(b.getAttribute("data-speed")) || 1;
        try { window.localStorage.setItem(SPEED_KEY, String(speed)); } catch (e) { /* ignore */ }
        paintSpeed();
      });
    });

    FACETS.forEach(function (f) {
      if (!selects[f]) return;
      selects[f].addEventListener("change", function () { state[f] = this.value; render(); });
    });

    var timer = null;
    search.addEventListener("input", function () {
      var v = this.value.toLowerCase();
      clearTimeout(timer);
      timer = setTimeout(function () { state.q = v; render(); }, 120);
    });

    sortEl.addEventListener("change", function () { state.sort = this.value; render(); });

    if (runSel) runSel.addEventListener("change", function () { RUN = this.value; fillRunStates(); render(); });

    function runSearch() {
      clearTimeout(timer);
      state.q = search.value.toLowerCase();
      render();
    }
    if (searchGo) searchGo.addEventListener("click", runSearch);
    search.addEventListener("keydown", function (ev) {
      if (ev.key === "Enter") { ev.preventDefault(); runSearch(); }
    });

    reset.addEventListener("click", function () {
      RUN = defaultRun; if (runSel) runSel.value = RUN; fillRunStates();
      FACETS.forEach(function (f) { state[f] = ""; if (selects[f]) selects[f].value = ""; });
      state.q = ""; search.value = "";
      state.sort = "review"; sortEl.value = "review";
      render();
    });

    /* ----------------------------------------------------- local edit daemon */

    var editEnabled = false;
    var taxonomy = null;

    // The button is always present: hiding it made the feature undiscoverable.
    // Without the daemon it explains how to turn editing on.
    function showEditButtons() {
      [].forEach.call(rows.querySelectorAll("[data-edit]"), function (b) {
        b.classList.toggle("row__edit--live", editEnabled);
        b.title = editEnabled
          ? "Edit status and tags"
          : wrongDoor
            ? "This is the preview port — click to open " + wrongDoor + ", where editing is on"
            : "Run `make edit` to enable editing";
      });
    }

    window.rbEdit = {
      api: null,
      enable: function (base, tax) {
        this.api = base; taxonomy = tax; editEnabled = true; showEditButtons();
        root.classList.add("tl--editable");
      }
    };

    function openEditor(row) {
      if (!editEnabled) return;
      var id = row.getAttribute("data-id");
      var t = byId[id];
      if (row.querySelector(".ed")) { row.querySelector(".ed").remove(); return; }

      // Tags the task's annotated BEHAVIOR skills imply, so the common case
      // is confirming a suggestion rather than reading the whole vocabulary.
      var suggested = {};
      (t.skills || []).forEach(function (sk) {
        ((taxonomy.skillMap || {})[sk] || []).forEach(function (id) { suggested[id] = true; });
      });

      var groups = taxonomy.capabilities.map(function (grp) {
        var boxes = (grp.subcapabilities || []).map(function (c) {
          var on = t.capIds.indexOf(c.id) !== -1;
          var hint = suggested[c.id] && !on ? " ed__tag--sug" : "";
          return '<button type="button" class="ed__tag' + (on ? " is-on" : "") + hint +
            '" data-label="' + esc(c.id) + '">' + esc(c.name) +
            (suggested[c.id] ? '<i title="implied by this task\u2019s skills">\u00b7</i>' : "") +
            "</button>";
        }).join("");
        return '<div class="ed__grp ed__grp--' + esc(grp.id) + '" data-group="' + esc(grp.id) + '"><b>' +
          esc(grp.name) + "</b><div class=\"ed__tags\">" + boxes + "</div></div>";
      }).join("");

      var el = document.createElement("div");
      el.className = "ed";
      el.innerHTML =
        '<div class="ed__row"><span>Status</span><span class="ed__seg" data-ed-status>' +
          STATUSES.map(function (s) {
            return '<button type="button" data-v="' + s + '"' +
              (t.status === s ? ' class="is-on"' : "") + ">" + s + "</button>";
          }).join("") + "</span></div>" +
        '<div class="ed__row"><span>Difficulty</span><span class="ed__seg" data-ed-diff>' +
          DIFFICULTIES.map(function (d) {
            return '<button type="button" data-v="' + d + '"' +
              (t.difficulty === d ? ' class="is-on"' : "") + ">" + d + "</button>";
          }).join("") + "</span></div>" +
        '<div class="ed__caps">' + groups + "</div>" +
        '<div class="ed__row"><span>New tag</span>' +
          '<select class="ed__new ed__new--group" data-ed-group aria-label="Group of the new tag">' +
            taxonomy.capabilities.map(function (grp) {
              return '<option value="' + esc(grp.id) + '">' + esc(grp.name) + "</option>";
            }).join("") + "</select>" +
          '<input class="ed__new" type="text" placeholder="e.g. Reflective surfaces" data-ed-new>' +
          '<button type="button" class="ed__add" data-ed-add>Add &amp; tag</button></div>' +
        '<div class="ed__foot"><span class="ed__msg" data-ed-msg></span>' +
          '<button type="button" class="ed__cancel" data-ed-cancel>Cancel</button>' +
          '<button type="button" class="ed__save" data-ed-save>Save</button></div>';
      row.querySelector(".row__main").appendChild(el);

      var pick = { status: t.status, difficulty: t.difficulty };
      el.querySelectorAll("[data-ed-status] button, [data-ed-diff] button").forEach(function (b) {
        b.addEventListener("click", function () {
          var seg = b.parentNode;
          seg.querySelectorAll("button").forEach(function (o) { o.classList.remove("is-on"); });
          b.classList.add("is-on");
          if (seg.hasAttribute("data-ed-status")) pick.status = b.getAttribute("data-v");
          else pick.difficulty = b.getAttribute("data-v");
        });
      });

      el.querySelectorAll(".ed__tag").forEach(function (b) {
        b.addEventListener("click", function () {
          b.classList.toggle("is-on");
          b.classList.remove("ed__tag--sug");
        });
      });

      function chosen() {
        return [].slice.call(el.querySelectorAll(".ed__tag.is-on"))
          .map(function (b) { return b.getAttribute("data-label"); });
      }

      var msg = el.querySelector("[data-ed-msg]");

      el.querySelector("[data-ed-cancel]").addEventListener("click", function () { el.remove(); });

      el.querySelector("[data-ed-add]").addEventListener("click", function () {
        var name = el.querySelector("[data-ed-new]").value.trim();
        if (!name) return;
        msg.textContent = "adding…";
        fetch(window.rbEdit.api + "/api/capability", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: name, parent: el.querySelector("[data-ed-group]").value })
        }).then(function (r) { return r.json(); }).then(function (res) {
          if (!res.ok) { msg.textContent = res.error || "failed"; return; }
          taxonomy = res.taxonomy;
          msg.textContent = "added " + res.id + " — reload to see it everywhere";
          var host = el.querySelector('.ed__grp[data-group="' + res.parent + '"] .ed__tags') ||
            el.querySelector(".ed__grp:last-child .ed__tags");
          if (host) {
            var b = document.createElement("button");
            b.type = "button";
            b.className = "ed__tag is-on";
            b.setAttribute("data-label", res.id);
            b.textContent = name;
            b.addEventListener("click", function () { b.classList.toggle("is-on"); });
            host.appendChild(b);
          }
          el.querySelector("[data-ed-new]").value = "";
        }).catch(function () { msg.textContent = "edit daemon unreachable"; });
      });

      el.querySelector("[data-ed-save]").addEventListener("click", function () {
        msg.textContent = "saving…";
        fetch(window.rbEdit.api + "/api/task/" + encodeURIComponent(id), {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            status: pick.status, difficulty: pick.difficulty, display_tags: chosen()
          })
        }).then(function (r) { return r.json(); }).then(function (res) {
          if (!res.ok) { msg.textContent = res.error || "failed"; return; }
          // Update in place so the row reflects the save without a rebuild.
          t.status = res.task.status;
          t.difficulty = res.task.difficulty;
          t.capIds = res.task.displayTags;
          t.caps = res.task.tagNames;
          t.capGroups = res.task.tagGroups;
          el.remove();
          var fresh = document.createElement("div");
          fresh.innerHTML = rowHtml(t);
          var node = fresh.firstChild;
          row.parentNode.replaceChild(node, row);
          observeMedia(node.parentNode);
          if (editEnabled) showEditButtons();
        }).catch(function () { msg.textContent = "edit daemon unreachable"; });
      });
    }

    // Probe for the local edit daemon. Absent => read-only site, no UI shown. Never on the public site.
    (function probe() {
      if (PUBLIC) return;
      // Same origin as the page: `make edit` serves the API and the site from
      // one address, so there is no port here to guess, collide or be blocked.
      fetch("/api/health")
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (res) {
          if (res && res.ok) window.rbEdit.enable("", res.taxonomy);
          else wrongDoor = frontDoor();
        })
        .catch(function () { wrongDoor = frontDoor(); });
    })();

    render();
  }

  /* --------------------------------------------- single video on task pages */

  function initSingle() {
    var v = document.querySelector("video[data-demo]");
    if (!v) return;
    var speed = 2;
    try {
      var saved = parseFloat(window.localStorage.getItem(SPEED_KEY));
      if (saved > 0) speed = saved;
    } catch (e) { /* ignore */ }
    var btns = [].slice.call(document.querySelectorAll("[data-speed]"));
    function paint() {
      v.playbackRate = speed;
      btns.forEach(function (b) {
        b.classList.toggle("is-on", parseFloat(b.getAttribute("data-speed")) === speed);
      });
    }
    btns.forEach(function (b) {
      b.addEventListener("click", function () {
        speed = parseFloat(b.getAttribute("data-speed")) || 1;
        try { window.localStorage.setItem(SPEED_KEY, String(speed)); } catch (e) { /* ignore */ }
        paint();
      });
    });
    v.addEventListener("play", function () { v.playbackRate = speed; });
    paint();
  }

  function boot() { init(); initSingle(); }

  // Running pills (task list, task pages, Runs pages) count their minutes live, so an open page stays right
  // between rebuilds; the data itself changes only when scripts/import_runs.py writes it.
  setInterval(function () {
    [].forEach.call(document.querySelectorAll(".rpill[data-started] [data-since]"), function (el) {
      el.textContent = fmtMinutes(Date.now() - Date.parse(el.parentNode.getAttribute("data-started")));
    });
  }, 30000);

  if (typeof window.document$ !== "undefined") {
    window.document$.subscribe(boot);
  } else if (document.readyState !== "loading") {
    boot();
  } else {
    document.addEventListener("DOMContentLoaded", boot);
  }
})();

/* =========================================================================
 * Labels page: edit the display tags (two groups) and write them back to
 * state/display_tags.yml. Only active when the local edit daemon answers.
 * ========================================================================= */

(function () {
  "use strict";

  function esc(v) {
    return String(v == null ? "" : v)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  // Where editing lives, according to the page itself.
  //
  // `make edit` runs mkdocs on an internal port behind a front door that also
  // serves /api/*. Land on the internal port — an old tab, a URL mkdocs printed
  // — and /api/health is a 404, so editing is off with no way to tell that from
  // a published read-only site. `site_url` cannot tell it apart either, because
  // `mkdocs serve` overwrites that with its own dev address — so the Makefile
  // passes the front door in as RB_FRONT_URL and scripts/hooks.py writes it into
  // every page. The page therefore knows the address that works even while it is
  // being served from the one that does not. Absent in a published build.
  function frontDoor() {
    var meta = document.querySelector('meta[name="rb-front"]');
    if (!meta || !meta.content) return "";
    try {
      var url = new URL(meta.content, window.location.href);
      return url.origin === window.location.origin ? "" : url.origin;
    } catch (e) { return ""; }
  }

  function init() {
    var host = document.querySelector("[data-taxonomy-editor]");
    if (!host) return;

    // Same origin as the page — see the probe in the task-list module above.
    var base = "";

    // A published site has no daemon behind /api/, and its 404 is the normal
    // read-only case, so only a real network failure is worth reporting.
    function offline(why) {
      var hint = host.querySelector(".tax__hint");
      if (!hint) return;
      var note = document.createElement("span");
      note.className = "tax__offline";
      note.textContent = " (/api/health: " + why + ")";
      hint.appendChild(note);
    }

    // Served from the preview port instead of the front door: say so, and link.
    function offlineLink(where) {
      var hint = host.querySelector(".tax__hint");
      if (!hint) return;
      hint.innerHTML = "This is the preview port, where editing is off. " +
        'Editing is on at <a href="' + where + '">' + where + "</a>.";
    }

    fetch("/api/health")
      .then(function (r) {
        if (r.status === 404) return null;            // no daemon behind this origin
        return r.ok ? r.json() : Promise.reject("HTTP " + r.status);
      })
      .then(function (res) {
        if (res && res.ok) { mount(host, base, res.taxonomy); return; }
        var front = frontDoor();
        if (front) {
          offlineLink(front + window.location.pathname);
        }
      })
      .catch(function (e) {
        var front = frontDoor();
        if (front) offlineLink(front + window.location.pathname);
        else offline(String(e && e.message ? e.message : e));
      });
  }

  function mount(host, base, tax) {
    var doc = JSON.parse(JSON.stringify(tax));

    function draw() {
      var html = '<div class="tax__bar"><b>Editing</b>' +
        '<span class="tax__msg" data-msg>writes to <code>state/display_tags.yml</code></span>' +
        '<button type="button" class="tax__add" data-add-cap>+ Group</button>' +
        '<button type="button" class="tax__save" data-save>Save tags</button></div>';

      html += doc.capabilities.map(function (cap, ci) {
        var subs = (cap.subcapabilities || []).map(function (sub, si) {
          return '<div class="tax__sub">' +
            '<input class="tax__name" value="' + esc(sub.name) + '" data-ci="' + ci +
              '" data-si="' + si + '" data-f="name" placeholder="Tag name">' +
            '<input class="tax__desc" value="' + esc(sub.description || "") + '" data-ci="' + ci +
              '" data-si="' + si + '" data-f="description" placeholder="One line: when does this apply?">' +
            (sub.from_skills && sub.from_skills.length
              ? '<span class="tax__from" title="BEHAVIOR skills this rolls up">' +
                sub.from_skills.length + " skills</span>"
              : '<span class="tax__from tax__from--ours">ours</span>') +
            '<button type="button" class="tax__del" data-del-sub data-ci="' + ci +
              '" data-si="' + si + '" title="Remove">&times;</button>' +
            "</div>";
        }).join("");

        return '<div class="tax__cap">' +
          '<div class="tax__caphead">' +
            '<input class="tax__capname" value="' + esc(cap.name) + '" data-ci="' + ci +
              '" data-f="name" placeholder="Group">' +
            '<input class="tax__desc" value="' + esc(cap.description || "") + '" data-ci="' + ci +
              '" data-f="description" placeholder="What does this group cover?">' +
            '<button type="button" class="tax__del" data-del-cap data-ci="' + ci +
              '" title="Remove group">&times;</button>' +
          "</div>" + subs +
          '<button type="button" class="tax__addsub" data-add-sub data-ci="' + ci +
            '">+ Tag</button>' +
          "</div>";
      }).join("");

      host.innerHTML = html;
      wire();
    }

    function wire() {
      host.querySelectorAll("input").forEach(function (el) {
        el.addEventListener("input", function () {
          var ci = +el.getAttribute("data-ci");
          var si = el.getAttribute("data-si");
          var f = el.getAttribute("data-f");
          if (si === null) doc.capabilities[ci][f] = el.value;
          else doc.capabilities[ci].subcapabilities[+si][f] = el.value;
        });
      });

      host.querySelectorAll("[data-del-sub]").forEach(function (b) {
        b.addEventListener("click", function () {
          doc.capabilities[+b.getAttribute("data-ci")]
            .subcapabilities.splice(+b.getAttribute("data-si"), 1);
          draw();
        });
      });

      host.querySelectorAll("[data-del-cap]").forEach(function (b) {
        b.addEventListener("click", function () {
          doc.capabilities.splice(+b.getAttribute("data-ci"), 1);
          draw();
        });
      });

      host.querySelectorAll("[data-add-sub]").forEach(function (b) {
        b.addEventListener("click", function () {
          var cap = doc.capabilities[+b.getAttribute("data-ci")];
          (cap.subcapabilities = cap.subcapabilities || [])
            .push({ id: "", name: "New tag", description: "" });
          draw();
        });
      });

      var addCap = host.querySelector("[data-add-cap]");
      if (addCap) addCap.addEventListener("click", function () {
        doc.capabilities.push({ id: "", name: "New group", description: "", subcapabilities: [] });
        draw();
      });

      var save = host.querySelector("[data-save]");
      var msg = host.querySelector("[data-msg]");
      if (save) save.addEventListener("click", function () {
        msg.textContent = "saving…";
        fetch(base + "/api/taxonomy", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify(doc)
        }).then(function (r) { return r.json(); }).then(function (res) {
          if (!res.ok) { msg.innerHTML = '<span class="tax__err">' + esc(res.error) + "</span>"; return; }
          doc = JSON.parse(JSON.stringify(res.taxonomy));
          msg.textContent = "saved — reload to refresh the page below";
        }).catch(function () { msg.textContent = "edit daemon unreachable"; });
      });
    }

    draw();
  }

  if (typeof window.document$ !== "undefined") window.document$.subscribe(init);
  else if (document.readyState !== "loading") init();
  else document.addEventListener("DOMContentLoaded", init);
})();
