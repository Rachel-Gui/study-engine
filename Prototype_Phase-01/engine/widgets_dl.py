r"""widgets_dl.py - interactive figures for Module 3 (deep learning).

Same contract as widgets.py: each entry is (html, figure_id). The html is a
self-contained block with an inline <script>; the figure_id is the static
diagram used in the video frame. Everything is plain SVG rewritten by a
few lines of JavaScript - no libraries, no build step.

These strings are raw strings (r-prefixed) because the scripts contain "\n".
"""

# ------------------------------------------------------- gradient descent lab

GRADIENT_LAB = r"""
<div class="wg" id="wg-grad">
  <div class="wg-hd"><span class="k">Interactive</span>
    <strong>Gradient descent on a loss bowl</strong>
    <span class="wg-eq" id="gq">loss 0.00 &middot; step 0</span></div>
  <div class="wg-bd">
    <div class="wg-ctl">
      <label><span>Learning rate &eta;</span><input type="range" id="glr" min="0.01" max="0.32"
             step="0.01" value="0.08"><output>0.08</output></label>
      <label><span>Momentum</span><input type="range" id="gmo" min="0" max="0.95"
             step="0.05" value="0"><output>0</output></label>
      <label class="wg-sel"><span>Features</span><select id="gsc">
        <option value="raw">unscaled (bowl is 4&times; longer one way)</option>
        <option value="std">standardised (round bowl)</option>
      </select></label>
      <div>
        <button class="wg-btn primary" id="gstep">Step</button>
        <button class="wg-btn" id="grun">Run 40 steps</button>
        <button class="wg-btn" id="greset">Reset</button>
      </div>
      <div class="wg-loss">
        <div><b id="gl">&ndash;</b><span>loss</span></div>
        <div><b id="gg">&ndash;</b><span>|gradient|</span></div>
        <div><b id="gn">0</b><span>steps</span></div>
      </div>
      <p class="wg-hint" id="gnote">Press <em>Step</em> and watch one update:
        w &larr; w &minus; &eta;&middot;&part;L/&part;w. The contour lines are the loss.</p>
    </div>
    <svg viewBox="0 0 460 300" class="wg-svg" stroke="#111" fill="none" stroke-width="1.2">
      <g id="gcont"></g>
      <polyline id="gpath" stroke="#4b2e83" stroke-width="2" fill="none"/>
      <circle id="gdot" r="5" fill="#4b2e83" stroke="none"/>
      <circle cx="230" cy="150" r="3" fill="#111" stroke="none"/>
      <text x="236" y="146" class="t sm">minimum</text>
      <g id="gcurve"></g>
      <text x="14" y="292" class="t sm">loss over steps &rarr;</text>
    </svg>
  </div>
  <p class="wg-note">The long axis of the bowl is the badly scaled feature. One learning
    rate has to serve both axes: small enough not to overshoot the narrow one, which
    makes it slow along the wide one. Standardise the features and the problem goes
    away &mdash; that is why Episode 3.7 scales its inputs before training.</p>
</div>
<script>(function(){
  const $ = i => document.getElementById(i);
  const CX = 230, CY = 150;
  let A, B, w, v, hist, n;
  function curv(){ return $("gsc").value === "std" ? [2, 2] : [0.5, 8.0]; }
  const L = (x, y) => 0.5 * (A * x * x + B * y * y);
  function reset(){
    [A, B] = curv(); w = [-5.5, 1.2]; v = [0, 0]; hist = [L(w[0], w[1])]; n = 0;
    let c = "";
    const L0 = L(w[0], w[1]);
    for (const q of [1, .6, .35, .18, .08, .03]) {
      const k = L0 * q, rx = Math.sqrt(2 * k / A) * 30, ry = Math.sqrt(2 * k / B) * 30;
      if (ry > 138 || rx > 226) continue;
      c += `<ellipse cx="${CX}" cy="${CY}" rx="${rx.toFixed(1)}" ry="${ry.toFixed(1)}" opacity=".35"/>`;
    }
    $("gcont").innerHTML = c;
    draw("Press <em>Step</em> and watch one update: w &larr; w &minus; &eta;&middot;&part;L/&part;w. The contour lines are the loss.");
  }
  const X = x => CX + x * 30, Y = y => CY - y * 30;
  function step(){
    const lr = +$("glr").value, mo = +$("gmo").value;
    const g = [A * w[0], B * w[1]];
    v = [mo * v[0] - lr * g[0], mo * v[1] - lr * g[1]];
    w = [w[0] + v[0], w[1] + v[1]];
    w = [Math.max(-40, Math.min(40, w[0])), Math.max(-40, Math.min(40, w[1]))];
    hist.push(L(w[0], w[1])); n++;
  }
  function draw(note){
    ["glr", "gmo"].forEach(i => $(i).nextElementSibling.value = $(i).value);
    $("gdot").setAttribute("cx", X(w[0])); $("gdot").setAttribute("cy", Y(w[1]));
    const loss = L(w[0], w[1]), gn = Math.hypot(A * w[0], B * w[1]);
    $("gl").textContent = loss > 999 ? "diverged" : loss.toFixed(3);
    $("gg").textContent = gn > 999 ? "huge" : gn.toFixed(3);
    $("gn").textContent = n;
    $("gq").innerHTML = `loss ${loss > 999 ? "&#8734;" : loss.toFixed(3)} &middot; step ${n}`;
    // loss sparkline (log scale)
    const m = Math.max(...hist.map(h => Math.min(h, 1e4)));
    const sx = i => 14 + i * (150 / Math.max(1, hist.length - 1));
    const sy = h => 288 - 42 * Math.log10(1 + Math.min(h, 1e4)) / Math.log10(1 + m);
    let d = "";
    hist.forEach((h, i) => d += (d ? "L" : "M") + sx(i).toFixed(1) + "," + sy(h).toFixed(1));
    $("gcurve").innerHTML = `<rect x="8" y="238" width="164" height="56" fill="#fff" opacity=".88" stroke="none"/>` +
      `<path d="${d}" stroke="#4b2e83" stroke-width="1.5"/>` +
      `<line x1="14" y1="288" x2="164" y2="288" stroke="#ccc"/>`;
    if (note) $("gnote").innerHTML = note;
  }
  const trail = [];
  function after(){
    trail.push([X(w[0]), Y(w[1])]);
    $("gpath").setAttribute("points", trail.map(p => p[0].toFixed(1) + "," + p[1].toFixed(1)).join(" "));
    const lr = +$("glr").value;
    let note;
    if (L(w[0], w[1]) > 999) note = "The loss is growing every step: &eta; is too large for the narrow axis (it needs &eta; &lt; 2/" + B + " = " + (2 / B).toFixed(2) + "). Lower it.";
    else if (lr > 1 / B) note = "Overshooting: each step jumps across the narrow axis and lands on the other side. It still converges, but by bouncing.";
    else if (n > 30 && L(w[0], w[1]) > 0.05) note = "Converging, slowly: the narrow axis limits &eta;, so progress along the long axis is a crawl. Try momentum, or standardise.";
    else if (L(w[0], w[1]) < 0.01) note = "At the bottom. Note how many steps it took &mdash; then switch to standardised features and count again.";
    draw(note);
  }
  $("gstep").addEventListener("click", () => { step(); after(); });
  $("grun").addEventListener("click", () => {
    let k = 0; const t = setInterval(() => { step(); after(); if (++k >= 40 || L(w[0], w[1]) > 999) clearInterval(t); }, 45);
  });
  $("greset").addEventListener("click", () => { trail.length = 0; $("gpath").setAttribute("points", ""); reset(); trail.push([X(w[0]), Y(w[1])]); });
  ["glr", "gmo"].forEach(i => $(i).addEventListener("input", () => draw()));
  $("gsc").addEventListener("change", () => { trail.length = 0; $("gpath").setAttribute("points", ""); reset(); trail.push([X(w[0]), Y(w[1])]); });
  reset(); trail.push([X(w[0]), Y(w[1])]);
})();</script>
"""

