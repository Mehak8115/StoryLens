"""
Hybrid: Claude vision (image analysis) + Groq (story generation)
"""

import os
import random

_groq_client = None

def _get_groq():
    global _groq_client
    if _groq_client is not None:
        return _groq_client
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        print("[WARN] GROQ_API_KEY not set.")
        return None
    try:
        from groq import Groq
        _groq_client = Groq(api_key=key)
        print("[INFO] Groq client initialized.")
        return _groq_client
    except ImportError:
        print("[WARN] groq not installed. Run: pip install groq")
        return None


def _groq(prompt: str, max_tokens: int = 1024, system: str = None) -> str:
    client = _get_groq()
    if not client:
        return ""
    try:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            temperature=0.9,
            # seed=random.randint(1, 999999),  # different every call
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[WARN] Groq error: {e}")
        return ""


def _analyze_image_with_claude(image_b64: str) -> str:
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        return ""
    try:
        import anthropic
        if "," in image_b64:
            header, data = image_b64.split(",", 1)
            mime = header.split(":")[1].split(";")[0]
        else:
            data = image_b64
            mime = "image/jpeg"
        client = anthropic.Anthropic(api_key=key)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": mime, "data": data}},
                    {"type": "text", "text": (
                        "Analyze this image and describe exactly what you see in 3-4 sentences. "
                        "Be very specific: name the subjects, their expressions, poses, colours, "
                        "setting, lighting, mood. This will be used as the basis for a story."
                    )}
                ]
            }]
        )
        result = msg.content[0].text.strip()
        print(f"[INFO] Claude image analysis: {result[:100]}...")
        return result
    except Exception as e:
        print(f"[WARN] Claude vision failed: {e}")
        return ""


def _analyze_image_with_blip(image_b64: str) -> str:
    try:
        from services.caption import generate_caption
        caption = generate_caption(image_b64)
        if caption and len(caption) > 15:
            print(f"[INFO] BLIP caption: {caption}")
            return caption
    except Exception as e:
        print(f"[WARN] BLIP failed: {e}")
    return ""


# def analyze_image(image_b64: str) -> str:
#     result = _analyze_image_with_claude(image_b64)
#     if result:
#         return result
#     result = _analyze_image_with_blip(image_b64)
#     if result:
#         return result
#     return "An interesting scene with compelling subjects and atmosphere."


def _analyze_image_with_groq(image_b64: str) -> str:
    client = _get_groq()
    if not client:
        return ""
    try:
        if "," in image_b64:
            header, data = image_b64.split(",", 1)
            mime = header.split(":")[1].split(";")[0]
        else:
            data = image_b64
            mime = "image/jpeg"

        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime};base64,{data}"
                        }
                    },
                    {
                        "type": "text",
                        "text": (
                            "Analyze this image in 3-4 sentences. "
                            "Be very specific: name the subjects, expressions, poses, "
                            "colors, setting, lighting, and mood. "
                            "This will be used as the basis for a story."
                        )
                    }
                ]
            }]
        )
        result = response.choices[0].message.content.strip()
        print(f"[INFO] Groq vision analysis: {result[:100]}...")
        return result
    except Exception as e:
        print(f"[WARN] Groq vision failed: {e}")
        return ""


def analyze_image(image_b64: str) -> str:
    # 1. Try Groq vision first (free + good)
    result = _analyze_image_with_groq(image_b64)
    if result:
        return result
    # 2. Try Claude (paid)
    result = _analyze_image_with_claude(image_b64)
    if result:
        return result
    # 3. BLIP fallback
    result = _analyze_image_with_blip(image_b64)
    if result:
        return result
    return "An interesting scene with compelling subjects and atmosphere."


# ── Theme definitions ──────────────────────────────────────────────────────

