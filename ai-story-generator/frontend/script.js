const API = "http://localhost:8080";
const S = { img: null, caption: "", desc: "", story: "" };
const $ = id => document.getElementById(id);

const upzone=$("upzone"),fileIn=$("file-in"),prev=$("prev"),upph=$("upph");
const genBtn=$("gen-btn"),gIco=$("g-ico"),gTxt=$("g-txt");
const empty=$("empty"),pbar=$("pbar"),stats=$("stats");
const cCap=$("c-cap"),cDesc=$("c-desc"),cStory=$("c-story");
const oCap=$("o-cap"),oDesc=$("o-desc"),oStory=$("o-story");
const rCap=$("r-cap"),rDesc=$("r-desc"),rStory=$("r-story");
const wcLive=$("wc-live"),wcIn=$("wc-in");
const wcNum=$("wc-num"),wcPct=$("wc-pct");
const stTarget=$("st-target"),stActual=$("st-actual"),stAcc=$("st-acc");
const dlBtn=$("dl-btn"),toast=$("toast");

// ── Theme ─────────────────────────────────────────────
function applyTheme(t) {
  document.body.classList.toggle("light", t === "light");
  localStorage.setItem("sl-theme", t);
  document.querySelectorAll(".tbtn").forEach(x => x.classList.remove("active"));
  const btn = document.getElementById("tbtn-" + t);
  if (btn) btn.classList.add("active");
}
applyTheme(localStorage.getItem("sl-theme") || "dark");

// ── Word count ─────────────────────────────────────────
if (wcIn) wcIn.addEventListener("input", () => {
  if (wcLive) wcLive.textContent = `${wcIn.value || 0} words`;
});
document.querySelectorAll(".chip").forEach(c =>
  c.addEventListener("click", () => {
    // active class fix
    document.querySelectorAll(".chip").forEach(x => x.classList.remove("active"));
    c.classList.add("active");
    if (wcIn) { wcIn.value = c.dataset.wc; }
    if (wcLive) wcLive.textContent = `${c.dataset.wc} words`;
  })
);

// ── Upload + Drag & Drop ───────────────────────────────
upzone.addEventListener("click", () => fileIn.click());
upzone.addEventListener("dragover", e => {
  e.preventDefault();
  upzone.style.borderColor = "var(--accent)";
  upzone.style.background = "var(--bg)";
});
upzone.addEventListener("dragleave", () => {
  upzone.style.borderColor = "";
  upzone.style.background = "";
});
upzone.addEventListener("drop", e => {
  e.preventDefault();
  upzone.style.borderColor = "";
  upzone.style.background = "";
  if (e.dataTransfer.files[0]) loadImg(e.dataTransfer.files[0]);
});
fileIn.addEventListener("change", () => { if (fileIn.files[0]) loadImg(fileIn.files[0]); });

function loadImg(file) {
  if (!file.type.startsWith("image/")) { showToast("Please upload JPG, PNG or WEBP", true); return; }
  const reader = new FileReader();
  reader.onload = e => {
    S.img = e.target.result;
    prev.src = S.img;
    prev.style.display = "block";
    upph.style.display = "none";
    upzone.classList.add("has-img");
    genBtn.disabled = false;
    S.caption = S.desc = S.story = "";
    // hide all cards
    [cCap, cDesc, cStory].forEach(c => { if(c) c.style.display = "none"; });
    if (empty) empty.style.display = "flex";
    if (stats) stats.style.display = "none";
    [rCap, rDesc, rStory].forEach(b => { if(b) b.disabled = true; });
  };
  reader.readAsDataURL(file);
}

// ── Skeleton ──────────────────────────────────────────
function skel(el, n = 2) {
  el.innerHTML = `<div class="skel-wrap">${Array.from({length:n}, (_,i) =>
    `<div class="skel" style="width:${i===n-1?55:100}%"></div>`).join("")}</div>`;
}

function prog(p) {
  if (!pbar) return;
  pbar.style.width = p + "%";
  if (p >= 100) setTimeout(() => pbar.style.width = "0%", 500);
}

function showWC(text, target) {
  if (!text) return;
  const actual = text.trim().split(/\s+/).filter(Boolean).length;
  const pct = Math.round((actual / target) * 100);
  const cls = pct >= 85 && pct <= 115 ? "good" : pct >= 70 && pct <= 130 ? "warn" : "bad";

  if (wcNum) wcNum.textContent = `${actual} words`;
  if (wcPct) {
    wcPct.textContent = pct + "%";
    wcPct.style.color = pct >= 85 && pct <= 115
      ? "var(--bar-good)"
      : pct >= 70 && pct <= 130
        ? "var(--bar-warn)"
        : "var(--bar-bad)";
  }
  if (stTarget) stTarget.textContent = `${target} words`;
  if (stActual) stActual.textContent = `${actual} words`;
  if (stAcc) {
    const diff = actual - target;
    stAcc.textContent = `${pct}%  (${diff > 0 ? "+" : ""}${diff} words)`;
    stAcc.className = "stat-val " + cls;
  }
  if (stats) stats.style.display = "flex";
}