# ----------------------------------------------------------- fit / capacity lab

FIT_LAB = r"""
<div class="wg" id="wg-fit">
  <div class="wg-hd"><span class="k">Interactive</span>
    <strong>Underfit, fit, overfit</strong>
    <span class="wg-eq" id="fq">degree 3</span></div>
  <div class="wg-bd">
    <div class="wg-ctl">
      <label><span>Model capacity</span><input type="range" id="fdeg" min="1" max="14"
             step="1" value="3"><output>3</output></label>
      <label><span>Noise in data</span><input type="range" id="fnoise" min="0" max="0.3"
             step="0.02" value="0.1"><output>0.1</output></label>
      <div>
        <button class="wg-btn" id="fnew">Resample the data</button>
      </div>
      <div class="wg-loss">
        <div><b id="ftr">&ndash;</b><span>train RMSE</span></div>
        <div><b id="fva">&ndash;</b><span>validation RMSE</span></div>
        <div><b id="fgap">&ndash;</b><span>regime</span></div>
      </div>
      <p class="wg-hint">Filled points were used to fit; hollow points were held out.
        Capacity here is the degree of a polynomial, which plays the role of layers and
        neurons in a network. Push it up and watch the two numbers separate.</p>
    </div>
    <svg viewBox="0 0 460 300" class="wg-svg" stroke="#111" fill="none" stroke-width="1.2">
      <line x1="30" y1="260" x2="440" y2="260" stroke="#ccc"/>
      <line x1="30" y1="20" x2="30" y2="260" stroke="#ccc"/>
      <path id="ftruth" stroke="#bbb" stroke-dasharray="5 4" stroke-width="1.6"/>
      <path id="ffit" stroke="#4b2e83" stroke-width="2.2"/>
      <g id="fpts"></g>
      <text x="440" y="280" class="t sm" text-anchor="end">input feature &rarr;</text>
      <text x="36" y="18" class="t sm">target</text>
    </svg>
  </div>
  <p class="wg-note">Training error falls forever as capacity grows. Validation error falls,
    bottoms out, and rises again &mdash; the rise is the model fitting noise it will never see
    again. Only the validation number is honest, and only if you did not tune against it.</p>
</div>
<script>(function(){
  const $ = i => document.getElementById(i);
  let seed = 3;
  const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
  const gauss = () => { let u = 0, v = 0; while (!u) u = rnd(); while (!v) v = rnd();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
  const truth = x => Math.sin(x * 4.2) * 0.55 + 0.5;
  let xs = [], raw = [], tr = [];
  function sample(){
    xs = []; raw = []; tr = [];
    for (let i = 0; i < 26; i++) { xs.push((i + 0.5) / 26 + (rnd() - .5) * .02); raw.push(gauss()); tr.push(i % 3 !== 1); }
  }
  function ys(){ const nz = +$("fnoise").value; return xs.map((x, i) => truth(x) + raw[i] * nz); }
  // least squares on a Chebyshev-like basis, tiny ridge for stability
  function fit(deg, X, Y){
    const n = X.length, m = deg + 1;
    const phi = x => { const t = 2 * x - 1, r = [1, t]; for (let k = 2; k <= deg; k++) r.push(2 * t * r[k - 1] - r[k - 2]); return r.slice(0, m); };
    const A = Array.from({length: m}, () => new Array(m).fill(0)), b = new Array(m).fill(0);
    for (let i = 0; i < n; i++) { const p = phi(X[i]); for (let a = 0; a < m; a++) { b[a] += p[a] * Y[i]; for (let c = 0; c < m; c++) A[a][c] += p[a] * p[c]; } }
    for (let a = 0; a < m; a++) A[a][a] += 1e-9;
    // gaussian elimination
    for (let c = 0; c < m; c++) { let p = c; for (let r = c + 1; r < m; r++) if (Math.abs(A[r][c]) > Math.abs(A[p][c])) p = r;
      [A[c], A[p]] = [A[p], A[c]]; [b[c], b[p]] = [b[p], b[c]];
      for (let r = c + 1; r < m; r++) { const f = A[r][c] / A[c][c]; for (let k = c; k < m; k++) A[r][k] -= f * A[c][k]; b[r] -= f * b[c]; } }
    const w = new Array(m).fill(0);
    for (let r = m - 1; r >= 0; r--) { let s = b[r]; for (let k = r + 1; k < m; k++) s -= A[r][k] * w[k]; w[r] = s / A[r][r]; }
    return x => { const p = phi(x); let s = 0; for (let a = 0; a < m; a++) s += w[a] * p[a]; return s; };
  }
  const X = x => 30 + x * 410, Y = y => 260 - Math.max(-0.4, Math.min(1.5, y)) * 160 - 10;
  function path(fn, step){ let d = ""; for (let x = 0; x <= 1.0001; x += step) d += (d ? "L" : "M") + X(x).toFixed(1) + "," + Y(fn(x)).toFixed(1); return d; }
  function draw(){
    const deg = +$("fdeg").value; ["fdeg", "fnoise"].forEach(i => $(i).nextElementSibling.value = $(i).value);
    const Yv = ys();
    const Xt = xs.filter((_, i) => tr[i]), Yt = Yv.filter((_, i) => tr[i]);
    const f = fit(deg, Xt, Yt);
    const rmse = (idx) => Math.sqrt(idx.reduce((s, i) => s + (f(xs[i]) - Yv[i]) ** 2, 0) / idx.length);
    const trI = xs.map((_, i) => i).filter(i => tr[i]), vaI = xs.map((_, i) => i).filter(i => !tr[i]);
    const et = rmse(trI), ev = rmse(vaI);
    $("ftruth").setAttribute("d", path(truth, .01)); $("ffit").setAttribute("d", path(f, .005));
    $("fpts").innerHTML = xs.map((x, i) => `<circle cx="${X(x).toFixed(1)}" cy="${Y(Yv[i]).toFixed(1)}" r="4" ${tr[i] ? 'fill="#111" stroke="none"' : 'fill="#fff" stroke="#111" stroke-width="1.6"'}/>`).join("");
    $("ftr").textContent = et.toFixed(3); $("fva").textContent = ev.toFixed(3);
    const regime = (ev > 1.6 * et + 0.02 && deg >= 6) ? "overfit" : (deg <= 2 && et > 0.15) ? "underfit" : "good";
    $("fgap").textContent = regime;
    $("fq").textContent = "degree " + deg + " · gap " + (ev - et).toFixed(3);
  }
  ["fdeg", "fnoise"].forEach(i => $(i).addEventListener("input", draw));
  $("fnew").addEventListener("click", () => { sample(); draw(); });
  sample(); draw();
})();</script>
"""