THEME_CONFIG = {
    "Adventure": {
        "guidance": "an action-driven adventure with exploration, danger, and discovery",
        "tone": "exciting and fast-paced, full of movement and tension",
        "elements": "a journey or quest, obstacles to overcome, a moment of bravery",
    },
    "Horror": {
        "guidance": "a slow-burn horror that builds dread through atmosphere",
        "tone": "unsettling and eerie, with growing unease",
        "elements": "something that seems ordinary but feels wrong, creeping dread, an unexpected dark twist",
    },
    "Fantasy": {
        "guidance": "a magical fantasy where the ordinary becomes mythic",
        "tone": "wondrous and imaginative, rich with magic and ancient mystery",
        "elements": "a magical element tied to what is visible, a sense of wonder, an ancient or mystical force",
    },
    "Sci-Fi": {
        "guidance": "a science fiction story reimagining the scene in a futuristic world",
        "tone": "speculative and thought-provoking, with a sense of technological wonder or danger",
        "elements": "futuristic technology, an alien or cosmic context, a twist on reality",
    },
    "Emotional": {
        "guidance": "a quiet, emotionally resonant story grounded in human feeling",
        "tone": "warm, tender, and deeply human",
        "elements": "a memory or longing, a relationship between characters, a small moment that carries great weight",
    },
    "Mystery": {
        "guidance": "a gripping mystery where nothing is what it seems",
        "tone": "tense and curious, with clues hiding in plain sight",
        "elements": "a puzzle or secret tied to the scene, a detective or curious observer, a surprising reveal at the end",
    },
    "Romance": {
        "guidance": "a heartfelt romance story full of feeling and connection",
        "tone": "warm, longing, and emotionally charged",
        "elements": "two souls drawn together, an unspoken feeling, a moment that changes everything",
    },
    "Comedy": {
        "guidance": "a lighthearted and funny story with witty observations",
        "tone": "playful, humorous, and warm",
        "elements": "an absurd situation, comic misunderstanding, a funny but heartwarming ending",
    },
    "Thriller": {
        "guidance": "a high-stakes thriller with tension and danger",
        "tone": "gripping and intense, with a sense of urgency",
        "elements": "a race against time, a dangerous secret, a shocking twist",
    },
    "Historical": {
        "guidance": "a historical story set in a rich past era inspired by the scene",
        "tone": "vivid and immersive, grounded in a specific time and place",
        "elements": "period-accurate details, a character facing the challenges of their era, a timeless human truth",
    },
}

THEME_OPENINGS = {
    "Adventure": "The map had ended three days ago. Now there was only this.",
    "Horror":    "No one had heard from the photographer since that night.",
    "Fantasy":   "The old ones called this place the edge of the known world.",
    "Sci-Fi":    "The scanner flagged the anomaly at 04:17 ship time.",
    "Emotional": "Some places hold your breath long after you have left them.",
    "Mystery":   "The answer had been there all along — hiding in plain sight.",
    "Romance":   "She almost walked past him. Almost.",
    "Comedy":    "In hindsight, none of it should have gone this badly.",
    "Thriller":  "He had exactly four minutes before everything fell apart.",
    "Historical":"The year was different then, and so were the people in it.",
}


def _fallback_description(scene: str) -> str:
    return (
        f"{scene.rstrip('.')}. "
        "The light gives the scene a quiet intensity — as if the moment has been held carefully, "
        "just long enough for someone to notice."
    )


def _fallback_story(scene: str, theme: str, word_count: int) -> str:
    opening = THEME_OPENINGS.get(theme, "This is where the story begins.")
    body = (
        f"{opening}\n\n"
        f"{scene.rstrip('.')}. It felt like so much more than what the eye could see.\n\n"
        "The moment stretched — elastic, impossible to pin down. "
        "And yet, standing there, everything suddenly made perfect sense."
    )
    words = body.split()
    if len(words) > word_count:
        body = " ".join(words[:word_count]).rstrip(",") + "…"
    return body


