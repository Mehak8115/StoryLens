# from fastapi import APIRouter, HTTPException
# from models import (
#     CaptionRequest, CaptionResponse,
#     DescriptionRequest, DescriptionResponse,
#     StoryRequest, StoryResponse,
# )
# from services.caption import generate_caption
# from services.story import (
#     generate_all_at_once,
#     generate_caption_from_image,
#     generate_description,
#     generate_story,
#     _fallback_description,
#     _fallback_story,
# )
# from pydantic import BaseModel

# router = APIRouter()


# class GenerateAllRequest(BaseModel):
#     image_b64: str
#     theme: str = "Adventure"
#     word_count: int = 120


# class GenerateAllResponse(BaseModel):
#     caption: str
#     description: str
#     story: str


# @router.post("/generate-all", response_model=GenerateAllResponse)
# async def generate_all_endpoint(req: GenerateAllRequest):
#     """
#     Single endpoint — one Claude vision call returns caption + description + story.
#     Fastest possible path.
#     """
#     try:
#         # Try single-shot JSON approach first
#         result = generate_all_at_once(req.image_b64, req.theme, req.word_count)

#         if result and result.get("caption") and result.get("story"):
#             return GenerateAllResponse(**result)

#         # Fallback: generate caption separately, then use fallback text generators
#         print("[INFO] Single-shot failed or no API key — using fallbacks.")
#         caption = generate_caption(req.image_b64)
#         description = _fallback_description(caption)
#         story = _fallback_story(caption, description, req.theme, req.word_count)
#         return GenerateAllResponse(caption=caption, description=description, story=story)

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post("/caption", response_model=CaptionResponse)
# async def caption_endpoint(req: CaptionRequest):
#     try:
#         caption = generate_caption_from_image(req.image_b64)
#         if not caption:
#             caption = generate_caption(req.image_b64)
#         return CaptionResponse(caption=caption)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post("/description", response_model=DescriptionResponse)
# async def description_endpoint(req: DescriptionRequest):
#     try:
#         desc = generate_description(req.caption, req.image_b64)
#         return DescriptionResponse(description=desc)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post("/story", response_model=StoryResponse)
# async def story_endpoint(req: StoryRequest):
#     try:
#         story = generate_story(
#             caption=req.caption,
#             description=req.description,
#             theme=req.theme,
#             word_count=req.word_count,
#             image_b64=getattr(req, "image_b64", None),
#         )
#         return StoryResponse(story=story)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/check-api")
# async def check_api():
#     """Quick endpoint to verify if the API key is configured."""
#     import os
#     key = os.getenv("ANTHROPIC_API_KEY", "")
#     if not key:
#         return {"status": "missing", "message": "ANTHROPIC_API_KEY not set — fallback mode active"}
#     masked = key[:8] + "..." + key[-4:]
#     return {"status": "configured", "key_preview": masked}


from fastapi import APIRouter, HTTPException
from models import (
    CaptionRequest, CaptionResponse,
    DescriptionRequest, DescriptionResponse,
    StoryRequest, StoryResponse,
)
from services.story import (
    generate_all_at_once,
    generate_caption_from_image,
    generate_description,
    generate_story,
    _fallback_description,
    _fallback_story,
    analyze_image,
)
from pydantic import BaseModel

router = APIRouter()


class GenerateAllRequest(BaseModel):
    image_b64: str
    theme: str = "Adventure"
    word_count: int = 120


class GenerateAllResponse(BaseModel):
    caption: str
    description: str
    story: str


@router.post("/generate-all", response_model=GenerateAllResponse)
async def generate_all_endpoint(req: GenerateAllRequest):
    try:
        result = generate_all_at_once(req.image_b64, req.theme, req.word_count)
        if result and result.get("caption") and result.get("story"):
            return GenerateAllResponse(**result)
        # fallback
        scene = analyze_image(req.image_b64)
        caption = scene.split(".")[0].strip().capitalize()
        description = _fallback_description(scene)
        story = _fallback_story(scene, req.theme, req.word_count)
        return GenerateAllResponse(caption=caption, description=description, story=story)
    except Exception as e:
        print(f"[ERROR] /generate-all: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/caption", response_model=CaptionResponse)
async def caption_endpoint(req: CaptionRequest):
    try:
        caption = generate_caption_from_image(req.image_b64)
        return CaptionResponse(caption=caption)
    except Exception as e:
        print(f"[ERROR] /caption: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/description", response_model=DescriptionResponse)
async def description_endpoint(req: DescriptionRequest):
    try:
        desc = generate_description(req.caption, req.image_b64)
        return DescriptionResponse(description=desc)
    except Exception as e:
        print(f"[ERROR] /description: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/story", response_model=StoryResponse)
async def story_endpoint(req: StoryRequest):
    try:
        story = generate_story(
            caption=req.caption,
            description=req.description,
            theme=req.theme,
            word_count=req.word_count,
            image_b64=getattr(req, "image_b64", None),
        )
        return StoryResponse(story=story)
    except Exception as e:
        print(f"[ERROR] /story: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check-api")
async def check_api():
    import os
    groq_key = os.getenv("GROQ_API_KEY", "")
    claude_key = os.getenv("ANTHROPIC_API_KEY", "")
    return {
        "groq": "configured" if groq_key else "missing",
        "claude": "configured" if claude_key else "missing — using BLIP fallback",
    }


@router.get("/api-key")
async def get_api_key():
    import os
    from dotenv import load_dotenv
    load_dotenv()
    groq_key = os.getenv("GROQ_API_KEY", "")
    return {"groq_api_key": groq_key}