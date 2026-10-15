(function () {
"use strict";
const D = window.DATA, R = D.rows;
const EN = document.documentElement.lang === "en", L = (zh, en) => EN ? en : zh;
const $ = (s, el = document) => el.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const AGENTS = D.agents;
const BN = Object.fromEntries(D.benches.map(b => [b.key, b.name]));
const CODE = EN ? {
  G: "grasp / contact", C: "planning / control", S: "perception", Q: "stopped with time left", T: "timed out while working",
  M: "model / harness fault", X: "own code broke it", U: "misread a condition", D: "deliverable / replay failed", R: "rule violation",
  N1: "task text or instance wrong", N2: "infeasible / simulator defect", N3: "infrastructure" }
 : { G: "抓取 / 接触", C: "规划 / 控制", S: "感知", Q: "还有时间就停了", T: "时间到时仍在做", M: "模型 / harness 故障", X: "自己的代码出错",
  U: "读错了条件", D: "交付物 / 重放失败", R: "违规", N1: "任务文字或实例有误", N2: "不可行 / 仿真缺陷", N3: "基础设施" };
const CODES = ["G", "C", "S", "U", "X", "D", "Q", "T", "M", "R", "N1", "N2", "N3"];
const GRADE = EN ? { A: "A: real and repeatable", B: "B: marginal or lucky", J: "J: check passed before the task was done" }
 : { A: "A：真实完成、可重复", B: "B：勉强或带运气", J: "J：任务没做完判定就通过了" };
const ENDED = [
  ["success", L("成功", "success"), "--s1"],
  ["timeout", L("时间到", "timed out"), "--s2"],
  ["self_stop_gave_up", L("自己放弃", "gave up"), "--s3"],
  ["self_stop_believed_done", L("以为做完了", "believed it was done"), "--s4"],
  ["self_stop_believed_time_up", L("以为时间到了", "believed time was up"), "--s5"],
  ["episode", L("回合被结束 / reset 用完", "episode ended / resets used up"), "--s6"],
  ["crash", L("崩溃 / 模型故障", "crash / model fault"), "--s7"],
  ["infra", L("基础设施", "infrastructure"), "--s8"],
];
const endKey = e => !e ? "crash" : e === "resets_exhausted" || e === "episode_terminated" ? "episode" : ENDED.some(x => x[0] === e) ? e : "crash";
const isInfra = r => !r.s && (r.c === "N3" || r.c === "M" || r.e === "infra");
const cls = r => !r ? "N" : r.s ? (r.g || "A") : isInfra(r) ? "I" : "F";
const label = r => r.s ? (r.g || "A") : (r.c || "?");
const outcome = r => r.s ? (GRADE[r.g] || L("成功", "success")) : `${L("失败", "failed")} · ${r.c || "?"} ${CODE[r.c] || ""}`;
const short = t => String(t || "").replace(/^(robolab|robowits|behavior|robopaint|roboarc)-/, "").replace(/^strict-/, "").replace(/-i\d\d(-(privileged|standard))?$/, "");

// tooltip
const tip = document.createElement("div"); tip.id = "tip"; document.body.appendChild(tip);
function showTip(html, ev) { tip.innerHTML = html; tip.style.display = "block"; moveTip(ev); }
function moveTip(ev) {
  const w = tip.offsetWidth, h = tip.offsetHeight; let x = ev.clientX + 14, y = ev.clientY + 14;
  if (x + w > innerWidth - 8) x = ev.clientX - w - 14; if (y + h > innerHeight - 8) y = ev.clientY - h - 14;
  tip.style.left = Math.max(4, x) + "px"; tip.style.top = Math.max(4, y) + "px";
}
function hideTip() { tip.style.display = "none"; }
function trialTip(r) {
  return `<b>${esc(short(r.t))}</b> · ${esc(r.m)} · ${esc(r.a)}<br>${esc(outcome(r))}${r.st ? " · " + esc(r.st) : ""}<br>` +
    `<span class="muted">${r.min ?? "?"} / ${r.bud ?? "?"} ${L("分钟", "min")} · ${esc(r.e || "")} · ${esc(r.d || "")}</span><br>${esc((r.det || "").slice(0, 320))}${(r.det || "").length > 320 ? "…" : ""}<br><span class="muted">${L("点击看详情", "click for details")}</span>`;
}
function bindTips(root) {
  root.querySelectorAll("[data-id]").forEach(el => {
    const r = R.find(x => x.id === el.dataset.id); if (!r) return;
    el.addEventListener("mouseenter", ev => showTip(trialTip(r), ev));
    el.addEventListener("mousemove", moveTip);
    el.addEventListener("mouseleave", hideTip);
    el.addEventListener("click", () => { hideTip(); openTrial(r.id); });
  });
}

// dialog
const dlg = $("#trialdlg");
const findR = id => R.find(x => x.id === id) || R.find(x => (x.path || "").endsWith("__" + id) || (x.id || "").endsWith("__" + id));
function openTrial(id) {
  const r = findR(id); if (!r) return;
  $("#dlgtitle").innerHTML = `${esc(BN[r.b] || r.b)} · <b>${esc(short(r.t))}</b> · ${esc(r.m)} · ${esc(r.a)}`;
  const f = (k, v) => v == null || v === "" || (Array.isArray(v) && !v.length) ? "" : `<dt>${k}</dt><dd>${esc(typeof v === "string" ? v : JSON.stringify(v))}</dd>`;
  const vid = r.vid ? `<video src="${esc(r.vid)}" controls preload="metadata" style="width:100%;border-radius:6px;background:#000"></video>` : "";
  const rp = r.rp ? `<dt>${L("回放", "Replay")}</dt><dd><a href="${esc(r.rp)}" target="_blank" rel="noopener">${L("在 Batch Eval Live 面板上打开（需要登录）", "open on the Batch Eval Live dashboard (login needed)")}</a></dd>` : "";
  $("#dlgbody").innerHTML = `${vid}<dl>
    <dt>${L("结果", "Outcome")}</dt><dd><span class="pill ${cls(r)}">${esc(label(r))}</span> ${esc(outcome(r))}${r.st ? " · <code>" + esc(r.st) + "</code>" : ""}${r.c2 && r.c2.length ? " · " + L("次要", "secondary") + " " + esc(r.c2.join(", ")) : ""}</dd>
    ${f(L("经过", "What happened"), r.det)}
    <dt>${L("用时 / 结束", "Time / end")}</dt><dd>${r.min ?? "?"} / ${r.bud ?? "?"} ${L("分钟", "min")}${r.fs != null ? " · " + L("首次成功", "first success") + " " + r.fs + " min" : ""} · ${esc(r.e || "")}${r.rs != null ? " · resets " + r.rs : ""} · ${esc(r.d || "")}</dd>
    ${f(L("任务侧问题", "Task-side issue"), r.ts)}${f(L("控制方式", "Control style"), r.sty)}${f(L("搜索 / 优化", "Search"), r.srch)}${f(L("策略", "Strategy"), r.strat)}${f(L("感知", "Perception"), r.perc)}
    ${f(L("交卷前的验证", "Verification"), r.ver)}${f(L("看时间", "Clock use"), r.clk)}${f(L("对时间的判断", "Time belief"), r.tb)}${f(L("自我汇报", "Self-report"), r.rep)}
    ${f(L("外部材料", "External material"), r.ext)}${f(L("越界", "Rule bending"), r.rb)}${f(L("工具问题", "Tool issues"), r.ti)}${f(L("值得一提", "Notable"), r.nb)}${f(L("证据", "Evidence"), r.ev)}${f(L("基准特有字段", "Benchmark fields"), r.bs)}
    ${rp}<dt>trial</dt><dd><code>${esc(r.path)}</code>${r.lt ? " · " + L("日志被截断", "log truncated") : ""}</dd></dl>`;
  dlg.showModal();
}
$("#dlgclose").onclick = () => dlg.close();
dlg.addEventListener("click", e => { if (e.target === dlg) dlg.close(); });
document.addEventListener("click", e => { const a = e.target.closest("[data-open]"); if (a) { e.preventDefault(); openTrial(a.dataset.open); } });

function legend(el, cats) { el.innerHTML = cats.map(c => `<span><i class="sw" style="background:var(${c[2]})"></i>${esc(c[1])}</span>`).join(""); }

// stacked horizontal bars: one row per agent
function stacked(el, rows, cats) {
  const W = 760, lw = 92, rowH = 22, gap = 8, rw = 46;
  const max = Math.max(1, ...rows.map(r => r.total));
  const H = rows.length * (rowH + gap) + 4;
  let s = `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" style="max-width:${W}px">`;
  rows.forEach((row, i) => {
    const y = i * (rowH + gap);
    s += `<text x="${lw - 8}" y="${y + rowH / 2 + 4}" text-anchor="end">${esc(row.label)}</text>`;
    let x = lw; const scale = (W - lw - rw) / max;
    cats.forEach((c, j) => {
      const n = row.counts[c[0]] || 0; if (!n) return;
      const w = n * scale;
      s += `<rect data-row="${i}" data-cat="${j}" x="${x}" y="${y}" width="${Math.max(1, w - 2)}" height="${rowH}" rx="3" fill="var(${c[2]})"/>`;
      if (w > 18) s += `<text class="lbl-in${c[3] ? " dark" : ""}" x="${x + w / 2 - 1}" y="${y + rowH / 2 + 4}" text-anchor="middle" pointer-events="none">${n}</text>`;
      x += w;
    });
    s += `<text x="${x + 6}" y="${y + rowH / 2 + 4}">${row.right ?? row.total}</text>`;
  });
  s += "</svg>"; el.innerHTML = s;
  el.querySelectorAll("rect[data-row]").forEach(rc => {
    const row = rows[+rc.dataset.row], c = cats[+rc.dataset.cat];
    rc.addEventListener("mousemove", ev => showTip(`<b>${esc(row.label)}</b><br>${esc(c[1])}: ${row.counts[c[0]]} / ${row.total}`, ev));
    rc.addEventListener("mouseleave", hideTip);
  });
}
const sel = (bench, mode) => R.filter(r => (bench === "all" || r.b === bench) && (!mode || mode === "all" || r.m === mode));
const OCATS = [["A", GRADE.A, "--gA"], ["B", GRADE.B, "--gB", 1], ["J", GRADE.J, "--gJ"], ["F", L("失败（agent 原因）", "failed (agent)"), "--gF", 1], ["I", L("失败（基础设施 / harness）", "failed (infra / harness)"), "--gI", 1]];
document.querySelectorAll("[data-outcome]").forEach(el => {
  const [b, m] = el.dataset.outcome.split(":"); const xs = sel(b, m);
  const rows = AGENTS.filter(a => xs.some(r => r.a === a)).map(a => {
    const ys = xs.filter(r => r.a === a), counts = {};
    ys.forEach(r => { const k = cls(r); counts[k] = (counts[k] || 0) + 1; });
    const succ = ys.filter(r => r.s).length;
    return { label: a, counts, total: ys.length, right: `${succ}/${ys.length}` };
  });
  stacked(el, rows, OCATS);
});
document.querySelectorAll("[data-legend=outcome]").forEach(el => legend(el, OCATS));
document.querySelectorAll("[data-ended]").forEach(el => {
  const [b, m, only] = el.dataset.ended.split(":"); let xs = sel(b, m);
  if (only === "fail") xs = xs.filter(r => !r.s);
  const cats = only === "fail" ? ENDED.slice(1) : ENDED;
  const rows = AGENTS.filter(a => xs.some(r => r.a === a)).map(a => {
    const ys = xs.filter(r => r.a === a), counts = {};
    ys.forEach(r => { const k = endKey(r.e); counts[k] = (counts[k] || 0) + 1; });
    return { label: a, counts, total: ys.length };
  });
  stacked(el, rows, cats);
});
document.querySelectorAll("[data-legend=ended]").forEach(el => legend(el, ENDED));
document.querySelectorAll("[data-legend=endedfail]").forEach(el => legend(el, ENDED.slice(1)));

// failure-code table: agents x codes, sequential shading
document.querySelectorAll("[data-codes]").forEach(el => {
  const [b, m] = el.dataset.codes.split(":"); const xs = sel(b, m).filter(r => !r.s);
  const used = CODES.filter(c => xs.some(r => r.c === c));
  const agents = AGENTS.filter(a => xs.some(r => r.a === a));
  const max = Math.max(1, ...agents.flatMap(a => used.map(c => xs.filter(r => r.a === a && r.c === c).length)));
  const shade = n => !n ? "" : `background:var(--q${Math.min(6, 1 + Math.floor(5 * n / max))});color:${n / max > 0.45 ? "#fff" : "var(--ink)"}`;
  let h = `<table class="codes"><thead><tr><th></th>${used.map(c => `<th class="num" title="${esc(CODE[c])}">${c}</th>`).join("")}<th class="num">${L("失败数", "failures")}</th></tr></thead><tbody>`;
  for (const a of agents) {
    const ys = xs.filter(r => r.a === a);
    h += `<tr><th>${esc(a)}</th>${used.map(c => { const n = ys.filter(r => r.c === c).length; return `<td class="c" style="${shade(n)}" title="${esc(a)} · ${c} ${esc(CODE[c])}: ${n}">${n || ""}</td>`; }).join("")}<td class="num">${ys.length}</td></tr>`;
  }
  h += `</tbody></table><div class="legend">${used.map(c => `<span><b>${c}</b> ${esc(CODE[c])}</span>`).join("")}</div>`;
  el.innerHTML = h;
});

// overview grid: tasks x agents
function grid(el, bench, mode) {
  const xs = R.filter(r => r.b === bench && r.m === mode && !r.sup);
  const agents = AGENTS.filter(a => xs.some(r => r.a === a));
  const tasks = [...new Set(xs.map(r => short(r.t)))].sort((p, q) => p.localeCompare(q));
  let h = `<div class="chart-title">${esc(BN[bench])} · ${esc(mode)}</div><table class="hm"><thead><tr><th></th>${agents.map(a => `<th>${esc(a)}</th>`).join("")}</tr></thead><tbody>`;
  for (const t of tasks) {
    h += `<tr><th class="fam" title="${esc(t)}">${esc(t)}</th>`;
    for (const a of agents) {
      const r = xs.find(x => short(x.t) === t && x.a === a);
      h += r ? `<td class="${cls(r)}" data-id="${esc(r.id)}">${esc(label(r))}</td>` : `<td class="N">·</td>`;
    }
    h += "</tr>";
  }
  h += `<tr class="tot"><th class="fam">${L("成功", "successes")}</th>${agents.map(a => { const ys = xs.filter(r => r.a === a); return `<td>${ys.filter(r => r.s).length}/${ys.length}</td>`; }).join("")}</tr></tbody></table>`;
  el.innerHTML = h; bindTips(el);
}
document.querySelectorAll("[data-grid]").forEach(el => { const [b, m] = el.dataset.grid.split(":"); grid(el, b, m); });

// dot plot: time used / budget for self-stops
document.querySelectorAll("[data-stops]").forEach(el => {
  const b = el.dataset.stops;
  const kinds = ENDED.filter(e => el.dataset.kind === "timeup" ? e[0] === "self_stop_believed_time_up" : e[0].startsWith("self_stop"));
  const xs = sel(b).filter(r => kinds.some(k => k[0] === r.e) && r.min != null && r.bud);
  const agents = AGENTS.filter(a => xs.some(r => r.a === a));
  const W = 760, lw = 92, rowH = 30, H = agents.length * rowH + 30, pw = W - lw - 20;
  let s = `<svg viewBox="0 0 ${W} ${H}" width="100%" style="max-width:${W}px">`;
  for (let t = 0; t <= 1.0001; t += 0.25) { const x = lw + t * pw; s += `<line class="gridl" x1="${x}" x2="${x}" y1="0" y2="${H - 22}"/><text x="${x}" y="${H - 6}" text-anchor="middle">${Math.round(t * 100)}%</text>`; }
  agents.forEach((a, i) => {
    const y = i * rowH + rowH / 2;
    s += `<text x="${lw - 8}" y="${y + 4}" text-anchor="end">${esc(a)}</text>`;
    xs.filter(r => r.a === a).forEach((r, j) => {
      const k = kinds.find(k => k[0] === r.e); const x = lw + Math.min(1, r.min / r.bud) * pw; const jit = ((j * 7) % 11 - 5) * 1.2;
      s += `<circle data-id="${esc(r.id)}" cx="${x}" cy="${y + jit}" r="5" fill="var(${k[2]})" stroke="var(--surface)" stroke-width="1.5" style="cursor:pointer"/>`;
    });
  });
  s += "</svg>"; el.innerHTML = s; bindTips(el);
});
document.querySelectorAll("[data-legend=stops]").forEach(el => legend(el, ENDED.filter(e => e[0].startsWith("self_stop"))));

// searchable table
(function () {
  const tb = $("#trialtable tbody"); if (!tb) return;
  const fb = $("#f-bench"), fm = $("#f-mode"), fa = $("#f-agent"), fo = $("#f-out"), fq = $("#f-q"), cnt = $("#f-count");
  fb.innerHTML = `<option value="">${L("全部基准", "all benchmarks")}</option>` + D.benches.map(b => `<option value="${b.key}">${esc(b.name)}</option>`).join("");
  fa.innerHTML = `<option value="">${L("全部 agent", "all agents")}</option>` + AGENTS.map(a => `<option>${esc(a)}</option>`).join("");
  fo.innerHTML = `<option value="">${L("全部结果", "all outcomes")}</option><option value="s">${L("成功", "success")}</option><option value="A">A</option><option value="B">B</option><option value="J">J</option><option value="f">${L("失败", "failed")}</option>` + CODES.map(c => `<option value="c:${c}">${c} ${esc(CODE[c])}</option>`).join("");
  function render() {
    const q = fq.value.trim().toLowerCase();
    const xs = R.filter(r => (!fb.value || r.b === fb.value) && (!fm.value || r.m === fm.value) && (!fa.value || r.a === fa.value) &&
      (!fo.value || (fo.value === "s" ? r.s : fo.value === "f" ? !r.s : fo.value.startsWith("c:") ? (!r.s && r.c === fo.value.slice(2)) : (r.s && r.g === fo.value))) &&
      (!q || [r.t, r.st, r.det, r.nb, r.ev, r.strat].join(" ").toLowerCase().includes(q)));
    cnt.textContent = `${xs.length} / ${R.length}`;
    tb.innerHTML = xs.slice(0, 600).map(r => `<tr data-id="${esc(r.id)}"><td>${esc(BN[r.b])}</td><td>${esc(short(r.t))}</td><td>${r.m === "privileged" ? "priv" : "std"}</td><td>${esc(r.a)}</td>
      <td><span class="pill ${cls(r)}">${esc(label(r))}</span>${r.st ? ` <span class="muted">${esc(r.st)}</span>` : ""}</td><td class="num">${r.min ?? "?"} / ${r.bud ?? "?"}</td><td>${esc(r.e || "")}</td><td class="det">${esc((r.det || "").slice(0, 220))}${(r.det || "").length > 220 ? "…" : ""}</td></tr>`).join("") +
      (xs.length > 600 ? `<tr><td colspan="8" class="muted">${L("只显示前 600 行，请用筛选缩小范围", "showing the first 600 rows; filter to narrow down")}</td></tr>` : "");
  }
  [fb, fm, fa, fo].forEach(x => x.onchange = render); fq.oninput = render;
  tb.onclick = e => { const tr = e.target.closest("tr[data-id]"); if (tr) openTrial(tr.dataset.id); };
  render();
})();
setTimeout(() => { const m = location.hash.match(/^#t=(.+)$/); if (m) openTrial(decodeURIComponent(m[1])); }, 0);
})();