def generate_caption_from_image(image_b64: str) -> str:
    scene = analyze_image(image_b64)
    if not scene:
        return "A compelling scene with rich visual detail."
    
    # Use Groq to rephrase caption differently each time
    angles = [
        "Describe the main subject in one vivid sentence focusing on their expression.",
        "Describe the scene in one sentence focusing on mood and atmosphere.",
        "Describe what stands out most in one precise vivid sentence.",
        "Describe the lighting and colours of the scene in one sentence.",
        "Describe the energy and emotion of the scene in one sentence.",
    ]
    angle = random.choice(angles)
    
    prompt = (
        f'Scene: "{scene}"\n\n'
        f"{angle} "
        "Be specific, vivid, 15-20 words maximum. "
        "Do not start with 'The image shows' or 'A photo of'."
    )
    result = _groq(prompt, max_tokens=60,
                   system="Write only the single sentence caption. Nothing else.")
    
    if result:
        # Clean up — take only first sentence
        first = result.split(".")[0].strip().strip('"')
        return first.capitalize() + "." if first else scene.split(".")[0].capitalize()
    
    return scene.split(".")[0].strip().capitalize()

def generate_description(caption: str, image_b64: str = None) -> str:
    scene = analyze_image(image_b64) if image_b64 else caption
    prompt = (
        f'Scene: "{scene}"\n\n'
        "Write a vivid, immersive 4-5 sentence description. "
        "Focus on the subjects, their expressions and body language, "
        "colours, lighting, mood and atmosphere. "
        "Present tense. Specific and sensory. No generic filler."
    )
    result = _groq(
        prompt, max_tokens=300,
        system="You are a descriptive writer. Write only the description. No title, no preamble."
    )
    return result if result else _fallback_description(scene)


def generate_story(
    caption: str, description: str, theme: str, word_count: int, image_b64: str = None
) -> str:
    scene = analyze_image(image_b64) if image_b64 else f"{caption}. {description}"
    cfg = THEME_CONFIG.get(theme, THEME_CONFIG["Adventure"])

    # Pick a random narrative angle to force variation on regenerate
    angles = [
        "Focus on the main subject's inner thoughts and feelings.",
        "Tell the story from the perspective of an outside observer.",
        "Begin at the most dramatic moment, then show how it was reached.",
        "Focus on a small detail in the scene that holds a big secret.",
        "Tell it as a memory being recalled by someone years later.",
    ]
    angle = random.choice(angles)

    prompt = f"""Write a creative {theme} story in EXACTLY {word_count} words. Not more, not less.

Context:
Caption: {caption}
Description: {description}
Scene: {scene}

Narrative angle: {angle}

Requirements:
- EXACTLY {word_count} words — count every word carefully before finishing
- Clear beginning, middle, and ending
- Engaging, easy to read, emotionally alive
- Theme: {theme} — {cfg['guidance']}
- Tone: {cfg['tone']}
- Include: {cfg['elements']}
- Third person narrative
- Use specific details from the scene — name actual subjects and colours
- Do NOT mention photos, images, or cameras
- End with a surprising or resonant final line

Write ONLY the story. No title. No word count note. Just the story:"""

    result = _groq(
        prompt,
        max_tokens=max(word_count * 6, 4096),
        system=(
            "You are a precise creative fiction writer. "
            f"You must write EXACTLY {word_count} words — this is a hard requirement. "
            "Count your words. If you go over, cut. If under, expand. "
            "Write only the story — no title, no preamble, no word count at the end."
        )
    )

    # Trim if over
    if result:
        words = result.split()
        if len(words) > word_count + 50:
            result = " ".join(words[:word_count]).rstrip(",") + "."

    # Second pass — expand if too short (under 80%)
    if result and len(result.split()) < word_count * 0.80:
        shortfall = word_count - len(result.split())
        expand_prompt = (
            f"This story is {len(result.split())} words but needs to be {word_count} words. "
            f"Expand it by adding {shortfall} more words through richer dialogue, "
            f"sensory detail, and character thoughts. Return the FULL expanded story only:\n\n{result}"
        )
        expanded = _groq(
            expand_prompt,
            max_tokens=max(word_count * 6, 3000),
            system=f"Return ONLY the expanded story. No title. No preamble. Must be close to {word_count} words."
        )
        if expanded and len(expanded.split()) > len(result.split()):
            result = expanded

    return result if result else _fallback_story(scene, theme, word_count)


