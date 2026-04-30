"""
Home.py — NATURE-DEMO Decision Support Tool — Landing Page
Professional redesign with:
  - NATURE-DEMO logo in header
  - Single CTA: "Open the Decision Support Tool" → General DST (entry point)
  - Documentation links for BOTH: DST and Climate Visualisation
  - Sidebar removed everywhere
"""
import streamlit as st

# ── URLs ──────────────────────────────────────────────────────────────────────
LOGO_URL        = "https://raw.githubusercontent.com/NATURE-DEMO/Decision_Support_Tool/main/images/main_logo.png"
DST_URL         = "https://1-general-dst.streamlit.app"          # General DST entry point
DST_DOCS_URL    = "https://github.com/NATURE-DEMO/Decision_Support_Tool"
CLIMA_TOOL_URL  = "https://naturedemo-clima-ind.dic-cloudmate.eu"
CLIMA_DOCS_URL  = "https://nature-demo.github.io/clima-data/indicators/"
EU_GRANT        = "101157448"

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "NATURE-DEMO Decision Support Tool",
    page_icon  = "🌿",
    layout     = "wide",
    initial_sidebar_state = "collapsed",
)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background: #f7f8fa !important;
}}
.block-container {{
    padding-top: 0 !important;
    max-width: 1100px;
}}

/* ── Hide sidebar completely ── */
[data-testid="stSidebar"],
[data-testid="collapsedControl"] {{
    display: none !important;
}}

/* ── Header bar ── */
.nd-header {{
    background: #1b3a2d;
    padding: 14px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 0 -4rem 2rem -4rem;
}}
.nd-header-right {{
    font-size: 0.78em;
    color: #b7d5c4;
    text-align: right;
    line-height: 1.5;
}}
.nd-header-right a {{
    color: #d4edde !important;
    text-decoration: none;
}}
.nd-header-right a:hover {{ text-decoration: underline; }}

