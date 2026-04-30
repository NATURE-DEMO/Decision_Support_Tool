"""
Home.py — NATURE-DEMO Decision Support Tool landing page
Updated per Mohamed's instructions:
  - "Open the Decision Support Tool" leads directly to the General DST (renamed)
  - "Integrated DST (signup required)" secondary link REMOVED from landing page
    (that link now lives as the "High Resolution DST" button inside the DST itself)
  - Documentation link kept, updated to remove general/specific terminology
  - Sidebar hidden everywhere
  - Stats, About section, and Climate tool card kept as-is
"""
import streamlit as st

st.set_page_config(
    page_title="NATURE-DEMO Decision Support Tool",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    [data-testid="stSidebar"]       { display: none !important; }
    [data-testid="collapsedControl"]{ display: none !important; }

    /* ── Card styles ── */
    .landing-card {
        background: #ffffff;
        border: 1px solid #e8e8e8;
        border-radius: 12px;
        padding: 2.5rem 2rem;
        margin-bottom: 1.2rem;
    }
    .stat-card {
        background: #f9f9f9;
        border: 1px solid #e8e8e8;
        border-radius: 10px;
        padding: 1.2rem 1rem;
        text-align: center;
    }
    .stat-number { font-size: 2rem; font-weight: 700; color: #1b3a2d; margin: 0; }
    .stat-label  { font-size: 0.82rem; color: #555; margin: 0; line-height: 1.3; }
    .green-card  { background: #f0f7f2; border: 1px solid #b7d5c4; border-radius: 12px; padding: 1.4rem 1.6rem; }

    /* ── Primary CTA button ── */
    .cta-btn a {
        display: inline-block;
        background: #1b3a2d;
        color: #ffffff !important;
        padding: 14px 32px;
        border-radius: 8px;
        text-decoration: none !important;
        font-weight: 600;
        font-size: 1.05em;
        margin-top: 1rem;
        transition: background 0.2s;
    }
    .cta-btn a:hover { background: #2d6a4f; }

    .doc-link a { color: #2d6a4f !important; text-decoration: none; font-size: 0.92em; }
    .doc-link a:hover { text-decoration: underline; }
    </style>
    """,
    unsafe_allow_html=True,
)

DST_URL  = "https://1-general-dst.streamlit.app"
DOCS_URL = "https://github.com/NATURE-DEMO/Decision_Support_Tool"
CLIMA_TOOL_URL  = "https://naturedemo-clima-ind.dic-cloudmate.eu"
CLIMA_DOCS_URL  = "https://nature-demo.github.io/clima-data/indicators/"

st.markdown('<div class="landing-card" style="text-align:center; border-top: 3px solid #2d6a4f;">', unsafe_allow_html=True)

st.markdown(
    """
    <h1 style="font-size:2.2rem; font-weight:700; color:#1a1a1a; margin-bottom:0.3rem;">
        Nature-Based Solutions for
    </h1>
    <h1 style="font-size:2.2rem; font-weight:700; color:#2d6a4f; margin-top:0;">
        Climate-Resilient Infrastructure
    </h1>
    <p style="color:#555; font-size:1em; max-width:780px; margin:0.6rem auto 0;">
        A Horizon Europe decision support platform for climate risk assessment and
        Nature-Based Solution recommendation across European infrastructure.
    </p>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="cta-btn" style="margin-top:1.4rem;">'
    f'<a href="{DST_URL}" target="_blank">Open the Decision Support Tool &nbsp;→</a>'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="doc-link" style="margin-top:0.9rem;">'
    f'<a href="{DOCS_URL}" target="_blank">📖 Read the documentation</a>'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown('</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
stats = [
    ("5",  "Demo sites",          "across Europe"),
    ("12", "Infrastructure",      "categories"),
    ("29", "Natural hazard",      "types"),
    ("23", "EURO-CORDEX",         "climate indices"),
    ("3",  "Assessment",          "levels"),
]
for col, (num, label1, label2) in zip([c1,c2,c3,c4,c5], stats):
    with col:
        st.markdown(
            f'<div class="stat-card">'
            f'<p class="stat-number">{num}</p>'
            f'<p class="stat-label">{label1}<br>{label2}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="landing-card">', unsafe_allow_html=True)
st.markdown(
    """
    <h2 style="font-size:1.5rem; font-weight:700; color:#1a1a1a; margin-bottom:0.8rem;">
        About the Decision Support Tool
    </h2>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    NATURE-DEMO is a Horizon Europe Innovation Action (Grant No. 101157448) that develops and
    validates Nature-Based Solutions for protecting critical infrastructure against natural hazards
    and climate change, with a focus on Alpine and peri-Alpine regions.

    The Decision Support Tool — the primary software deliverable of Work Package 2, Task 2.4
    (University of Rostock) — integrates a multi-level risk assessment framework with EURO-CORDEX
    climate projections. Users can explore pre-configured demonstration sites or run a custom
    assessment for any European location, and receive ranked NbS recommendations under present and
    future climate scenarios.

    Pre-evaluated demonstration sites and high-resolution local analysis are accessible through the
    tool after pre-authorisation from NATURE-DEMO. Future upgrades will allow users to save their
    own site's data directly within the platform.
    """
)
st.markdown(
    f'<a href="{DOCS_URL}" target="_blank" style="color:#2d6a4f; font-weight:500;">'
    f'📖 Full documentation and user guide &nbsp;→</a>',
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="green-card">', unsafe_allow_html=True)
col_icon, col_text = st.columns([1, 11])
with col_icon:
    st.markdown("<div style='font-size:2rem; padding-top:4px;'>🌡️</div>", unsafe_allow_html=True)
with col_text:
    st.markdown(
        """
        <strong style="font-size:1.05rem;">European Climate Data Visualisation</strong>
        <p style="color:#444; margin:0.4rem 0 0.7rem;">
            An interactive companion tool — developed by IBM Research — for exploring the EURO-CORDEX
            climate index dataset that underpins the DST's hazard analysis. Search any European city or
            coordinate and visualise historical trends and scenario projections (RCP4.5 / RCP8.5) for
            all 23 climate indices to 2100.
        </p>
        """,
        unsafe_allow_html=True,
    )
    btn1, btn2 = st.columns([1, 2])
    with btn1:
        st.link_button("↗ Open tool", CLIMA_TOOL_URL)
    with btn2:
        st.markdown(
            f'<div style="padding-top:8px;">'
            f'<a href="{CLIMA_DOCS_URL}" target="_blank" style="color:#2d6a4f; font-size:0.9em;">📖 Documentation</a>'
            f'</div>',
            unsafe_allow_html=True,
        )
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="text-align:center; color:#888; font-size:0.78em; border-top:1px solid #e0e0e0; padding-top:1rem;">
        Funded by the European Union under Grant Agreement No. 101157448.
        Views and opinions expressed are those of the author(s) only and do not necessarily
        reflect those of the European Union or CINEA.
    </div>
    """,
    unsafe_allow_html=True,
)
