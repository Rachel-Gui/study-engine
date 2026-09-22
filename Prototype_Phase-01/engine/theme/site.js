/* site.js - contents panel, page motion, keyboard paging, and the Python labs.
   Pyodide loads lazily: nothing is fetched until a student presses Run. */

/* ------------------------------------------------------------ contents panel
   Modules and lessons both collapse. Click the chevron to toggle; click the
   name to navigate. What the student opens stays open across pages
   (localStorage); the lesson they are reading is always shown open. */
const NAV_KEY = "studyengine.nav";
function navState(){ try { return JSON.parse(localStorage.getItem(NAV_KEY) || "{}"); }
                     catch(e){ return {}; } }
function navSave(s){ try { localStorage.setItem(NAV_KEY, JSON.stringify(s)); } catch(e){} }

function markCurrent(i){
  const here = document.querySelector(`nav [data-i="${i}"]`);
  const st = navState(); st.m = st.m || {}; st.e = st.e || {};
  let curM, curE;
  if(here){
    here.classList.add("on", "show");
    curM = here.dataset.m ?? here.closest(".m")?.dataset.m;
    curE = here.dataset.ep ?? here.closest(".e")?.dataset.ep;
  }
  // open = where you are now (transient) OR what you chose to open (remembered)
  document.querySelectorAll("nav .m").forEach(x =>
    x.classList.toggle("open", x.dataset.m === curM || !!st.m[x.dataset.m]));
  document.querySelectorAll("nav .e").forEach(x =>
    x.classList.toggle("open", x.dataset.ep === curE || !!st.e[x.dataset.ep]));
  (window.requestAnimationFrame || setTimeout)(() => here?.scrollIntoView?.({block:"center"}));
}
// clicking a lesson name follows the link; it also opens that lesson in the tree
document.querySelectorAll("nav a.ep").forEach(a => a.addEventListener("click", () => {
  const e = a.closest(".e"), st = navState(); st.e = st.e || {};
  a.classList.add("open"); e.classList.add("open"); st.e[e.dataset.ep] = true; navSave(st);
}));
document.querySelectorAll("nav .m > .mh > .tg").forEach(btn => btn.onclick = () => {
  const m = btn.closest(".m"), st = navState(); st.m = st.m || {};
  m.classList.toggle("open"); st.m[m.dataset.m] = m.classList.contains("open"); navSave(st);
});
document.querySelectorAll("nav .e > .eh > .tg").forEach(btn => btn.onclick = () => {
  const e = btn.closest(".e"), st = navState(); st.e = st.e || {};
  e.classList.toggle("open"); st.e[e.dataset.ep] = e.classList.contains("open"); navSave(st);
});
document.getElementById("navbtn")?.addEventListener("click", () =>
  document.getElementById("nav").classList.toggle("open"));

/* ----------------------------------------------------------- page motion */
(function(){
  const stage = document.getElementById("stage"), bar = document.getElementById("readbar");
  if(stage && bar){
    const upd = () => {
      const max = stage.scrollHeight - stage.clientHeight;
      bar.style.width = (max > 0 ? Math.min(100, 100 * stage.scrollTop / max) : 100) + "%";
    };
    stage.addEventListener("scroll", upd, {passive:true}); upd();
  }
  // reveal each block as it scrolls into view; a staggered rise, once
  const items = [...document.querySelectorAll("article > *")];
  items.forEach((el, i) => { el.classList.add("rv"); el.style.setProperty("--d", Math.min(i, 8) * 45 + "ms"); });
  if("IntersectionObserver" in window){
    const io = new IntersectionObserver(es => es.forEach(e => {
      if(e.isIntersecting){ e.target.classList.add("in"); io.unobserve(e.target); }
    }), {root: stage, rootMargin: "0px 0px -8% 0px", threshold: 0.05});
    items.forEach(el => io.observe(el));
  } else items.forEach(el => el.classList.add("in"));
})();

document.addEventListener("keydown", e => {
  if(/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) return;
  if(e.key === "ArrowLeft")  document.querySelector("footer a.btn.prev")?.click();
  if(e.key === "ArrowRight") document.querySelector("footer a.btn.next")?.click();
});

/* ------------------------------------------------------------ OS tabs
   :::os blocks render Windows / macOS panes. One choice, remembered site-wide. */
(function(){
  const KEY = "studyengine.os";
  let os = null;
  try { os = localStorage.getItem(KEY); } catch(e){}
  if(!os) os = /Mac|iPhone|iPad/.test(navigator.platform) ? "mac" : "win";
  const apply = () => document.querySelectorAll(".os").forEach(box => {
    box.querySelectorAll(".os-tab").forEach(t => t.classList.toggle("on", t.dataset.os === os));
    box.querySelectorAll(".os-pane").forEach(p => p.hidden = p.dataset.os !== os);
  });
  document.querySelectorAll(".os .os-tab").forEach(t => t.onclick = () => {
    os = t.dataset.os; try { localStorage.setItem(KEY, os); } catch(e){} apply();
  });
  apply();
})();

