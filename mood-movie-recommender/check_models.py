"""Run:  py check_models.py
Lists the models your API key can use and tests each 'flash' model with a tiny request,
so you know exactly which names to put in config.yaml."""
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
if not key:
    raise SystemExit("GEMINI_API_KEY not found. Check your .env file.")

client = genai.Client(api_key=key)
names = []
for m in client.models.list():
    name = m.name.replace("models/", "")
    actions = getattr(m, "supported_actions", None) or []
    if "generateContent" in actions and "flash" in name and "image" not in name and "tts" not in name:
        names.append(name)

print(f"Found {len(names)} flash models. Testing each...\n")
working = []
for name in names:
    try:
        r = client.models.generate_content(model=name, contents="Reply with the word OK")
        print(f"  WORKS   {name}")
        working.append(name)
    except Exception as e:
        print(f"  FAILED  {name}  ->  {str(e)[:90]}")

print("\nPut these in config.yaml (first one as 'model', the rest under 'fallback_models'):")
print("\n".join(f"  {n}" for n in working) or "  (none worked right now - wait a few minutes and run again)")