# --------------------------------------------------------------- convolution lab

CONV_LAB = r"""
<div class="wg" id="wg-conv">
  <div class="wg-hd"><span class="k">Interactive</span>
    <strong>A convolution, by hand</strong>
    <span class="wg-eq" id="cvq">9 weights</span></div>
  <div class="wg-bd">
    <div class="wg-ctl">
      <label class="wg-sel"><span>Kernel preset</span><select id="cvp">
        <option value="vx">vertical edges</option><option value="hz">horizontal edges</option>
        <option value="bl">blur</option><option value="sh">sharpen</option>
        <option value="id">identity</option></select></label>
      <div class="wg-kern" id="cvk"></div>
      <label class="wg-sel"><span>After the sum</span><select id="cva">
        <option value="relu">ReLU (keep positive)</option><option value="abs">absolute value</option>
        <option value="none">nothing</option></select></label>
      <label class="wg-sel"><span>Then pool</span><select id="cvpool">
        <option value="0">no pooling (10&times;10)</option><option value="1">max-pool 2&times;2 (5&times;5)</option></select></label>
      <p class="wg-hint">Click cells in the facade to paint or erase a window. Edit the nine
        kernel numbers directly. The feature map on the right is
        <em>sum(window &times; kernel)</em> at every position.</p>
    </div>
    <div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;align-items:start">
        <div><div class="wg-hint" style="margin:0 0 6px">input 12&times;12 &mdash; a facade</div>
          <div class="wg-grid" id="cvin" style="grid-template-columns:repeat(12,1fr)"></div></div>
        <div><div class="wg-hint" style="margin:0 0 6px" id="cvlab">feature map 10&times;10</div>
          <div class="wg-grid" id="cvout" style="grid-template-columns:repeat(10,1fr)"></div></div>
      </div>
      <p class="wg-hint" id="cvnote" style="margin-top:10px"></p>
    </div>
  </div>
  <p class="wg-note">The same nine numbers are applied at all 100 positions: that is weight
    sharing. A dense layer producing the same 10&times;10 output from 144 pixels would need
    14,400 weights and would have to learn "edge" separately at every location.</p>
</div>
<script>(function(){
  const $ = i => document.getElementById(i);
  const N = 12;
  const img = Array.from({length: N}, () => new Array(N).fill(0.12));
  function windows(){
    for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) img[r][c] = 0.12 + ((r + c) % 3 === 0 ? 0.05 : 0);
    for (const r0 of [2, 6]) for (const c0 of [1, 5, 9]) for (let r = r0; r < r0 + 2; r++) for (let c = c0; c < c0 + 2; c++) img[r][c] = 0.9;
    for (let r = 9; r < 12; r++) for (let c = 5; c < 7; c++) img[r][c] = 0.75;
  }
  const presets = { vx: [-1, 0, 1, -1, 0, 1, -1, 0, 1], hz: [-1, -1, -1, 0, 0, 0, 1, 1, 1],
    bl: [1, 1, 1, 1, 1, 1, 1, 1, 1].map(v => v / 9), sh: [0, -1, 0, -1, 5, -1, 0, -1, 0], id: [0, 0, 0, 0, 1, 0, 0, 0, 0] };
  $("cvk").innerHTML = Array.from({length: 9}, (_, i) => `<input type="text" inputmode="decimal" data-k="${i}" value="0">`).join("");
  const kin = [...$("cvk").querySelectorAll("input")];
  function setPreset(){ presets[$("cvp").value].forEach((v, i) => kin[i].value = +v.toFixed(2)); }
  function kernel(){ return kin.map(k => parseFloat(k.value) || 0); }
  const shade = v => `rgba(17,17,17,${Math.max(0, Math.min(1, v)).toFixed(2)})`;
  function draw(){
    const K = kernel(), act = $("cva").value, pool = $("cvpool").value === "1";
    let out = [];
    for (let r = 0; r < N - 2; r++) { const row = []; for (let c = 0; c < N - 2; c++) {
      let s = 0; for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) s += img[r + i][c + j] * K[i * 3 + j];
      row.push(act === "relu" ? Math.max(0, s) : act === "abs" ? Math.abs(s) : s); } out.push(row); }
    if (pool) { const p = []; for (let r = 0; r < 10; r += 2) { const row = []; for (let c = 0; c < 10; c += 2)
      row.push(Math.max(out[r][c], out[r][c + 1], out[r + 1][c], out[r + 1][c + 1])); p.push(row); } out = p; }
    const m = Math.max(0.05, ...out.flat().map(Math.abs));
    $("cvout").style.gridTemplateColumns = `repeat(${out.length},1fr)`;
    $("cvout").innerHTML = out.flat().map(v => `<i title="${v.toFixed(2)}" style="background:${v < 0 ? 'rgba(75,46,131,' + (-v / m).toFixed(2) + ')' : shade(v / m)}"></i>`).join("");
    $("cvlab").textContent = pool ? "pooled feature map 5×5" : "feature map 10×10";
    $("cvin").innerHTML = img.flat().map((v, i) => `<i data-i="${i}" style="background:${shade(v)};cursor:pointer"></i>`).join("");
    const sumK = K.reduce((a, b) => a + b, 0);
    $("cvq").textContent = "9 weights · kernel sum " + sumK.toFixed(2);
    const pos = out.flat().filter(v => v > 0.02 * m).length;
    $("cvnote").innerHTML = ($("cvp").value === "vx" ? "A vertical-edge kernel responds where a bright column sits next to a dark one: the left and right sides of every window. Nothing fires on the flat wall." :
      $("cvp").value === "hz" ? "A horizontal-edge kernel finds the tops and bottoms of the windows instead. Same picture, different filter, different feature map." :
      $("cvp").value === "bl" ? "A blur averages each window: edges soften, the brick texture disappears. Real networks learn blurs as well as edges." :
      $("cvp").value === "sh" ? "Sharpen exaggerates differences from the neighbourhood: the windows pop, and so does the texture noise." :
      "The identity kernel copies the input, minus a one-pixel border: a 12×12 image gives a 10×10 map with no padding.") +
      ` Active cells: <strong>${pos}</strong> of ${out.flat().length}.` + (pool ? " Pooling kept the strongest response in each 2×2 block, so the map is smaller but the windows are still there." : "");
  }
  $("cvin").addEventListener("click", e => { const t = e.target.closest("i"); if (!t) return;
    const i = +t.dataset.i, r = Math.floor(i / N), c = i % N; img[r][c] = img[r][c] > 0.5 ? 0.12 : 0.9; draw(); });
  $("cvp").addEventListener("change", () => { setPreset(); draw(); });
  kin.forEach(k => k.addEventListener("input", draw));
  ["cva", "cvpool"].forEach(i => $(i).addEventListener("change", draw));
  windows(); setPreset(); draw();
})();</script>
"""

