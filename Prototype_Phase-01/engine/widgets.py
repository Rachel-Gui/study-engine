"""
widgets.py - interactive figures.

Each widget is a dict with:
    web()    HTML + inline SVG + a <script>, live in the browser
    frame()  a static SVG for the video, from figures.py

A widget is a figure you can push on. Everything here is dependency-free:
no charting library, no build step, just SVG the script rewrites.
"""
import json
import figures

# --------------------------------------------------------------- live neuron

NEURON = """
<div class="wg" id="wg-neuron">
  <div class="wg-hd"><span class="k">Interactive</span>
    <strong>One neuron, live</strong>
    <span class="wg-eq" id="nq">z = 0.00 &nbsp;&rarr;&nbsp; a = 0.00</span></div>
  <div class="wg-bd">
    <div class="wg-ctl">
      <label><span>x<sub>1</sub> temperature</span><input type="range" id="x1" min="15" max="30"
             step="0.5" value="21.5"><output>21.5</output></label>
      <label><span>x<sub>2</sub> humidity</span><input type="range" id="x2" min="20" max="90"
             step="1" value="44"><output>44</output></label>
      <label><span>x<sub>3</sub> hour</span><input type="range" id="x3" min="0" max="23"
             step="1" value="19"><output>19</output></label>
      <hr>
      <label><span>w<sub>1</sub></span><input type="range" id="w1" min="-2" max="2" step="0.1"
             value="0.8"><output>0.8</output></label>
      <label><span>w<sub>2</sub></span><input type="range" id="w2" min="-2" max="2" step="0.1"
             value="-0.2"><output>-0.2</output></label>
      <label><span>w<sub>3</sub></span><input type="range" id="w3" min="-2" max="2" step="0.1"
             value="1.4"><output>1.4</output></label>
      <label><span>b bias</span><input type="range" id="bb" min="-40" max="20" step="0.5"
             value="-3"><output>-3</output></label>
      <label class="wg-sel"><span>&#966; activation</span><select id="phi">
        <option value="relu">ReLU</option><option value="sigmoid">Sigmoid</option>
        <option value="tanh">Tanh</option><option value="linear">Linear</option>
      </select></label>
    </div>
    <svg viewBox="0 0 460 300" class="wg-svg" stroke="#111" fill="none"
         stroke-width="1.3" stroke-linecap="round">
      <text x="14" y="20" class="t sm">contribution of each input</text>
      <line x1="150" y1="30" x2="150" y2="128" stroke="#ccc"/>
      <g id="bars"></g>
      <text x="14" y="152" class="t sm">z, before activation</text>
      <line x1="150" y1="160" x2="150" y2="196" stroke="#ccc"/>
      <rect id="zbar" x="150" y="166" width="0" height="22" fill="#111" stroke="none"/>
      <text id="zt" x="156" y="182" class="t">0.00</text>
      <text x="270" y="220" class="t sm" text-anchor="middle">activation &#966;</text>
      <line x1="180" y1="286" x2="360" y2="286" stroke="#ccc"/>
      <line x1="270" y1="226" x2="270" y2="292" stroke="#ccc"/>
      <path id="curve" stroke-width="2"/>
      <circle id="dot" r="4.5" fill="#111" stroke="none"/>
      <text id="at" x="374" y="262" class="t">a = 0.00</text>
    </svg>
  </div>
  <p class="wg-note">Push the bias down until z goes negative. With ReLU the output
    clips flat at zero and the neuron stops responding at all &mdash; that clipping
    <em>is</em> the nonlinearity.</p>
</div>
<script>(function(){
  const $ = i => document.getElementById(i);
  const ids = ["x1","x2","x3","w1","w2","w3","bb"];
  const phis = {
    relu:    z => Math.max(0, z),
    sigmoid: z => 1/(1+Math.exp(-z)),
    tanh:    z => Math.tanh(z),
    linear:  z => z
  };
  function draw(){
    const v = {}; ids.forEach(i => { v[i] = +$(i).value; $(i).nextElementSibling.value = $(i).value; });
    const contrib = [v.x1*v.w1, v.x2*v.w2, v.x3*v.w3];
    const z = contrib.reduce((a,b)=>a+b,0) + v.bb;
    const f = phis[$("phi").value], a = f(z);

    const scale = 90/Math.max(12, ...contrib.map(Math.abs));
    $("bars").innerHTML = contrib.map((c,i)=>{
      const y = 36+i*30, w = Math.abs(c)*scale, x = c<0 ? 150-w : 150;
      return `<rect x="${x}" y="${y}" width="${w}" height="17" fill="#111" stroke="none"/>`
           + `<text x="14" y="${y+13}" class="t sm">w${i+1}x${i+1}</text>`
           + `<text x="${c<0?x-6:x+w+6}" y="${y+13}" class="t sm" `
           + `text-anchor="${c<0?'end':'start'}">${c.toFixed(1)}</text>`;
    }).join("");

    const zs = Math.min(Math.abs(z)*3, 110), zx = z<0 ? 150-zs : 150;
    $("zbar").setAttribute("x", zx); $("zbar").setAttribute("width", zs);
    $("zt").setAttribute("x", z<0 ? zx-6 : zx+zs+6);
    $("zt").setAttribute("text-anchor", z<0 ? "end" : "start");
    $("zt").textContent = z.toFixed(2);

    const X = t => 270 + t*9, Y = u => 256 - u*26;
    let d = "";
    for(let t=-10; t<=10; t+=0.25)
      d += (d?"L":"M") + X(t).toFixed(1) + "," + Math.max(228, Math.min(288, Y(f(t)))).toFixed(1);
    $("curve").setAttribute("d", d);
    const cz = Math.max(-10, Math.min(10, z));
    $("dot").setAttribute("cx", X(cz));
    $("dot").setAttribute("cy", Math.max(228, Math.min(288, Y(f(cz)))));
    $("at").textContent = "a = " + a.toFixed(2);
    $("nq").innerHTML = `z = ${z.toFixed(2)} &nbsp;&rarr;&nbsp; a = ${a.toFixed(2)}`;
  }
  ids.concat(["phi"]).forEach(i => $(i).addEventListener("input", draw));
  draw();
})();</script>
"""

# ------------------------------------------------------- activation explorer

