import streamlit as st

st.set_page_config(
    page_title="NATURE-DEMO — Decision Support Tool",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

LOGO_URL = "https://raw.githubusercontent.com/NATURE-DEMO/Decision_Support_Tool/main/images/main_logo.png"

# ── GLOBAL STYLES ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,300;0,400;0,600;1,300&family=Inter:wght@300;400;500;600&display=swap');

[data-testid="stSidebarNav"]      { display: none; }
[data-testid="stAppViewContainer"]{ background: #f5f7f5; }
[data-testid="stHeader"]          { background: transparent; }
html, body, [class*="css"]        { font-family: 'Inter', sans-serif; }

/* ── HERO ── */
.nd-hero {
    background: #ffffff;
    border: 1px solid #d6e4d6;
    border-top: 4px solid #3a7a3a;
    border-radius: 12px;
    padding: 2.5rem 3rem 2.25rem;
    margin-bottom: 2rem;
    text-align: center;
}
.nd-hero-title {
    font-family: 'Source Serif 4', serif;
    font-size: 2.4rem;
    font-weight: 300;
    color: #1c3c1c;
    letter-spacing: -0.01em;
    margin: 1.25rem 0 0.6rem;
    line-height: 1.25;
}
.nd-hero-title strong {
    font-weight: 600;
    color: #2e6b2e;
}
.nd-hero-sub {
    font-size: 1rem;
    font-weight: 300;
    color: #5a7a5a;
    letter-spacing: 0.02em;
    margin: 0 0 1.75rem;
}
.nd-badges {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
}
.nd-badge {
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #3a7a3a;
    background: #edf5ed;
    border: 1px solid #c4dcc4;
    padding: 0.3rem 0.85rem;
    border-radius: 20px;
}

/* ── KPI BAR ── */
.nd-kpi-row {
    display: flex;
    gap: 1px;
    background: #d6e4d6;
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 2rem;
    border: 1px solid #d6e4d6;
}
.nd-kpi-cell {
    flex: 1;
    background: #ffffff;
    padding: 1.1rem 0.75rem;
    text-align: center;
}
.nd-kpi-num {
    font-family: 'Source Serif 4', serif;
    font-size: 1.9rem;
    font-weight: 600;
    color: #2e6b2e;
    display: block;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.nd-kpi-lbl {
    font-size: 0.68rem;
    font-weight: 400;
    color: #7a9a7a;
    line-height: 1.4;
}

/* ── SECTION LABELS ── */
.nd-eyebrow {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #3a7a3a;
    margin-bottom: 0.4rem;
}
.nd-heading {
    font-family: 'Source Serif 4', serif;
    font-size: 1.65rem;
    font-weight: 400;
    color: #1c3c1c;
    margin: 0 0 1.25rem;
}

/* ── TOOL CARDS ── */
.nd-card {
    background: #ffffff;
    border: 1px solid #d6e4d6;
    border-radius: 12px;
    padding: 1.75rem 1.75rem 1.5rem;
    height: 100%;
    box-shadow: 0 1px 6px rgba(30,60,30,0.05);
    transition: box-shadow 0.2s, transform 0.2s;
}
.nd-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 24px rgba(30,60,30,0.10);
}
.nd-card-tag {
    display: inline-block;
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    background: #edf5ed;
    color: #2e6b2e;
    padding: 0.2rem 0.65rem;
    border-radius: 10px;
    margin-bottom: 0.75rem;
}
.nd-card-title {
    font-family: 'Source Serif 4', serif;
    font-size: 1.35rem;
    font-weight: 600;
    color: #1c3c1c;
    margin: 0 0 0.5rem;
    line-height: 1.3;
}
.nd-card-desc {
    font-size: 0.85rem;
    font-weight: 300;
    color: #4a6a4a;
    line-height: 1.75;
    margin-bottom: 1.25rem;
}
.nd-card-divider {
    border: none;
    border-top: 1px solid #edf5ed;
    margin: 0 0 1rem;
}
.nd-feat-list {
    list-style: none;
    padding: 0;
    margin: 0 0 1.5rem;
}
.nd-feat-list li {
    font-size: 0.8rem;
    color: #3a5a3a;
    padding: 0.28rem 0;
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    line-height: 1.5;
}
.nd-feat-list li::before {
    content: '▸';
    color: #5aaa5a;
    font-size: 0.7rem;
    margin-top: 0.12rem;
    flex-shrink: 0;
}
.nd-btn {
    display: block;
    text-align: center;
    background: #2e6b2e;
    color: #ffffff !important;
    text-decoration: none !important;
    padding: 0.65rem 1.25rem;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 500;
    letter-spacing: 0.03em;
    transition: background 0.18s;
}
.nd-btn:hover {
    background: #1c3c1c;
    color: #c4dcc4 !important;
    text-decoration: none !important;
}
.nd-btn-ghost {
    display: block;
    text-align: center;
    background: transparent;
    color: #2e6b2e !important;
    text-decoration: none !important;
    padding: 0.65rem 1.25rem;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 500;
    letter-spacing: 0.03em;
    border: 1.5px solid #2e6b2e;
    transition: all 0.18s;
}
.nd-btn-ghost:hover {
    background: #edf5ed;
    color: #1c3c1c !important;
    text-decoration: none !important;
}

/* ── ABOUT / WORKFLOW PANELS ── */
.nd-panel {
    background: #ffffff;
    border: 1px solid #d6e4d6;
    border-radius: 12px;
    padding: 1.75rem 2rem;
    box-shadow: 0 1px 6px rgba(30,60,30,0.04);
}
.nd-panel p {
    font-size: 0.87rem;
    font-weight: 300;
    color: #3a5a3a;
    line-height: 1.85;
    margin: 0;
}
.nd-step {
    display: flex;
    gap: 1.1rem;
    padding: 0.9rem 0;
    border-bottom: 1px solid #edf5ed;
}
.nd-step:last-child { border-bottom: none; }
.nd-step-num {
    font-family: 'Source Serif 4', serif;
    font-size: 1.4rem;
    font-weight: 600;
    color: #90c890;
    min-width: 1.6rem;
    line-height: 1;
    margin-top: 0.15rem;
}
.nd-step-title {
    font-size: 0.84rem;
    font-weight: 600;
    color: #1c3c1c;
    margin-bottom: 0.2rem;
}
.nd-step-desc {
    font-size: 0.78rem;
    font-weight: 300;
    color: #6a8a6a;
    line-height: 1.6;
    margin: 0;
}

/* ── FOOTER ── */
.nd-footer {
    background: #1c3c1c;
    border-radius: 10px;
    padding: 1.6rem 2.25rem;
    margin-top: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}
.nd-footer-main {
    font-size: 0.78rem;
    color: rgba(196,220,196,0.75);
    line-height: 1.7;
    font-weight: 300;
}
.nd-footer-main strong {
    color: rgba(196,220,196,0.95);
    font-weight: 500;
}
.nd-footer-eu {
    font-size: 0.7rem;
    color: rgba(196,220,196,0.45);
    text-align: right;
    line-height: 1.6;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] { background: #1c3c1c !important; }
[data-testid="stSidebar"] * { color: #c4dcc4 !important; }
[data-testid="stSidebar"] .stLinkButton > a {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(144,200,120,0.18) !important;
    border-radius: 7px !important;
    color: #c4dcc4 !important;
    font-size: 0.83rem !important;
    transition: background 0.18s !important;
}
[data-testid="stSidebar"] .stLinkButton > a:hover {
    background: rgba(144,200,120,0.14) !important;
}
.nd-sb-rule {
    border: none;
    border-top: 1px solid rgba(144,200,120,0.15);
    margin: 0.9rem 0;
}
.nd-sb-section {
    font-size: 0.62rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    color: rgba(144,200,120,0.45) !important;
    margin: 1rem 0 0.4rem !important;
}
.nd-sb-link {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.65rem 0;
    border-bottom: 1px solid rgba(144,200,120,0.1);
    text-decoration: none !important;
    color: #b4ccb4 !important;
    font-size: 0.82rem;
    font-weight: 400;
    transition: color 0.15s;
}
.nd-sb-link:last-child { border-bottom: none; }
.nd-sb-link:hover { color: #e0f0e0 !important; }
</style>
""", unsafe_allow_html=True)

# ── HERO — logo via st.image (avoids base64-in-HTML rendering issue) ───────────
_, logo_col, _ = st.columns([1, 2, 1])
with logo_col:
    try:
        st.image(LOGO_URL, use_container_width=True)
    except Exception:
        st.empty()

st.markdown("""
<div class="nd-hero">
    <h1 class="nd-hero-title">
        Nature-Based Solutions for<br><strong>Climate-Resilient Infrastructure</strong>
    </h1>
    <p class="nd-hero-sub">
        A digital decision support platform for risk assessment and NbS evaluation across Europe
    </p>
    <div class="nd-badges">
        <span class="nd-badge">Horizon Europe · Grant 101157448</span>
        <span class="nd-badge">Work Package 2 · Task 2.3</span>
        <span class="nd-badge">University of Rostock</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI BAR ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nd-kpi-row">
    <div class="nd-kpi-cell">
        <span class="nd-kpi-num">6</span>
        <span class="nd-kpi-lbl">Demo sites<br>across Europe</span>
    </div>
    <div class="nd-kpi-cell">
        <span class="nd-kpi-num">12</span>
        <span class="nd-kpi-lbl">Infrastructure<br>categories</span>
    </div>
    <div class="nd-kpi-cell">
        <span class="nd-kpi-num">29</span>
        <span class="nd-kpi-lbl">Natural hazard<br>types</span>
    </div>
    <div class="nd-kpi-cell">
        <span class="nd-kpi-num">20</span>
        <span class="nd-kpi-lbl">EURO-CORDEX<br>climate indices</span>
    </div>
    <div class="nd-kpi-cell">
        <span class="nd-kpi-num">3</span>
        <span class="nd-kpi-lbl">Assessment<br>levels</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── TOOLS ─────────────────────────────────────────────────────────────────────
st.markdown('<p class="nd-eyebrow">Platform</p><h2 class="nd-heading">Available Tools</h2>',
            unsafe_allow_html=True)

col_dst, col_clim = st.columns(2, gap="large")

with col_dst:
    st.markdown("""
    <div class="nd-card">
        <span class="nd-card-tag">Primary Platform</span>
        <h3 class="nd-card-title">🌿&nbsp; Decision Support Tool</h3>
        <p class="nd-card-desc">
            An integrated web application for multi-level climate risk assessment and
            Nature-Based Solution recommendation — covering pre-configured demonstration
            sites and free-form analysis for any location across Europe.
        </p>
        <hr class="nd-card-divider">
        <ul class="nd-feat-list">
            <li>Specific Site DST for the 6 NATURE-DEMO demonstration sites with expert consensus</li>
            <li>Custom Site Analysis for any European location via OpenStreetMap extraction</li>
            <li>Three assessment levels: Perceived Risk · Regional Screening · High-Resolution</li>
            <li>Quantitative risk indices (HI, EI, VI, PRI) from EURO-CORDEX climate projections</li>
            <li>NbS ranking engine with SSF, SEI and HIA scoring under RCP4.5 / RCP8.5</li>
            <li>AI-generated interpretation reports via Google Gemini</li>
        </ul>
        <a href="/integrated_dst" class="nd-btn">Launch Decision Support Tool →</a>
    </div>
    """, unsafe_allow_html=True)

with col_clim:
    st.markdown("""
    <div class="nd-card">
        <span class="nd-card-tag">Companion Tool · IBM Research</span>
        <h3 class="nd-card-title">🌡️&nbsp; European Climate Data Visualisation</h3>
        <p class="nd-card-desc">
            An interactive front-end for exploring the EURO-CORDEX climate index dataset
            that underpins the DST's hazard analysis — useful before or alongside a
            full Level 2 assessment.
        </p>
        <hr class="nd-card-divider">
        <ul class="nd-feat-list">
            <li>City- and coordinate-based location search across the EURO-CORDEX EUR-11 domain</li>
            <li>Interactive time-series for all 20 climate indices: historical and projected to 2100</li>
            <li>Scenario comparison with ensemble uncertainty bands (RCP4.5 / RCP8.5)</li>
            <li>Powered by the IBM clima-ind-viz API — same data source as the DST Level 2</li>
        </ul>
        <br>
        <a href="https://naturedemo-clima-ind.dic-cloudmate.eu" target="_blank" class="nd-btn-ghost">
            Open Climate Visualisation ↗
        </a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── ABOUT + WORKFLOW ──────────────────────────────────────────────────────────
col_about, col_flow = st.columns([3, 2], gap="large")

with col_about:
    st.markdown('<p class="nd-eyebrow">Project</p><h2 class="nd-heading">About NATURE-DEMO</h2>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="nd-panel">
        <p>
            NATURE-DEMO (Nature-Based Solutions for Demonstrating Climate-Resilient Critical Infrastructure)
            is a Horizon Europe Innovation Action under Grant Agreement No.&nbsp;101157448. The project
            develops, validates, and deploys a comprehensive framework for assessing and implementing
            Nature-Based Solutions (NbS) that protect critical infrastructure against natural hazards
            and climate change, with a particular focus on the Alpine and peri-Alpine region.
        </p>
        <br>
        <p>
            This Decision Support Tool is the primary software deliverable of Work Package 2, Task 2.3,
            developed by the University of Rostock (UROS). It consolidates the multi-level risk
            assessment framework from T2.1 (IHCantabria / FIHAC) and the EURO-CORDEX climate data
            from T2.2 (IBM Research) into a single operational platform accessible to infrastructure
            managers, climate risk experts, and project partners.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_flow:
    st.markdown('<p class="nd-eyebrow">Getting started</p><h2 class="nd-heading">How It Works</h2>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="nd-panel" style="padding: 1.4rem 1.6rem;">
        <div class="nd-step">
            <span class="nd-step-num">1</span>
            <div>
                <p class="nd-step-title">Authenticate</p>
                <p class="nd-step-desc">Log in or register and request an expert or viewer role pending admin approval.</p>
            </div>
        </div>
        <div class="nd-step">
            <span class="nd-step-num">2</span>
            <div>
                <p class="nd-step-title">Select a mode</p>
                <p class="nd-step-desc">Choose a pre-configured demo site or use the Custom Site Analysis for any European location.</p>
            </div>
        </div>
        <div class="nd-step">
            <span class="nd-step-num">3</span>
            <div>
                <p class="nd-step-title">Define your scope</p>
                <p class="nd-step-desc">Select infrastructure types, draw a polygon, and extract OSM data and EURO-CORDEX indicators.</p>
            </div>
        </div>
        <div class="nd-step">
            <span class="nd-step-num">4</span>
            <div>
                <p class="nd-step-title">Run the assessment</p>
                <p class="nd-step-desc">Compute HI, EI, VI and PRI risk indices, then rank NbS solutions by RPRI under your chosen scenario.</p>
            </div>
        </div>
        <div class="nd-step">
            <span class="nd-step-num">5</span>
            <div>
                <p class="nd-step-title">Save &amp; share</p>
                <p class="nd-step-desc">Expert users can save named analysis snapshots to the database and reload them at any time.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nd-footer">
    <div class="nd-footer-main">
        <strong>NATURE-DEMO</strong> · Horizon Europe Programme · Grant Agreement No. 101157448<br>
        University of Rostock (UROS) · Work Package 2, Task 2.3 · Deliverable D2.3
    </div>
    <div class="nd-footer-eu">
        Funded by the European Union.<br>
        Views expressed are those of the authors only<br>
        and do not reflect those of the EU or CINEA.
    </div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    try:
        st.image(LOGO_URL, use_container_width=True)
    except Exception:
        st.markdown("**NATURE-DEMO**")

    st.markdown('<hr class="nd-sb-rule">', unsafe_allow_html=True)
    st.markdown('<p class="nd-sb-section">Navigation</p>', unsafe_allow_html=True)

    st.link_button("🌿  Decision Support Tool", "/integrated_dst", use_container_width=True)
    st.link_button("🌡️  Climate Visualisation",
                   "https://naturedemo-clima-ind.dic-cloudmate.eu", use_container_width=True)

    st.markdown('<hr class="nd-sb-rule">', unsafe_allow_html=True)
    st.markdown('<p class="nd-sb-section">Resources</p>', unsafe_allow_html=True)

    st.markdown("""
    <div style="padding: 0 0.1rem;">
        <a class="nd-sb-link" href="https://www.nature-demo.eu" target="_blank">
            🌐&nbsp; Project Website
        </a>
        <a class="nd-sb-link" href="https://github.com/NATURE-DEMO/Decision_Support_Tool" target="_blank">
            ⌨️&nbsp; GitHub Repository
        </a>
        <a class="nd-sb-link" href="https://naturedemo-clima-ind.dic-cloudmate.eu" target="_blank">
            📈&nbsp; Climate Data API
        </a>
        <a class="nd-sb-link" href="https://nature-demo.eu/contact" target="_blank">
            📧&nbsp; Contact
        </a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="nd-sb-rule">', unsafe_allow_html=True)
    st.markdown("""
    <p style="font-size:0.68rem; color:rgba(144,200,120,0.35) !important;
       line-height:1.65; padding:0 0.1rem;">
        Horizon Europe · Grant 101157448<br>
        © 2026 NATURE-DEMO Consortium
    </p>
    """, unsafe_allow_html=True)
