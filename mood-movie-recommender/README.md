# 🎬 MoodFlix: Mood-Based Movie Recommender (Gemini + Retrieval)

Describe how you feel in plain words (English or Hinglish) and get movie recommendations
with a personal explanation for each. A two-step LLM pipeline understands the *mood and the
desired feeling*, then recommends **only real movies from a dataset**, so there are no
hallucinated titles.

## How it works

```
 user text ──► LLM call 1: Mood Analyzer ──► structured JSON (emotions, desired feeling,
 "yaar bore ho                                 mood tags, genres, pacing, max runtime)
  raha hai..."                                        │
                                                      ▼
                                   Dataset filter + scoring (movies.csv)
                                                      │ top 12 real candidates
                                                      ▼
                         LLM call 2: Reranker ──► top 5 with "why this fits you"
                                                      │
                                                      ▼
                          Grounding check: drop any title not in the candidate list
```

**Key ideas**
- **Mood goal, not just mood:** "sad" can mean *cheer me up* or *let me cry*. The LLM extracts both.
- **Grounded recommendations:** the LLM only reranks real movies, and titles are re-validated in code.
- **Spoiler-free plots:** the reranker prompt asks for a 2-sentence premise-only summary (first act, no twists or endings).
- **Posters:** fetched from TMDB if `TMDB_API_KEY` is set, otherwise from Wikipedia; a placeholder is shown if none is found.
- **Feedback loop:** type "too slow" or "something lighter" and press *Refine*; seen movies are excluded.
- **Reliable structured output:** JSON mode + Pydantic validation + retry with the error fed back to the model.
- **Efficiency:** low temperature for extraction, in-memory caching of repeated inputs, a small candidate pool to keep prompts short.

## Project structure

| File | Purpose |
|---|---|
| `app.py` | Streamlit UI (mood chips, surprise me, refine buttons, watchlist) |
| `ui.py` | CSS, quick-pick text and HTML for movie cards |
| `posters.py` | Poster lookup: TMDB (optional key) or Wikipedia, with placeholder fallback |
| `check_models.py` | Lists which Gemini models your key can use |
| `cli.py` | Command-line interface |
| `pipeline.py` | Builds the full pipeline |
| `llm_client.py` | Gemini API wrapper: JSON mode, retries, backoff, validation |
| `mood_analyzer.py` | LLM call 1 (text → `MoodProfile`) |
| `recommender.py` | Filtering/scoring + LLM call 2 + grounding |
| `models.py` | Pydantic schemas |
| `prompts.yaml` | **All prompts** (system prompts, rules, few-shot examples) |
| `config.yaml` | **Configuration** (model, temperatures, retries, pool size, vocabulary) |
| `data/movies.csv` | Sample dataset (50 films); `data/build_dataset.py` regenerates it |
| `tests/` | Offline unit tests (LLM is mocked) |
| `.env.example` | Template for the API key |

## Setup

```bash
git clone <your-repo-url> && cd mood-movie-recommender
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # then paste your key into .env
```

Get a free key at https://aistudio.google.com/apikey and set `GEMINI_API_KEY` in `.env`.

## Run

```bash
streamlit run app.py     # web UI
python cli.py            # terminal version
pytest                   # tests (no API key needed)
```

## Example

**Input:** `yaar bore ho raha hai, kuch hatke dekhna hai, 2 ghante se kam`

**Step 1 output (abridged):**
```json
{"current_emotions": ["bored"], "desired_feeling": "surprised and engaged",
 "desired_mood_tags": ["mind-bending", "thrilling", "adventurous"],
 "pacing": "fast", "max_runtime_minutes": 120}
```
**Step 2:** five real movies under 120 minutes, each with a 1-2 sentence reason tied to your mood.
(Exact results vary with the model.)

## Configuration

Change the model, temperatures, retries, number of results, or the mood vocabulary in
`config.yaml`. To switch LLM providers, edit only `llm_client.py`.

## Using a bigger dataset

Replace `data/movies.csv` with any file that has the columns
`title, year, genres, runtime, rating, pacing, moods, overview`
(`genres` and `moods` are `|`-separated; `moods` should use the vocabulary in `config.yaml`).

## Limitations / future work
- Sample dataset is small; mood tags were assigned by hand. A TMDB or Kaggle dataset with LLM-generated mood tags would scale this up.
- Ratings in the sample file are approximate.
- Possible extensions: "watch with friends" mode that merges two moods, streaming-availability filters.