ACTIVATIONS = """
<div class="wg" id="wg-act">
  <div class="wg-hd"><span class="k">Interactive</span>
    <strong>Why depth needs a nonlinearity</strong>
    <span class="wg-eq" id="aq">two layers &ne; one matrix</span></div>
  <div class="wg-bd">
    <div class="wg-ctl">
      <label class="wg-sel"><span>Activation</span><select id="af">
        <option value="none">none (linear)</option><option value="relu" selected>ReLU</option>
        <option value="sigmoid">Sigmoid</option><option value="tanh">Tanh</option>
      </select></label>
      <label><span>Hidden units</span><input type="range" id="au" min="1" max="12" step="1"
             value="6"><output>6</output></label>
      <p class="wg-hint">The grey line is the target. The black line is what a
        one-hidden-layer network can trace with this activation. Set the activation
        to <em>none</em> and it can only ever draw a straight line, no matter how
        many units you give it.</p>
    </div>
    <svg viewBox="0 0 460 260" class="wg-svg" stroke="#111" fill="none" stroke-width="1.3">
      <line x1="30" y1="230" x2="440" y2="230" stroke="#ccc"/>
      <line x1="30" y1="20" x2="30" y2="230" stroke="#ccc"/>
      <path id="target" stroke="#bbb" stroke-width="2" stroke-dasharray="5 4"/>
      <path id="fit" stroke-width="2.2"/>
      <text x="440" y="248" class="t sm" text-anchor="end">input</text>
    </svg>
  </div>
</div>
<script>(function(){
  const $ = i => document.getElementById(i);
  const F = { none: z=>z, relu: z=>Math.max(0,z),
              sigmoid: z=>1/(1+Math.exp(-z)), tanh: z=>Math.tanh(z) };
  // fixed pseudo-random layer so the picture is stable across reloads
  let s = 7; const rnd = () => (s = (s*1103515245+12345) % 2147483648) / 2147483648 - .5;
  const W1=[],B1=[],W2=[];
  for(let i=0;i<12;i++){ W1.push(rnd()*6); B1.push(rnd()*6); W2.push(rnd()*2.4); }
  const target = x => Math.sin(x*1.6)*0.8 + x*0.25;
  const X = x => 30 + (x+3)/6*410, Y = y => 125 - y*52;
  function path(fn){ let d=""; for(let x=-3;x<=3;x+=0.05){
      const y = Math.max(-2, Math.min(2, fn(x)));
      d += (d?"L":"M") + X(x).toFixed(1) + "," + Y(y).toFixed(1); } return d; }
  function draw(){
    const f = F[$("af").value], n = +$("au").value;
    $("au").nextElementSibling.value = n;
    $("target").setAttribute("d", path(target));
    $("fit").setAttribute("d", path(x => {
      let o = 0; for(let i=0;i<n;i++) o += W2[i]*f(W1[i]*x + B1[i]);
      return o/Math.sqrt(n)*0.9;
    }));
    $("aq").innerHTML = $("af").value === "none"
      ? "with no activation, W&#8322;(W&#8321;x) = (W&#8322;W&#8321;)x &mdash; a straight line"
      : n + " units &times; " + $("af").value + " &rarr; a curve";
  }
  ["af","au"].forEach(i => $(i).addEventListener("input", draw));
  draw();
})();</script>
"""

# --------------------------------------------------------- capacity explorer

CAPACITY = """
<div class="wg" id="wg-cap">
  <div class="wg-hd"><span class="k">Interactive</span>
    <strong>Depth, width, and parameter count</strong>
    <span class="wg-eq" id="cq">0 parameters</span></div>
  <div class="wg-bd">
    <div class="wg-ctl">
      <label><span>Hidden layers</span><input type="range" id="cd" min="1" max="5" step="1"
             value="3"><output>3</output></label>
      <label><span>Width of first layer</span><input type="range" id="cw" min="16" max="512"
             step="16" value="256"><output>256</output></label>
      <p class="wg-hint">Each layer halves. Inputs are the 28 sensor channels plus
        three clock features. Watch how fast the parameter count climbs &mdash; and
        remember that on the Episode 3.7 data, <strong>64-32 scored R&sup2; 0.380
        while 512-256-128-64 scored 0.353</strong>. Capacity is not accuracy.</p>
    </div>
    <svg viewBox="0 0 460 260" class="wg-svg" stroke="#111" fill="none" stroke-width="1.2">
      <g id="net"></g>
    </svg>
  </div>
</div>
<script>(function(){
  const $ = i => document.getElementById(i);
  function draw(){
    const d = +$("cd").value, w0 = +$("cw").value;
    $("cd").nextElementSibling.value = d; $("cw").nextElementSibling.value = w0;
    const widths = []; for(let i=0;i<d;i++) widths.push(Math.max(8, w0 >> i));
    const sizes = [31, ...widths, 1];
    let params = 0;
    for(let i=0;i<sizes.length-1;i++) params += sizes[i]*sizes[i+1] + sizes[i+1];

    const cols = sizes.length, gap = 400/(cols-1);
    let g = "", pos = [];
    sizes.forEach((n,i)=>{
      const shown = Math.min(n, 7), x = 30 + i*gap;
      const ys = []; for(let j=0;j<shown;j++) ys.push(120 + (j-(shown-1)/2)*26);
      pos.push({x, ys});
      g += `<text x="${x}" y="34" class="t sm" text-anchor="middle">${n}</text>`;
      if(n > shown) g += `<text x="${x}" y="${120+(shown/2)*26+16}" class="t sm" `
                       + `text-anchor="middle">&#8942;</text>`;
    });
    for(let i=0;i<pos.length-1;i++)
      pos[i].ys.forEach(y1 => pos[i+1].ys.forEach(y2 =>
        g += `<line x1="${pos[i].x+9}" y1="${y1}" x2="${pos[i+1].x-9}" y2="${y2}" `
           + `opacity=".13"/>`));
    pos.forEach(p => p.ys.forEach(y =>
      g += `<circle cx="${p.x}" cy="${y}" r="8.5" fill="#fff"/>`));
    $("net").innerHTML = g;
    $("cq").textContent = params.toLocaleString() + " parameters";
  }
  ["cd","cw"].forEach(i => $(i).addEventListener("input", draw));
  draw();
})();</script>
"""

