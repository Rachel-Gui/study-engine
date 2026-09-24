r"""widgets_py.py - interactive figures for the Python-from-zero and EDA chapters.
Same contract as widgets.py: (html, figure_id). Raw strings: the JS has "\n".
"""
import csv, json, os

# --------------------------------------------------------------- slice lab

SLICE_LAB = r"""
<div class="wg" id="wg-slice">
  <div class="wg-hd"><span class="k">Interactive</span>
    <strong>Indexing and slicing, by hand</strong>
    <span class="wg-eq" id="slq">rooms[0]</span></div>
  <div class="wg-bd">
    <div class="wg-ctl">
      <label class="wg-sel"><span>Mode</span><select id="slm">
        <option value="index">one item: rooms[i]</option>
        <option value="slice">a slice: rooms[start:stop:step]</option></select></label>
      <div id="slidx">
        <label><span>index i</span><input type="range" id="sli" min="-10" max="9" step="1" value="0"><output>0</output></label>
      </div>
      <div id="slsl" hidden>
        <label><span>start</span><input type="range" id="sla" min="-8" max="8" step="1" value="1"><output>1</output></label>
        <label><span>stop</span><input type="range" id="slb" min="-8" max="8" step="1" value="4"><output>4</output></label>
        <label><span>step</span><input type="range" id="slc" min="-3" max="3" step="1" value="1"><output>1</output></label>
      </div>
      <div class="wg-loss">
        <div><b id="slr" style="font-size:12px">&ndash;</b><span>result</span></div>
        <div><b id="sln">1</b><span>items</span></div>
        <div><b id="slt">str</b><span>type</span></div>
      </div>
      <p class="wg-hint" id="slnote"></p>
    </div>
    <svg viewBox="0 0 460 200" class="wg-svg" stroke="#111" fill="none" stroke-width="1.2">
      <text x="14" y="24" class="t sm">rooms = ["entry", "living", "kitchen", "hall", "bed 1", "bath", "bed 2", "study"]</text>
      <g id="slcells"></g>
    </svg>
  </div>
  <p class="wg-note">Positive indices count from the front starting at 0; negative ones count
    from the back starting at &minus;1. A slice includes <em>start</em> and stops just before
    <em>stop</em>. Push the index past the end and watch what Python says.</p>
</div>
<script>(function(){
  const $ = i => document.getElementById(i);
  const rooms = ["entry", "living", "kitchen", "hall", "bed 1", "bath", "bed 2", "study"];
  const n = rooms.length;
  function slice(a, b, c){
    // Python semantics for [a:b:c] on a list of length n
    if (c === 0) return null;
    const norm = (v, def) => v === null ? def : (v < 0 ? Math.max(v + n, c > 0 ? 0 : -1) : Math.min(v, c > 0 ? n : n - 1));
    let start, stop;
    if (c > 0) { start = norm(a, 0); stop = norm(b, n); }
    else { start = a === null ? n - 1 : (a < 0 ? Math.max(a + n, -1) : Math.min(a, n - 1));
           stop = b === null ? -1 : (b < 0 ? Math.max(b + n, -1) : Math.min(b, n - 1)); }
    const out = [];
    if (c > 0) for (let i = start; i < stop; i += c) out.push(i);
    else for (let i = start; i > stop; i += c) out.push(i);
    return out;
  }
  function draw(){
    const mode = $("slm").value;
    $("slidx").hidden = mode !== "index"; $("slsl").hidden = mode !== "slice";
    ["sli", "sla", "slb", "slc"].forEach(i => $(i).nextElementSibling.value = $(i).value);
    let hit = [], expr, result, note, err = false;
    if (mode === "index") {
      const i = +$("sli").value; expr = `rooms[${i}]`;
      const j = i < 0 ? i + n : i;
      if (j < 0 || j >= n) { err = true; result = "IndexError: list index out of range"; note = `There is no item ${i}. Valid indices run from 0 to ${n - 1}, or -1 to -${n} from the end.`; }
      else { hit = [j]; result = `"${rooms[j]}"`; note = i < 0 ? `-${-i} counts from the back: that is item ${j} counting from the front.` : `Item ${i} — the ${["first","second","third","fourth","fifth","sixth","seventh","eighth"][i]} one, because counting starts at 0.`; }
      $("sln").textContent = err ? "0" : "1"; $("slt").textContent = err ? "error" : "str";
    } else {
      const a = +$("sla").value, b = +$("slb").value, c = +$("slc").value;
      expr = `rooms[${a}:${b}${c === 1 ? "" : ":" + c}]`;
      if (c === 0) { err = true; result = "ValueError: slice step cannot be zero"; note = "A step of 0 would never move. Python refuses."; }
      else { hit = slice(a, b, c); result = "[" + hit.map(i => `"${rooms[i]}"`).join(", ") + "]";
        note = hit.length ? (c > 0 ? `Start ${a} is included, stop ${b} is not: indices ${hit.join(", ")}.` : `A negative step walks backwards: indices ${hit.join(", ")}.`) : "An empty list: nothing lies between start and stop in that direction. Not an error — slices never raise."; }
      $("sln").textContent = err ? "0" : hit.length; $("slt").textContent = err ? "error" : "list";
    }
    $("slq").textContent = expr; $("slr").textContent = result; $("slr").style.color = err ? "#b23b3b" : "";
    $("slnote").textContent = note;
    $("slcells").innerHTML = rooms.map((r, i) => {
      const x = 14 + i * 55, on = hit.includes(i);
      return `<rect x="${x}" y="70" width="50" height="40" rx="3" fill="${on ? '#4b2e83' : '#fff'}" stroke="${on ? '#4b2e83' : '#111'}"/>` +
        `<text x="${x + 25}" y="94" class="t" text-anchor="middle" style="fill:${on ? '#fff' : '#111'};font-size:10.5px">${r}</text>` +
        `<text x="${x + 25}" y="60" class="t sm" text-anchor="middle" style="fill:#4b2e83;font-weight:600">${i}</text>` +
        `<text x="${x + 25}" y="128" class="t sm" text-anchor="middle">${i - n}</text>`;
    }).join("") + `<text x="14" y="160" class="t sm">top row: index from the front &middot; bottom row: from the back</text>`;
  }
  ["slm", "sli", "sla", "slb", "slc"].forEach(i => $(i).addEventListener("input", draw));
  draw();
})();</script>
"""

