"""Presentation helpers: CSS, quick-pick content, and HTML for a movie card."""
from html import escape

QUICK_MOODS = [
    ("😴 Exhausted", "exhausted after a long day, want something easy and comforting"),
    ("🥳 Hyped", "feeling hyped and energetic, want something fast and fun"),
    ("💔 Heartbroken", "heartbroken, want a film that lets me feel it and let it out"),
    ("🥱 Bored", "bored, want something unusual and gripping"),
    ("😰 Stressed", "stressed out, want to escape and relax"),
    ("🤔 Reflective", "in a thoughtful mood, want something that makes me think"),
]

REFINEMENTS = [
    ("⚡ Faster", "too slow, give me something faster paced"),
    ("🌤️ Lighter", "too heavy, something lighter and funnier"),
    ("🕒 Shorter", "something shorter, under 110 minutes"),
    ("😭 More emotional", "something more emotional"),
    ("🧠 Mind-bending", "something more mind-bending"),
]

SURPRISES = [
    "rainy Sunday, feeling cozy but a little lonely",
    "just aced my exam and want to celebrate",
    "yaar bore ho raha hai, kuch hatke dekhna hai",
    "need a good cry tonight",
    "can't sleep, brain is buzzing, want something clever",
    "friends are coming over, want a crowd-pleaser",
    "Monday blues, need motivation",
]

CSS = """
<style>
.stApp { background: radial-gradient(circle at 20% 0%, #2a1636 0%, #0e1117 45%); }
.hero { text-align:center; padding: 0.5rem 0 1rem; }
.hero h1 { font-size: 3rem; margin: 0; background: linear-gradient(90deg,#ff4b5c,#ffb347);
           -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero p { color:#b8b8c4; font-size:1.1rem; margin-top:.2rem; }
.card { display:flex; gap:1.2rem; flex-wrap:wrap; background:rgba(255,255,255,.05);
        border:1px solid rgba(255,255,255,.10); border-radius:18px; padding:1rem; margin:.9rem 0 .2rem;
        transition: transform .2s, box-shadow .2s; }
.card:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(255,75,92,.25); }
.poster { flex:0 0 170px; }
.poster img { width:170px; border-radius:12px; box-shadow:0 6px 18px rgba(0,0,0,.5); display:block; }
.noposter { width:170px; height:255px; border-radius:12px; display:flex; flex-direction:column;
            align-items:center; justify-content:center; text-align:center; padding:.8rem; color:#fff;
            background: linear-gradient(160deg,#ff4b5c,#7b2ff7); font-weight:700; }
.noposter span { font-size:2.4rem; }
.info { flex:1 1 280px; min-width:0; }
.info h3 { margin:0; font-size:1.5rem; color:#fff; }
.info h3 small { color:#9a9aa8; font-weight:400; }
.meta { color:#b8b8c4; font-size:.9rem; margin:.2rem 0 .5rem; }
.pill { display:inline-block; padding:.15rem .6rem; margin:0 .3rem .3rem 0; border-radius:999px;
        font-size:.78rem; background:rgba(255,75,92,.18); color:#ffb3bb; border:1px solid rgba(255,75,92,.35); }
.pill.mood { background:rgba(123,47,247,.2); color:#cdb4ff; border-color:rgba(123,47,247,.4); }
.bar { height:8px; border-radius:6px; background:rgba(255,255,255,.12); overflow:hidden; width:220px; }
.bar div { height:100%; background:linear-gradient(90deg,#ff4b5c,#ffb347); }
.matchlabel { color:#ffb347; font-size:.85rem; margin:.25rem 0 .6rem; }
.why { color:#f5f5f7; margin:.3rem 0; }
.plot { color:#c9c9d3; font-size:.93rem; margin:.4rem 0 0; }
.plot b { color:#ffb347; }
.stButton > button { border-radius: 999px; }
</style>
"""


def _pills(csv_text: str, extra_class: str = "") -> str:
    items = [p.strip() for p in csv_text.split(",") if p.strip()]
    return "".join(f'<span class="pill {extra_class}">{escape(p)}</span>' for p in items)


def card_html(r: dict) -> str:
    """HTML for one recommendation. All model/dataset text is escaped."""
    title, year = escape(r["title"]), r["year"]
    if r.get("poster"):
        poster = f'<img src="{escape(r["poster"], quote=True)}" alt="Poster of {title}" loading="lazy">'
    else:
        poster = f'<div class="noposter"><span>🎞️</span>{title}</div>'
    score = max(1, min(10, int(r["match_score"])))
    return f"""
<div class="card">
  <div class="poster">{poster}</div>
  <div class="info">
    <h3>{title} <small>({year})</small></h3>
    <div class="meta">{r['runtime']} min &nbsp;•&nbsp; ⭐ {r['rating']}</div>
    <div>{_pills(r['genres'])}{_pills(r.get('moods', ''), 'mood')}</div>
    <div class="bar"><div style="width:{score * 10}%"></div></div>
    <div class="matchlabel">{score}/10 mood match</div>
    <p class="why">💡 {escape(r['reason'])}</p>
    <p class="plot"><b>Plot (no spoilers):</b> {escape(r.get('plot', ''))}</p>
  </div>
</div>"""
