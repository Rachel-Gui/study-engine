/* site.js - contents highlighting, keyboard paging, and the Python labs.
   Pyodide loads lazily: nothing is fetched until a student presses Run. */

/* With 90+ topics the contents only stays usable if it collapses: show the
   topic list for the episode you are in, and nothing else. */
function markCurrent(i){
  const here = document.querySelector(`nav [data-i="${i}"]`);
  if(!here) return;
  here.classList.add("on");
  const ep = here.dataset.ep;
  document.querySelectorAll("nav a.tp").forEach(a =>
    a.classList.toggle("show", a.dataset.ep === ep));
  document.querySelectorAll("nav a.ep").forEach(a =>
    a.classList.toggle("open", a.dataset.ep === ep));
  here.scrollIntoView({block:"center"});
}

/* clicking an episode you are not in expands it without navigating away */
document.querySelectorAll("nav a.ep").forEach(a => {
  a.addEventListener("click", e => {
    if(a.classList.contains("open")) return;          // already open: follow the link
    e.preventDefault();
    document.querySelectorAll("nav a.ep").forEach(x => x.classList.remove("open"));
    a.classList.add("open");
    document.querySelectorAll("nav a.tp").forEach(t =>
      t.classList.toggle("show", t.dataset.ep === a.dataset.ep));
  });
});

document.getElementById("navbtn")?.addEventListener("click", () =>
  document.getElementById("nav").classList.toggle("open"));

document.addEventListener("keydown", e => {
  if(/INPUT|TEXTAREA/.test(e.target.tagName)) return;
  const go = s => document.querySelector(`footer a.btn:${s}-of-type`)?.click();
  if(e.key === "ArrowLeft")  go("first");
  if(e.key === "ArrowRight") go("last");
});

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
      try {
        const py = await getPyodide(packages, m => { boot.textContent = m; });
        boot.textContent = "python ready";
        py.setStdout({ batched: t => { out.textContent += t + "\n"; } });
        out.textContent = "";
        const value = await py.runPythonAsync(src.value);
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

/* ------------------------------------------------------------ check answers */
document.querySelectorAll(".reflect .chk").forEach(btn => {
  btn.onclick = () => {
    const box = btn.closest(".reflect");
    const picked = box.querySelector("input[type=radio]:checked");
    const v = box.querySelector(".verdict");
    v.hidden = false;
    if (!picked) { v.textContent = "Pick an option first."; return; }
    v.textContent = picked.value === btn.dataset.correct
      ? "Correct." + (btn.dataset.feedback ? " " + btn.dataset.feedback : "")
      : "Not quite — have another look at the options.";
  };
});

/* Native disclosure state keeps reference-answer labels in sync, including studios. */
document.addEventListener("toggle", event => {
  if (event.target.tagName !== "DETAILS") return;
  const summary = event.target.firstElementChild;
  if (summary?.hasAttribute("data-reference-answer")) {
    summary.textContent = event.target.open ? "Hide reference answer" : "Show reference answer";
  }
}, true);