# ------------------------------------------------------ regression line lab
# Teaching interaction adapted from Everly's buildConceptRegression prototype.
# The script owns only the immediately preceding widget; no global IDs or state.
REGRESSION_LINE = """
<div class="wg wg-regression-line">
  <div class="wg-hd"><span class="k">Interactive</span>
    <strong>Observe, predict, refit</strong>
    <span class="wg-eq" data-equation></span></div>
  <div class="wg-bd">
    <div class="wg-ctl">
      <p class="wg-hint">Drag a filled observation. The open point is the prediction
        at the same x; the dashed vertical gap is its residual.</p>
      <div class="regression-actions">
        <button type="button" data-refit>Refit</button>
        <button type="button" data-reset>Reset</button>
      </div>
      <p class="wg-hint" data-status role="status"></p>
    </div>
    <svg class="wg-svg" viewBox="0 0 720 390" role="group"
         aria-label="Draggable observations, predictions and vertical residuals">
      <path d="M70,30 V335 H660" class="regression-axis"/>
      <g data-ticks></g>
      <text x="365" y="378" class="regression-label">Building area (illustrative scale)</text>
      <text x="12" y="185" transform="rotate(-90 12 185)"
            class="regression-label regression-ylabel">Annual energy (illustrative scale)</text>
      <line data-line class="regression-fit"/>
      <g data-residuals></g><g data-predictions></g><g data-observations></g>
    </svg>
    <div class="regression-legend" aria-label="Plot legend">
      <span>● Observed y</span><span>○ Predicted ŷ</span>
      <span>— Current line</span><span>┆ Vertical residual</span>
    </div>
    <output class="regression-feedback" data-feedback aria-live="polite" aria-atomic="true"></output>
  </div>
  <p class="wg-note">Seven illustrative observations, not UW measurements.
    Select a point to inspect it; drag to move it. Refit minimises the sum of squared
    residuals. Reset restores the example line and observations.</p>
</div>
<script>(function(){
  const root = document.currentScript.previousElementSibling;
  const $ = selector => root.querySelector(selector);
  const defaults = __REGRESSION_DEFAULTS__;
  const points = defaults.points.map(([x, y]) => ({x, y}));
  let slope = defaults.line[0], intercept = defaults.line[1];
  let selected = defaults.selected, drag = null;
  const svg = $("svg"), status = $("[data-status]");
  const X = x => 70 + x * 5.9;
  let yMin = 0, yMax = 100;
  const Y = y => 335 - (y - yMin) / (yMax - yMin) * 305;
  const set = (node, attrs) => Object.entries(attrs).forEach(([k, v]) => node.setAttribute(k, v));
  const node = (tag, attrs) => {
    const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
    set(el, attrs); return el;
  };
  // Keep observation nodes stable during dragging and keyboard focus.
  const marks = points.map((p, i) => {
    const residual = node("line", {class: "regression-residual"});
    const prediction = node("circle", {r: 5, class: "regression-prediction"});
    const observation = node("circle", {r: 7, class: "regression-observation",
      tabindex: 0, role: "button", "data-point": i});
    $("[data-residuals]").append(residual);
    $("[data-predictions]").append(prediction);
    $("[data-observations]").append(observation);
    observation.addEventListener("focus", () => { selected = i; draw(); });
    observation.addEventListener("keydown", e => {
      if(e.key === "Enter" || e.key === " ") {
        e.preventDefault(); selected = i; draw();
      }
    });
    return {residual, prediction, observation};
  });
  function draw(){
    // Show the entire line and residuals, including predictions outside 0–100.
    yMin = Math.floor(Math.min(0, intercept, slope * 100 + intercept) / 10) * 10;
    yMax = Math.ceil(Math.max(100, intercept, slope * 100 + intercept) / 10) * 10;
    set($("[data-line]"), {x1: X(0), y1: Y(intercept), x2: X(100), y2: Y(slope * 100 + intercept)});
    const ticks = $("[data-ticks]"); ticks.replaceChildren();
    [0, 50, 100].forEach(t => {
      const label = node("text", {x: X(t), y: 355, class: "regression-label"});
      label.textContent = t; ticks.append(label);
    });
    [yMin, (yMin + yMax) / 2, yMax].forEach(t => {
      const label = node("text", {x: 58, y: Y(t) + 4, class: "regression-tick"});
      label.textContent = t; ticks.append(label);
    });
    points.forEach((p, i) => {
      const predicted = slope * p.x + intercept, m = marks[i];
      set(m.residual, {x1: X(p.x), y1: Y(p.y), x2: X(p.x), y2: Y(predicted)});
      set(m.prediction, {cx: X(p.x), cy: Y(predicted)});
      set(m.observation, {cx: X(p.x), cy: Y(p.y), "aria-pressed": i === selected,
        "aria-label": `Observation ${i + 1}: x ${p.x.toFixed(2)}, y ${p.y.toFixed(2)}. Select to inspect; drag to move.`});
      m.residual.classList.toggle("is-selected", i === selected);
    });
    $("[data-equation]").textContent = `ŷ = ${slope.toFixed(3)}x ${intercept < 0 ? "−" : "+"} ${Math.abs(intercept).toFixed(3)}`;
    const p = points[selected], predicted = slope * p.x + intercept, residual = p.y - predicted;
    const signed = `${residual >= 0 ? "+" : ""}${residual.toFixed(2)}`;
    $("[data-feedback]").textContent = `Point ${selected + 1} · x = ${p.x.toFixed(2)} · Observed y = ${p.y.toFixed(2)} · Predicted ŷ = ${predicted.toFixed(2)} · Residual y − ŷ = ${signed}`;
  }
  function endDrag(){
    if(!drag) return;
    const id = drag.id; drag = null;
    if(svg.hasPointerCapture(id)) svg.releasePointerCapture(id);
  }
  svg.addEventListener("pointerdown", e => {
    const point = e.target.closest("[data-point]");
    if(!point || drag || !e.isPrimary || e.button !== 0) return;
    e.preventDefault(); selected = Number(point.dataset.point);
    point.focus({preventScroll: true});
    drag = {id: e.pointerId, index: selected};
    svg.setPointerCapture(e.pointerId); draw();
  });
  svg.addEventListener("pointermove", e => {
    if(!drag || drag.id !== e.pointerId) return;
    const matrix = svg.getScreenCTM(); if(!matrix) return;
    const cursor = svg.createSVGPoint(); cursor.x = e.clientX; cursor.y = e.clientY;
    const pos = cursor.matrixTransform(matrix.inverse());
    const p = points[drag.index];
    p.x = Math.max(0, Math.min(100, (pos.x - 70) / 5.9));
    p.y = Math.max(0, Math.min(100, yMin + (335 - pos.y) / 305 * (yMax - yMin)));
    status.textContent = "Observations changed. The current line is unchanged; press Refit.";
    draw();
  });
  ["pointerup", "pointercancel", "lostpointercapture"].forEach(type => {
    svg.addEventListener(type, e => { if(drag?.id === e.pointerId) endDrag(); });
  });
  $("[data-refit]").addEventListener("click", () => {
    endDrag();
    const meanX = points.reduce((sum, p) => sum + p.x, 0) / points.length;
    const meanY = points.reduce((sum, p) => sum + p.y, 0) / points.length;
    const xx = points.reduce((sum, p) => sum + (p.x - meanX) ** 2, 0);
    if(xx <= 1e-10) {
      status.textContent = "Cannot fit a unique line: the x values are the same or too close together. Move a point horizontally, then Refit. The current line is retained.";
      return;
    }
    const xy = points.reduce((sum, p) => sum + (p.x - meanX) * (p.y - meanY), 0);
    slope = xy / xx; intercept = meanY - slope * meanX;
    status.textContent = "Least-squares line fitted to the current observations. Displayed numbers are rounded; calculations use full precision.";
    draw();
  });
  function reset(){
    endDrag();
    defaults.points.forEach(([x, y], i) => Object.assign(points[i], {x, y}));
    [slope, intercept] = defaults.line; selected = defaults.selected;
    status.textContent = "Example line — not yet fitted. Drag an observation or press Refit.";
    draw();
  }
  $("[data-reset]").addEventListener("click", reset);
  reset();
})();</script>
""".replace("__REGRESSION_DEFAULTS__", json.dumps({
    "points": figures.REGRESSION_POINTS, "line": figures.REGRESSION_LINE,
    "selected": figures.REGRESSION_SELECTED,
}))


