"""Dataset filtering (grounding) + LLM call 2: rerank and explain."""
import pandas as pd

from llm_client import LLMClient
from mood_analyzer import MoodAnalyzer
from models import MoodProfile, Recommendation, RerankResult


def load_movies(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["runtime"] = df["runtime"].astype(int)
    return df


def _split(value: str) -> set[str]:
    return {x.strip().lower() for x in str(value).split("|") if x.strip()}


def filter_candidates(df: pd.DataFrame, profile: MoodProfile, pool_size: int, exclude_titles=()) -> pd.DataFrame:
    """Score real movies against the mood profile and return the top `pool_size`."""
    work = df[~df["title"].str.lower().isin({t.lower() for t in exclude_titles})].copy()

    avoid = {g.lower() for g in profile.avoid_genres}
    if avoid:
        work = work[work["genres"].apply(lambda g: not (_split(g) & avoid))]

    if profile.max_runtime_minutes > 0:
        timed = work[work["runtime"] <= profile.max_runtime_minutes]
        if len(timed) >= pool_size:  # relax the limit if it would leave too few options
            work = timed

    wanted_moods = set(profile.desired_mood_tags)
    wanted_genres = {g.lower() for g in profile.preferred_genres}

    def score(row) -> float:
        s = 3 * len(_split(row["moods"]) & wanted_moods)
        s += 2 * len(_split(row["genres"]) & wanted_genres)
        if profile.pacing != "any" and row["pacing"] == profile.pacing:
            s += 1.5
        return s + row["rating"] / 10

    work["score"] = work.apply(score, axis=1)
    return work.sort_values("score", ascending=False).head(pool_size)


class Recommender:
    def __init__(self, llm: LLMClient, analyzer: MoodAnalyzer, movies: pd.DataFrame, cfg: dict, prompts: dict):
        self.llm = llm
        self.analyzer = analyzer
        self.movies = movies
        self.pool = cfg["recommendation"]["candidate_pool"]
        self.n = cfg["recommendation"]["num_results"]
        self.temperature = cfg["llm"]["temperature_rerank"]
        self.system = prompts["rerank"]["system"].replace("{{N}}", str(self.n))

    def recommend(self, mood_text: str, exclude_titles=()) -> tuple[MoodProfile, list[dict]]:
        profile = self.analyzer.analyze(mood_text)
        candidates = filter_candidates(self.movies, profile, self.pool, exclude_titles)
        if candidates.empty:
            return profile, []

        result = self.llm.generate_json(
            self.system, self._build_user_prompt(mood_text, profile, candidates), RerankResult, self.temperature
        )
        return profile, self._ground(result.recommendations, candidates)

    @staticmethod
    def _build_user_prompt(mood_text: str, profile: MoodProfile, candidates: pd.DataFrame) -> str:
        lines = [
            f'{i}. {r.title} ({r.year}) | {r.genres} | {r.runtime} min | moods: {r.moods} | {r.overview}'
            for i, r in enumerate(candidates.itertuples(), 1)
        ]
        return (
            f'User said: "{mood_text}"\n'
            f"Understood mood: {profile.summary}\n"
            f"They want to feel: {profile.desired_feeling}\n\n"
            "CANDIDATES:\n" + "\n".join(lines)
        )

    def _ground(self, recs: list[Recommendation], candidates: pd.DataFrame) -> list[dict]:
        """Drop any title not in the candidate list (anti-hallucination) and attach dataset facts."""
        by_title = {r.title.lower(): r for r in candidates.itertuples()}
        out, seen = [], set()
        for rec in recs:
            row = by_title.get(rec.title.strip().lower())
            if row is None or row.title in seen:
                continue
            seen.add(row.title)
            out.append({
                "title": row.title, "year": int(row.year), "genres": row.genres.replace("|", ", "),
                "runtime": int(row.runtime), "rating": float(row.rating),
                "match_score": rec.match_score, "reason": rec.reason,
                "plot": rec.plot.strip() or row.overview, "moods": row.moods.replace("|", ", "),
            })
        if not out:  # LLM returned nothing usable: fall back to the filter ranking
            for row in candidates.head(self.n).itertuples():
                out.append({
                    "title": row.title, "year": int(row.year), "genres": row.genres.replace("|", ", "),
                    "runtime": int(row.runtime), "rating": float(row.rating),
                    "match_score": 5, "reason": "Closest match to your mood based on genre and tone.",
                    "plot": row.overview, "moods": row.moods.replace("|", ", "),
                })
        return out[: self.n]
