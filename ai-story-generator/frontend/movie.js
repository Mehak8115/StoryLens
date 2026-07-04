/* =====================================================
   StoryLens — movie.js
   Uses Groq API with vision support
   ===================================================== */

const BACKEND = "http://localhost:8080";

// Fetch key from backend
fetch(`${BACKEND}/api-key`)
  .then(r => r.json())
  .then(d => { GROQ_API_KEY = d.groq_api_key || ''; })
  .catch(() => {});

// ── Theme ──────────────────────────────────────────────
function setTheme(t) {
  document.body.classList.toggle('light', t === 'light');
  localStorage.setItem('sl-theme', t);
  document.getElementById('tbtn-light').classList.toggle('active', t === 'light');
  document.getElementById('tbtn-dark').classList.toggle('active', t === 'dark');
}
(function () {
  const t = localStorage.getItem('sl-theme') || 'dark';
  setTheme(t);
})();

// ── State ──────────────────────────────────────────────
let uploadedImage  = null;
let selectedTone   = 'Dark';
let selectedDur    = '30 sec';
let currentConcept = null;
let GROQ_API_KEY   = '';

// Fetch API key from backend on page load
// fetch('/api-key')
//   .then(r => r.json())
//   .then(d => { GROQ_API_KEY = d.groq_api_key || ''; })
//   .catch(() => {});

// fetch(`${window.location.origin}/api-key`)
//   .then(r => r.json())
//   .then(d => { GROQ_API_KEY = d.groq_api_key || ''; })
//   .catch(() => {});

// ── Pill selectors ─────────────────────────────────────
document.getElementById('tone-pills').addEventListener('click', e => {
  const p = e.target.closest('.pill');
  if (!p) return;
  document.querySelectorAll('#tone-pills .pill').forEach(x => x.classList.remove('active'));
  p.classList.add('active');
  selectedTone = p.dataset.v;
});

document.getElementById('dur-pills').addEventListener('click', e => {
  const p = e.target.closest('.pill');
  if (!p) return;
  document.querySelectorAll('#dur-pills .pill').forEach(x => x.classList.remove('active'));
  p.classList.add('active');
  selectedDur = p.dataset.v;
});


function loadMovieImg(file) {
  if (!file) return;
  if (!file.type.startsWith('image/')) {
    showErr('Please upload JPG, PNG or WEBP');
    return;
  }
  const reader = new FileReader();
  reader.onload = ev => {
    uploadedImage = ev.target.result;
    const img = document.getElementById('preview-img');
    img.src = uploadedImage;
    img.style.display = 'block';
    document.getElementById('up-hint').style.display = 'none';
  };
  reader.readAsDataURL(file);
}

// Click upload
document.getElementById('file-input').addEventListener('change', function (e) {
  if (e.target.files[0]) loadMovieImg(e.target.files[0]);
});

// Drag & Drop
const movieUpZone = document.getElementById('upload-zone');

movieUpZone.addEventListener('click', () => {
  document.getElementById('file-input').click();
});

movieUpZone.addEventListener('dragover', e => {
  e.preventDefault();
  e.stopPropagation();
  movieUpZone.style.borderColor = 'var(--accent)';
  movieUpZone.style.background = 'var(--accent-dim)';
});

movieUpZone.addEventListener('dragleave', e => {
  e.stopPropagation();
  movieUpZone.style.borderColor = '';
  movieUpZone.style.background = '';
});

movieUpZone.addEventListener('drop', e => {
  e.preventDefault();
  e.stopPropagation();
  movieUpZone.style.borderColor = '';
  movieUpZone.style.background = '';
  if (e.dataTransfer.files[0]) loadMovieImg(e.dataTransfer.files[0]);
});


// // ── Image upload ───────────────────────────────────────
// document.getElementById('file-input').addEventListener('change', function (e) {
//   const file = e.target.files[0];
//   if (!file) return;
//   const reader = new FileReader();
//   reader.onload = ev => {
//     uploadedImage = ev.target.result;
//     const img = document.getElementById('preview-img');
//     img.src = uploadedImage;
//     img.style.display = 'block';
//     document.getElementById('up-hint').style.display = 'none';
//   };
//   reader.readAsDataURL(file);
// });

