"""Poster lookup. No extra dependencies (standard library only).

1. TMDB (best quality) if TMDB_API_KEY is set in .env  (free key: themoviedb.org/settings/api)
2. Otherwise Wikipedia's page image for the film (no key needed)
3. Otherwise None, and the UI shows a styled placeholder.
Successful lookups are cached in memory.
"""
import json
import os
import urllib.parse
import urllib.request

from dotenv import load_dotenv

load_dotenv()
_UA = {"User-Agent": "MoodMovieRecommender/1.0 (student NLP project)"}
_cache: dict[tuple[str, int], str] = {}


def _get_json(url: str, timeout: float = 6.0) -> dict:
    with urllib.request.urlopen(urllib.request.Request(url, headers=_UA), timeout=timeout) as resp:
        return json.load(resp)


def _from_tmdb(title: str, year: int) -> str | None:
    key = os.getenv("TMDB_API_KEY")
    if not key:
        return None
    query = urllib.parse.urlencode({"api_key": key, "query": title, "year": year})
    for hit in _get_json(f"https://api.themoviedb.org/3/search/movie?{query}").get("results", []):
        if hit.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500" + hit["poster_path"]
    return None


def _from_wikipedia(title: str, year: int) -> str | None:
    for candidate in (f"{title} ({year} film)", f"{title} (film)", title):
        slug = urllib.parse.quote(candidate.replace(" ", "_"), safe="")
        try:
            data = _get_json(f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}")
        except Exception:
            continue
        text = (data.get("description", "") + " " + data.get("extract", "")[:300]).lower()
        thumb = (data.get("thumbnail") or {}).get("source")
        if thumb and "film" in text:
            return thumb
    return None


def get_poster(title: str, year: int) -> str | None:
    key = (title, year)
    if key in _cache:
        return _cache[key]
    for source in (_from_tmdb, _from_wikipedia):
        try:
            url = source(title, year)
        except Exception:
            url = None
        if url:
            _cache[key] = url
            return url
    return None