/* ── Hero card ── */
.hero-card {{
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #e2e8e4;
    border-top: 4px solid #2d6a4f;
    padding: 3rem 2.5rem;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,.05);
}}
.hero-title {{
    font-size: 2.1rem;
    font-weight: 700;
    color: #111;
    margin: 0 0 0.15rem;
    line-height: 1.2;
}}
.hero-title span {{ color: #2d6a4f; }}
.hero-sub {{
    color: #555;
    font-size: 1rem;
    max-width: 700px;
    margin: 0.5rem auto 1.8rem;
    line-height: 1.6;
}}
.cta-btn {{
    display: inline-block;
    background: #1b3a2d;
    color: #fff !important;
    padding: 14px 36px;
    border-radius: 8px;
    text-decoration: none !important;
    font-weight: 600;
    font-size: 1.05em;
    letter-spacing: 0.01em;
    transition: background .2s;
}}
.cta-btn:hover {{ background: #2d6a4f; }}
.cta-docs-row {{
    margin-top: 1.1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
}}
.cta-docs-row a {{
    color: #2d6a4f !important;
    font-size: 0.9em;
    text-decoration: none;
    font-weight: 500;
}}
.cta-docs-row a:hover {{ text-decoration: underline; }}
.cta-docs-sep {{ color: #ccc; font-size: 0.9em; }}

/* ── Stat grid ── */
.stat-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 1.5rem;
}}
.stat-card {{
    background: #fff;
    border: 1px solid #e2e8e4;
    border-radius: 12px;
    padding: 1.2rem 0.8rem;
    text-align: center;
    box-shadow: 0 1px 6px rgba(0,0,0,.04);
}}
.stat-num  {{ font-size: 2rem; font-weight: 700; color: #1b3a2d; margin: 0; }}
.stat-lbl  {{ font-size: 0.78rem; color: #666; margin: 2px 0 0; line-height: 1.3; }}

/* ── Content cards ── */
.content-card {{
    background: #ffffff;
    border: 1px solid #e2e8e4;
    border-radius: 14px;
    padding: 2rem 2.2rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 1px 8px rgba(0,0,0,.04);
}}
.card-title {{
    font-size: 1.25rem;
    font-weight: 700;
    color: #111;
    margin: 0 0 0.7rem;
}}
.card-body {{
    color: #444;
    font-size: 0.93rem;
    line-height: 1.7;
    margin: 0 0 1rem;
}}
.card-link {{
    color: #2d6a4f !important;
    font-weight: 600;
    text-decoration: none;
    font-size: 0.92rem;
}}
.card-link:hover {{ text-decoration: underline; }}

/* ── Climate companion card ── */
.clima-card {{
    background: #f0f7f2;
    border: 1px solid #b7d5c4;
    border-left: 4px solid #2d6a4f;
    border-radius: 14px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.2rem;
}}
.doc-chip {{
    display: inline-block;
    background: #fff;
    border: 1px solid #b7d5c4;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.84em;
    font-weight: 500;
    color: #2d6a4f !important;
    text-decoration: none !important;
    margin-right: 8px;
    margin-top: 8px;
    transition: background .15s;
}}
.doc-chip:hover {{ background: #e0f0e8; }}

/* ── EU footer ── */
.eu-footer {{
    text-align: center;
    color: #999;
    font-size: 0.77em;
    border-top: 1px solid #e0e0e0;
    padding: 1.2rem 0 0.5rem;
    margin-top: 1rem;
    line-height: 1.6;
}}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# HEADER BAR with logo
# ════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="nd-header">
    <a href="https://www.nature-demo.eu" target="_blank">
        <img src="{LOGO_URL}"
             style="height:44px; object-fit:contain;"
             alt="NATURE-DEMO">
    </a>
    <div class="nd-header-right">
        Horizon Europe · Grant No. {EU_GRANT}<br>
        <a href="https://www.nature-demo.eu" target="_blank">www.nature-demo.eu</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero-card">
    <p class="hero-title">Nature-Based Solutions for<br>
        <span>Climate-Resilient Infrastructure</span>
    </p>
    <p class="hero-sub">
        A Horizon Europe decision support platform for climate risk assessment
        and Nature-Based Solution recommendation across European infrastructure.
    </p>
    <a class="cta-btn" href="{DST_URL}" target="_blank">
        Open the Decision Support Tool &nbsp;→
    </a>
    <div class="cta-docs-row">
        <a href="{DST_DOCS_URL}" target="_blank">📖 DST Documentation</a>
        <span class="cta-docs-sep">·</span>
        <a href="{CLIMA_DOCS_URL}" target="_blank">📖 Climate Data Documentation</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# STATS
# ════════════════════════════════════════════════════════════════
stats = [
    ("5",  "Demo sites",        "across Europe"),
    ("12", "Infrastructure",    "categories"),
    ("29", "Natural hazard",    "types"),
    ("23", "EURO-CORDEX",       "climate indices"),
    ("3",  "Assessment",        "levels"),
]
st.markdown('<div class="stat-grid">', unsafe_allow_html=True)
for num, l1, l2 in stats:
    st.markdown(f"""
    <div class="stat-card">
        <p class="stat-num">{num}</p>
        <p class="stat-lbl">{l1}<br>{l2}</p>
    </div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# ABOUT THE DST
# ════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="content-card">
    <p class="card-title">About the Decision Support Tool</p>
    <p class="card-body">
        NATURE-DEMO is a Horizon Europe Innovation Action (Grant No. {EU_GRANT}) that develops and
        validates Nature-Based Solutions for protecting critical infrastructure against natural hazards
        and climate change, with a focus on Alpine and peri-Alpine regions.
    </p>
    <p class="card-body">
        The Decision Support Tool — the primary software deliverable of Work Package 2, Task 2.4
        (University of Rostock) — integrates a multi-level risk assessment framework with EURO-CORDEX
        climate projections. Users can explore pre-configured demonstration sites or run a custom
        assessment for any European location, and receive ranked NbS recommendations under present and
        future climate scenarios.
        Pre-evaluated sites and high-resolution local analysis are available after pre-authorisation
        from NATURE-DEMO. Future upgrades will allow saving your own site's data.
    </p>
    <a class="card-link" href="{DST_DOCS_URL}" target="_blank">
        📖 Full DST documentation and user guide &nbsp;→
    </a>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# CLIMATE COMPANION TOOL
# ════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="clima-card">
    <div style="display:flex; align-items:flex-start; gap:14px;">
        <div style="font-size:1.8rem; line-height:1; padding-top:2px;">🌡️</div>
        <div>
            <p style="font-size:1.05rem; font-weight:700; color:#1b3a2d; margin:0 0 0.5rem;">
                European Climate Data Visualisation
            </p>
            <p style="color:#3a5a4a; font-size:0.92rem; margin:0 0 0.8rem; line-height:1.6;">
                An interactive companion tool — developed by IBM Research — for exploring the
                EURO-CORDEX climate index dataset that underpins the DST's hazard analysis.
                Search any European city or coordinate and visualise historical trends and
                scenario projections (RCP4.5&nbsp;/&nbsp;RCP8.5) for all 23 climate indices to 2100.
            </p>
            <a class="doc-chip" href="{CLIMA_TOOL_URL}" target="_blank">↗ Open tool</a>
            <a class="doc-chip" href="{CLIMA_DOCS_URL}" target="_blank">📖 Documentation</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# EU FOOTER
# ════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="eu-footer">
    Funded by the European Union under Grant Agreement No. {EU_GRANT}.<br>
    Views and opinions expressed are those of the author(s) only and do not necessarily
    reflect those of the European Union or CINEA.
</div>
""", unsafe_allow_html=True)