# ------------------------------------------------------- UW feature set lab
# A local, dependency-free adaptation of Everly's earlier feature-selection
# interaction. It uses the same cleaned rows and fixed random_state=42 split as
# the cumulative Python lab. Warehouse is deliberately the program reference.
UW_FEATURE_LAB = """
<div class="wg wg-uw-features">
  <div class="wg-hd"><span class="k">Interactive</span>
    <strong>Feature-set test bench</strong>
    <span class="wg-eq">Predict → Test → Interpret → Reflect</span></div>
  <div class="uw-feature-body">
    <div class="uw-feature-controls">
      <div class="uw-stage"><span>01 · Predict</span>
        <label>Before testing, what do you expect to happen?
          <textarea data-expectation rows="3" placeholder="I expect test MAE to… because…"></textarea>
        </label>
      </div>
      <div class="uw-stage"><span>02 · Choose features</span>
        <fieldset><legend>Geometric</legend>
          <label><input type="checkbox" data-feature="Area_m" checked> Area_m</label>
          <label><input type="checkbox" data-feature="Height" checked> Height</label>
          <label><input type="checkbox" data-feature="Building_Length_m"> Building length</label>
          <label><input type="checkbox" data-feature="Orientation (degrees north)"> Orientation</label>
          <label><input type="checkbox" data-feature="Relative Compactness"> Relative compactness</label>
        </fieldset>
        <fieldset><legend>Operational</legend>
          <label><input type="checkbox" data-feature="Year_Built" checked> Year built</label>
          <label><input type="checkbox" data-feature="Occupants"> Occupants</label>
        </fieldset>
        <fieldset><legend>Program · warehouse omitted</legend>
          <label><input type="checkbox" data-feature="apartments"> Apartments</label>
          <label><input type="checkbox" data-feature="parking"> Parking</label>
          <label><input type="checkbox" data-feature="stadium"> Stadium</label>
          <label><input type="checkbox" data-feature="university"> University</label>
          <label><input type="checkbox" data-feature="utility"> Utility</label>
        </fieldset>
        <fieldset><legend>Environmental</legend>
          <label><input type="checkbox" data-feature="Tree_Canopy"> Tree canopy</label>
          <label><input type="checkbox" data-feature="Land_Surface_Temp"> Land-surface temperature</label>
        </fieldset>
      </div>
      <div class="uw-feature-actions">
        <button type="button" data-test>Test selected features</button>
        <button type="button" data-reset>Reset baseline</button>
      </div>
      <p class="uw-feature-status" data-status role="status">Choose a feature set, write a prediction, then test it.</p>
    </div>
    <div class="uw-feature-results" data-results>
      <div class="uw-feature-empty">
        <strong>03 · Test and interpret</strong>
        <p>Results will use the same 91 training and 23 test buildings as the guided workflow.</p>
      </div>
    </div>
  </div>
  <p class="wg-note">The course scope retains 114 rows. Every comparison uses the
    fixed <code>random_state=42</code> split. Coefficients are associations; their raw
    magnitudes are not comparable measures of feature importance.</p>
</div>
<script>(function(){
  const root = document.currentScript.previousElementSibling;
  const $ = selector => root.querySelector(selector);
  const $$ = selector => [...root.querySelectorAll(selector)];
  const target = "Energy_Use_kWh";
  const testPositions = __UW_TEST_POSITIONS__;
  const defaults = new Set(["Area_m", "Height", "Year_Built"]);
  const programFeatures = ["apartments", "parking", "stadium", "university", "utility"];
  const contexts = {
    "Area_m": "per dataset area unit; definition/unit unresolved",
    "Height": "per dataset height unit; unit unresolved",
    "Building_Length_m": "per metre of building length",
    "Orientation (degrees north)": "per degree north",
    "Relative Compactness": "per compactness unit; calculation unresolved",
    "Year_Built": "per calendar year",
    "Occupants": "per occupant-field unit; derivation unresolved",
    "Tree_Canopy": "per tree-canopy unit; unit/derivation unresolved",
    "Land_Surface_Temp": "per temperature-field unit; unit unresolved"
  };
  let rowsPromise = null;
  let history = [];
  // Only successful tests advance the pair; changing the checkboxes does not.
  let currentModel = null, previousModel = null;
  let axisLimits = null;

  function parseCsv(text){
    const records = []; let row = [], field = "", quoted = false;
    for(let i = 0; i < text.length; i++){
      const c = text[i];
      if(c === '"'){
        if(quoted && text[i + 1] === '"'){ field += '"'; i++; }
        else quoted = !quoted;
      } else if(c === "," && !quoted){ row.push(field); field = ""; }
      else if((c === "\\n" || c === "\\r") && !quoted){
        if(c === "\\r" && text[i + 1] === "\\n") i++;
        row.push(field); field = "";
        if(row.some(value => value !== "")) records.push(row);
        row = [];
      } else field += c;
    }
    if(field || row.length){ row.push(field); records.push(row); }
    const headers = records.shift().map(h => h.trim());
    return records.map(values => Object.fromEntries(headers.map((h, i) => [h, (values[i] || "").trim()])));
  }

  async function loadRows(){
    if(!rowsPromise){
      rowsPromise = fetch("assets/data/UW_building_energy.csv")
        .then(response => {
          if(!response.ok) throw new Error("The UW dataset could not be loaded from site assets.");
          return response.text();
        })
        .then(parseCsv)
        .then(raw => raw.map(row => {
          const converted = {...row};
          Object.keys(converted).forEach(key => {
            if(key !== "Name") converted[key] = Number(converted[key]);
          });
          return converted;
        }).filter(row => row[target] <= 10_000_000 && row.Area_m <= 60_000));
    }
    return rowsPromise;
  }

  function solve(matrix, vector){
    const n = vector.length;
    const augmented = matrix.map((row, i) => [...row, vector[i]]);
    for(let col = 0; col < n; col++){
      let pivot = col;
      for(let row = col + 1; row < n; row++)
        if(Math.abs(augmented[row][col]) > Math.abs(augmented[pivot][col])) pivot = row;
      if(Math.abs(augmented[pivot][col]) < 1e-9) return null;
      [augmented[col], augmented[pivot]] = [augmented[pivot], augmented[col]];
      const divisor = augmented[col][col];
      for(let j = col; j <= n; j++) augmented[col][j] /= divisor;
      for(let row = 0; row < n; row++){
        if(row === col) continue;
        const factor = augmented[row][col];
        for(let j = col; j <= n; j++) augmented[row][j] -= factor * augmented[col][j];
      }
    }
    return augmented.map(row => row[n]);
  }

  function redundantFeatures(training, features){
    const basis = [];
    const redundant = [];
    features.forEach(feature => {
      const values = training.map(row => row[feature]);
      const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
      let vector = values.map(value => value - mean);
      const originalNorm = Math.hypot(...vector);
      if(originalNorm < 1e-10){ redundant.push(feature); return; }
      basis.forEach(unit => {
        const projection = vector.reduce((sum, value, i) => sum + value * unit[i], 0);
        vector = vector.map((value, i) => value - projection * unit[i]);
      });
      const norm = Math.hypot(...vector);
      if(norm / originalNorm < 1e-8) redundant.push(feature);
      else basis.push(vector.map(value => value / norm));
    });
    return redundant;
  }

  function fitModel(rows, features){
    if(rows.length !== 114)
      throw new Error(`Expected 114 in-scope buildings, but found ${rows.length}. Check the published dataset.`);
    const testSet = new Set(testPositions);
    const training = rows.filter((_, i) => !testSet.has(i));
    const testing = rows.filter((_, i) => testSet.has(i));
    const redundant = redundantFeatures(training, features);
    if(redundant.length)
      throw new Error(`These selected features repeat information already in the model: ${redundant.join(", ")}. Remove one and test again.`);

    const means = {}, scales = {};
    features.forEach(feature => {
      means[feature] = training.reduce((sum, row) => sum + row[feature], 0) / training.length;
      scales[feature] = Math.sqrt(training.reduce((sum, row) => sum + (row[feature] - means[feature]) ** 2, 0) / training.length);
      if(!Number.isFinite(scales[feature]) || scales[feature] < 1e-10)
        throw new Error(`${feature} has no usable variation in the training buildings.`);
    });
    const design = row => [1, ...features.map(feature => (row[feature] - means[feature]) / scales[feature])];
    const p = features.length + 1;
    const gram = Array.from({length: p}, () => Array(p).fill(0));
    const rhs = Array(p).fill(0);
    training.forEach(row => {
      const x = design(row);
      for(let i = 0; i < p; i++){
        rhs[i] += x[i] * row[target];
        for(let j = 0; j < p; j++) gram[i][j] += x[i] * x[j];
      }
    });
    const standardized = solve(gram, rhs);
    if(!standardized || standardized.some(value => !Number.isFinite(value)))
      throw new Error("This feature combination is too redundant to fit reliably. Remove a related feature and test again.");
    const coefficients = standardized.slice(1).map((value, i) => value / scales[features[i]]);
    const intercept = standardized[0] - coefficients.reduce((sum, value, i) => sum + value * means[features[i]], 0);
    const predict = row => intercept + features.reduce((sum, feature, i) => sum + coefficients[i] * row[feature], 0);
    const actual = testing.map(row => row[target]);
    const predicted = testing.map(predict);
    if(predicted.some(value => !Number.isFinite(value)))
      throw new Error("This feature combination could not produce usable predictions. Adjust it and try again.");
    const errors = actual.map((value, i) => predicted[i] - value);
    const mae = errors.reduce((sum, value) => sum + Math.abs(value), 0) / errors.length;
    const rmse = Math.sqrt(errors.reduce((sum, value) => sum + value * value, 0) / errors.length);
    const meanActual = actual.reduce((sum, value) => sum + value, 0) / actual.length;
    const rss = errors.reduce((sum, value) => sum + value * value, 0);
    const tss = actual.reduce((sum, value) => sum + (value - meanActual) ** 2, 0);
    return {training, testing, features, coefficients, intercept, actual, predicted,
            mae, rmse, r2: 1 - rss / tss};
  }

  function fmt(value, digits = 0){
    return Number(value).toLocaleString(undefined, {maximumFractionDigits: digits, minimumFractionDigits: digits});
  }

  function extendAxisLimits(rows, result){
    // Start with the course-scope energy range, as in the original interaction.
    // Expand only when needed: no independent rescaling or clipped predictions.
    const values = [0, ...rows.map(row => row[target]), ...result.predicted];
    const low = Math.min(...values), high = Math.max(...values);
    const padding = Math.max((high - low) * 0.06, 1);
    axisLimits = axisLimits
      ? [low < axisLimits[0] ? low - padding : axisLimits[0],
         high > axisLimits[1] ? high + padding : axisLimits[1]]
      : [low - padding, high + padding];
  }

  function plot(actual, predicted, previous = null){
    const [low, high] = axisLimits;
    const left = 68, top = 28, width = 332, height = 252;
    const x = value => left + (value - low) / (high - low) * width;
    const y = value => top + height - (value - low) / (high - low) * height;
    // Restore the original ghost points and vertical prediction-shift connectors.
    const shifts = previous ? actual.map((value, i) =>
      `<line class="uw-prediction-shift" x1="${x(value).toFixed(2)}" x2="${x(value).toFixed(2)}"`
      + ` y1="${y(previous[i]).toFixed(2)}" y2="${y(predicted[i]).toFixed(2)}"/>`).join("") : "";
    const ghosts = previous ? actual.map((value, i) =>
      `<circle class="uw-prediction-previous" cx="${x(value).toFixed(2)}" cy="${y(previous[i]).toFixed(2)}" r="5.5">`
      + `<title>Actual ${fmt(value)} kWh; previous prediction ${fmt(previous[i])} kWh</title></circle>`).join("") : "";
    const dots = actual.map((value, i) =>
      `<circle class="uw-prediction-current" cx="${x(value).toFixed(2)}" cy="${y(predicted[i]).toFixed(2)}" r="4.2">`
      + `<title>Actual ${fmt(value)} kWh; current prediction ${fmt(predicted[i])} kWh</title></circle>`).join("");
    return `<svg viewBox="0 0 440 330" role="img" aria-label="Actual versus predicted annual energy use for 23 test buildings">
      <text x="220" y="15" class="uw-plot-title">Actual vs Predicted · test buildings</text>
      <path d="M${left},${top} V${top + height} H${left + width}" class="uw-axis"/>
      <line x1="${x(low)}" y1="${y(low)}" x2="${x(high)}" y2="${y(high)}" class="uw-reference"/>
      ${shifts}${ghosts}${dots}
      <text x="${left}" y="${top + height + 20}" class="uw-tick">${fmt(low)}</text>
      <text x="${left + width}" y="${top + height + 20}" class="uw-tick uw-end">${fmt(high)}</text>
      <text x="${left - 8}" y="${top + height}" class="uw-tick uw-y">${fmt(low)}</text>
      <text x="${left - 8}" y="${top + 4}" class="uw-tick uw-y">${fmt(high)}</text>
      <text x="${left + width / 2}" y="318" class="uw-label">Actual annual energy use (kWh)</text>
      <text x="16" y="${top + height / 2}" transform="rotate(-90 16 ${top + height / 2})" class="uw-label">Predicted annual energy use (kWh)</text>
      <text x="${left + width - 4}" y="${top + 14}" class="uw-reference-label">y = x</text>
    </svg>`;
  }

  function renderFeaturePlot(compare = false){
    if(!currentModel) return;
    const showPrevious = compare && previousModel !== null;
    $("[data-plot]").innerHTML = `
      <label class="uw-compare-models"><input type="checkbox" data-compare-models
        ${showPrevious ? "checked" : ""} ${previousModel ? "" : "disabled"}> Compare with previous model</label>
      <p class="uw-comparison-note">${previousModel
        ? "Previous means the immediately preceding successful test."
        : "Test another feature set to enable comparison."}
        Both models share the same axes. Limits stay fixed unless a new prediction needs more room.</p>
      <div class="uw-plot-legend" aria-label="Plot legend">
        <span><i class="uw-current-key" aria-hidden="true"></i> Current model</span>
        ${showPrevious ? `<span><i class="uw-previous-key" aria-hidden="true"></i> Previous model</span>
        <span><i class="uw-shift-key" aria-hidden="true"></i> Prediction change</span>` : ""}
        <span><i class="uw-reference-key" aria-hidden="true"></i> y = x</span>
      </div>
      ${plot(currentModel.actual, currentModel.predicted, showPrevious ? previousModel.predicted : null)}
      ${showPrevious ? `<p class="uw-comparison-note">Previous model features: ${previousModel.features.join(", ")}</p>` : ""}`;
    $("[data-compare-models]").addEventListener("change", event => {
      renderFeaturePlot(event.target.checked);
      $("[data-compare-models]").focus({preventScroll: true});
    });
  }

  function render(result, previousMae){
    const direction = value => value > 0 ? "positive" : value < 0 ? "negative" : "zero";
    const allProgramDummies = programFeatures.every(feature => result.features.includes(feature));
    const contextFor = feature => programFeatures.includes(feature)
      ? `${feature} versus ${allProgramDummies ? "warehouse" : "pooled omitted programs"}`
      : contexts[feature];
    const change = previousMae == null ? "First result in this comparison." :
      `${fmt(Math.abs(result.mae - previousMae))} kWh ${result.mae < previousMae ? "lower" : "higher"} than the previous test MAE.`;
    const coefficientRows = result.features.map((feature, i) =>
      `<tr><th scope="row">${feature}</th><td>${fmt(result.coefficients[i], 1)}</td>`
      + `<td>${direction(result.coefficients[i])}</td><td>${contextFor(feature)}</td></tr>`).join("");
    const historyRows = history.slice(0, 4).map(item =>
      `<li><span>${item.features.join(", ")}</span><strong>${fmt(item.mae)} kWh MAE</strong></li>`).join("");
    const negative = result.r2 < 0
      ? `<p class="uw-warning">Negative test R² means this model generalizes poorly on the fixed split. It is a modeling result, not a software failure.</p>` : "";
    $("[data-results]").innerHTML = `
      <div class="uw-result-head"><span>03 · Test</span><strong>${result.features.join(", ")}</strong></div>
      <div class="uw-metrics">
        <div class="primary"><span>Primary · test MAE</span><b>${fmt(result.mae)} kWh</b><small>${change}</small></div>
        <div><span>Test RMSE</span><b>${fmt(result.rmse)} kWh</b></div>
        <div><span>Test R²</span><b>${result.r2.toFixed(3)}</b></div>
      </div>
      ${negative}
      <div class="uw-plot" data-plot></div>
      <div class="uw-stage uw-interpret"><span>04 · Interpret</span>
        <div class="uw-table-wrap"><table><thead><tr><th>Feature</th><th>Coefficient</th><th>Direction</th><th>Context</th></tr></thead>
        <tbody>${coefficientRows}</tbody></table></div>
        <p>Each coefficient holds the other selected predictors constant. Coefficient does not mean causality, and raw magnitudes are not feature importance when scales differ.</p>
      </div>
      <div class="uw-stage uw-reflect"><span>05 · Reflect</span>
        <label>Did the result match your prediction?
          <select data-match><option value="">Choose after comparing</option><option>Yes</option><option>Partly</option><option>No</option></select>
        </label>
        <p data-reflection hidden>Use the prediction you wrote to explain what changed in test MAE, then ask whether the coefficient directions are plausible associations.</p>
      </div>
      <div class="uw-history"><span>Recent fixed-split comparisons</span><ol>${historyRows}</ol></div>`;
    renderFeaturePlot();
    $("[data-match]").addEventListener("change", event => {
      const note = $("[data-reflection]");
      note.hidden = !event.target.value;
    });
  }

  $("[data-test]").addEventListener("click", async event => {
    const button = event.currentTarget;
    const selected = $$("[data-feature]:checked").map(input => input.dataset.feature);
    if(!selected.length){ $("[data-status]").textContent = "Select at least one predictor."; return; }
    button.disabled = true;
    $("[data-reset]").disabled = true;
    $("[data-status]").textContent = "Loading the published dataset and fitting this feature set…";
    try {
      const rows = await loadRows();
      const result = fitModel(rows, selected);
      // Fitting must succeed before either saved model or the chart range changes.
      previousModel = currentModel;
      currentModel = result;
      extendAxisLimits(rows, result);
      history.unshift({features: [...selected], mae: result.mae});
      render(result, previousModel?.mae ?? null);
      $("[data-status]").textContent = `Tested ${selected.length} feature${selected.length === 1 ? "" : "s"} on 23 unseen buildings.`;
    } catch(error){
      $("[data-status]").textContent = error.message || "This feature set could not be evaluated. Adjust it and try again.";
    } finally {
      button.disabled = false;
      $("[data-reset]").disabled = false;
    }
  });

  $("[data-reset]").addEventListener("click", () => {
    $$("[data-feature]").forEach(input => { input.checked = defaults.has(input.dataset.feature); });
    $("[data-expectation]").value = "";
    history = [];
    currentModel = null; previousModel = null; axisLimits = null;
    $("[data-status]").textContent = "Baseline restored. Write a prediction, then test it.";
    $("[data-results]").innerHTML = `<div class="uw-feature-empty"><strong>03 · Test and interpret</strong><p>Results will use the same 91 training and 23 test buildings as the guided workflow.</p></div>`;
  });
})();</script>
""".replace("__UW_TEST_POSITIONS__", json.dumps([
    80, 4, 40, 69, 10, 45, 70, 66, 47, 11, 98, 36,
    83, 112, 18, 0, 72, 26, 81, 53, 103, 91, 12,
]))


