"""Loads config.yaml and prompts.yaml once."""
from pathlib import Path
import yaml

ROOT = Path(__file__).parent


def _load(name: str) -> dict:
    with open(ROOT / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_config() -> dict:
    return _load("config.yaml")


def load_prompts() -> dict:
    return _load("prompts.yaml")
