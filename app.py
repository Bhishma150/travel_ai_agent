import json
import re
import streamlit as st
from agent import travel_agent

# ══════════════════════════════════════════════════════════════════════════════
#  THEME  — Luxury Editorial: deep ink + warm gold
# ══════════════════════════════════════════════════════════════════════════════
INK     = "#060D1A"
SURFACE = "#0D1B2A"
CARD    = "#122336"
BORDER  = "#1A3A52"
GOLD    = "#00B4D8"
GOLD_LT = "#90E0EF"
TEXT    = "#E8F4FC"
MUTED   = "#6A90A8"
SUCCESS = "#4CAF82"
WARNING = "#E8924C"
ERROR   = "#E85C4C"
# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def load_cities() -> list[str]:
    cities: set[str] = set()
    for filepath in ["data/flights.json", "data/hotels.json", "data/places.json"]:
        try:
            with open(filepath) as f:
                for item in json.load(f):
                    for key in ("city", "from", "to"):
                        if key in item:
                            cities.add(item[key])
        except Exception:
            pass
    if not cities:
        cities = {
            "Delhi", "Mumbai", "Goa", "Bangalore",
            "Chennai", "Hyderabad", "Kolkata", "Jaipur",
        }
    return sorted(cities)


def _inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*",     r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`",       r"<code>\1</code>", text)
    return text


def md_to_html(md: str) -> str:
    """Convert a Markdown subset to styled HTML for st.markdown rendering."""
    lines = md.split("\n")
    html: list[str] = []
    in_list = in_table = False

    for line in lines:
        # ── Tables ──────────────────────────────────────────────────────
        if "|" in line and line.strip().startswith("|"):
            if not in_table:
                in_table = True
                html.append("<table><tbody>")
                continue
            if re.match(r"^\s*\|[-: |]+\|\s*$", line):
                if html and "<tr><td>" in html[-1]:
                    html[-1] = html[-1].replace("<tr><td>", "<tr><th>").replace("</td></tr>", "</th></tr>")
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            html.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
            continue
        else:
            if in_table:
                html.append("</tbody></table>")
                in_table = False

        # ── Close list if leaving list context ───────────────────────────
        if in_list and not re.match(r"^[-*+] ", line):
            html.append("</ul>")
            in_list = False

        # ── Headings ─────────────────────────────────────────────────────
        if line.startswith("## "):
            html.append(f"<h2>{line[3:].strip()}</h2>"); continue
        if line.startswith("### "):
            html.append(f"<h3>{line[4:].strip()}</h3>"); continue
        if line.startswith("#### "):
            html.append(f"<h4>{line[5:].strip()}</h4>"); continue

        # ── Bullet list items ─────────────────────────────────────────────
        if re.match(r"^[-*+] ", line):
            if not in_list:
                html.append("<ul>")
                in_list = True
            html.append(f"<li>{_inline(line[2:].strip())}</li>")
            continue

        # ── Blank lines & paragraphs ──────────────────────────────────────
        stripped = line.strip()
        if not stripped:
            html.append("<br>")
        else:
            html.append(f"<p>{_inline(stripped)}</p>")

    if in_list:  html.append("</ul>")
    if in_table: html.append("</tbody></table>")

    return "\n".join(html)


# ══════════════════════════════════════════════════════════════════════════════
#  DATA
# ══════════════════════════════════════════════════════════════════════════════
CITIES = load_cities()

PREFERENCES = [
    "🏖️  Beach", "🧗  Adventure", "💎  Luxury", "💸  Budget",
    "👨‍👩‍👧  Family", "🎉  Nightlife", "🏛️  Historical", "🧘  Relaxation",
    "🌿  Nature", "🍜  Food & Culinary", "🛍️  Shopping",
    "🕌  Religious / Spiritual", "🎭  Mixed",
]

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Voyager — AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400&display=swap');

html, body, [data-testid="stAppViewContainer"] {{
    background: {INK} !important;
    color: {TEXT};
    font-family: 'DM Sans', sans-serif;
}}
[data-testid="stHeader"] {{ background: transparent !important; }}
.block-container {{ padding: 2rem 3rem 4rem !important; max-width: 1160px; }}