/* ------------------------------------------------------------ python labs */
/* Native textareas print only their editor viewport in some browsers. Keep the
   live value and screen scroll position intact; use normal flowing text on paper. */
function clearPrintValues(){
  document.querySelectorAll('[data-print-value]').forEach(node=>node.remove());
  document.querySelectorAll('textarea.print-source').forEach(node=>node.classList.remove('print-source'));
}
window.addEventListener('beforeprint',()=>{
  clearPrintValues();
  document.querySelectorAll('article textarea').forEach(editor=>{
    if(editor.hidden)return;
    const text=document.createElement('pre');
    text.className='print-value';text.dataset.printValue='';
    text.textContent=editor.value || ' ';
    editor.after(text);editor.classList.add('print-source');
  });
});
window.addEventListener('afterprint',clearPrintValues);

let pyodideReady = null;

async function getPyodide(packages, onStatus){
  if(!pyodideReady){
    const url = document.body.dataset.pyodide;
    onStatus("loading python…");
    await new Promise((ok, fail) => {
      const s = document.createElement("script");
      s.src = url + "pyodide.js"; s.onload = ok; s.onerror = fail;
      document.head.appendChild(s);
    });
    pyodideReady = loadPyodide({ indexURL: url });
  }
  const py = await pyodideReady;
  if(packages.length){
    onStatus("loading " + packages.join(", ") + "…");
    await py.loadPackage(packages);
  }
  return py;
}

/* Any matplotlib figure left open after a step is captured automatically, so a
   lab can just call plt.plot(...) and the picture appears under the code. */
const MPL_PRELUDE = "import os as _os\n_os.environ.setdefault('MPLBACKEND','AGG')\n";
const MPL_HARVEST = `
import sys as _sys, io as _io, base64 as _b64
_out = []
if 'matplotlib.pyplot' in _sys.modules:
    import matplotlib.pyplot as _plt
    for _n in _plt.get_fignums():
        _f = _plt.figure(_n); _buf = _io.BytesIO()
        _f.savefig(_buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        _out.append('data:image/png;base64,' + _b64.b64encode(_buf.getvalue()).decode())
    _plt.close('all')
_out
`;

/* Optional JSON result: {type:"pylab-output", blocks:[...]}.
   Content authors can return metrics, tables, text, PNGs and collapsed details.
   Use DOM text nodes, never HTML from Python results. Plain results still work. */
function pylabBlock(block){
  const el = (tag, text, className) => {
    const node = document.createElement(tag);
    if(text != null) node.textContent = String(text);
    if(className) node.className = className;
    return node;
  };
  if(block.type === "text") return el("p", block.text);
  if(block.type === "metrics"){
    const group = el("div", null, "pylab-metrics");
    for(const item of block.items){
      const card = el("div", null, item.primary ? "primary" : "");
      card.append(el("span", item.label), el("strong", item.value));
      group.append(card);
    }
    return group;
  }
  if(block.type === "table"){
    const wrap = el("div", null, "pylab-table-wrap");
    wrap.tabIndex = 0;
    wrap.setAttribute("role", "region");
    wrap.setAttribute("aria-label", block.caption || "Python result table");
    const table = el("table");
    if(block.caption) table.append(el("caption", block.caption));
    const head = el("thead"), row = el("tr"), body = el("tbody");
    for(const label of block.columns){
      const cell = el("th", label); cell.scope = "col"; row.append(cell);
    }
    head.append(row);
    for(const values of block.rows){
      const row = el("tr");
      for(const value of values) row.append(el("td", value));
      body.append(row);
    }
    table.append(head, body); wrap.append(table); return wrap;
  }
  if(block.type === "image" && String(block.src).startsWith("data:image/png;base64,")){
    const figure = el("figure"), image = el("img");
    image.src = block.src; image.alt = block.alt || "Python-generated plot";
    figure.append(image);
    if(block.caption) figure.append(el("figcaption", block.caption));
    return figure;
  }
  if(block.type === "details"){
    const details = el("details", null, "exp");
    details.append(el("summary", block.summary));
    for(const child of block.blocks) details.append(pylabBlock(child));
    return details;
  }
  return el("p", "Unsupported result block.");
}