# ---------------------------------------------------------- histogram lab
# Real values from assets/data/energy_efficiency.csv, embedded at build time so
# the widget works with nothing loaded.

def _energy():
    path = os.path.join(os.path.dirname(__file__), "..", "assets", "data", "energy_efficiency.csv")
    cols = {"heating_load": [], "cooling_load": [], "surface_area": [], "orientation": [], "glazing_area": []}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for k in cols:
                cols[k].append(float(row[k]))
    return cols


def hist_lab():
    d = _energy()
    data = json.dumps({k: [round(v, 2) for v in vs] for k, vs in d.items()}, separators=(",", ":"))
    return r"""
<div class="wg" id="wg-hist">
  <div class="wg-hd"><span class="k">Interactive</span>
    <strong>The same 768 buildings, different bins</strong>
    <span class="wg-eq" id="hq">heating_load &middot; 20 bins</span></div>
  <div class="wg-bd">
    <div class="wg-ctl">
      <label class="wg-sel"><span>Column</span><select id="hv">
        <option value="heating_load">heating_load (kWh/m&sup2;)</option>
        <option value="cooling_load">cooling_load (kWh/m&sup2;)</option>
        <option value="surface_area">surface_area (m&sup2;)</option>
        <option value="glazing_area">glazing_area (fraction)</option></select></label>
      <label><span>Bins</span><input type="range" id="hb" min="3" max="60" step="1" value="20"><output>20</output></label>
      <label class="wg-sel"><span>Split by</span><select id="hs">
        <option value="none">nothing</option><option value="orientation">orientation (2 N, 3 E, 4 S, 5 W)</option></select></label>
      <div class="wg-loss">
        <div><b id="hmean">&ndash;</b><span>mean</span></div>
        <div><b id="hmed">&ndash;</b><span>median</span></div>
        <div><b id="hsd">&ndash;</b><span>std dev</span></div>
      </div>
      <p class="wg-hint" id="hnote"></p>
    </div>
    <svg viewBox="0 0 460 260" class="wg-svg" stroke="#111" fill="none" stroke-width="1.2">
      <g id="hbars"></g>
      <line x1="40" y1="220" x2="440" y2="220" stroke="#ccc"/>
      <g id="hax"></g>
    </svg>
  </div>
  <p class="wg-note">A histogram has one free choice, the number of bins, and it changes the
    story. Too few and every column looks like a single lump; too many and noise looks like
    structure. Heating load here is <em>bimodal</em>: two clusters, one for each building
    height in the dataset. Split by orientation and the four histograms sit on top of each
    other &mdash; which is the first hint that orientation barely matters.</p>
</div>
<script>(function(){
  const $ = i => document.getElementById(i);
  const D = __DATA__;
  const cols = ["#4b2e83", "#b7a57a", "#767676", "#111"];
  function stats(v){ const s = [...v].sort((a, b) => a - b), m = v.reduce((a, b) => a + b, 0) / v.length;
    const med = s.length % 2 ? s[(s.length - 1) / 2] : (s[s.length / 2 - 1] + s[s.length / 2]) / 2, sd = Math.sqrt(v.reduce((a, b) => a + (b - m) ** 2, 0) / v.length); return [m, med, sd]; }
  function draw(){
    const col = $("hv").value, nb = +$("hb").value, split = $("hs").value;
    $("hb").nextElementSibling.value = nb;
    const v = D[col], lo = Math.min(...v), hi = Math.max(...v), w = (hi - lo) / nb || 1;
    const groups = split === "none" ? [null] : [2, 3, 4, 5];
    const hist = groups.map(g => { const h = new Array(nb).fill(0);
      v.forEach((x, i) => { if (g === null || D.orientation[i] === g) h[Math.min(nb - 1, Math.floor((x - lo) / w))]++; }); return h; });
    const mx = Math.max(...hist.flat());
    let out = "";
    hist.forEach((h, gi) => h.forEach((c, i) => {
      const x = 40 + i * 400 / nb, bw = 400 / nb, hgt = 190 * c / mx;
      if (groups.length === 1) out += `<rect x="${x.toFixed(1)}" y="${(220 - hgt).toFixed(1)}" width="${Math.max(1, bw - 1).toFixed(1)}" height="${hgt.toFixed(1)}" fill="#4b2e83" stroke="none" opacity=".85"/>`;
      else out += `<rect x="${(x + gi * bw / 4).toFixed(1)}" y="${(220 - hgt).toFixed(1)}" width="${Math.max(1, bw / 4 - .5).toFixed(1)}" height="${hgt.toFixed(1)}" fill="${cols[gi]}" stroke="none" opacity=".9"/>`;
    }));
    $("hbars").innerHTML = out;
    let ax = "";
    for (let k = 0; k <= 4; k++) { const x = 40 + k * 100, val = lo + (hi - lo) * k / 4;
      ax += `<text x="${x}" y="238" class="t sm" text-anchor="middle">${val.toFixed(val < 5 ? 2 : 0)}</text>`; }
    ax += `<text x="440" y="254" class="t sm" text-anchor="end">${col}</text>`;
    if (groups.length > 1) ax += ["N", "E", "S", "W"].map((n, i) => `<rect x="${360 + i * 22}" y="8" width="10" height="10" fill="${cols[i]}"/><text x="${372 + i * 22}" y="17" class="t sm">${n}</text>`).join("");
    $("hax").innerHTML = ax;
    const [m, med, sd] = stats(v);
    $("hmean").textContent = m.toFixed(2); $("hmed").textContent = med.toFixed(2); $("hsd").textContent = sd.toFixed(2);
    $("hq").innerHTML = col + " &middot; " + nb + " bins";
    $("hnote").textContent = nb <= 4 ? "With this few bins the shape is gone: you would never guess there are two clusters." :
      nb >= 45 ? "With this many bins each bar holds a handful of buildings and the gaps are sampling noise, not structure." :
      col === "heating_load" || col === "cooling_load" ? "Two clusters. The dataset has two building heights (3.5 m and 7 m); the taller buildings need far more heating and cooling." :
      col === "glazing_area" ? "Only four distinct values: 0, 0.1, 0.25, 0.4. This column is categorical in disguise; a histogram is the wrong plot for it." :
      "Surface area takes a handful of distinct values because the buildings were generated from twelve base shapes.";
  }
  ["hv", "hb", "hs"].forEach(i => $(i).addEventListener("input", draw));
  draw();
})();</script>
""".replace("__DATA__", data)


ALL = {
    "slice-lab": (SLICE_LAB, "indexing"),
}


def register():
    ALL["hist-lab"] = (hist_lab(), "dataframe_anatomy")
    return ALL