/* ── Hero ───────────────────────────────────────────────────────────── */
.hero {{
    text-align: center;
    padding: 3.5rem 0 2.5rem;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 2.5rem;
}}
.hero-eyebrow {{
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.32em;
    color: {GOLD};
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}}
.hero-title {{
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(2.6rem, 5.5vw, 4.8rem);
    font-weight: 300;
    line-height: 1.05;
    color: {TEXT};
    margin: 0 0 0.7rem;
}}
.hero-title em {{ font-style: italic; color: {GOLD_LT}; }}
.hero-sub {{ font-size: 0.92rem; color: {MUTED}; font-weight: 300; letter-spacing: 0.04em; }}

/* ── Section label ──────────────────────────────────────────────────── */
.section-label {{
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.28em;
    color: {GOLD};
    text-transform: uppercase;
    margin-bottom: 1.4rem;
    display: block;
}}

/* ── Widget overrides ───────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div,
[data-testid="stDateInput"] input,
[data-testid="stNumberInput"] input {{
    background: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT} !important;
    font-family: 'DM Sans', sans-serif !important;
}}
[data-testid="stSelectbox"] > div > div:focus-within,
[data-testid="stMultiSelect"] > div > div:focus-within,
[data-testid="stNumberInput"] input:focus,
[data-testid="stDateInput"] input:focus {{
    border-color: {GOLD} !important;
    box-shadow: 0 0 0 3px {GOLD}22 !important;
}}
label[data-testid="stWidgetLabel"] > div > p {{
    color: {MUTED} !important;
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.02em;
}}
[data-baseweb="tag"] {{
    background: {GOLD}2A !important;
    border: 1px solid {GOLD}55 !important;
    color: {GOLD_LT} !important;
    border-radius: 6px !important;
    font-size: 0.8rem !important;
}}

/* ── CTA button ─────────────────────────────────────────────────────── */
[data-testid="stFormSubmitButton"] button {{
    background: linear-gradient(135deg, {GOLD} 0%, {GOLD_LT} 100%) !important;
    color: {INK} !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 12px !important;
    height: 52px !important;
    width: 100% !important;
    transition: opacity 0.18s, transform 0.14s !important;
}}
[data-testid="stFormSubmitButton"] button:hover {{
    opacity: 0.86 !important;
    transform: translateY(-1px) !important;
}}

/* ── Budget bar ─────────────────────────────────────────────────────── */
.budget-bar-bg {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    height: 7px;
    overflow: hidden;
    margin-top: 0.35rem;
}}
.budget-bar-fill {{
    height: 100%;
    border-radius: 8px;
    transition: width 0.5s cubic-bezier(.4,0,.2,1);
}}

/* ── Result card ────────────────────────────────────────────────────── */
.result-wrapper {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 2.4rem 2.8rem;
    margin-top: 1.8rem;
    animation: fadeUp 0.45s ease;
}}
.result-wrapper h2 {{
    font-family: 'Cormorant Garamond', serif;
    font-weight: 400;
    font-size: 1.55rem;
    color: {GOLD_LT};
    margin-top: 1.8rem;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid {BORDER};
    padding-bottom: 0.35rem;
}}
.result-wrapper h3 {{
    font-family: 'Cormorant Garamond', serif;
    font-weight: 400;
    font-size: 1.18rem;
    color: {TEXT};
    margin-top: 1rem;
}}
.result-wrapper p, .result-wrapper li {{
    line-height: 1.78;
    color: {TEXT};
    font-size: 0.92rem;
}}
.result-wrapper ul {{ padding-left: 1.3rem; }}
.result-wrapper strong {{ color: {GOLD_LT}; font-weight: 500; }}
.result-wrapper em {{ color: {MUTED}; font-style: italic; }}
.result-wrapper code {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 0.1em 0.4em;
    font-family: 'DM Mono', monospace;
    font-size: 0.82em;
    color: {GOLD_LT};
}}
.result-wrapper table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
    margin: 1rem 0 1.4rem;
}}
.result-wrapper th {{
    background: {CARD};
    color: {GOLD};
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 0.6rem 1rem;
    border: 1px solid {BORDER};
    text-align: left;
}}
.result-wrapper td {{
    padding: 0.55rem 1rem;
    border: 1px solid {BORDER};
    color: {TEXT};
}}
.result-wrapper tr:last-child td {{
    font-weight: 500;
    color: {GOLD_LT};
}}