def generate_all_at_once(image_b64: str, theme: str, word_count: int) -> dict:
    print(f"[INFO] Analyzing image...")
    scene = analyze_image(image_b64)
    print(f"[INFO] Scene: {scene[:120]}...")

    caption = scene.split(".")[0].strip().capitalize() or "A vivid scene full of life and detail."

    print(f"[INFO] Generating description...")
    desc_prompt = (
        f'Scene: "{scene}"\n\n'
        "Write a vivid, immersive 4-5 sentence description. "
        "Cover the subjects, their expressions and body language, "
        "colours, lighting, mood and atmosphere. "
        "Present tense. Specific and sensory. No filler."
    )
    description = _groq(
        desc_prompt, max_tokens=350,
        system="You are a descriptive writer. Write only the description. No title."
    ) or _fallback_description(scene)

    print(f"[INFO] Generating story...")
    cfg = THEME_CONFIG.get(theme, THEME_CONFIG["Adventure"])

    angles = [
        "Focus on the main subject's inner thoughts and feelings.",
        "Tell the story from the perspective of an outside observer.",
        "Begin at the most dramatic moment, then show how it was reached.",
        "Focus on a small detail in the scene that holds a big secret.",
        "Tell it as a memory being recalled by someone years later.",
    ]
    angle = random.choice(angles)

    story_prompt = f"""Write a creative {theme} story in EXACTLY {word_count} words. Not more, not less.

Context:
Caption: {caption}
Description: {description}
Scene: {scene}

Narrative angle: {angle}

Requirements:
- EXACTLY {word_count} words — count every word carefully
- Clear beginning, middle, and ending
- Engaging, easy to read, emotionally alive
- Theme: {theme} — {cfg['guidance']}
- Tone: {cfg['tone']}
- Include: {cfg['elements']}
- Third person narrative
- Use specific details from the scene — name actual subjects and colours
- Do NOT mention photos, images, or cameras
- End with a surprising or resonant final line

Write ONLY the story. No title. No word count note. Just the story:"""

    story = _groq(
        story_prompt,
        max_tokens=max(word_count * 6, 4096),
        system=(
            "You are a precise creative fiction writer. "
            f"You must write EXACTLY {word_count} words — this is a hard requirement. "
            "Count your words. If you go over, cut. If under, expand. "
            "Write only the story — no title, no preamble, no word count at the end."
        )
    ) or _fallback_story(scene, theme, word_count)

    # Trim if over
 
    if story:
        words = story.split()
        if len(words) > word_count + 50:
            story = " ".join(words[:word_count]).rstrip(",") + "."

    # Second pass — expand if too short (under 80%)
    if story and len(story.split()) < word_count * 0.80:
        shortfall = word_count - len(story.split())
        print(f"[INFO] Story too short ({len(story.split())} words), expanding by {shortfall}...")
        expand_prompt = (
            f"This story is {len(story.split())} words but needs to be {word_count} words. "
            f"Expand it by adding {shortfall} more words through richer dialogue, "
            f"sensory detail, inner thoughts, and scene descriptions. "
            f"Return the FULL expanded story only:\n\n{story}"
        )
        expanded = _groq(
            expand_prompt,
            max_tokens=max(word_count * 6, 4096),
            system=(
                f"Return ONLY the full expanded story. No title. No preamble. No word count note. "
                f"Target is {word_count} words — keep writing until you reach it."
            )
        )
        if expanded and len(expanded.split()) > len(story.split()):
            story = expanded
            print(f"[INFO] After expansion: {len(story.split())} words")

    # Third pass — if still short, try once more
    if story and len(story.split()) < word_count * 0.70:
        shortfall = word_count - len(story.split())
        print(f"[INFO] Still short ({len(story.split())} words), third pass...")
        expand_prompt2 = (
            f"Continue and expand this {theme} story by adding {shortfall} more words. "
            f"Add new scenes, dialogue, and details. "
            f"Return the complete story:\n\n{story}"
        )
        expanded2 = _groq(
            expand_prompt2,
            max_tokens=max(word_count * 3, 1000),
            system=f"Return the COMPLETE expanded story. Target: {word_count} words total."
        )
        if expanded2 and len(expanded2.split()) > len(story.split()):
            story = expanded2

    print(f"[INFO] Done. Final story words: {len(story.split())}")
    return {"caption": caption, "description": description, "story": story}