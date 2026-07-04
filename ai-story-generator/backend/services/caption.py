"""
Caption service - uses BLIP for image captioning.
Falls back to a simple placeholder if model not available.
"""

import base64
import io
from PIL import Image

_blip_processor = None
_blip_model = None
_blip_available = False


def _load_blip():
    """Lazy-load BLIP model to save memory."""
    global _blip_processor, _blip_model, _blip_available
    if _blip_available or _blip_model is not None:
        return _blip_available
    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration
        import torch
        print("[INFO] Loading BLIP model (first run may take a moment)...")
        _blip_processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )
        _blip_model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )
        _blip_model.eval()
        _blip_available = True
        print("[INFO] BLIP model loaded successfully.")
    except Exception as e:
        print(f"[WARN] BLIP not available: {e}. Using fallback captions.")
        _blip_available = False
    return _blip_available


def decode_image(image_b64: str) -> Image.Image:
    """Decode base64 image string to PIL Image."""
    # Strip data URL prefix if present
    if "," in image_b64:
        image_b64 = image_b64.split(",", 1)[1]
    img_bytes = base64.b64decode(image_b64)
    return Image.open(io.BytesIO(img_bytes)).convert("RGB")


def generate_caption(image_b64: str) -> str:
    """Generate a short caption for the given base64 image."""
    img = decode_image(image_b64)

    if _load_blip():
        try:
            import torch
            inputs = _blip_processor(images=img, return_tensors="pt")
            with torch.no_grad():
                out = _blip_model.generate(**inputs, max_new_tokens=40)
            caption = _blip_processor.decode(out[0], skip_special_tokens=True)
            return caption.strip().capitalize()
        except Exception as e:
            print(f"[ERROR] BLIP inference failed: {e}")

    # --- Fallback: basic heuristic placeholder ---
    w, h = img.size
    ratio = "landscape" if w > h else "portrait" if h > w else "square"
    return f"A {ratio} image with rich visual detail and interesting composition."