# ------------------------------------------------------- prompt anatomy
# NOTE: these are RAW strings. The JS below contains \n escapes that belong to
# JavaScript, not to Python - a plain "..." string would turn them into real
# newlines and break the JS string literals.

PROMPT_LAB = r"""
<div class="wg" id="wg-prompt">
  <div class="wg-hd"><span class="k">Interactive</span>
    <strong>What actually gets sent to the model</strong>
    <span class="wg-eq" id="pq">0 chars</span></div>
  <div class="wg-bd" style="grid-template-columns:1fr 1.3fr">
    <div class="wg-ctl">
      <label class="wg-sel"><span>Instructions</span><select id="pi">
        <option value="vague">Vague version</option>
        <option value="sharp" selected>Sharp version</option>
      </select></label>
      <label class="wg-sel"><span>Output schema</span><select id="ps">
        <option value="on" selected>appended</option>
        <option value="off">omitted</option>
      </select></label>
      <label class="wg-sel"><span>Context</span><select id="pc">
        <option value="on" selected>geometry + climate</option>
        <option value="off">none</option>
      </select></label>
      <p class="wg-hint">Switch to the vague version and read what changes. The model
        receives the same building data either way &mdash; the only difference is how
        much you constrained it. That difference is the whole job.</p>
      <p class="wg-hint" id="pw"></p>
    </div>
    <div class="pr">
      <div class="pr-h">system prompt</div><pre id="psys"></pre>
      <div class="pr-h">user message</div><pre id="pusr"></pre>
    </div>
  </div>
</div>
<script>(function(){
  var $ = function(i){ return document.getElementById(i); };
  var INSTR = {
    vague: [
      "You are the energy efficiency advocate.",
      "Comment on the building's energy performance."
    ].join("\n"),
    sharp: [
      "You are the energy efficiency advocate. Your ONLY concern is",
      "reducing operational energy use.",
      "",
      "Argue from these angles:",
      "- Is the surface-to-volume ratio efficient for this climate?",
      "- Is the WWR causing excessive heat loss or cooling load?",
      "- Does the orientation exploit passive solar heating?",
      "",
      "Reference specific numbers from the data. Take a strong position.",
      "If the WWR is too high for a heating-dominated climate, say so and",
      "propose a specific lower number.",
      "",
      "You may NOT consider daylight quality or embodied carbon. Those are",
      "other advocates' concerns."
    ].join("\n")
  };
  var SCHEMA = [
    "", "",
    "Respond ONLY with JSON:",
    "{ 'argument': str, 'critical_finding': str,",
    "  'proposed_changes': [ {'parameter': str, 'value': num} ] }"
  ].join("\n");
  var CTX = [
    "## Geometry",
    "A 6-storey block, 42 x 24 m, 21 m tall.",
    "WWR 0.55, oriented 15 degrees east of south.",
    "{ 'L': 42, 'W': 24, 'H': 21, 'floors': 6,",
    "  'wwr': 0.55, 'orientation': 15 }",
    "",
    "## Climate",
    "Seattle, WA. ASHRAE 4C, heating-dominated.",
    "{ 'zone': '4C', 'HDD18': 2800, 'CDD18': 180 }"
  ].join("\n");
  function draw(){
    var sharp = $("pi").value === "sharp";
    var sys = INSTR[$("pi").value] + ($("ps").value === "on" ? SCHEMA : "");
    var usr = $("pc").value === "on" ? CTX : "(no context supplied)";
    $("psys").textContent = sys;
    $("pusr").textContent = usr;
    $("pq").textContent = (sys.length + usr.length) + " chars";
    $("pw").innerHTML = sharp
      ? "<strong>Scoped, checklisted, bounded, and forced to give a number.</strong> This is what separates an agent from a chatbot."
      : "<strong>Nothing here constrains the answer.</strong> It will return something fluent, general, and useless for a design decision.";
  }
  ["pi","ps","pc"].forEach(function(i){ $(i).addEventListener("input", draw); });
  draw();
})();</script>
"""

