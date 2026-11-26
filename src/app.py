"""Streamlit UI — preference form → grounded restaurant recommendations.

Visual system follows the Stitch export (Nocturne Gastronomy): dark canvas,
editorial serif headings, mint accent, and stacked recommendation cards.
"""

from __future__ import annotations

import html
import json
import logging
import sys
from pathlib import Path

import streamlit as st
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import settings
from src.data.store import RestaurantStore, get_store
from src.models.preferences import PreferenceInput, RecommendationResponse
from src.services.recommender import recommend

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("src.app")

POPULAR_CUISINES = [
    "North Indian",
    "Chinese",
    "South Indian",
    "Fast Food",
    "Biryani",
    "Cafe",
    "Italian",
    "Continental",
    "Desserts",
    "Street Food",
]

BUDGET_OPTIONS = ["Low", "Medium", "High"]

_STAR = (
    '<svg class="rr-star" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 '
    '9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>'
)


def _inject_styles() -> None:
    # Style-only HTML is applied to the app, not rendered as a block.
    st.html(
        """
        <style>
          @import url("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Manrope:wght@400;500;600;700;800&display=swap");

          :root {
            --bg: #050505;
            --surface: #121212;
            --surface-2: #141414;
            --inset: #0e0e0e;
            --border: #2a2a2a;
            --text: #f2f2f2;
            --muted: #a3a3a3;
            --accent: #3dd68c;
            --accent-hover: #32b876;
            --warning: #fbbf24;
            --warning-bg: #241a0d;
            --warning-border: #684514;
            --error: #f87171;
            --error-bg: #241010;
            --error-border: #632020;
          }

          html, body, [data-testid="stAppViewContainer"],
          [data-testid="stHeader"], .stApp {
            background-color: var(--bg) !important;
            color: var(--text);
            font-family: "Manrope", "Segoe UI", sans-serif !important;
          }

          [data-testid="stHeader"],
          [data-testid="stToolbar"],
          [data-testid="stDecoration"],
          footer,
          #MainMenu {
            display: none !important;
          }

          .block-container {
            max-width: 960px;
            padding-top: 2.25rem !important;
            padding-bottom: 3rem !important;
          }

          [data-testid="stMarkdownContainer"] h1,
          [data-testid="stMarkdownContainer"] h2,
          [data-testid="stMarkdownContainer"] h3,
          .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
          .rr-serif {
            font-family: "Fraunces", Georgia, serif !important;
            font-weight: 400 !important;
            letter-spacing: -0.02em;
            color: var(--text) !important;
          }

          p, span, div, input, textarea, select, button, label {
            font-family: "Manrope", "Segoe UI", sans-serif;
          }

          [data-testid="stWidgetLabel"] p,
          [data-testid="stWidgetLabel"] label {
            font-size: 11px !important;
            font-weight: 700 !important;
            letter-spacing: 0.06em !important;
            text-transform: uppercase !important;
            color: var(--muted) !important;
          }

          [data-testid="stForm"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.35rem 1.5rem 1.15rem;
          }

          div[data-baseweb="select"] > div,
          [data-testid="stTextInput"] input {
            background-color: var(--surface-2) !important;
            border: 1px solid var(--border) !important;
            border-radius: 14px !important;
            color: var(--text) !important;
            min-height: 44px !important;
          }

          [data-testid="stTextInput"] input::placeholder {
            color: rgba(163, 163, 163, 0.55) !important;
          }

          div[data-baseweb="select"] > div:focus-within,
          [data-testid="stTextInput"] input:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 1px var(--accent) !important;
          }

          [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
            background: var(--accent) !important;
            border: 2px solid var(--accent) !important;
          }

          [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--inset) !important;
            border: 1px solid rgba(42, 42, 42, 0.9) !important;
            border-radius: 14px !important;
            padding: 0.85rem 0.95rem 0.55rem !important;
          }

          [data-testid="stSegmentedControl"],
          [data-testid="stButtonGroup"] {
            background: var(--surface-2) !important;
            border: 1px solid var(--border) !important;
            border-radius: 14px !important;
            padding: 4px !important;
            width: 100%;
          }

          button[kind^="segmented_control"] {
            background: transparent !important;
            color: var(--muted) !important;
            border: 1px solid transparent !important;
            border-radius: 10px !important;
            min-height: 36px !important;
            box-shadow: none !important;
          }

          button[data-testid="stBaseButton-segmented_controlActive"] {
            background: #242424 !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
          }

          @media (min-width: 760px) {
            [data-testid="stHorizontalBlock"] {
              flex-wrap: nowrap !important;
              gap: 1.1rem !important;
            }
            [data-testid="stColumn"] {
              min-width: 0 !important;
              flex: 1 1 0 !important;
              width: auto !important;
            }
          }

          [data-testid="stFormSubmitButton"] button {
            background: var(--accent) !important;
            color: #050505 !important;
            border: none !important;
            border-radius: 14px !important;
            min-height: 48px !important;
            font-weight: 700 !important;
            letter-spacing: 0.01em;
          }

          [data-testid="stFormSubmitButton"] button:hover {
            background: var(--accent-hover) !important;
            color: #050505 !important;
          }

          [data-testid="stFormSubmitButton"] button p {
            color: #050505 !important;
            font-weight: 700 !important;
          }

          .rr-header { margin-bottom: 1.35rem; }
          .rr-title-row {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
          }
          .rr-title {
            font-family: "Fraunces", Georgia, serif;
            font-weight: 400;
            font-size: 42px;
            line-height: 1.15;
            letter-spacing: -0.02em;
            color: var(--text);
            margin: 0;
          }
          .rr-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            background: var(--surface-2);
            border: 1px solid var(--border);
            color: var(--muted);
            font-size: 11px;
            letter-spacing: 0.02em;
          }
          .rr-dot {
            width: 6px;
            height: 6px;
            border-radius: 999px;
            background: var(--accent);
            display: inline-block;
          }
          .rr-chip strong { color: var(--text); font-weight: 500; }
          .rr-sub {
            margin: 0.7rem 0 0;
            color: var(--muted);
            font-size: 16px;
            line-height: 1.55;
            max-width: 40rem;
          }

          .rr-form-head {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            padding-bottom: 1rem;
            margin-bottom: 0.35rem;
            border-bottom: 1px solid rgba(42, 42, 42, 0.7);
          }
          .rr-form-head h2 {
            font-family: "Fraunces", Georgia, serif;
            font-weight: 400;
            font-size: 24px;
            margin: 0;
            color: var(--text);
          }
          .rr-form-head p {
            margin: 0.2rem 0 0;
            color: var(--muted);
            font-size: 13px;
          }

          .rr-status {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.45rem;
            color: var(--muted);
            font-size: 12px;
            margin: 0.85rem 0 0.25rem;
          }

          .rr-metrics {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 1.25rem 0 0.85rem;
          }
          .rr-metric {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 0.85rem 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.5rem;
          }
          .rr-metric span { color: var(--muted); font-size: 12px; font-weight: 500; }
          .rr-metric strong {
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 15px;
            color: var(--text);
            background: #1a1a1a;
            border: 1px solid rgba(42, 42, 42, 0.9);
            border-radius: 8px;
            padding: 0.1rem 0.45rem;
          }
          .rr-metric strong.rr-mint {
            color: var(--accent);
            background: rgba(61, 214, 140, 0.1);
            border-color: rgba(61, 214, 140, 0.3);
          }

          .rr-banner, .rr-card, .rr-state, .rr-details {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
          }
          .rr-banner {
            display: flex;
            gap: 0.75rem;
            align-items: flex-start;
            padding: 1rem 1.05rem;
            margin-bottom: 0.85rem;
            background: var(--surface-2);
          }
          .rr-banner-icon {
            width: 28px;
            height: 28px;
            border-radius: 8px;
            display: grid;
            place-items: center;
            background: rgba(61, 214, 140, 0.1);
            border: 1px solid rgba(61, 214, 140, 0.2);
            color: var(--accent);
            flex: none;
            font-weight: 700;
          }
          .rr-banner h3, .rr-state h3 {
            margin: 0;
            font-family: "Fraunces", Georgia, serif;
            font-weight: 400;
            font-size: 16px;
            color: var(--text);
          }
          .rr-banner p, .rr-state p { margin: 0.25rem 0 0; color: var(--muted); font-size: 13px; line-height: 1.5; }
          .rr-banner.warn { background: var(--warning-bg); border-color: var(--warning-border); }
          .rr-banner.warn .rr-banner-icon { color: var(--warning); background: transparent; border-color: var(--warning-border); }

          .rr-list { display: flex; flex-direction: column; gap: 0.8rem; }
          .rr-card { padding: 1.15rem 1.35rem 1.05rem; }
          .rr-card-top {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 0.6rem 1rem;
            padding-bottom: 0.7rem;
          }
          .rr-name-wrap { display: flex; align-items: center; gap: 0.7rem; }
          .rr-rank {
            width: 28px;
            height: 28px;
            border-radius: 8px;
            display: grid;
            place-items: center;
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 12px;
            font-weight: 700;
            background: #222;
            color: var(--text);
            border: 1px solid var(--border);
          }
          .rr-rank.first { background: var(--accent); color: #050505; border-color: var(--accent); }
          .rr-name {
            margin: 0;
            font-family: "Fraunces", Georgia, serif;
            font-weight: 400;
            font-size: 24px;
            letter-spacing: -0.01em;
            color: var(--text);
          }
          .rr-meta {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.4rem;
            color: var(--muted);
            font-size: 12px;
          }
          .rr-meta .rr-cuisine { color: var(--text); font-weight: 600; }
          .rr-rating {
            display: inline-flex;
            align-items: center;
            gap: 0.2rem;
            color: var(--accent);
            font-weight: 700;
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
          }
          .rr-star { width: 13px; height: 13px; fill: var(--accent); }
          .rr-fit {
            margin: 0;
            padding-top: 0.75rem;
            border-top: 1px solid rgba(42, 42, 42, 0.7);
            color: var(--muted);
            font-size: 14px;
            line-height: 1.55;
          }
          .rr-fit b {
            color: var(--accent);
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 11px;
            letter-spacing: 0.06em;
            margin-right: 0.35rem;
          }

          .rr-details { margin-top: 0.9rem; overflow: hidden; }
          .rr-details summary {
            list-style: none;
            cursor: pointer;
            padding: 0.95rem 1.15rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: var(--muted);
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
          }
          .rr-details summary::-webkit-details-marker { display: none; }
          .rr-details pre {
            margin: 0;
            padding: 0.9rem 1.15rem 1.1rem;
            border-top: 1px solid rgba(42, 42, 42, 0.7);
            background: #0a0a0a;
            color: #d4d4d4;
            font-size: 12px;
            line-height: 1.5;
            overflow-x: auto;
          }

          .rr-state { padding: 2rem 1.5rem; text-align: center; margin-top: 1rem; }
          .rr-state.left { text-align: left; display: flex; gap: 1rem; align-items: flex-start; }
          .rr-state h3 { font-size: 22px; }
          .rr-state code {
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 12px;
            color: var(--text);
            background: #1c1c1c;
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 0.05rem 0.35rem;
          }
          .rr-icon-circle {
            width: 44px;
            height: 44px;
            border-radius: 999px;
            display: grid;
            place-items: center;
            margin: 0 auto 0.75rem;
            font-size: 18px;
          }
          .rr-icon-circle.spin { color: var(--accent); background: rgba(61, 214, 140, 0.1); border: 1px solid rgba(61, 214, 140, 0.25); }
          .rr-icon-circle.warn { color: var(--warning); background: var(--warning-bg); border: 1px solid var(--warning-border); }
          .rr-icon-box {
            width: 42px;
            height: 42px;
            border-radius: 14px;
            display: grid;
            place-items: center;
            flex: none;
            color: var(--error);
            background: var(--error-bg);
            border: 1px solid var(--error-border);
            font-size: 18px;
          }

          @media (max-width: 720px) {
            .rr-title { font-size: 32px; }
            .rr-metrics { grid-template-columns: 1fr; }
            .rr-name { font-size: 22px; }
            .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
          }
        </style>
        """
    )