# ------------------------------------------------------------ message passing lab

MESSAGE_LAB = r"""
<div class="wg" id="wg-msg">
  <div class="wg-hd"><span class="k">Interactive</span>
    <strong>Message passing on a floor plan</strong>
    <span class="wg-eq" id="mq">0 layers applied</span></div>
  <div class="wg-bd">
    <div class="wg-ctl">
      <label class="wg-sel"><span>Node signal</span><select id="mmode">
        <option value="onehot">a signal starting in one room</option>
        <option value="temp">room temperatures (&deg;C)</option></select></label>
      <label class="wg-sel"><span>Aggregation</span><select id="magg">
        <option value="mean">mean of self + neighbours</option>
        <option value="sum">sum of neighbours (unnormalised)</option>
        <option value="max">max of self + neighbours</option></select></label>
      <div>
        <button class="wg-btn primary" id="mstep">Apply one layer</button>
        <button class="wg-btn" id="mreset">Reset</button>
      </div>
      <p class="wg-hint" id="mnote">Click a room to start the signal there. Each layer lets
        every node mix its own value with its neighbours'. Count how many layers the signal
        needs to reach the far bedroom.</p>
    </div>
    <svg viewBox="0 0 460 300" class="wg-svg" stroke="#111" fill="none" stroke-width="1.3">
      <g id="medges"></g><g id="mnodes"></g>
    </svg>
  </div>
  <p class="wg-note">One layer = one hop. Two layers reach neighbours of neighbours. Keep
    going with mean aggregation and every room converges to the same number &mdash;
    <em>over-smoothing</em>, the reason deep GNNs are rarely deeper than three or four layers.</p>
</div>
<script>(function(){
  const $ = i => document.getElementById(i);
  const names = ["Entry", "Living", "Kitchen", "Hall", "Bed 1", "Bath", "Bed 2"];
  const pos = [[70, 70], [190, 60], [330, 70], [90, 160], [60, 250], [200, 250], [360, 220]];
  const E = [[0, 1], [0, 3], [1, 2], [3, 4], [3, 5], [1, 6], [5, 6], [1, 3]];
  const nb = names.map(() => []); E.forEach(([a, b]) => { nb[a].push(b); nb[b].push(a); });
  const temps = [17, 21, 24, 18, 19, 23, 20];
  let h = [], k = 0, src = 0;
  function reset(){ k = 0; h = $("mmode").value === "temp" ? temps.slice() : names.map((_, i) => i === src ? 1 : 0); draw(); }
  function step(){
    const agg = $("magg").value;
    h = h.map((v, i) => {
      const vals = nb[i].map(j => h[j]);
      if (agg === "sum") return vals.reduce((a, b) => a + b, 0);
      if (agg === "max") return Math.max(v, ...vals);
      return (v + vals.reduce((a, b) => a + b, 0)) / (vals.length + 1);
    }); k++; draw();
  }
  function draw(){
    const temp = $("mmode").value === "temp";
    const lo = temp ? 16 : 0, hi = temp ? 25 : Math.max(1, ...h);
    $("medges").innerHTML = E.map(([a, b]) => `<line x1="${pos[a][0]}" y1="${pos[a][1]}" x2="${pos[b][0]}" y2="${pos[b][1]}" opacity=".45"/>`).join("");
    $("mnodes").innerHTML = names.map((n, i) => {
      const t = Math.max(0, Math.min(1, (h[i] - lo) / (hi - lo)));
      const fill = `rgba(75,46,131,${(0.08 + 0.85 * t).toFixed(2)})`;
      return `<g data-i="${i}" style="cursor:pointer"><circle cx="${pos[i][0]}" cy="${pos[i][1]}" r="24" fill="${fill}" stroke="${i === src && !temp ? '#4b2e83' : '#111'}" stroke-width="${i === src && !temp ? 2.4 : 1.3}"/>` +
        `<text x="${pos[i][0]}" y="${pos[i][1] - 3}" class="t sm" text-anchor="middle" fill="${t > .5 ? '#fff' : '#111'}" style="fill:${t > .5 ? '#fff' : '#111'}">${n}</text>` +
        `<text x="${pos[i][0]}" y="${pos[i][1] + 11}" class="t" text-anchor="middle" style="fill:${t > .5 ? '#fff' : '#111'};font-weight:600">${temp ? h[i].toFixed(1) : h[i].toFixed(2)}</text></g>`;
    }).join("");
    $("mq").textContent = k + (k === 1 ? " layer" : " layers") + " applied";
    const spread = Math.max(...h) - Math.min(...h);
    $("mnote").innerHTML = k === 0 ? (temp ? "Seven rooms, seven readings. Apply a layer and watch each room take on its neighbours' values." : "Click a room to start the signal there. Each layer lets every node mix its own value with its neighbours'. Count how many layers the signal needs to reach the far bedroom.")
      : temp ? `After ${k} layer${k > 1 ? "s" : ""} the spread between the warmest and coldest room is <strong>${spread.toFixed(2)} &deg;C</strong>${spread < 0.5 ? " &mdash; the rooms are indistinguishable now. That is over-smoothing." : "."}`
      : `After ${k} layer${k > 1 ? "s" : ""} the signal has reached <strong>${h.filter(v => v > 1e-6).length} of 7</strong> rooms${h.every(v => v > 1e-6) ? " &mdash; every room, so the receptive field covers the whole plan." : "."}`;
  }
  $("mnodes").addEventListener("click", e => { const g = e.target.closest("g[data-i]"); if (!g || $("mmode").value === "temp") return; src = +g.dataset.i; reset(); });
  $("mstep").addEventListener("click", step); $("mreset").addEventListener("click", reset);
  ["mmode", "magg"].forEach(i => $(i).addEventListener("change", reset));
  reset();
})();</script>
"""

