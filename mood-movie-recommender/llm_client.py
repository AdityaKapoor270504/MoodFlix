"""Thin wrapper around the Gemini API.

All LLM traffic goes through generate_json(), so swapping providers later
means changing this one file (plus the model name in config.yaml).

Resilience:
- invalid JSON  -> retry on the same model, feeding the error back to it
- 429/5xx       -> retry with exponential backoff, then fall back to the next model
- 404           -> model not available to this key, skip to the next model
- other errors  -> (bad key, bad request) fail immediately with a clear message
"""
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ValidationError

RETRYABLE_CODES = {429, 500, 502, 503, 504}


class LLMError(RuntimeError):
    """Raised when the LLM cannot return a valid response."""


def _strip_fences(text: str) -> str:
    """Remove ```json fences in case the model adds them."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        text = text.rsplit("```", 1)[0]
    return text.strip()


class LLMClient:
    def __init__(self, llm_cfg: dict):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise LLMError("GEMINI_API_KEY is missing. Copy .env.example to .env and add your key.")
        self.client = genai.Client(api_key=api_key)
        self.cfg = llm_cfg
        self.models = [llm_cfg["model"]] + list(llm_cfg.get("fallback_models") or [])
        self.last_errors: dict[str, str] = {}  # model -> last API error code, for clear messages

    def _call_model(self, model: str, system: str, user: str, schema: type[BaseModel], temperature: float):
        """Try one model with retries. Returns the parsed object, or None to signal 'try next model'."""
        prompt = user
        for attempt in range(self.cfg["max_retries"] + 1):
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system,
                        temperature=temperature,
                        max_output_tokens=self.cfg["max_output_tokens"],
                        response_mime_type="application/json",
                    ),
                )
                return schema.model_validate_json(_strip_fences(response.text or ""))
            except (ValidationError, ValueError) as err:
                prompt = (
                    f"{user}\n\nYour previous reply was not valid ({err}). "
                    "Return ONLY valid JSON in the required shape."
                )
            except errors.APIError as err:
                self.last_errors[model] = f"{err.code}"
                if err.code == 404:
                    return None  # model not available for this key
                if err.code not in RETRYABLE_CODES:
                    raise LLMError(f"Gemini API error {err.code}: {err}") from err
                time.sleep(self.cfg["retry_backoff_seconds"] * (2 ** attempt))
        return None

    def generate_json(self, system: str, user: str, schema: type[BaseModel], temperature: float) -> BaseModel:
        """Call the model(s), parse JSON, validate against `schema`."""
        self.last_errors = {}
        for model in self.models:
            result = self._call_model(model, system, user, schema, temperature)
            if result is not None:
                return result
        reasons = ", ".join(f"{m}: {self.last_errors.get(m, 'invalid output')}" for m in self.models)
        raise LLMError(
            f"All models failed ({reasons}). 404 = model not available for your key, "
            "503 = busy. Run 'py check_models.py' to find working model names for config.yaml."
        )
