"""Offline tests: no API key needed (LLM is faked)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config_loader import ROOT, load_config, load_prompts
from models import MoodProfile, Recommendation, RerankResult
from recommender import Recommender, filter_candidates, load_movies

CFG = load_config()
MOVIES = load_movies(str(ROOT / "data/movies.csv"))


def test_filter_respects_avoid_and_runtime():
    p = MoodProfile(desired_mood_tags=["tense", "thrilling"], avoid_genres=["Horror"], max_runtime_minutes=140)
    out = filter_candidates(MOVIES, p, pool_size=10)
    assert not any("Horror" in g for g in out["genres"])
    assert (out["runtime"] <= 140).all()


def test_filter_prefers_matching_moods():
    p = MoodProfile(desired_mood_tags=["inspiring", "energetic"], preferred_genres=["Sport"], pacing="medium")
    top = filter_candidates(MOVIES, p, pool_size=3)["title"].tolist()
    assert any(t in top for t in ["Rocky", "Chak De! India", "Dangal"])


def test_exclude_titles():
    p = MoodProfile(desired_mood_tags=["funny"])
    out = filter_candidates(MOVIES, p, 5, exclude_titles=["Superbad"])
    assert "Superbad" not in out["title"].tolist()


class FakeLLM:
    def generate_json(self, system, user, schema, temperature):
        return RerankResult(recommendations=[
            Recommendation(title="Totally Made Up Movie", match_score=9, reason="hallucinated"),
            Recommendation(title="superbad", match_score=8, reason="real, different casing"),
        ])


class FakeAnalyzer:
    def analyze(self, text):
        return MoodProfile(desired_mood_tags=["funny", "energetic"], preferred_genres=["Comedy"])


def test_hallucinated_titles_are_dropped():
    rec = Recommender(FakeLLM(), FakeAnalyzer(), MOVIES, CFG, load_prompts())
    _, results = rec.recommend("anything")
    titles = [r["title"] for r in results]
    assert "Totally Made Up Movie" not in titles
    assert "Superbad" in titles


def test_card_html_escapes_and_handles_missing_poster():
    from ui import card_html
    r = {"title": "A <b>Movie</b>", "year": 2020, "genres": "Drama, Comedy", "moods": "funny",
         "runtime": 100, "rating": 7.5, "match_score": 12, "reason": "<script>x</script>",
         "plot": "Setup only.", "poster": None}
    html = card_html(r)
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "noposter" in html and "Plot (no spoilers)" in html
    assert 'style="width:100%"' in html  # score clamped to 10


def test_plot_passes_through_and_falls_back_to_overview():
    class L:
        def generate_json(self, *a, **k):
            return RerankResult(recommendations=[
                Recommendation(title="Superbad", match_score=8, reason="r", plot="Two teens plan a party."),
                Recommendation(title="The Hangover", match_score=7, reason="r"),
            ])
    rec = Recommender(L(), FakeAnalyzer(), MOVIES, CFG, load_prompts())
    _, res = rec.recommend("x")
    plots = {r["title"]: r["plot"] for r in res}
    assert plots["Superbad"] == "Two teens plan a party."
    assert plots["The Hangover"]  # dataset overview used when LLM gives none