# --------------------------------------------------- orchestration cost

ORCH_LAB = r"""
<div class="wg" id="wg-orch">
  <div class="wg-hd"><span class="k">Interactive</span>
    <strong>Sequential or parallel</strong>
    <span class="wg-eq big" id="oq">0 s</span></div>
  <div class="wg-bd">
    <div class="wg-ctl">
      <label><span>Advocates</span><input type="range" id="oa" min="1" max="6"
             step="1" value="3"><output>3</output></label>
      <label><span>Seconds per call</span><input type="range" id="ot" min="2" max="30"
             step="1" value="12"><output>12</output></label>
      <label class="wg-sel"><span>Advocates run</span><select id="om">
        <option value="par" selected>in parallel</option>
        <option value="seq">one after another</option>
      </select></label>
      <p class="wg-hint"><strong>Who waits for whom.</strong> The <em>researcher</em>
        runs first and alone, because every advocate needs its site data. The
        <em>advocates</em> are independent &mdash; none reads another's output &mdash;
        so they can all run at once. The <em>manager</em> runs last, because it needs
        every advocate's result. Dependency, not speed, decides the shape.</p>
      <p class="wg-hint" id="onote"></p>
    </div>
    <svg viewBox="0 0 460 260" class="wg-svg" stroke="#111" fill="none" stroke-width="1.2">
      <g id="gantt"></g>
    </svg>
  </div>
</div>
<script>(function(){
  var $ = function(i){ return document.getElementById(i); };
  function draw(){
    var n = +$("oa").value, t = +$("ot").value, par = $("om").value === "par";
    $("oa").nextElementSibling.value = n;
    $("ot").nextElementSibling.value = t;
    var total = t + (par ? t : n * t) + t;
    var px = 340 / Math.max(total, 1), x0 = 112, y = 26, g = "";
    function bar(lab, start, dur, kind){
      var fill = kind === "gate" ? "#4b2e83" : "#d9d3e6";
      var s = '<rect x="' + (x0 + start*px) + '" y="' + y + '" width="'
        + Math.max(2, dur*px) + '" height="20" rx="2" fill="' + fill + '" stroke="none"/>'
        + '<text x="' + (x0-10) + '" y="' + (y+14) + '" font-size="12" font-weight="600" '
        + 'text-anchor="end" font-family="Montserrat,sans-serif" fill="#111" '
        + 'stroke="none">' + lab + '</text>';
      y += 27; return s;
    }
    g += bar("researcher", 0, t, "gate");
    for(var i=0;i<n;i++) g += bar("advocate " + (i+1), par ? t : t + i*t, t, "par");
    g += bar("manager", par ? 2*t : t + n*t, t, "gate");
    // dependency markers: the two waits that cannot be parallelised away
    var xr = x0 + t*px, xm = x0 + (par ? 2*t : t + n*t)*px;
    g += '<line x1="' + xr + '" y1="20" x2="' + xr + '" y2="' + (y-4) + '" stroke="#4b2e83" stroke-dasharray="3 3" opacity=".6"/>'
       + '<line x1="' + xm + '" y1="20" x2="' + xm + '" y2="' + (y-4) + '" stroke="#4b2e83" stroke-dasharray="3 3" opacity=".6"/>'
       + '<text x="' + (xr+4) + '" y="18" font-size="9" font-family="Montserrat,sans-serif" fill="#4b2e83" stroke="none">advocates wait here</text>'
       + '<text x="' + (xm+4) + '" y="' + (y+6) + '" font-size="9" font-family="Montserrat,sans-serif" fill="#4b2e83" stroke="none">manager waits here</text>';
    g += '<line x1="' + x0 + '" y1="' + (y+12) + '" x2="' + (x0+340) + '" y2="'
       + (y+12) + '" stroke="#ccc"/>'
       + '<text x="' + (x0+340) + '" y="' + (y+28) + '" font-size="11" font-weight="600" '
       + 'text-anchor="end" font-family="Montserrat,sans-serif" fill="#111" '
       + 'stroke="none">' + total + ' s total</text>'
       + '<text x="' + x0 + '" y="' + (y+28) + '" font-size="9.5" '
       + 'font-family="Montserrat,sans-serif" fill="#767676" stroke="none">time &#8594;</text>';
    $("gantt").innerHTML = g;
    $("oq").textContent = total + " s to a verdict";
    $("onote").innerHTML = par
      ? "Parallel: adding an advocate costs <strong>nothing</strong> in wall-clock time. The two purple bars are the fixed cost - the researcher and the manager cannot be parallelised away."
      : "Sequential: every advocate adds a full <strong>" + t + " s</strong>. With " + n + " advocates that is " + (n*t) + " s spent waiting on work that never needed to wait.";
  }
  ["oa","ot","om"].forEach(function(i){ $(i).addEventListener("input", draw); });
  draw();
})();</script>
"""

ALL = {
    "neuron-lab":        (NEURON,      "neuron"),
    "activation-lab":    (ACTIVATIONS, "activations"),
    "capacity-lab":      (CAPACITY,    "network"),
    "regression-line-lab": (REGRESSION_LINE, "regression-line"),
    "uw-feature-lab":    (UW_FEATURE_LAB, ""),
    "prompt-lab":        (PROMPT_LAB,  "agent_anatomy"),
    "orchestration-lab": (ORCH_LAB,    "orchestration"),
}


# Module 3 (deep learning) widgets live in their own file.
import widgets_dl, widgets_py
ALL.update(widgets_dl.ALL)
ALL.update(widgets_py.register())


def web(name):
    entry = ALL.get(name)
    return entry[0] if entry else f"<!-- unknown widget: {name} -->"


def frame(name):
    """Video frames are static, so a widget falls back to its diagram."""
    entry = ALL.get(name)
    if not entry:
        return ""
    fn = figures.ALL.get(entry[1])
    return f'<div class="f-fig">{fn()}</div>' if fn else ""