// // Drag & Drop 
// const uploadZone = document.getElementById('upload-zone');

// uploadZone.addEventListener('dragover', e => {
//   e.preventDefault();
//   uploadZone.style.borderColor = 'var(--accent)';
// });

// uploadZone.addEventListener('dragleave', () => {
//   uploadZone.style.borderColor = '';
// });

// uploadZone.addEventListener('drop', e => {
//   e.preventDefault();
//   uploadZone.style.borderColor = '';
//   const file = e.dataTransfer.files[0];
//   if (!file) return;
//   if (!file.type.startsWith('image/')) {
//     showErr('Please upload JPG, PNG or WEBP');
//     return;
//   }
//   const reader = new FileReader();
//   reader.onload = ev => {
//     uploadedImage = ev.target.result;
//     const img = document.getElementById('preview-img');
//     img.src = uploadedImage;
//     img.style.display = 'block';
//     document.getElementById('up-hint').style.display = 'none';
//   };
//   reader.readAsDataURL(file);
// });

// ── Helpers ────────────────────────────────────────────
const loader = document.getElementById('loader');
const errBox = document.getElementById('err');

function showLoader() { loader.classList.add('show'); }
function hideLoader() { loader.classList.remove('show'); }
function showErr(msg) {
  errBox.textContent = msg;
  errBox.style.display = 'block';
  setTimeout(() => { errBox.style.display = 'none'; }, 7000);
}

