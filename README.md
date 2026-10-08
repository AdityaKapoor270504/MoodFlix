Tell MoodFlix how you feel in your own words, in English or Hinglish, and it recommends movies with posters, a personal "why this fits you" explanation, and a spoiler-free plot summary.

"yaar bore ho raha hai, kuch hatke dekhna hai, 2 ghante se kam" → five real movies under two hours, each explained for that mood.

Features
Free-text mood understanding: informal and code-mixed (Hinglish) input, no dropdowns required.
Mood goal, not just mood: the LLM extracts what you feel and what you want to feel (cheer up vs. let it out).
Grounded recommendations: the LLM only ranks real movies from a dataset, and every returned title is re-checked in code, so there are no invented movies.
Spoiler-free plots: a premise-only, two-sentence summary for each movie.
Posters: fetched from TMDB (optional key) or Wikipedia, with a styled placeholder fallback.
Interactive UI: one-click mood buttons, "Surprise me", quick refine buttons (faster, lighter, shorter, ...), and a watchlist.
Reliable LLM layer: JSON mode, Pydantic validation, retry with error feedback, exponential backoff, and automatic fallback to backup models.
How it works
top 12 real candidates
'too slow', 'lighter'...
User mood text
LLM call 1: Mood Analyzertext → structuredMoodProfile JSON
Dataset filter + scoringdata/movies.csv
LLM call 2: Rerankerpick 5, explain, spoiler-freeplot
Grounding checkdrop any title not in thecandidates
Poster lookup (TMDB /Wikipedia)
Streamlit cards
Mood Analyzer (mood_analyzer.py): Gemini converts free text into emotions, desired feeling, mood tags, preferred/avoided genres, pacing, and a runtime limit.
Filtering (recommender.py): real movies are scored against that profile (mood-tag overlap, genre overlap, pacing match, rating).
Reranker (recommender.py): Gemini chooses the best five from the candidates, explains each choice, and writes a spoiler-free plot.
Grounding: titles not present in the candidate list are dropped.
Feedback loop: refine requests are appended to the original mood, and movies already shown are excluded.
Project structure
mood-movie-recommender/
├── app.py               # Streamlit UI
├── ui.py                # CSS, quick-pick text, HTML for movie cards
├── cli.py               # Command-line interface
├── pipeline.py          # Builds the full pipeline
├── llm_client.py        # Gemini API wrapper (JSON mode, retries, fallback models)
├── mood_analyzer.py     # LLM call 1: text → MoodProfile
├── recommender.py       # Filtering/scoring + LLM call 2 + grounding
├── posters.py           # Poster lookup (TMDB or Wikipedia)
├── models.py            # Pydantic schemas
├── config_loader.py     # Loads YAML files
├── check_models.py      # Shows which Gemini models your API key can use
├── prompts.yaml         # All prompts (rules, few-shot examples, JSON shapes)
├── config.yaml          # Model, fallbacks, temperatures, retries, vocabulary
├── data/
│   ├── movies.csv       # Sample dataset (50 films)
│   └── build_dataset.py # Regenerates movies.csv
├── tests/               # Offline unit tests (LLM is mocked)
├── .streamlit/config.toml
├── .env.example
└── requirements.txt
Setup

Requirements: Python 3.10 or newer and a free Gemini API key.

Get a Gemini API key at https://aistudio.google.com/apikey (free tier, no credit card needed).
Clone and install
bash
   git clone https://github.com/<your-username>/mood-movie-recommender.git
   cd mood-movie-recommender
   python -m venv .venv

Activate the environment:

OS	Command
Windows (PowerShell / CMD)	.venv\Scripts\activate
macOS / Linux	source .venv/bin/activate
bash
   pip install -r requirements.txt
Add your key
bash
   cp .env.example .env        # Windows: copy .env.example .env

Open .env and set:

   GEMINI_API_KEY=your_key_here
   TMDB_API_KEY=               # optional, for better posters

If pip or python is not recognized on Windows, use py -m pip ... and py -m streamlit ... instead.

Run
bash
streamlit run app.py     # web UI at http://localhost:8501
python cli.py            # terminal version
pytest                   # unit tests (no API key needed)
Configuration

Everything tunable lives in config.yaml; prompts live in prompts.yaml. No code changes needed.

Setting	Purpose
llm.model	Main Gemini model
llm.fallback_models	Backups tried in order if the main model is busy (503) or unavailable (404)
llm.temperature_mood / temperature_rerank	Low for consistent extraction, higher for natural explanations
llm.max_retries, retry_backoff_seconds	Retry behavior
recommendation.candidate_pool / num_results	Movies sent to the reranker / shown to the user
vocab.moods, vocab.pacing	Controlled vocabulary shared by dataset, prompt, and filter

Gemini model names change over time. Run python check_models.py to list and test the models your key can use, then update llm.model and llm.fallback_models.

The tests use a fake LLM, so they run offline and need no API key. They cover filtering and scoring, title exclusion, dropping of hallucinated titles, plot fallback, and HTML escaping.

Troubleshooting
Problem	Fix
GEMINI_API_KEY is missing	Create .env (not .env.example) in the project root and restart the app
404 NOT_FOUND for a model	The model name is retired for your key. Run python check_models.py and update config.yaml
503 UNAVAILABLE	The model is overloaded. Wait a minute, or add more fallback_models
429 RESOURCE_EXHAUSTED	Free-tier rate limit reached. Wait a few minutes
ModuleNotFoundError	Activate the virtual environment and run pip install -r requirements.txt
ScannerError in config.yaml	YAML needs spaces, not tabs, and a space after each colon
Missing posters	Wikipedia has no image for that film. Add a free TMDB_API_KEY to .env
Limitations
The sample dataset has only 50 films, and the mood tags were assigned by hand. Ratings are approximate.
Plot summaries come from the LLM's knowledge and the dataset overview. The prompt discourages spoilers, but it is not a guarantee, so review output before relying on it.
The free Gemini API tier has rate limits, and prompts may be used by Google to improve its products. Avoid entering personal information.
Future work
Larger dataset (TMDB or Kaggle) with LLM-generated mood tags
Embedding-based semantic retrieval before reranking
"Watch with friends" mode that merges two people's moods
Streaming-availability filters

Tech stack
Python, Google Gemini API (google-genai), Streamlit, Pydantic, pandas, PyYAML, python-dotenv, pytest.
