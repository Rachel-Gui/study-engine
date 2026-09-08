"""
widgets.py - interactive figures.

Each widget is a dict with:
    web()    HTML + inline SVG + a <script>, live in the browser
    frame()  a static SVG for the video, from figures.py

A widget is a figure you can push on. Everything here is dependency-free:
no charting library, no build step, just SVG the script rewrites.
"""
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

ALL = {
    "neuron-lab":     (NEURON,      "neuron"),
    "activation-lab": (ACTIVATIONS, "activations"),
    "capacity-lab":   (CAPACITY,    "network"),
}


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