document.querySelectorAll(".pylab").forEach(lab => {
  const packages = JSON.parse(lab.dataset.packages || "[]");
  const boot  = lab.querySelector(".boot");
  const steps = [...lab.querySelectorAll(".step")];
  const original = steps.map(s => s.querySelector(".src").value);

  steps.forEach((step, idx) => {
    const src = step.querySelector(".src");
    const out = step.querySelector(".out");
    const run = step.querySelector(".run");

    step.querySelector(".rst").onclick = () => {
      src.value = original[idx]; out.hidden = true;
    };

    run.onclick = async () => {
      run.disabled = true;
      out.hidden = false;
      out.classList.remove("has-image", "has-rich-output");
      out.textContent = "running…";
      step.querySelector(".state").textContent = "running";
      try {
        const py = await getPyodide(packages, m => { boot.textContent = m; });
        boot.textContent = "python ready";
        py.setStdout({ batched: t => { out.textContent += t + "\n"; } });
        out.textContent = "";
        const value = await py.runPythonAsync(MPL_PRELUDE + src.value);
        if(value !== undefined && value !== null){
          const result = String(value);
          let structured;
          try { structured = JSON.parse(result); } catch (_) { /* ordinary output */ }
          if(structured?.type === "pylab-output" && Array.isArray(structured.blocks)){
            const content = document.createElement("div");
            content.className = "pylab-result";
            for(const block of structured.blocks) content.append(pylabBlock(block));
            out.append(content);
            out.classList.add("has-rich-output");
          } else if(result.startsWith("data:image/png;base64,")){
            const image = document.createElement("img");
            image.src = result;
            image.alt = step.querySelector(".nm")?.textContent || "Python-generated plot";
            out.appendChild(image);
            out.classList.add("has-image");
          } else {
            out.textContent += result + "\n";
          }
        }
        // harvest any matplotlib figures the step left open
        try {
          const figs = (await py.runPythonAsync(MPL_HARVEST)).toJs();
          for(const src of figs){
            const image = document.createElement("img");
            image.src = src; image.alt = step.querySelector(".nm")?.textContent || "plot";
            out.appendChild(image); out.classList.add("has-image");
          }
        } catch (_) { /* no matplotlib in this step */ }
        if(!out.textContent.trim() && !out.children.length) out.textContent = "(no output)";
        step.querySelector(".state").textContent = "done";
        const next = steps[idx + 1];
        if(next){
          next.querySelector(".run").disabled = false;
          next.querySelector(".state").textContent = "ready";
        }
      } catch (err) {
        out.textContent = String(err);
        step.querySelector(".state").textContent = "error";
      } finally {
        run.disabled = false;
      }
    };
  });
});

/* ---------------------------------------------------------------- slide deck */
document.querySelectorAll(".deck[data-n]").forEach(deck => {
  const imgs = [...deck.querySelectorAll(".stage img")];
  const slider = deck.querySelector("input"), cnt = deck.querySelector(".cnt b");
  let i = 0;
  const show = n => {
    i = Math.max(0, Math.min(imgs.length - 1, n));
    imgs.forEach((im, j) => im.hidden = j !== i);
    slider.value = i + 1; cnt.textContent = i + 1;
  };
  deck.querySelector(".prev").onclick = () => show(i - 1);
  deck.querySelector(".next").onclick = () => show(i + 1);
  slider.oninput = () => show(+slider.value - 1);
});

/* ------------------------------------------------------------ check answers
   Each option may carry its own feedback (data-fb). If it does, the student
   reads why, not just whether. A block-level data-feedback is kept for the
   studio pages that use it. */
document.querySelectorAll(".reflect .chk").forEach(btn => {
  btn.onclick = () => {
    const box = btn.closest(".reflect");
    const picked = box.querySelector("input[type=radio]:checked");
    const v = box.querySelector(".verdict");
    v.hidden = false;
    if (!picked) { v.textContent = "Pick an option first."; v.className = "verdict"; return; }
    const ok = picked.value === btn.dataset.correct;
    const fb = picked.dataset.fb || "";
    v.className = "verdict " + (ok ? "ok" : "no");
    v.textContent = ok
      ? "Correct. " + (fb || btn.dataset.feedback || "")
      : "Not quite. " + (fb || "Have another look at the options.");
  };
});

/* Native disclosure state keeps reference-answer labels in sync, including studios.
   Both the toggle event and the open attribute are watched, so a programmatic
   details.open = true is reflected as well as a click. */
(function(){
  const sync = d => {
    const summary = d.firstElementChild;
    if (summary?.hasAttribute("data-reference-answer"))
      summary.textContent = d.open ? "Hide reference answer" : "Show reference answer";
  };
  document.querySelectorAll("details").forEach(d => {
    d.addEventListener("toggle", () => sync(d));
    if ("MutationObserver" in window)
      new MutationObserver(() => sync(d)).observe(d, {attributes: true, attributeFilter: ["open"]});
  });
})();
