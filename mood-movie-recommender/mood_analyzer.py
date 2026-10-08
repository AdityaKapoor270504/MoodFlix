"""LLM call 1: free-text mood -> structured MoodProfile."""
import json

from llm_client import LLMClient
from models import MoodProfile


class MoodAnalyzer:
    def __init__(self, llm: LLMClient, cfg: dict, prompts: dict):
        self.llm = llm
        self.vocab = cfg["vocab"]
        self.temperature = cfg["llm"]["temperature_mood"]
        self.system = self._build_system(prompts["mood_analysis"])
        self._cache: dict[str, MoodProfile] = {}  # same text -> no repeat API call

    def _build_system(self, p: dict) -> str:
        examples = "\n".join(
            f'Input: "{e["input"]}"\nOutput: {e["output"].strip()}' for e in p["examples"]
        )
        return (
            p["system"]
            .replace("{{MOODS}}", ", ".join(self.vocab["moods"]))
            .replace("{{PACING}}", ", ".join(self.vocab["pacing"]))
            .replace("{{EXAMPLES}}", examples)
        )

    def analyze(self, text: str) -> MoodProfile:
        key = text.strip().lower()
        if key in self._cache:
            return self._cache[key]

        profile = self.llm.generate_json(self.system, f'Input: "{text.strip()}"', MoodProfile, self.temperature)

        # Guardrails: keep only known tags/pacing, sane runtime
        profile.desired_mood_tags = [t.lower() for t in profile.desired_mood_tags if t.lower() in self.vocab["moods"]]
        if profile.pacing not in self.vocab["pacing"]:
            profile.pacing = "any"
        profile.max_runtime_minutes = max(0, profile.max_runtime_minutes)

        self._cache[key] = profile
        return profile

    @staticmethod
    def to_json(profile: MoodProfile) -> str:
        return json.dumps(profile.model_dump(), ensure_ascii=False)
