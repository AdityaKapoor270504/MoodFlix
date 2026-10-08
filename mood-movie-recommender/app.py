"""Streamlit UI:  streamlit run app.py"""
import random
from concurrent.futures import ThreadPoolExecutor

import streamlit as st

from llm_client import LLMError
from pipeline import build_recommender
from posters import get_poster
from ui import CSS, QUICK_MOODS, REFINEMENTS, SURPRISES, card_html

st.set_page_config(page_title="MoodFlix", page_icon="🎬", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)
st.markdown(
    '<div class="hero"><h1>🎬 MoodFlix</h1>'
    "<p>Tell me how you feel, in English or Hinglish, and I'll pick what to watch.</p></div>",
    unsafe_allow_html=True,
)


@st.cache_resource
def get_recommender():
    return build_recommender()


try:
    rec = get_recommender()
except (LLMError, FileNotFoundError) as err:
    st.error(str(err))
    st.stop()

for key, default in dict(mood="", mood_input="", shown=[], results=None, profile=None, watchlist=[]).items():
    st.session_state.setdefault(key, default)


# ---- button callbacks: they only set a "trigger"; the work happens once below ----
def trigger_new(text: str):
    st.session_state.mood_input = text
    st.session_state.trigger = ("new", text)


def trigger_refine(text: str):
    st.session_state.trigger = ("refine", text)


def trigger_surprise():
    trigger_new(random.choice(SURPRISES))


def toggle_watchlist(movie: dict):
    wl = st.session_state.watchlist
    if any(m["title"] == movie["title"] for m in wl):
        st.session_state.watchlist = [m for m in wl if m["title"] != movie["title"]]
    else:
        wl.append(movie)


def attach_posters(results: list[dict]):
    with ThreadPoolExecutor(max_workers=5) as pool:
        urls = list(pool.map(lambda r: get_poster(r["title"], r["year"]), results))
    for r, url in zip(results, urls):
        r["poster"] = url


def run(mood: str):
    with st.spinner("🎞️ Reading your mood and rolling the reel..."):
        try:
            profile, results = rec.recommend(mood, exclude_titles=st.session_state.shown)
            attach_posters(results)
        except LLMError as err:
            st.error(str(err))
            return
    st.session_state.mood, st.session_state.profile, st.session_state.results = mood, profile, results
    st.session_state.shown += [r["title"] for r in results]
    st.toast("Your movies are ready! 🍿")


# ---- handle a pending click (if any) ----
pending = st.session_state.pop("trigger", None)
if pending:
    kind, text = pending
    if not text.strip():
        st.warning("Tell me how you feel first, or tap one of the mood buttons.")
    elif kind == "new":
        st.session_state.shown = []
        run(text.strip())
    else:
        run(f"{st.session_state.mood}. Feedback: {text.strip()}")

# ---- sidebar: watchlist ----
with st.sidebar:
    st.header("❤️ My watchlist")
    if not st.session_state.watchlist:
        st.caption("Tap ❤️ on a movie to save it here.")
    for m in st.session_state.watchlist:
        st.write(f"🎬 **{m['title']}** ({m['year']})")

# ---- input area ----
st.markdown("##### How are you feeling?")
cols = st.columns(len(QUICK_MOODS))
for col, (label, text) in zip(cols, QUICK_MOODS):
    col.button(label, key=f"q_{label}", use_container_width=True, on_click=trigger_new, args=(text,))

st.text_area(
    "Or describe it in your own words",
    key="mood_input",
    height=90,
    placeholder="e.g. exhausted after exams, want something light but not dumb "
                "(or Hinglish: yaar bore ho raha hai, kuch hatke dekhna hai)",
)
b1, b2, _ = st.columns([1, 1, 3])
b1.button("🎯 Find my movies", type="primary", use_container_width=True,
          on_click=lambda: trigger_new(st.session_state.mood_input))
b2.button("🎲 Surprise me", use_container_width=True, on_click=trigger_surprise)

# ---- results ----
if st.session_state.profile:
    st.markdown("---")
    st.success(f"🧠 {st.session_state.profile.summary}")
    with st.expander("See what the AI understood about your mood"):
        st.json(st.session_state.profile.model_dump())

    st.markdown("##### Not quite right? Tweak it:")
    rcols = st.columns(len(REFINEMENTS))
    for col, (label, text) in zip(rcols, REFINEMENTS):
        col.button(label, key=f"r_{label}", use_container_width=True, on_click=trigger_refine, args=(text,))
    c1, c2 = st.columns([4, 1])
    custom = c1.text_input("Or say what to change", key="custom_feedback", label_visibility="collapsed",
                           placeholder="e.g. no sad endings, something with a good soundtrack")
    c2.button("Refine", use_container_width=True, on_click=lambda: trigger_refine(st.session_state.custom_feedback))

if st.session_state.results == []:
    st.info("No more matches for that. Try a different mood or loosen your constraints.")

for r in st.session_state.results or []:
    st.markdown(card_html(r), unsafe_allow_html=True)
    saved = any(m["title"] == r["title"] for m in st.session_state.watchlist)
    st.button("💔 Remove from watchlist" if saved else "❤️ Save to watchlist", key=f"wl_{r['title']}",
              on_click=toggle_watchlist, args=(r,))