def _esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _format_cost(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"₹{value:,.0f} for two"


def _format_rating(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.1f}"


def _friendly_error(exc: BaseException) -> str:
    message = str(exc).strip() or exc.__class__.__name__
    lowered = message.lower()
    if "api key" in lowered or ("groq" in lowered and "missing" in lowered):
        return (
            "Groq API key is missing or invalid. Set GROQ_API_KEY in .env, "
            "or set USE_MOCK_LLM=true for offline demo mode."
        )
    if "dataset" in lowered or "parquet" in lowered or "huggingface" in lowered:
        return (
            "Could not load the restaurant dataset. Check your network, "
            "DATA_CACHE_PATH, or regenerate the local parquet cache."
        )
    return f"Something went wrong: {message}"


def _mode_label() -> str:
    if settings.use_mock_llm:
        return "Mode: <strong>Mock LLM</strong> · offline"
    return f"Mode: <strong>Groq</strong> · {_esc(settings.llm_model)}"


def _render_header() -> None:
    st.html(
        f"""
        <header class="rr-header">
          <div class="rr-title-row">
            <h1 class="rr-title">SPICE AI</h1>
            <div class="rr-chip"><span class="rr-dot"></span><span>{_mode_label()}</span></div>
          </div>
          <p class="rr-sub">Filter real Zomato listings, then let AI rank and explain the best fits.</p>
        </header>
        """
    )


def _render_status(count: int) -> None:
    st.html(
        f"""
        <div class="rr-status">
          <span class="rr-dot"></span>
          <span>Dataset ready · {count:,} restaurants cached.</span>
        </div>
        """
    )


def _state_card(kind: str, title: str, body: str) -> None:
    if kind == "loading":
        icon = '<div class="rr-icon-circle spin">↻</div>'
        extra_class = ""
    elif kind == "empty":
        icon = '<div class="rr-icon-circle warn">!</div>'
        extra_class = ""
    else:
        icon = '<div class="rr-icon-box">!</div>'
        extra_class = " left"
    st.html(
        f"""
        <section class="rr-state{extra_class}">
          {icon}
          <div>
            <h3>{_esc(title)}</h3>
            <p>{body}</p>
          </div>
        </section>
        """
    )


def _render_recommendations(response: RecommendationResponse, prefs: PreferenceInput) -> None:
    meta = response.meta
    result_count = len(response.recommendations)

    if meta.message and not response.recommendations:
        _state_card(
            "empty",
            meta.message,
            "Try a broader location, different cuisine, lower min rating, or another budget.",
        )
        return

    summary = response.summary.strip() if response.summary else ""
    if not summary:
        noun = "spot" if result_count == 1 else "spots"
        summary = (
            f"{result_count} {prefs.cuisine} {noun} in {prefs.location} match a "
            f"{prefs.budget} budget and a {prefs.min_rating:.1f}+ rating."
        )
    detail = "Filtered from the Zomato dataset, then ranked with an explanation for each fit."
    banner_class = "rr-banner"
    if meta.used_fallback:
        banner_class = "rr-banner warn"
        detail = meta.message or "Showing rating-based matches because AI ranking was unavailable."

    cards = []
    for item in response.recommendations:
        rank_class = "rr-rank first" if item.rank == 1 else "rr-rank"
        cards.append(
            f"""
            <article class="rr-card">
              <div class="rr-card-top">
                <div class="rr-name-wrap">
                  <span class="{rank_class}">#{item.rank}</span>
                  <h3 class="rr-name">{_esc(item.name or "Unknown restaurant")}</h3>
                </div>
                <div class="rr-meta">
                  <span class="rr-cuisine">{_esc(item.cuisine or "Cuisine N/A")}</span>
                  <span>·</span>
                  <span class="rr-rating">{_STAR}{_esc(_format_rating(item.rating))}</span>
                  <span>·</span>
                  <span>{_esc(_format_cost(item.estimated_cost))}</span>
                  <span>·</span>
                  <span>{_esc(item.location or "Location N/A")}</span>
                </div>
              </div>
              <p class="rr-fit"><b>AI FIT</b>{_esc(item.explanation or "No explanation available.")}</p>
            </article>
            """
        )

    payload = {
        "filters_applied": meta.filters_applied,
        "candidate_count": meta.candidate_count,
        "hard_match_count": meta.hard_match_count,
        "results": result_count,
        "used_llm": meta.used_llm,
        "used_fallback": meta.used_fallback,
        "llm_provider": meta.llm_provider,
    }
    payload_json = html.escape(json.dumps(payload, indent=2), quote=False)

    st.html(
        f"""
        <section class="rr-metrics">
          <div class="rr-metric"><span>Candidates sent to AI</span><strong>{meta.candidate_count}</strong></div>
          <div class="rr-metric"><span>Hard filter matches</span><strong>{meta.hard_match_count}</strong></div>
          <div class="rr-metric"><span>Results</span><strong class="rr-mint">{result_count}</strong></div>
        </section>
        <section class="{banner_class}">
          <div class="rr-banner-icon">i</div>
          <div>
            <h3>{_esc(summary)}</h3>
            <p>{_esc(detail)}</p>
          </div>
        </section>
        <section class="rr-list">{''.join(cards)}</section>
        <details class="rr-details">
          <summary>Request details</summary>
          <pre>{payload_json}</pre>
        </details>
        """
    )


@st.cache_resource(show_spinner=False)
def load_restaurant_store() -> RestaurantStore:
    return get_store(settings)


def main() -> None:
    st.set_page_config(
        page_title="SPICE AI",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    _inject_styles()
    _render_header()

    try:
        with st.spinner("Loading restaurant data…"):
            store = load_restaurant_store()
    except Exception as exc:  # noqa: BLE001 — surface any load failure to the UI
        logger.exception("Dataset load failed")
        _state_card("error", "Could not load the restaurant dataset.", _esc(_friendly_error(exc)))
        st.stop()

    locations = sorted(store.frame["location"].dropna().astype(str).unique().tolist())
    default_location = "Indiranagar" if "Indiranagar" in locations else locations[0]
    default_top_k = min(10, max(1, settings.top_k))

    with st.form("prefs_form"):
        st.html(
            f"""
            <div class="rr-form-head">
              <div>
                <h2>Your preferences</h2>
                <p>Define your dining filters to query {len(store):,} curated entries.</p>
              </div>
            </div>
            """
        )
        location_col, budget_col = st.columns(2)
        location = location_col.selectbox(
            "Location",
            options=locations,
            index=locations.index(default_location),
        )
        budget_label = budget_col.segmented_control(
            "Budget",
            options=BUDGET_OPTIONS,
            default="Medium",
            selection_mode="single",
        )
        cuisine_col, custom_col = st.columns(2)
        cuisine = cuisine_col.selectbox(
            "Cuisine",
            options=POPULAR_CUISINES,
            index=POPULAR_CUISINES.index("Italian"),
        )
        cuisine_custom = custom_col.text_input(
            "Or type a cuisine",
            placeholder="e.g. Thai",
        )
        rating_col, count_col = st.columns(2)
        with rating_col.container(border=True):
            min_rating = st.slider(
                "Minimum rating",
                min_value=0.0,
                max_value=5.0,
                value=4.0,
                step=0.1,
            )
        with count_col.container(border=True):
            top_k = st.slider(
                "How many recommendations?",
                min_value=1,
                max_value=10,
                value=default_top_k,
            )
        additional_preferences = st.text_input(
            "Additional preferences",
            placeholder="e.g. family-friendly, cafe, outdoor seating",
        )
        submitted = st.form_submit_button(
            "Get recommendations  →",
            type="primary",
            use_container_width=True,
        )

    _render_status(len(store))

    if not submitted:
        return

    chosen_cuisine = cuisine_custom.strip() or cuisine
    budget = (budget_label or "Medium").strip().lower()
    try:
        prefs = PreferenceInput(
            location=location,
            budget=budget,  # type: ignore[arg-type]
            cuisine=chosen_cuisine,
            min_rating=float(min_rating),
            additional_preferences=additional_preferences,
            top_k=int(top_k),
        )
    except ValidationError as exc:
        _state_card(
            "error",
            "Please check your preferences.",
            _esc(str(exc)),
        )
        return

    if not settings.use_mock_llm and not settings.llm_api_key:
        _state_card(
            "error",
            "Groq API key is missing or invalid.",
            "Set <code>GROQ_API_KEY</code> in <code>.env</code>, or set "
            "<code>USE_MOCK_LLM=true</code> for offline demo mode.",
        )
        return

    loading = st.empty()
    with loading.container():
        _state_card(
            "loading",
            "Finding matches and asking the AI to rank them…",
            f"Filtering {len(store):,} restaurant listings against your budget and rating.",
        )
    try:
        response = recommend(prefs, store.frame)
    except Exception as exc:  # noqa: BLE001 — keep demo UI from crashing
        logger.exception("Recommend failed")
        loading.empty()
        _state_card("error", "Something went wrong.", _esc(_friendly_error(exc)))
        return

    loading.empty()
    _render_recommendations(response, prefs)


if __name__ == "__main__":
    main()