// ── Show card helper ──────────────────────────────────
function showCard(card) {
  if (!card) return;
  card.style.display = "block";
  card.style.animation = "none";
  card.offsetHeight; // reflow
  card.style.animation = "";
}

// Error function
function showErr(msg) {
  const errBox = document.getElementById("err");
  if (errBox) {
    errBox.textContent = msg;
    errBox.style.display = "block";
    setTimeout(() => { errBox.style.display = "none"; }, 4000);
  }
}

// ── Generate ──────────────────────────────────────────
genBtn.addEventListener("click", async () => {
  if (!S.img) {
    showErr("Please upload an image first!");
    return;
  }
  genBtn.disabled = true;
  gTxt.textContent = "Analyzing…";
  gIco.textContent = "⟳";
  [rCap, rDesc, rStory].forEach(b => { if(b) b.disabled = true; });
  if (empty) empty.style.display = "none";

  // show cards with skeleton
  showCard(cCap); showCard(cDesc); showCard(cStory);
  skel(oCap, 1); skel(oDesc, 3); skel(oStory, 6);
  prog(10);

  const theme = $("sel-theme").value;
  const wc = parseInt(wcIn.value) || 120;

  try {
    prog(20);
    const res = await fetch(`${API}/generate-all`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image_b64: S.img, theme, word_count: wc }),
    });
    prog(80);

    const text = await res.text();
    console.log("Raw response:", text.slice(0, 200));

    if (!res.ok) throw new Error(text);

    let d;
    try {
      d = JSON.parse(text);
    } catch (parseErr) {
      throw new Error("Invalid JSON from server: " + text.slice(0, 100));
    }

    if (!d.caption && !d.description && !d.story) {
      throw new Error("Empty response from server");
    }

    S.caption = d.caption     || "";
    S.desc    = d.description || "";
    S.story   = d.story       || "";

    oCap.textContent   = S.caption || "Could not generate caption.";
    oDesc.textContent  = S.desc    || "Could not generate description.";
    oStory.textContent = S.story   || "Could not generate story.";

    if (S.story) showWC(S.story, wc);
    prog(100);
    showToast("Story generated!");

  } catch (e) {
    console.error("Generate error:", e);
    oCap.textContent   = "⚠ " + e.message;
    oDesc.textContent  = "";
    oStory.textContent = "";
    showToast(e.message, true);
    prog(100);
  }

  genBtn.disabled = false;
  gTxt.textContent = "Generate Story";
  gIco.textContent = "✦";
  [rCap, rDesc, rStory].forEach(b => { if(b) b.disabled = false; });
});

// ── Regen buttons ─────────────────────────────────────
rCap.addEventListener("click", async () => {
  busy(rCap, true); skel(oCap, 1);
  try {
    const r = await post("/caption", { image_b64: S.img });
    S.caption = r.caption;
    oCap.textContent = S.caption;
    showToast("Caption regenerated!");
  } catch (e) { showToast(e.message, true); }
  busy(rCap, false);
});

rDesc.addEventListener("click", async () => {
  busy(rDesc, true); skel(oDesc, 3);
  try {
    await doDesc();
    showToast("Description regenerated!");
  } catch (e) { showToast(e.message, true); }
  busy(rDesc, false);
});

rStory.addEventListener("click", async () => {
  busy(rStory, true); skel(oStory, 6);
  try { await doStory(); }
  catch (e) { showToast(e.message, true); }
  busy(rStory, false);
});

async function doDesc() {
  const r = await post("/description", { caption: S.caption, image_b64: S.img });
  S.desc = r.description;
  oDesc.textContent = S.desc;
}

async function doStory() {
  const wc = parseInt(wcIn.value) || 120;
  const r = await post("/story", {
    caption: S.caption, description: S.desc,
    theme: $("sel-theme").value, word_count: wc, image_b64: S.img,
  });
  S.story = r.story;
  oStory.textContent = S.story;
  showWC(S.story, wc);
}

// ── Download ──────────────────────────────────────────
dlBtn.addEventListener("click", () => {
  if (!S.story) return;
  const wc = S.story.trim().split(/\s+/).filter(Boolean).length;
  const theme = $("sel-theme").value;
  const txt = `STORYLENS — ${theme.toUpperCase()}\n${"─".repeat(40)}\n\nCaption:\n${S.caption}\n\nDescription:\n${S.desc}\n\nStory (${wc} words):\n${S.story}`;
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([txt], { type: "text/plain" }));
  a.download = `storylens-${theme.toLowerCase()}.txt`;
  a.click();
  showToast("Downloaded!");
});

// ── Helpers ───────────────────────────────────────────
async function post(path, body) {
  const res = await fetch(API + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function busy(btn, on) {
  btn.classList.toggle("busy", on);
  btn.disabled = on;
  // swap spin-ico / rtxt via CSS class
  const spin = btn.querySelector(".spin-ico");
  const rtxt = btn.querySelector(".rtxt");
  if (spin) spin.style.display = on ? "inline-block" : "none";
  if (rtxt) rtxt.style.display = on ? "none" : "inline";
}

let tt;
function showToast(msg, err = false) {
  toast.textContent = msg;
  toast.className = "toast on" + (err ? " err" : "");
  clearTimeout(tt);
  tt = setTimeout(() => toast.classList.remove("on"), 3200);
}