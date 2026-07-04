"""
Standalone utility to pre-download / verify the BLIP captioning model.
Run once before starting the server:  python ml_models/caption_model.py
"""

def download_model():
    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration
        print("Downloading BLIP model (Salesforce/blip-image-captioning-base)...")
        BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        print("✅ Model downloaded and cached successfully.")
    except ImportError:
        print("❌ transformers not installed. Run: pip install transformers torch")
    except Exception as e:
        print(f"❌ Download failed: {e}")


if __name__ == "__main__":
    download_model()
