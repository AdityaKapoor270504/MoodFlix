"""Builds the full pipeline once; used by both the CLI and the Streamlit app."""
from config_loader import ROOT, load_config, load_prompts
from llm_client import LLMClient
from mood_analyzer import MoodAnalyzer
from recommender import Recommender, load_movies


def build_recommender() -> Recommender:
    cfg, prompts = load_config(), load_prompts()
    llm = LLMClient(cfg["llm"])
    analyzer = MoodAnalyzer(llm, cfg, prompts)
    movies = load_movies(str(ROOT / cfg["data"]["movies_path"]))
    return Recommender(llm, analyzer, movies, cfg, prompts)
