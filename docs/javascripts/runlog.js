/*
 * Run log page: what one agent run did, minute by minute.
 *
 * The data is docs/assets/<benchmark>/runs/<run>/<task>/<mode>/log.json (scripts/runlog.py, rebuilt by
 * scripts/import_runs.py from the trial's model-gateway log, robot call log and graded replay). The page draws:
 *   - the outcome and the numbers that describe the run;
 *   - a timeline with one lane each for model requests, tool runs, robot calls (limited mode), the images the
 *     model was shown, and what the agent said;
 *   - the graded replay;
 *   - the transcript: every message and tool run, with its output and the images the model saw.
 * Clicking anything on the timeline jumps to it in the transcript.
 */
(function () {
  "use strict";

  var LANE_H = 26, AXIS_H = 24, LABEL_W = 78, PAD_R = 14;

  function esc(v) {
    return String(v == null ? "" : v)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function clock(s) {
    s = Math.max(0, Math.round(s || 0));
    var h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = s % 60;
    return (h ? h + ":" + String(m).padStart(2, "0") : m) + ":" + String(x).padStart(2, "0");
  }

  function dur(s) {
    if (s == null) return "—";
    if (s < 60) return (s < 10 ? s.toFixed(1) : Math.round(s)) + " s";
    var m = Math.round(s / 60);
    return m >= 60 ? Math.floor(m / 60) + " h " + String(m % 60).padStart(2, "0") + " min" : m + " min";
  }

  function num(n) {
    if (n == null) return "—";
    return n >= 1e6 ? (n / 1e6).toFixed(1) + "M" : n >= 1e4 ? Math.round(n / 1e3) + "k" : n.toLocaleString();
  }

  function localTime(epoch) {
    if (!epoch) return "—";
    var d = new Date(epoch * 1000);
    return d.toLocaleDateString(undefined, { month: "short", day: "numeric" }) + " " +
      d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
  }

  // Just enough Markdown for what agents write: `code`, **bold**, bullet lines, paragraphs.
  function prose(text) {
    return esc(text).split(/\n{2,}/).map(function (para) {
      var lines = para.split("\n");
      var html = lines.map(function (l) {
        return l.replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
          .replace(/\[([^\]]+)\]\(([^)]+)\)/g, "<u>$1</u>");
      });
      if (lines.every(function (l) { return /^\s*([-*]|\d+\.)\s/.test(l); })) {
        return "<ul>" + html.map(function (l) { return "<li>" + l.replace(/^\s*([-*]|\d+\.)\s/, "") + "</li>"; }).join("") + "</ul>";
      }
      return "<p>" + html.join("<br>") + "</p>";
    }).join("");
  }

  var OUTCOME = {
    success: ["✓", "Success"], failed: ["✗", "No success"], error: ["!", "Ended without a grade"],
    running: ["●", "Running"], grading: ["◐", "Grading"], setup: ["○", "Setting up"], stalled: ["!", "Stalled"]
  };

  /* ------------------------------------------------------------------ header */

  function header(d) {
    var o = OUTCOME[d.state] || ["", d.state], rw = d.reward || {}, t = d.totals || {};
    var agent = d.agent_wall_s != null ? d.agent_wall_s : d.span;
    var reasoningShare = t.output ? Math.round(100 * (t.reasoning || 0) / t.output) : 0;
    var cachedShare = t.input ? Math.round(100 * (t.cached || 0) / t.input) : 0;
    var failedRuns = d.steps.filter(function (s) { return s.k === "run" && s.status === "failed"; }).length;
    var cards = [
      ["Agent time", dur(agent), d.agent_wall_s == null ? "so far" : ""],
      ["Model requests", num(t.calls), t.failed ? t.failed + " failed" : "all answered"],
      ["Output tokens", num(t.output), reasoningShare + "% reasoning"],
      ["Input tokens", num(t.input), cachedShare + "% from cache"],
      ["Tool runs", num(t.runs), failedRuns ? failedRuns + " failed" : "none failed"],
      ["Images seen", num(t.images), "shown to the model"]
    ];
    // The episode's call log is collected from the simulator container when the trial ends.
    if (d.mode === "limited") {
      cards.push(t.robot || ["success", "failed", "error"].indexOf(d.state) >= 0
        ? ["Robot calls", num(t.robot), "to the live episode"] : ["Robot calls", "—", "logged when the trial ends"]);
    }
    if (rw.n_actions != null) cards.push(["Actions graded", num(rw.n_actions), rw.deterministic ? "replay deterministic" : "replay differs"]);
    var facts = [
      d.host ? "host <b>" + esc(d.host) + "</b>" : "",
      d.start ? "started " + esc(localTime(d.start)) : "",
      d.built ? "page data " + esc(localTime(Date.parse(d.built) / 1000)) : ""
    ].filter(Boolean).join(" · ");
    return '<section class="rl-head rl-head--' + esc(d.state) + '">' +
      '<div class="rl-outcome"><span class="rl-outcome__mark">' + esc(o[0]) + "</span>" +
        "<div><b>" + esc(o[1]) + "</b><span>" + esc(d.mode) + " mode" +
        (d.exception ? " · " + esc(d.exception) : "") + "</span></div></div>" +
      '<div class="rl-cards">' + cards.map(function (c) {
        return '<div class="rl-card"><span>' + esc(c[0]) + "</span><b>" + esc(c[1]) + "</b><i>" + esc(c[2]) + "</i></div>";
      }).join("") + "</div>" +
      '<p class="rl-facts">' + facts + "</p>" + (d.note ? '<p class="rl-note">' + esc(d.note) + "</p>" : "") + "</section>";
  }

  /* ---------------------------------------------------------------- timeline */

  function niceStep(span) {
    var steps = [30, 60, 120, 300, 600, 900, 1800, 3600];
    for (var i = 0; i < steps.length; i++) if (span / steps[i] <= 8) return steps[i];
    return 7200;
  }

  function timeline(d, width) {
    // A lane is drawn only when it has something on it (unlimited runs have no robot calls, many see no image).
    var lanes = [["model", "Model"], ["tools", "Tools"]];
    if (d.robot.some(function (r) { return r.call; })) lanes.push(["robot", "Robot"]);
    if (d.steps.some(function (s) { return s.img; })) lanes.push(["seen", "Seen"]);
    lanes.push(["said", "Said"]);
    var span = Math.max(d.span || 0, 1), w = Math.max(width - LABEL_W - PAD_R, 120);
    var x = function (t) { return LABEL_W + Math.max(0, Math.min(1, t / span)) * w; };
    var laneY = {}, h = AXIS_H + lanes.length * LANE_H + 6;
    lanes.forEach(function (l, i) { laneY[l[0]] = AXIS_H + i * LANE_H; });
    var out = ['<svg class="rl-tl" viewBox="0 0 ' + width + " " + h + '" width="' + width + '" height="' + h + '">'];

    var step = niceStep(span);
    for (var t = 0; t <= span + 0.1; t += step) {
      out.push('<line class="rl-grid" x1="' + x(t) + '" x2="' + x(t) + '" y1="' + (AXIS_H - 4) + '" y2="' + (h - 4) + '"/>' +
        '<text class="rl-axis" x="' + x(t) + '" y="' + (AXIS_H - 9) + '">' + Math.round(t / 60) + "m</text>");
    }
    lanes.forEach(function (l) {
      out.push('<text class="rl-lane" x="0" y="' + (laneY[l[0]] + LANE_H / 2 + 4) + '">' + l[1] + "</text>" +
        '<rect class="rl-lanebg" x="' + LABEL_W + '" y="' + (laneY[l[0]] + 3) + '" width="' + w + '" height="' + (LANE_H - 6) + '" rx="4"/>');
    });

    var maxReason = Math.max.apply(null, d.calls.map(function (c) { return c[6] || 0; }).concat([1]));
    d.calls.forEach(function (c, i) {
      var frac = 0.35 + 0.65 * Math.sqrt((c[6] || 0) / maxReason), bh = (LANE_H - 8) * frac;
      out.push('<rect class="rl-call' + (c[2] !== 200 ? " rl-call--failed" : "") + '" data-call="' + i + '" x="' + x(c[0]) +
        '" y="' + (laneY.model + LANE_H - 4 - bh) + '" width="' + Math.max(1.5, x(c[1]) - x(c[0])) + '" height="' + bh + '" rx="1.5"/>');
    });
    d.steps.forEach(function (s, i) {
      if (s.k === "run") {
        var end = s.te != null ? s.te : span;
        out.push('<rect class="rl-run rl-run--' + esc(s.status || "open") + '" data-step="' + i + '" x="' + x(s.t) +
          '" y="' + (laneY.tools + 6) + '" width="' + Math.max(2, x(end) - x(s.t)) + '" height="' + (LANE_H - 12) + '" rx="2"/>');
        if (s.img) out.push('<rect class="rl-seen" data-step="' + i + '" x="' + (x(s.te != null ? s.te : s.t) - 4) +
          '" y="' + (laneY.seen + 7) + '" width="8" height="' + (LANE_H - 14) + '" rx="2"/>');
      } else if (s.k === "say") {
        out.push('<circle class="rl-said" data-step="' + i + '" cx="' + x(s.t) + '" cy="' + (laneY.said + LANE_H / 2) + '" r="4.5"/>');
      }
    });
    d.robot.forEach(function (r, i) {
      if (!r.call) return;
      var cy = laneY.robot + LANE_H / 2;
      out.push(r.ev === "submit"
        ? '<rect class="rl-robot rl-robot--submit" data-robot="' + i + '" x="' + (x(r.t) - 4) + '" y="' + (cy - 4) + '" width="8" height="8" transform="rotate(45 ' + x(r.t) + " " + cy + ')"/>'
        : '<circle class="rl-robot" data-robot="' + i + '" cx="' + x(r.t) + '" cy="' + cy + '" r="3"/>');
    });
    if (OUTCOME[d.state] && ["running", "setup", "grading"].indexOf(d.state) >= 0) {
      out.push('<line class="rl-now" x1="' + x(span) + '" x2="' + x(span) + '" y1="' + (AXIS_H - 4) + '" y2="' + (h - 4) + '"/>');
    }
    out.push("</svg>");
    return out.join("");
  }

  function shares(d) {
    var model = 0, tools = 0, span = Math.max(d.span || 0, 1);
    d.calls.forEach(function (c) { model += Math.max(0, c[1] - c[0]); });
    d.steps.forEach(function (s) { if (s.k === "run" && s.te != null) tools += Math.max(0, s.te - s.t); });
    var other = Math.max(0, span - model - tools);
    var part = function (cls, label, v) {
      var p = 100 * v / (model + tools + other || 1);
      return '<span class="rl-share__' + cls + '" style="width:' + p.toFixed(2) + '%" title="' + esc(label + ": " + dur(v)) + '"></span>';
    };
    var pct = function (v) { return Math.round(100 * v / (model + tools + other || 1)) + "%"; };
    return '<div class="rl-share"><div class="rl-share__bar">' + part("model", "Model thinking", model) +
      part("tools", "Tools running", tools) + part("other", "Between steps", other) + "</div>" +
      '<p><i class="rl-dot rl-dot--model"></i>model thinking ' + pct(model) + ' <i class="rl-dot rl-dot--tools"></i>tools running ' +
      pct(tools) + ' <i class="rl-dot rl-dot--other"></i>between steps ' + pct(other) + "</p></div>";
  }

  /* -------------------------------------------------------------- transcript */

  function runItem(s, i, base) {
    var dt = s.te != null ? s.te - s.t : null, text = s.cmd != null ? s.cmd : (s.code || "");
    var lines = text.split("\n"), long = lines.length > 8;
    var status = s.status === "failed" ? "failed" : s.status === "background" ? "still running" : s.status ? "ok" : "running";
    var imgs = base === null
      ? (s.img && s.img.length ? '<span class="rl-offmedia">' + s.img.length + " image" + (s.img.length > 1 ? "s" : "") +
          " the model saw: media not yet published</span>" : "")
      : (s.img || []).map(function (src) {
          return '<button type="button" class="rl-thumb" data-img="' + esc(base + src) + '"><img src="' + esc(base + src) + '" alt="" loading="lazy"></button>';
        }).join("");
    return '<article class="rl-item rl-item--run rl-item--' + esc(s.status || "open") + '" id="rl-' + i + '" data-kind="run' +
      (s.status === "failed" ? " failed" : "") + (s.img ? " images" : "") + '">' +
      '<div class="rl-when">' + clock(s.t) + "</div>" +
      '<div class="rl-body"><div class="rl-meta"><b>' + esc(s.tool === "exec" ? "ran" : s.tool) + "</b>" +
        '<span class="rl-chip rl-chip--' + esc(s.status || "open") + '">' + esc(status) + "</span>" +
        (s.wall != null ? '<span class="rl-chip">' + esc(dur(s.wall)) + "</span>" : dt != null ? '<span class="rl-chip">' + esc(dur(dt)) + "</span>" : "") +
        (s.cmd == null && s.code ? '<span class="rl-chip">script</span>' : "") + "</div>" +
        '<pre class="rl-cmd' + (long ? " is-folded" : "") + '"><code>' + esc(text) + "</code></pre>" +
        (long ? '<button type="button" class="rl-more" data-unfold>Show all ' + lines.length + " lines</button>" : "") +
        (imgs ? '<div class="rl-thumbs">' + imgs + "</div>" : "") +
        (s.out != null
          ? "<details class=\"rl-out\"><summary>Output · " + esc((s.n || 0).toLocaleString()) + " characters</summary><pre><code>" +
            esc(s.out || "(empty)") + "</code></pre></details>"
          : '<p class="rl-pending">' + (s.te == null ? "running now" : "output not logged") + "</p>") +
      "</div></article>";
  }

  function sayItem(s, i, last) {
    return '<article class="rl-item rl-item--say' + (last ? " rl-item--final" : "") + '" id="rl-' + i + '" data-kind="say">' +
      '<div class="rl-when">' + clock(s.t) + "</div>" +
      '<div class="rl-body"><div class="rl-meta"><b>' + (last ? "final message" : "said") + "</b></div>" +
      '<div class="rl-say">' + prose(s.text) + "</div></div></article>";
  }

  function robotTable(d) {
    var rows = d.robot.filter(function (r) { return r.call; });
    if (!rows.length) return "";
    return '<details class="rl-robots"><summary>' + rows.length + " robot calls</summary><table><thead><tr>" +
      "<th>#</th><th>at</th><th>call</th><th>type</th><th>steps</th><th>clipped</th><th>the agent's note</th></tr></thead><tbody>" +
      rows.map(function (r) {
        return "<tr><td>" + esc(r.call) + "</td><td>" + clock(r.t) + "</td><td>" + esc(r.ev) + "</td><td>" + esc(r.type || "") +
          "</td><td>" + esc(r.steps != null ? r.steps : "") + "</td><td>" + esc(r.clip || "") + "</td><td>" + esc(r.note || "") + "</td></tr>";
      }).join("") + "</tbody></table></details>";
  }

  /* ------------------------------------------------------------------ replay */

  // Every graded trajectory has a replay, failed or not. A run without one handed no trajectory in (typically it ran
  // out of time); its page says so and shows the newest images the agent saved and its gen.py instead.
  // base: where the replay and the images are (null: the public site has not published them yet, see mediaBase).
  function replay(d, base, finished) {
    var media = d.media || {}, rw = d.reward || {};
    if (media.video && base === null) {
      return '<section class="rl-panel rl-replay rl-replay--none"><h2>Graded replay</h2><p class="rl-why">' +
        "The replay of the trajectory the agent handed in" + (d.state === "success" ? "" : ", although it did not succeed") +
        ": media not yet published. The video, and the images below, are hosted apart from this site.</p></section>";
    }
    if (media.video) {
      return '<section class="rl-panel rl-replay"><h2>Graded replay</h2><video controls preload="metadata" playsinline data-src="' +
        esc(base + media.video) + '"' + (media.last ? ' poster="' + esc(base + media.last) + '"' : "") + "></video>" +
        "<p>The trajectory the agent handed in" + (d.state === "success" ? "" : ", although it did not succeed") +
        ", replayed by the separate verifier in a fresh process.</p></section>";
    }
    if (!finished) {
      return '<section class="rl-panel rl-replay rl-replay--none"><h2>Graded replay</h2><p class="rl-why">' +
        "The verifier replays the trajectory once the agent has handed it in; the video appears here then.</p></section>";
    }
    var ended = d.ended || {};
    var why = rw.missing_trajectory
      ? "No replay: the agent handed in no trajectory" +
        (d.exception === "AgentTimeoutError" ? ", because it ran out of its " + dur(d.agent_wall_s) + " time budget first." : ".")
      : d.state === "error" ? "No replay: the trial ended without a grade (" + esc(d.exception || "no reward") + ")."
      : media.problem ? media.problem
      : ended.reason === "error" ? "No replay: the live episode ended with a simulator error" +
        (ended.error ? " (" + ended.error + ")" : "") + ", so there was nothing to replay."
      : "No replay video was rendered for this run.";
    var snaps = base === null ? "" : (d.snapshots || []).map(function (sn) {
      return '<figure><button type="button" class="rl-thumb" data-img="' + esc(base + sn.src) + '"><img src="' + esc(base + sn.src) +
        '" alt="" loading="lazy"></button><figcaption>' + esc(sn.name) + (sn.t != null ? " · " + clock(sn.t) : "") + "</figcaption></figure>";
    }).join("");
    return '<section class="rl-panel rl-replay rl-replay--none"><h2>Graded replay</h2><p class="rl-why">' + esc(why) + "</p>" +
      (snaps ? "<h3>The newest images the agent saved</h3><div class=\"rl-snaps\">" + snaps + "</div>" : "") +
      (d.gen ? "<details class=\"rl-out\"><summary>Its generator script at the end, /app/output/gen.py</summary><pre><code>" +
        esc(d.gen) + "</code></pre></details>" : "") + "</section>";
  }

  /* -------------------------------------------------------------------- page */

  // Local preview servers (mkdocs serve, python -m http.server) answer no HTTP Range requests, and the replay MP4s keep
  // their index (moov) at the end, so a <video> pointed at the file cannot seek. Reading the whole file into a Blob first
  // makes the progress bar work on any server (the files are local). If that fails, the plain file still plays.
  function seekable(root) {
    root.querySelectorAll(".rl-replay video[data-src]").forEach(function (v) {
      var src = v.getAttribute("data-src");
      if (!window.fetch || !window.URL || !URL.createObjectURL) { v.src = src; return; }
      // A replay on the media host (the public site: data/public.yml run_media_base) is served with Range requests
      // and its index first: the video plays and seeks as it streams, so it is never read whole first.
      try {
        if (new URL(src, window.location.href).origin !== window.location.origin) { v.src = src; return; }
      } catch (e) { v.src = src; return; }
      var note = document.createElement("p");
      note.className = "rl-loading";
      note.textContent = "Loading the video so that it can be scrubbed…";
      v.parentNode.insertBefore(note, v.nextSibling);
      fetch(src)
        .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.blob(); })
        .then(function (b) { v.src = URL.createObjectURL(b); note.remove(); })
        .catch(function () { v.src = src; note.textContent = "Could not preload the video: it plays, but seeking may not work here."; });
    });
  }

  // The public site keeps a trial's data here but its replay and images elsewhere: data-media is their address,
  // empty until they are published (data/public.yml run_media_base). Locally both sit next to log.json.
  function mediaBase(el) {
    if (!el.hasAttribute("data-media")) return el.getAttribute("data-runlog");
    return el.getAttribute("data-media") || null;
  }

  function render(el, d) {
    var base = mediaBase(el);
    var lastSay = -1;
    d.steps.forEach(function (s, i) { if (s.k === "say") lastSay = i; });
    var finished = ["success", "failed", "error"].indexOf(d.state) >= 0;
    var media = d.media || {};
    el.innerHTML =
      header(d) +
      '<section class="rl-panel"><h2>Timeline</h2><div class="rl-tlwrap" data-tl></div>' + shares(d) +
        '<div class="rl-tip" data-tip hidden></div></section>' +
      replay(d, base, finished) +
      '<section class="rl-panel"><h2>Transcript</h2><div class="rl-filter" data-filter>' +
        [["all", "Everything"], ["say", "What it said"], ["run", "Tool runs"], ["failed", "Failed runs"], ["images", "With images"]]
          .map(function (f, i) { return '<button type="button" data-f="' + f[0] + '"' + (i ? "" : ' class="is-on"') + ">" + f[1] + "</button>"; }).join("") +
        "</div><div class=\"rl-items\">" +
        d.steps.map(function (s, i) { return s.k === "say" ? sayItem(s, i, finished && i === lastSay) : runItem(s, i, base); }).join("") +
        "</div>" + robotTable(d) + "</section>" +
      '<section class="rl-panel rl-where"><h2>Full record</h2><p>Everything this page is drawn from, and more ' +
        "(the Codex stream and session, the ATIF trajectory, the artifacts, the verifier's logs), stays where the trial ran:</p>" +
        "<pre><code>" + esc(d.where || "<trial>") + "/\n  agent/       codex.txt · gateway.jsonl · sessions/ · trajectory.json\n  artifacts/   the agent's outputs" +
        (d.mode === "limited" ? " · data/episode.jsonl (every robot call)" : "") + "\n  verifier/    reward.json · grade.log · replay.mp4</code></pre></section>";

    seekable(el);
    var wrap = el.querySelector("[data-tl]"), tip = el.querySelector("[data-tip]");
    function drawTimeline() { wrap.innerHTML = timeline(d, Math.max(320, Math.floor(wrap.clientWidth))); }
    drawTimeline();
    var resizeTimer;
    window.addEventListener("resize", function () { clearTimeout(resizeTimer); resizeTimer = setTimeout(drawTimeline, 150); });

    function describe(node) {
      if (node.hasAttribute("data-call")) {
        var c = d.calls[+node.getAttribute("data-call")];
        return "<b>Model request</b> " + clock(c[0]) + " · " + dur(c[1] - c[0]) + (c[2] !== 200 ? " · status " + esc(c[2]) : "") +
          "<br>" + num(c[5]) + " output tokens (" + num(c[6]) + " reasoning) · " + num(c[3]) + " input (" + num(c[4]) + " cached)";
      }
      if (node.hasAttribute("data-robot")) {
        var r = d.robot[+node.getAttribute("data-robot")];
        return "<b>Robot " + esc(r.ev) + " #" + esc(r.call) + "</b> " + clock(r.t) + (r.type ? " · " + esc(r.type) : "") +
          (r.steps != null ? " · " + esc(r.steps) + " control steps" : "") + (r.note ? "<br>" + esc(r.note) : "");
      }
      var s = d.steps[+node.getAttribute("data-step")];
      if (s.k === "say") return "<b>Said</b> " + clock(s.t) + "<br>" + esc(s.text.slice(0, 220)) + (s.text.length > 220 ? "…" : "");
      var first = (s.cmd != null ? s.cmd : s.code || "").split("\n")[0].slice(0, 140);
      return "<b>" + (s.img ? s.img.length + " image(s) shown to the model" : "Tool run") + "</b> " + clock(s.t) +
        (s.te != null ? " → " + clock(s.te) : " → now") + (s.status ? " · " + esc(s.status) : "") + "<br><code>" + esc(first) + "</code>";
    }
    wrap.addEventListener("mousemove", function (ev) {
      var node = ev.target.closest("[data-call],[data-step],[data-robot]");
      if (!node) { tip.hidden = true; return; }
      tip.innerHTML = describe(node);
      tip.hidden = false;
      var box = el.getBoundingClientRect();
      tip.style.left = Math.min(ev.clientX - box.left + 14, box.width - 330) + "px";
      tip.style.top = (ev.clientY - box.top + 16) + "px";
    });
    wrap.addEventListener("mouseleave", function () { tip.hidden = true; });
    wrap.addEventListener("click", function (ev) {
      var node = ev.target.closest("[data-step]");
      if (!node) return;
      var item = document.getElementById("rl-" + node.getAttribute("data-step"));
      if (!item) return;
      setFilter("all");
      item.scrollIntoView({ behavior: "smooth", block: "center" });
      item.classList.remove("is-flash"); void item.offsetWidth; item.classList.add("is-flash");
    });

    var filterBar = el.querySelector("[data-filter]");
    function setFilter(f) {
      [].forEach.call(filterBar.querySelectorAll("button"), function (b) { b.classList.toggle("is-on", b.getAttribute("data-f") === f); });
      [].forEach.call(el.querySelectorAll(".rl-item"), function (it) {
        it.hidden = f !== "all" && (" " + it.getAttribute("data-kind") + " ").indexOf(" " + f + " ") < 0;
      });
    }
    filterBar.addEventListener("click", function (ev) {
      var b = ev.target.closest("button[data-f]");
      if (b) setFilter(b.getAttribute("data-f"));
    });

    el.addEventListener("click", function (ev) {
      var more = ev.target.closest("[data-unfold]");
      if (more) { more.previousElementSibling.classList.remove("is-folded"); more.remove(); return; }
      var thumb = ev.target.closest("[data-img]");
      if (thumb) lightbox(el, thumb.getAttribute("data-img"));
    });
  }

  function lightbox(el, first) {
    var all = [].map.call(el.querySelectorAll("[data-img]"), function (b) { return b.getAttribute("data-img"); });
    var at = Math.max(0, all.indexOf(first));
    var box = document.createElement("div");
    box.className = "rl-lightbox";
    function show() {
      box.innerHTML = '<img src="' + esc(all[at]) + '" alt=""><span>' + (at + 1) + " / " + all.length +
        " · the image as the model received it · ← → to step, Esc to close</span>";
    }
    function key(ev) {
      if (ev.key === "Escape") close();
      else if (ev.key === "ArrowRight") { at = (at + 1) % all.length; show(); }
      else if (ev.key === "ArrowLeft") { at = (at - 1 + all.length) % all.length; show(); }
    }
    function close() { box.remove(); document.removeEventListener("keydown", key); }
    box.addEventListener("click", close);
    document.addEventListener("keydown", key);
    show();
    document.body.appendChild(box);
  }

  function init() {
    [].forEach.call(document.querySelectorAll("[data-runlog]"), function (el) {
      if (el.getAttribute("data-ready")) return;
      el.setAttribute("data-ready", "1");
      el.innerHTML = '<p class="rl-loading">Loading the run…</p>';
      // XMLHttpRequest rather than fetch: it also works on a build opened straight from disk.
      var xhr = new XMLHttpRequest();
      xhr.open("GET", el.getAttribute("data-runlog") + "log.json?" + Date.now());
      xhr.onload = function () {
        try { render(el, JSON.parse(xhr.responseText)); }
        catch (e) { el.innerHTML = '<p class="rl-loading">Could not read this run’s log data: ' + esc(e.message) + "</p>"; }
      };
      xhr.onerror = function () {
        el.innerHTML = '<p class="rl-loading">No log data here yet: run <code>make runs</code>.</p>';
      };
      xhr.send();
    });
  }

  if (typeof window.document$ !== "undefined") window.document$.subscribe(init);
  else if (document.readyState !== "loading") init();
  else document.addEventListener("DOMContentLoaded", init);
})();
