from dotenv import load_dotenv
load_dotenv()
from services.story import generate_all_at_once

result = generate_all_at_once("fake", "Adventure", 100)
print("Caption:", result.get("caption", ""))
print("Description:", result.get("description", "")[:80])
print("Story:", result.get("story", "")[:80])