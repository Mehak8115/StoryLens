from dotenv import load_dotenv
load_dotenv()  # loads .env from the project root — must be before anything else

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
import os

app = FastAPI(title="AI Image Story Generator", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    key_set = bool(os.getenv("ANTHROPIC_API_KEY", ""))
    return {
        "status": "running",
        "api_key_configured": key_set,
        "mode": "AI (Claude)" if key_set else "Fallback (rule-based)",
    }

@app.get("/check-api")
def check_api():
    return {
        "status": "OK",
        "service": "AI Image Story Generator",
        "port": 8080
    }

from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