# ------------------------------------------------------------------ PINN lab

PINN_LAB = r"""
<div class="wg" id="wg-pinn">
  <div class="wg-hd"><span class="k">Interactive</span>
    <strong>Train a physics-informed network, live</strong>
    <span class="wg-eq" id="pq">step 0</span></div>
  <div class="wg-bd">
    <div class="wg-ctl">
      <label><span>Collocation points</span><input type="range" id="pnc" min="2" max="40"
             step="1" value="20"><output>20</output></label>
      <label><span>&lambda; boundary</span><input type="range" id="plb" min="0" max="20"
             step="1" value="10"><output>10</output></label>
      <label><span>&lambda; data</span><input type="range" id="pld" min="0" max="10"
             step="0.5" value="0"><output>0</output></label>
      <label><span>Learning rate</span><input type="range" id="plr" min="0.002" max="0.05"
             step="0.002" value="0.01"><output>0.01</output></label>
      <div>
        <button class="wg-btn primary" id="ptrain">Train 1500 steps</button>
        <button class="wg-btn" id="pstep">+100</button>
        <button class="wg-btn" id="preset">Reset</button>
      </div>
      <div class="wg-loss">
        <div><b id="ppde">&ndash;</b><span>PDE residual</span></div>
        <div><b id="pbc">&ndash;</b><span>boundary</span></div>
        <div><b id="perr">&ndash;</b><span>max error</span></div>
      </div>
      <p class="wg-hint" id="pnote">u&Prime;(x) = &minus;&pi;&sup2; sin(&pi;x), u(0) = u(1) = 0.
        The network never sees the answer sin(&pi;x); it only sees the equation at the
        tick marks and the two ends. Press <em>Train</em>.</p>
    </div>
    <svg viewBox="0 0 460 300" class="wg-svg" stroke="#111" fill="none" stroke-width="1.3">
      <rect x="30" y="20" width="300" height="200" fill="#fbfbfa" stroke="none"/>
      <line x1="30" y1="120" x2="430" y2="120" stroke="#ccc"/>
      <line x1="30" y1="20" x2="30" y2="220" stroke="#ccc"/>
      <line x1="330" y1="20" x2="330" y2="220" stroke="#ccc" stroke-dasharray="3 3"/>
      <text x="335" y="34" class="t sm">outside the domain &rarr;</text>
      <path id="pexact" stroke="#aaa" stroke-width="2" stroke-dasharray="6 4"/>
      <path id="pnet" stroke="#4b2e83" stroke-width="2.4"/>
      <g id="pcol"></g><g id="pdata"></g>
      <circle cx="30" cy="120" r="4" fill="#111" stroke="none"/>
      <circle cx="330" cy="120" r="4" fill="#111" stroke="none"/>
      <text x="30" y="236" class="t sm" text-anchor="middle">x = 0</text>
      <text x="330" y="236" class="t sm" text-anchor="middle">x = 1</text>
      <text x="430" y="236" class="t sm" text-anchor="end">x = 1.33</text>
      <text x="36" y="34" class="t sm">grey dashed: exact &middot; purple: network</text>
      <text x="30" y="262" class="t sm">residual |u&Prime; &minus; f| along x</text>
      <g id="pres"></g>
    </svg>
  </div>
  <p class="wg-note">Try three things. Set &lambda; boundary to 0: the equation alone has
    infinitely many solutions, so the curve drifts. Set collocation points to 2 or 3: the
    residual is only checked there, and the curve is wrong in between. Then look right of
    x = 1: nothing constrained the network there, and the residual grows immediately.</p>
</div>
<script>(function(){
  const $ = i => document.getElementById(i);
  const H = 12, PI = Math.PI;
  const f = x => -PI * PI * Math.sin(PI * x), exact = x => Math.sin(PI * x);
  let w1, b1, w2, b2, m, v, t, timer = null;
  let seed = 11; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
  const gauss = () => { let u = 0, q = 0; while (!u) u = rnd(); while (!q) q = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * PI * q); };
  const XD = [0.15, 0.4, 0.62, 0.85]; let UD = [];
  function reset(){
    if (timer) { clearInterval(timer); timer = null; }
    seed = 11;
    w1 = Float64Array.from({length: H}, () => gauss() * 1.5); b1 = Float64Array.from({length: H}, () => (rnd() - .5) * 3);
    w2 = Float64Array.from({length: H}, () => gauss() * .3); b2 = 0; t = 0;
    m = {w1: new Float64Array(H), b1: new Float64Array(H), w2: new Float64Array(H), b2: 0};
    v = {w1: new Float64Array(H), b1: new Float64Array(H), w2: new Float64Array(H), b2: 0};
    UD = XD.map(x => exact(x) + gauss() * 0.05);
    draw(true);
  }
  function u(x){ let s = b2; for (let j = 0; j < H; j++) s += w2[j] * Math.tanh(w1[j] * x + b1[j]); return s; }
  function upp(x){ let s = 0; for (let j = 0; j < H; j++) { const th = Math.tanh(w1[j] * x + b1[j]), sj = 1 - th * th; s += -2 * w2[j] * w1[j] * w1[j] * th * sj; } return s; }
  function step(){
    const nc = +$("pnc").value, lb = +$("plb").value, ld = +$("pld").value, lr = +$("plr").value;
    const g = {w1: new Float64Array(H), b1: new Float64Array(H), w2: new Float64Array(H), b2: 0};
    let Lp = 0, Lb = 0, Ld = 0;
    // PDE residual at collocation points
    for (let i = 0; i < nc; i++) {
      const x = nc === 1 ? .5 : i / (nc - 1);
      let r = -f(x); const th = new Float64Array(H), sj = new Float64Array(H);
      for (let j = 0; j < H; j++) { th[j] = Math.tanh(w1[j] * x + b1[j]); sj[j] = 1 - th[j] * th[j]; r += -2 * w2[j] * w1[j] * w1[j] * th[j] * sj[j]; }
      Lp += r * r / nc; const c = 2 * r / nc;
      for (let j = 0; j < H; j++) {
        g.w2[j] += c * (-2 * w1[j] * w1[j] * th[j] * sj[j]);
        g.w1[j] += c * (-2 * w2[j] * (2 * w1[j] * th[j] * sj[j] + w1[j] * w1[j] * x * sj[j] * (1 - 3 * th[j] * th[j])));
        g.b1[j] += c * (-2 * w2[j] * w1[j] * w1[j] * sj[j] * (1 - 3 * th[j] * th[j]));
      }
    }
    // boundary and data terms share the same derivative of u
    function fitPoint(x, target, lam, n, acc){
      const e = u(x) - target; acc.L += e * e / n; const c = lam * 2 * e / n;
      for (let j = 0; j < H; j++) { const th = Math.tanh(w1[j] * x + b1[j]), sj = 1 - th * th;
        g.w2[j] += c * th; g.w1[j] += c * w2[j] * sj * x; g.b1[j] += c * w2[j] * sj; }
      g.b2 += c;
    }
    const ab = {L: 0}; fitPoint(0, 0, lb, 2, ab); fitPoint(1, 0, lb, 2, ab); Lb = ab.L;
    if (ld > 0) { const ad = {L: 0}; XD.forEach((x, i) => fitPoint(x, UD[i], ld, XD.length, ad)); Ld = ad.L; }
    // Adam
    t++; const B1 = .9, B2 = .999, eps = 1e-8;
    const upd = (p, gp, k) => { for (let j = 0; j < H; j++) { m[k][j] = B1 * m[k][j] + (1 - B1) * gp[j]; v[k][j] = B2 * v[k][j] + (1 - B2) * gp[j] * gp[j];
      p[j] -= lr * (m[k][j] / (1 - Math.pow(B1, t))) / (Math.sqrt(v[k][j] / (1 - Math.pow(B2, t))) + eps); } };
    upd(w1, g.w1, "w1"); upd(b1, g.b1, "b1"); upd(w2, g.w2, "w2");
    m.b2 = B1 * m.b2 + (1 - B1) * g.b2; v.b2 = B2 * v.b2 + (1 - B2) * g.b2 * g.b2;
    b2 -= lr * (m.b2 / (1 - Math.pow(B1, t))) / (Math.sqrt(v.b2 / (1 - Math.pow(B2, t))) + eps);
    return [Lp, Lb, Ld];
  }
  const X = x => 30 + x * 300, Y = y => 120 - y * 88;
  function draw(initial){
    ["pnc", "plb", "pld", "plr"].forEach(i => $(i).nextElementSibling.value = $(i).value);
    let de = "", dn = "";
    for (let x = 0; x <= 1.3334; x += 0.01) { de += (de ? "L" : "M") + X(x).toFixed(1) + "," + Y(Math.max(-1.1, Math.min(1.1, exact(x)))).toFixed(1);
      dn += (dn ? "L" : "M") + X(x).toFixed(1) + "," + Y(Math.max(-1.1, Math.min(1.1, u(x)))).toFixed(1); }
    $("pexact").setAttribute("d", de); $("pnet").setAttribute("d", dn);
    const nc = +$("pnc").value;
    $("pcol").innerHTML = Array.from({length: nc}, (_, i) => { const x = nc === 1 ? .5 : i / (nc - 1);
      return `<line x1="${X(x).toFixed(1)}" y1="214" x2="${X(x).toFixed(1)}" y2="222" stroke="#4b2e83" stroke-width="1.6"/>`; }).join("");
    $("pdata").innerHTML = +$("pld").value > 0 ? XD.map((x, i) => `<circle cx="${X(x).toFixed(1)}" cy="${Y(UD[i]).toFixed(1)}" r="4.5" fill="#fff" stroke="#111" stroke-width="1.6"/>`).join("") : "";
    // residual strip
    let rs = "", maxr = 0; const rv = [];
    for (let x = 0; x <= 1.3334; x += 0.02) { const r = Math.abs(upp(x) - f(x)); rv.push([x, r]); maxr = Math.max(maxr, r); }
    const sc = 26 / Math.max(1, maxr);
    rv.forEach(([x, r]) => rs += `<rect x="${X(x).toFixed(1)}" y="${(292 - r * sc).toFixed(1)}" width="5.4" height="${(r * sc).toFixed(1)}" fill="${x > 1 ? '#b7a57a' : '#4b2e83'}" stroke="none" opacity=".8"/>`);
    $("pres").innerHTML = rs + `<line x1="30" y1="292" x2="430" y2="292" stroke="#ccc"/>`;
    let err = 0; for (let x = 0; x <= 1.0001; x += 0.01) err = Math.max(err, Math.abs(u(x) - exact(x)));
    $("perr").textContent = err.toFixed(3);
    $("pq").textContent = "step " + t + " · max |u − exact| = " + err.toFixed(3);
    if (initial) { $("ppde").textContent = "–"; $("pbc").textContent = "–"; }
  }
  function run(n){
    if (timer) clearInterval(timer);
    let k = 0, last = [0, 0, 0];
    timer = setInterval(() => { for (let i = 0; i < 25 && k < n; i++, k++) last = step();
      $("ppde").textContent = last[0].toFixed(4); $("pbc").textContent = last[1].toExponential(1); draw();
      const lb = +$("plb").value, nc = +$("pnc").value;
      $("pnote").innerHTML = lb === 0 ? "With no boundary term the residual can reach zero while the curve sits anywhere: u = sin(&pi;x) + a + bx solves the equation for any a and b. Physics alone is not enough." :
        nc <= 3 ? "The residual is only checked at " + nc + " points. Between them the network is free, and it uses that freedom. More collocation points, not more neurons, is the fix." :
        k >= n ? "Trained. Inside [0, 1] the purple curve sits on the exact solution. Right of x = 1 it leaves immediately: the equation was never enforced there. A PINN is only as good as its collocation set." :
        "Training. The PDE residual is falling; the boundary loss is pinning both ends to zero.";
      if (k >= n) { clearInterval(timer); timer = null; } }, 30);
  }
  $("ptrain").addEventListener("click", () => run(1500)); $("pstep").addEventListener("click", () => run(100));
  $("preset").addEventListener("click", reset);
  ["pnc", "plb", "pld", "plr"].forEach(i => $(i).addEventListener("input", () => draw()));
  reset();
})();</script>
"""

