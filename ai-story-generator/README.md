# 🌌 StoryLens — AI Image Story Generator

Upload any image and instantly get a **caption**, **description**, and **creative story** — all independently regeneratable, with theme controls and 4 UI themes.

---

## 📁 Project Structure

```
ai-story-generator/
├── backend/
│   ├── main.py          ← FastAPI app entry point
│   ├── routes.py        ← API endpoints
│   ├── models.py        ← Pydantic request/response models
│   └── services/
│       ├── caption.py   ← BLIP image captioning
│       └── story.py     ← Description & story generation
├── frontend/
│   ├── index.html       ← Main UI
│   ├── style.css        ← All styles + 4 themes
│   └── script.js        ← App logic & API calls
├── ml_models/
│   └── caption_model.py ← BLIP model downloader utility
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚡ Quick Start (5 steps)

### 1. Clone / unzip the project
```bash
cd ai-story-generator
```

### 2. Create a Python virtual environment
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

**Minimal install (fallback mode — no AI model required):**
```bash
pip install fastapi uvicorn python-multipart pydantic pillow python-dotenv
```

**Full install (with BLIP + Claude API):**
```bash
# CPU-only PyTorch (recommended for 8 GB RAM):
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### 4. Configure API key (optional but recommended)
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

> Without an API key, the app uses built-in rule-based fallback generators — still fully functional!

### 5. Pre-download the BLIP model (optional, first run only)
```bash
python ml_models/caption_model.py
```

---

## 🚀 Running the App

### Start the backend
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
API docs available at: http://localhost:8000/docs

### Open the frontend
Simply open `frontend/index.html` in your browser:
```bash
# macOS
open frontend/index.html

# Linux
xdg-open frontend/index.html

# Windows
start frontend/index.html
```

> **Tip:** You can also serve the frontend with Python:
> ```bash
> cd frontend && python -m http.server 3000
> ```
> Then visit http://localhost:3000

---

## 🌐 API Reference

### `POST /caption`
Generate a short caption from a base64 image.

**Request:**
```json
{
  "image_b64": "data:image/jpeg;base64,/9j/4AAQ..."
}
```

**Response:**
```json
{
  "caption": "a golden retriever playing in autumn leaves"
}
```

---

### `POST /description`
Generate a detailed description based on a caption.

**Request:**
```json
{
  "caption": "a golden retriever playing in autumn leaves"
}
```

**Response:**
```json
{
  "description": "Warm amber and russet leaves cascade around a joyful dog..."
}
```

---

### `POST /story`
Generate a themed creative story.

**Request:**
```json
{
  "caption": "a golden retriever playing in autumn leaves",
  "description": "Warm amber and russet leaves...",
  "theme": "Adventure",
  "word_count": 150
}
```

**Response:**
```json
{
  "story": "The dog had a mission. Somewhere beneath those ten thousand fallen leaves..."
}
```

---

## 🎨 UI Themes

| Theme   | Aesthetic                          |
|---------|------------------------------------|
| Light   | Warm parchment, editorial serif    |
| Dark    | Deep navy, soft violet accents     |
| Neon    | Cyberpunk green on black           |
| Minimal | Pure white, strict monochrome      |

---

## 🎭 Story Themes

- **Adventure** — Bold, exploratory, action-driven
- **Horror** — Eerie, atmospheric, foreboding
- **Fantasy** — Magical, mystical, otherworldly
- **Sci-Fi** — Futuristic, technological, cosmic
- **Emotional** — Tender, nostalgic, introspective

---

## 💡 Tips for Low-Resource Systems (8 GB RAM)

- Use **CPU-only PyTorch** (see install step above) — saves ~2 GB
- BLIP base model uses ~500 MB RAM — well within limits
- The app also works with **zero ML dependencies** using fallback mode
- Avoid running multiple browser tabs with large images simultaneously

---

## 🔁 Regeneration Logic

| Button | What regenerates |
|--------|-----------------|
| ↺ Caption | Caption only → then cascades to Description + Story |
| ↺ Description | Description only → then cascades to Story |
| ↺ Story | Story only (uses current caption + description + theme + word count) |

---

## 📦 Dependencies Summary

| Package | Purpose |
|---------|---------|
| `fastapi` | REST API framework |
| `uvicorn` | ASGI server |
| `pydantic` | Data validation |
| `pillow` | Image processing |
| `transformers` | BLIP captioning model |
| `torch` | ML inference backend |
| `anthropic` | Claude API for text generation |
| `python-dotenv` | Environment variables |

---

## 🛠 Troubleshooting

**CORS error in browser?**
→ Make sure the backend is running on port 8000 before opening the frontend.

**BLIP model download fails?**
→ Check your internet connection. The model is ~900 MB and downloads once to `~/.cache/huggingface`.

**Out of memory with BLIP?**
→ The fallback caption generator will be used automatically — no action needed.

**`anthropic` not found?**
→ Run `pip install anthropic` or the app will use rule-based story generation.