/* ── Spinner ────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] p {{
    color: {GOLD} !important;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.18em;
}}

@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(14px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <p class="hero-eyebrow">AI-Powered · India Travel Planner</p>
    <h1 class="hero-title">Your next journey,<br><em>crafted by intelligence.</em></h1>
    <p class="hero-sub">Personalised itineraries &nbsp;·&nbsp; Real-time data &nbsp;·&nbsp; ₹ Budget-aware planning</p>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FORM
# ══════════════════════════════════════════════════════════════════════════════
with st.form("planner", border=False):
    st.markdown('<span class="section-label">Trip Details</span>', unsafe_allow_html=True)

    left, right = st.columns([1, 1], gap="large")

    with left:
        source      = st.selectbox("🏠  Departing from", CITIES)
        travel_date = st.date_input("📅  Trip start date")
        days        = st.number_input("🗓️  Duration (days)", min_value=1, max_value=60, value=3, step=1)
        budget      = st.number_input("💰  Total budget (₹)", min_value=1_000, max_value=10_000_000, value=25_000, step=500)

    with right:
        destinations = st.multiselect(
            "✈️  Destinations  (up to 4)",
            [c for c in CITIES if c != source],
            max_selections=4,
            placeholder="Select one or more cities…",
        )
        preference = st.selectbox("🎯  Travel style", PREFERENCES)

        # Live budget health bar
        if destinations:
            min_budget = len(destinations) * days * 3_000
            pct        = min(budget / max(min_budget, 1) * 100, 100)
            healthy    = budget >= min_budget
            bar_grad   = (f"linear-gradient(90deg,{SUCCESS},{SUCCESS}88)"
                          if healthy else
                          f"linear-gradient(90deg,{WARNING},{WARNING}88)")
            status_col = SUCCESS if healthy else WARNING
            status_txt = "✓ Budget looks healthy" if healthy else f"⚠ Suggested minimum: ₹{min_budget:,}"

            st.markdown(f"""
            <div style="font-size:0.77rem;color:{MUTED};margin-top:1.1rem;margin-bottom:0.25rem;">
                Budget coverage
            </div>
            <div class="budget-bar-bg">
                <div class="budget-bar-fill" style="width:{pct:.0f}%;background:{bar_grad};"></div>
            </div>
            <div style="font-size:0.77rem;color:{status_col};margin-top:0.3rem;">{status_txt}</div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    submitted = st.form_submit_button("✈️   Generate My Itinerary")


# ══════════════════════════════════════════════════════════════════════════════
#  VALIDATION + AGENT
# ══════════════════════════════════════════════════════════════════════════════
if submitted:
    if not destinations:
        st.error("Please select at least one destination to continue.")
        st.stop()

    min_budget = len(destinations) * days * 3_000
    if budget < min_budget:
        st.warning(
            f"⚠️  ₹{budget:,} may be tight for {len(destinations)} city/cities "
            f"over {days} days. Suggested minimum: **₹{min_budget:,}**"
        )

    clean_pref = preference.split("  ")[-1]

    query = f"""
Create a detailed travel plan with the following parameters:

Source city: {source}
Destinations: {', '.join(destinations)}
Trip start date: {travel_date.strftime('%d %B %Y')}
Duration: {days} day(s)
Total budget: ₹{budget:,}
Travel style: {clean_pref}

Instructions:
- Use Markdown: ## headings, bullet lists, and a budget table.
- Cover all {days} days in the day-wise itinerary across {len(destinations)} destination(s).
- Recommend specific hotels and top sights from the provided data.
- Keep total response concise, informative, and well-structured.
"""

    with st.spinner("✦  Crafting your personalised itinerary…"):
        try:
            result = travel_agent(query)
        except Exception as exc:
            st.error(f"An error occurred while generating your plan: {exc}")
            st.stop()

    rendered = md_to_html(result)
    st.markdown(f'<div class="result-wrapper">{rendered}</div>', unsafe_allow_html=True)