# ------------------------------------------------------------- surrogate lab

SURROGATE_LAB = r"""
<div class="wg" id="wg-surr">
  <div class="wg-hd"><span class="k">Interactive</span>
    <strong>A surrogate inside and outside its range</strong>
    <span class="wg-eq" id="sq">query WWR 0.40</span></div>
  <div class="wg-bd">
    <div class="wg-ctl">
      <label><span>Query WWR</span><input type="range" id="sx" min="0" max="1" step="0.01"
             value="0.40"><output>0.40</output></label>
      <label class="wg-sel"><span>Surrogate</span><select id="sm">
        <option value="poly">polynomial (degree 3)</option>
        <option value="rbf">kernel (RBF) regression</option></select></label>
      <div class="wg-loss">
        <div><b id="sp">&ndash;</b><span>surrogate says</span></div>
        <div><b id="st">&ndash;</b><span>simulator says</span></div>
        <div><b id="se">&ndash;</b><span>error</span></div>
      </div>
      <p class="wg-hint" id="snote"></p>
    </div>
    <svg viewBox="0 0 460 300" class="wg-svg" stroke="#111" fill="none" stroke-width="1.3">
      <rect id="sband" x="0" y="20" width="0" height="240" fill="#f6f3ec" stroke="none"/>
      <line x1="30" y1="260" x2="440" y2="260" stroke="#ccc"/>
      <line x1="30" y1="20" x2="30" y2="260" stroke="#ccc"/>
      <path id="struth" stroke="#aaa" stroke-width="2" stroke-dasharray="6 4"/>
      <path id="sfit" stroke="#4b2e83" stroke-width="2.4"/>
      <g id="spts"></g>
      <line id="sqline" y1="20" y2="260" stroke="#111" stroke-dasharray="3 3"/>
      <circle id="sqdot" r="5" fill="#4b2e83" stroke="none"/>
      <text x="440" y="280" class="t sm" text-anchor="end">window-to-wall ratio &rarr;</text>
      <text x="36" y="18" class="t sm">cooling load, kWh/m&sup2; (illustrative)</text>
      <text id="sbl" y="34" class="t sm" text-anchor="middle">sampled range</text>
    </svg>
  </div>
  <p class="wg-note">The simulator was run twelve times, all between WWR 0.2 and 0.6. Inside
    that band both surrogates are close to it. Drag the query outside: the polynomial keeps
    going with total confidence, the kernel model relaxes to the mean. Both are wrong, in
    different ways, and neither reports it. The band is the deliverable.</p>
</div>
<script>(function(){
  const $ = i => document.getElementById(i);
  const truth = w => 22 + 58 * w * w + 6 * Math.sin(7 * w);
  let seed = 5; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
  const XS = Array.from({length: 12}, (_, i) => 0.2 + 0.4 * i / 11);
  const YS = XS.map(x => truth(x) + (rnd() - .5) * 3);
  // polynomial degree 3 least squares
  function polyfit(){
    const m = 4, A = Array.from({length: m}, () => new Array(m).fill(0)), b = new Array(m).fill(0);
    XS.forEach((x, i) => { const p = [1, x, x * x, x * x * x]; for (let a = 0; a < m; a++) { b[a] += p[a] * YS[i]; for (let c = 0; c < m; c++) A[a][c] += p[a] * p[c]; } });
    for (let c = 0; c < m; c++) { for (let r = c + 1; r < m; r++) { const f = A[r][c] / A[c][c]; for (let k = c; k < m; k++) A[r][k] -= f * A[c][k]; b[r] -= f * b[c]; } }
    const w = new Array(m).fill(0); for (let r = m - 1; r >= 0; r--) { let s = b[r]; for (let k = r + 1; k < m; k++) s -= A[r][k] * w[k]; w[r] = s / A[r][r]; }
    return x => w[0] + w[1] * x + w[2] * x * x + w[3] * x * x * x;
  }
  function rbf(){
    const mean = YS.reduce((a, b) => a + b, 0) / YS.length, ell = 0.08, lam = 0.05, n = XS.length;
    const K = XS.map(a => XS.map(b => Math.exp(-((a - b) ** 2) / (2 * ell * ell))));
    for (let i = 0; i < n; i++) K[i][i] += lam;
    const y = YS.map(v => v - mean), a = new Array(n).fill(0);
    for (let c = 0; c < n; c++) { for (let r = c + 1; r < n; r++) { const f = K[r][c] / K[c][c]; for (let k = c; k < n; k++) K[r][k] -= f * K[c][k]; y[r] -= f * y[c]; } }
    for (let r = n - 1; r >= 0; r--) { let s = y[r]; for (let k = r + 1; k < n; k++) s -= K[r][k] * a[k]; a[r] = s / K[r][r]; }
    return x => mean + XS.reduce((s, xi, i) => s + a[i] * Math.exp(-((x - xi) ** 2) / (2 * ell * ell)), 0);
  }
  const models = {poly: polyfit(), rbf: rbf()};
  const X = x => 30 + x * 410, Y = y => 260 - Math.max(0, Math.min(120, y)) * 2;
  function path(fn){ let d = ""; for (let x = 0; x <= 1.0001; x += 0.01) d += (d ? "L" : "M") + X(x).toFixed(1) + "," + Y(fn(x)).toFixed(1); return d; }
  function draw(){
    const q = +$("sx").value, fn = models[$("sm").value]; $("sx").nextElementSibling.value = q.toFixed(2);
    $("sband").setAttribute("x", X(0.2)); $("sband").setAttribute("width", X(0.6) - X(0.2)); $("sbl").setAttribute("x", X(0.4));
    $("struth").setAttribute("d", path(truth)); $("sfit").setAttribute("d", path(fn));
    $("spts").innerHTML = XS.map((x, i) => `<circle cx="${X(x).toFixed(1)}" cy="${Y(YS[i]).toFixed(1)}" r="3.5" fill="#111" stroke="none"/>`).join("");
    $("sqline").setAttribute("x1", X(q)); $("sqline").setAttribute("x2", X(q));
    $("sqdot").setAttribute("cx", X(q)); $("sqdot").setAttribute("cy", Y(fn(q)));
    const p = fn(q), tv = truth(q), e = p - tv;
    $("sp").textContent = p.toFixed(1); $("st").textContent = tv.toFixed(1); $("se").textContent = (e >= 0 ? "+" : "") + e.toFixed(1);
    const inside = q >= 0.2 && q <= 0.6;
    $("sq").textContent = "query WWR " + q.toFixed(2) + (inside ? " · inside" : " · OUTSIDE");
    $("snote").innerHTML = inside ? "Inside the sampled range. The error here is the kind you can measure with a held-out simulation run, and report."
      : "Outside the sampled range. The surrogate returns a number with the same confidence as before &mdash; nothing about the output says it is guessing. Only the band tells you.";
  }
  ["sx"].forEach(i => $(i).addEventListener("input", draw)); $("sm").addEventListener("change", draw);
  draw();
})();</script>
"""