// ── Main generate ──────────────────────────────────────
async function generate() {
  if (!uploadedImage) { showErr('Please upload an image first.'); return; }

  if (!GROQ_API_KEY) {
  try {
    const r = await fetch(`${BACKEND}/api-key`);
    const d = await r.json();
    GROQ_API_KEY = d.groq_api_key || '';
  } catch (_) {}
}

  if (!GROQ_API_KEY) {
    showErr('Groq API key not found. Make sure GROQ_API_KEY is set in your .env file.');
    return;
}


  // Retry fetching key if not loaded yet
  // if (!GROQ_API_KEY) {
  //   try {
  //     // const r = await fetch('/api-key');
  //     const r = await fetch(`${window.location.origin}/api-key`);
  //     const d = await r.json();
  //     GROQ_API_KEY = d.groq_api_key || '';
  //   } catch (_) {}
  // }

  // if (!GROQ_API_KEY) {
  //   showErr('Groq API key not found. Make sure GROQ_API_KEY is set in your .env file.');
  //   return;
  // }

  const genre     = document.getElementById('genre').value;
  const btn       = document.getElementById('gen-btn');
  btn.disabled    = true;
  showLoader();

  const imageData = uploadedImage.split(',')[1];
  const mediaType = uploadedImage.match(/data:(.*?);/)[1];

  const SYSTEM = `You are an expert film director, screenwriter, and visual storyteller.
Analyze the provided image and create a compelling short film concept.
Return ONLY valid JSON — no markdown, no code fences, no extra text whatsoever.
Use exactly this schema:
{
  "title": "short cinematic film title",
  "genre": "genre string",
  "tone": "tone string",
  "logline": "one compelling sentence summary",
  "plot": "100-150 word plot with beginning, conflict, climax, resolution",
  "scenes": [
    {
      "scene_title": "scene name",
      "description": "2-3 sentences of what happens",
      "emotion": "one-word emotional tone",
      "camera": "specific shot types e.g. Close-up on face, Wide establishing shot"
    }
  ],
  "visual_style": "full visual aesthetic description",
  "music": "genre, instruments, and mood description",
  "character": {
    "name": "character name",
    "role": "their role",
    "personality": "personality traits",
    "goal": "what they want",
    "conflict": "what stands in their way"
  }
}
Requirements: exactly 5 scenes, all fields populated, make it cinematic not generic.`;

  const USER = `Image attached. Create a film concept with:
Genre: ${genre}
Tone: ${selectedTone}
Duration: ${selectedDur}
Return ONLY the JSON object, nothing else.`;

  try {
    const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${GROQ_API_KEY}`
      },
      body: JSON.stringify({
        model: 'meta-llama/llama-4-scout-17b-16e-instruct',
        max_tokens: 1500,
        messages: [
          { role: 'system', content: SYSTEM },
          {
            role: 'user',
            content: [
              {
                type: 'image_url',
                image_url: {
                  url: `data:${mediaType};base64,${imageData}`
                }
              },
              { type: 'text', text: USER }
            ]
          }
        ]
      })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error?.message || `API error ${res.status}`);
    }

    const data  = await res.json();
    const raw   = data.choices?.[0]?.message?.content?.trim() || '';
    const clean = raw.replace(/```json|```/g, '').trim();

    let concept;
    try { concept = JSON.parse(clean); }
    catch { throw new Error('Could not parse response. Please try again.'); }

    currentConcept = concept;
    render(concept, genre);

  } catch (err) {
    showErr('Error: ' + err.message);
  } finally {
    hideLoader();
    btn.disabled = false;
  }
}

// ── Render ─────────────────────────────────────────────
function render(c, genre) {
  document.getElementById('empty').style.display = 'none';
  const result = document.getElementById('result');
  result.style.display = 'flex';

  document.getElementById('r-title').textContent   = c.title        || 'Untitled';
  document.getElementById('r-genre').textContent   = c.genre        || genre;
  document.getElementById('r-tone').textContent    = c.tone         || selectedTone;
  document.getElementById('r-dur').textContent     = selectedDur;
  document.getElementById('r-logline').textContent = c.logline      || '';
  document.getElementById('r-plot').textContent    = c.plot         || '';
  document.getElementById('r-visual').textContent  = c.visual_style || '';
  document.getElementById('r-music').textContent   = c.music        || '';

  // Character
  const ch = c.character || {};
  document.getElementById('r-char').innerHTML = [
    ['Name',        ch.name],
    ['Role',        ch.role],
    ['Personality', ch.personality],
    ['Goal',        ch.goal],
    ['Conflict',    ch.conflict]
  ].map(([k, v]) => `
    <div class="char-f">
      <span class="char-k">${k}</span>
      <span class="char-v">${v || '—'}</span>
    </div>`).join('');

  // Scenes
  const scenes = Array.isArray(c.scenes) ? c.scenes : [];
  document.getElementById('r-scenes').innerHTML = scenes.map((s, i) => `
    <div class="scene-card">
      <div class="scene-num">0${i + 1}</div>
      <div class="scene-body">
        <div class="scene-r1">
          <span class="scene-ttl">${s.scene_title || 'Scene ' + (i + 1)}</span>
          <span class="emo-tag">${s.emotion || ''}</span>
        </div>
        <div class="scene-desc">${s.description || ''}</div>
        <span class="cam-tag">▣ ${s.camera || ''}</span>
      </div>
    </div>`).join('');

  result.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Download ───────────────────────────────────────────
function dlConcept() {
  if (!currentConcept) return;
  const c = currentConcept;
  const txt = [
    `FILM CONCEPT: ${c.title}`,
    '='.repeat(50),
    `Genre: ${c.genre}  |  Tone: ${c.tone}  |  Duration: ${selectedDur}`,
    '',
    'LOGLINE',
    c.logline,
    '',
    'PLOT SUMMARY',
    c.plot,
    '',
    'CHARACTER SKETCH',
    `  Name        : ${c.character?.name}`,
    `  Role        : ${c.character?.role}`,
    `  Personality : ${c.character?.personality}`,
    `  Goal        : ${c.character?.goal}`,
    `  Conflict    : ${c.character?.conflict}`,
    '',
    'SCENE BREAKDOWN',
    ...(c.scenes || []).flatMap((s, i) => [
      '',
      `  Scene ${i + 1}: ${s.scene_title}`,
      `  ${s.description}`,
      `  Emotion : ${s.emotion}`,
      `  Camera  : ${s.camera}`
    ]),
    '',
    'VISUAL STYLE',
    c.visual_style,
    '',
    'BACKGROUND MUSIC',
    c.music,
    '',
    '— Generated by StoryLens'
  ].join('\n');

  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([txt], { type: 'text/plain' }));
  a.download = (c.title || 'film_concept').replace(/\s+/g, '_') + '.txt';
  a.click();
  URL.revokeObjectURL(a.href);
}