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
      out.textContent = "running…";
      try {
        const py = await getPyodide(packages, m => { boot.textContent = m; });
        boot.textContent = "python ready";
        py.setStdout({ batched: t => { out.textContent += t + "\n"; } });
        out.textContent = "";
        const value = await py.runPythonAsync(src.value);
        if(value !== undefined && value !== null)
          out.textContent += String(value) + "\n";
        if(!out.textContent.trim()) out.textContent = "(no output)";
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
      ? "That's the one."
      : "Not quite — have another look at the options.";
  };
});