# ------------------------------------------------------------- attention lab

ATTENTION_LAB = r"""
<div class="wg" id="wg-attn">
  <div class="wg-hd"><span class="k">Interactive</span>
    <strong>Attention over the last 24 hours</strong>
    <span class="wg-eq" id="aq2">prediction &ndash;</span></div>
  <div class="wg-bd">
    <div class="wg-ctl">
      <label><span>Recency</span><input type="range" id="arec" min="0" max="4"
             step="0.1" value="1"><output>1</output></label>
      <label><span>Same hour</span><input type="range" id="ahr" min="0" max="4"
             step="0.1" value="2.5"><output>2.5</output></label>
      <label><span>Sharpness 1/&tau;</span><input type="range" id="atau" min="0.2" max="6"
             step="0.1" value="3"><output>3</output></label>
      <label><span>Predict hour</span><input type="range" id="anow" min="0" max="23"
             step="1" value="19"><output>19</output></label>
      <div class="wg-loss">
        <div><b id="apred">&ndash;</b><span>weighted sum &yacute;</span></div>
        <div><b id="atrue">&ndash;</b><span>what happened</span></div>
        <div><b id="atop">&ndash;</b><span>top weight</span></div>
      </div>
      <p class="wg-hint" id="anote"></p>
    </div>
    <svg viewBox="0 0 460 300" class="wg-svg" stroke="#111" fill="none" stroke-width="1.2">
      <text x="14" y="18" class="t sm">appliance load, last 24 h (Wh per 10 min, illustrative)</text>
      <g id="abars"></g>
      <text x="14" y="176" class="t sm">attention weights &alpha; (sum to 1)</text>
      <g id="aw"></g>
      <line x1="30" y1="268" x2="440" y2="268" stroke="#ccc"/>
    </svg>
  </div>
  <p class="wg-note">In a Transformer the two weights and the sharpness are learned, and the
    keys and queries are learned projections; here they are sliders so you can see the
    mechanism. What survives from this toy to the real thing: the weights sum to one, they
    depend on the query, and you can read them off after the fact.</p>
</div>
<script>(function(){
  const $ = i => document.getElementById(i);
  // an illustrative day: morning and evening peaks
  const day = h => 40 + 60 * Math.exp(-((h - 7.5) ** 2) / 3) + 120 * Math.exp(-((h - 19) ** 2) / 4) + 15 * Math.sin(h);
  let seed = 9; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
  const yest = Array.from({length: 24}, (_, h) => day(h) * (0.85 + 0.3 * rnd()));
  const today = Array.from({length: 24}, (_, h) => day(h) * (0.85 + 0.3 * rnd()));
  function draw(){
    ["arec", "ahr", "atau", "anow"].forEach(i => $(i).nextElementSibling.value = $(i).value);
    const wr = +$("arec").value, wh = +$("ahr").value, inv = +$("atau").value, now = +$("anow").value;
    // the 24 readings before "now": today's hours < now, then yesterday's hours >= now
    const seq = []; for (let k = 24; k >= 1; k--) { const h = ((now - k) % 24 + 24) % 24; seq.push({h, v: k <= now ? today[h] : yest[h], age: k}); }
    const dh = h => { const d = Math.abs(((h - now) % 24 + 24) % 24); return Math.min(d, 24 - d); };
    const scores = seq.map(s => (wr * (1 - s.age / 24) + wh * Math.exp(-(dh(s.h) ** 2) / 4.5)) * inv);
    const mx = Math.max(...scores), ex = scores.map(s => Math.exp(s - mx)), Z = ex.reduce((a, b) => a + b, 0), al = ex.map(e => e / Z);
    const pred = seq.reduce((s, x, i) => s + al[i] * x.v, 0), actual = today[now];
    const vmax = Math.max(...seq.map(s => s.v)), amax = Math.max(...al);
    $("abars").innerHTML = seq.map((s, i) => { const x = 30 + i * 17, hgt = 110 * s.v / vmax;
      return `<rect x="${x}" y="${(150 - hgt).toFixed(1)}" width="13" height="${hgt.toFixed(1)}" fill="rgba(17,17,17,${(0.25 + 0.6 * al[i] / amax).toFixed(2)})" stroke="none"/>` +
        (i % 4 === 0 || i === 23 ? `<text x="${x + 6}" y="164" class="t sm" text-anchor="middle">${s.h}h</text>` : ""); }).join("") +
      `<text x="${30 + 24 * 17 + 4}" y="150" class="t sm" font-weight="600" style="fill:#4b2e83">${now}h?</text>`;
    $("aw").innerHTML = al.map((a, i) => { const x = 30 + i * 17, hgt = 80 * a / amax;
      return `<rect x="${x}" y="${(266 - hgt).toFixed(1)}" width="13" height="${hgt.toFixed(1)}" fill="#4b2e83" stroke="none" opacity=".85"/>`; }).join("");
    $("apred").textContent = pred.toFixed(0); $("atrue").textContent = actual.toFixed(0);
    const ti = al.indexOf(amax); $("atop").textContent = amax.toFixed(2) + " @ " + seq[ti].h + "h";
    $("aq2").innerHTML = "prediction " + pred.toFixed(0) + " &middot; actual " + actual.toFixed(0);
    $("anote").innerHTML = inv < 0.6 ? "Low sharpness spreads the weight almost evenly: the prediction is close to the 24-hour mean, whatever the query."
      : (wh > wr + 1) ? "The weight is on the same hour yesterday: the model is betting the day repeats." : (wr > wh + 1) ? "The weight is on the most recent readings: the model is betting the next hour looks like the last one." : "A blend of “recent” and “same time yesterday”. Both are real signals for appliance load, and a trained model finds the mix itself.";
  }
  ["arec", "ahr", "atau", "anow"].forEach(i => $(i).addEventListener("input", draw));
  draw();
})();</script>
"""

ALL = {
    "gradient-lab":  (GRADIENT_LAB,  "loss_landscape"),
    "fit-lab":       (FIT_LAB,       "fit_regimes"),
    "conv-lab":      (CONV_LAB,      "convolution"),
    "message-lab":   (MESSAGE_LAB,   "message_passing"),
    "pinn-lab":      (PINN_LAB,      "pinn_loss"),
    "surrogate-lab": (SURROGATE_LAB, "interpolation_region"),
    "attention-lab": (ATTENTION_LAB, "attention"),
}
