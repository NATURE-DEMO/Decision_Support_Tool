import streamlit as st
import base64
import requests

st.set_page_config(
    page_title="NATURE-DEMO — Decision Support Tool",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

LOGO_URL = "https://raw.githubusercontent.com/NATURE-DEMO/Decision_Support_Tool/main/images/main_logo.png"


@st.cache_data(ttl=3600)
def get_logo_base64(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return base64.b64encode(response.content).decode()
    except Exception:
        return None


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=DM+Sans:wght@300;400;500&display=swap');

[data-testid="stSidebarNav"] { display: none; }
[data-testid="stAppViewContainer"] { background: #f7f5f0; }
[data-testid="stHeader"] { background: transparent; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Hero ── */
.hero-wrap {
    background: linear-gradient(135deg, #1a2e1a 0%, #2d4a2d 40%, #1e3a2e 100%);
    border-radius: 16px;
    padding: 4rem 3rem 3.5rem;
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
}
.hero-wrap::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(144,200,120,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-wrap::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 20%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(100,180,100,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-logo {
    display: flex;
    justify-content: center;
    margin-bottom: 2rem;
}
.hero-logo img {
    filter: brightness(0) invert(1);
    opacity: 0.95;
}
.hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3rem;
    font-weight: 300;
    color: #f0f4f0;
    text-align: center;
    letter-spacing: 0.02em;
    margin: 0 0 0.75rem 0;
    line-height: 1.2;
}
.hero-title strong {
    font-weight: 600;
    color: #a8d5a2;
}
.hero-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.05rem;
    font-weight: 300;
    color: rgba(220,235,220,0.75);
    text-align: center;
    letter-spacing: 0.04em;
    margin: 0 0 2.5rem 0;
}
.hero-meta {
    display: flex;
    justify-content: center;
    gap: 2.5rem;
    flex-wrap: wrap;
}
.hero-badge {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem;
    font-weight: 500;
    color: rgba(200,225,200,0.65);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    border: 1px solid rgba(144,200,120,0.2);
    padding: 0.35rem 1rem;
    border-radius: 20px;
    background: rgba(255,255,255,0.04);
}

/* ── Section label ── */
.section-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #5a8a5a;
    margin-bottom: 0.75rem;
}
.section-heading {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2rem;
    font-weight: 400;
    color: #1a2e1a;
    margin: 0 0 1.5rem 0;
}

/* ── Tool cards ── */
.tool-card {
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid #e4ebe4;
    padding: 2rem 1.75rem 1.75rem;
    height: 100%;
    position: relative;
    transition: box-shadow 0.25s ease, transform 0.25s ease;
    box-shadow: 0 2px 12px rgba(30,60,30,0.06);
}
.tool-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(30,60,30,0.12);
}
.tool-card-icon {
    font-size: 2.2rem;
    margin-bottom: 1rem;
    display: block;
}
.tool-card-tag {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    background: #edf5ed;
    color: #3a6b3a;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    margin-bottom: 0.85rem;
}
.tool-card-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.5rem;
    font-weight: 600;
    color: #1a2e1a;
    margin: 0 0 0.6rem 0;
    line-height: 1.3;
}
.tool-card-desc {
    font-size: 0.88rem;
    color: #4a6a4a;
    line-height: 1.7;
    margin-bottom: 1.5rem;
    font-weight: 300;
}
.tool-card-features {
    list-style: none;
    padding: 0;
    margin: 0 0 1.75rem 0;
    border-top: 1px solid #edf5ed;
    padding-top: 1.25rem;
}
.tool-card-features li {
    font-size: 0.82rem;
    color: #3a5a3a;
    padding: 0.35rem 0;
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    line-height: 1.5;
    font-weight: 400;
}
.tool-card-features li::before {
    content: '→';
    color: #7ab87a;
    font-size: 0.75rem;
    margin-top: 0.05rem;
    flex-shrink: 0;
}
.tool-card-btn {
    display: block;
    text-align: center;
    background: #2d4a2d;
    color: #f0f4f0 !important;
    text-decoration: none !important;
    padding: 0.7rem 1.5rem;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.04em;
    transition: background 0.2s ease;
}
.tool-card-btn:hover {
    background: #1a2e1a;
    color: #a8d5a2 !important;
    text-decoration: none !important;
}
.tool-card-btn-outline {
    display: block;
    text-align: center;
    background: transparent;
    color: #2d4a2d !important;
    text-decoration: none !important;
    padding: 0.7rem 1.5rem;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.04em;
    border: 1.5px solid #2d4a2d;
    transition: all 0.2s ease;
}
.tool-card-btn-outline:hover {
    background: #2d4a2d;
    color: #f0f4f0 !important;
    text-decoration: none !important;
}

/* ── About section ── */
.about-strip {
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid #e4ebe4;
    padding: 2.5rem 2.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 12px rgba(30,60,30,0.05);
}
.about-strip p {
    font-size: 0.92rem;
    line-height: 1.85;
    color: #3a5a3a;
    font-weight: 300;
    margin: 0;
}

/* ── KPI bar ── */
.kpi-row {
    display: flex;
    gap: 1px;
    background: #e4ebe4;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 2.5rem;
}
.kpi-item {
    flex: 1;
    background: #ffffff;
    padding: 1.25rem 1rem;
    text-align: center;
}
.kpi-number {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2rem;
    font-weight: 600;
    color: #2d4a2d;
    line-height: 1;
    display: block;
    margin-bottom: 0.3rem;
}
.kpi-label {
    font-size: 0.72rem;
    color: #6a8a6a;
    font-weight: 400;
    letter-spacing: 0.04em;
    line-height: 1.4;
}

/* ── Workflow ── */
.workflow-step {
    display: flex;
    align-items: flex-start;
    gap: 1.25rem;
    padding: 1.25rem 0;
    border-bottom: 1px solid #edf5ed;
}
.workflow-step:last-child { border-bottom: none; }
.step-num {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.6rem;
    font-weight: 600;
    color: #a8d5a2;
    min-width: 2rem;
    line-height: 1;
    margin-top: 0.1rem;
}
.step-title {
    font-size: 0.88rem;
    font-weight: 500;
    color: #1a2e1a;
    margin-bottom: 0.25rem;
}
.step-desc {
    font-size: 0.8rem;
    color: #6a8a6a;
    font-weight: 300;
    line-height: 1.6;
    margin: 0;
}

/* ── Links ── */
.link-item {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    padding: 0.75rem 0;
    border-bottom: 1px solid #edf5ed;
    text-decoration: none !important;
    color: #1a2e1a !important;
    font-size: 0.85rem;
    font-weight: 400;
    transition: color 0.2s;
}
.link-item:last-child { border-bottom: none; }
.link-item:hover { color: #3a7a3a !important; }
.link-icon { font-size: 1.1rem; }

/* ── Footer ── */
.footer-wrap {
    background: #1a2e1a;
    border-radius: 14px;
    padding: 2rem 2.5rem;
    margin-top: 2.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}
.footer-left {
    font-size: 0.82rem;
    color: rgba(200,225,200,0.6);
    line-height: 1.7;
    font-weight: 300;
}
.footer-left strong {
    color: rgba(200,225,200,0.9);
    font-weight: 500;
}
.eu-badge {
    font-size: 0.75rem;
    color: rgba(200,225,200,0.5);
    letter-spacing: 0.05em;
    text-align: right;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a2e1a 0%, #2d4a2d 100%) !important;
}
[data-testid="stSidebar"] * { color: #d0e8d0 !important; }
[data-testid="stSidebar"] .stLinkButton > a {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(144,200,120,0.2) !important;
    border-radius: 8px !important;
    color: #c8e6c8 !important;
    font-size: 0.85rem !important;
    transition: background 0.2s !important;
}
[data-testid="stSidebar"] .stLinkButton > a:hover {
    background: rgba(144,200,120,0.15) !important;
}
.sidebar-divider {
    border: none;
    border-top: 1px solid rgba(144,200,120,0.2);
    margin: 1rem 0;
}
.sidebar-section {
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: rgba(168,213,162,0.55) !important;
    margin: 1.25rem 0 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
logo_b64 = get_logo_base64(LOGO_URL)
logo_html = ""
if logo_b64:
    logo_html = f"""
    <div class="hero-logo">
        <a href="https://www.nature-demo.eu" target="_blank">
            <img src="data:image/png;base64,{logo_b64}" width="320">
        </a>
    </div>"""

st.markdown(f"""
<div class="hero-wrap">
    {logo_html}
    <h1 class="hero-title">Nature-Based Solutions for<br><strong>Climate-Resilient Infrastructure</strong></h1>
    <p class="hero-subtitle">A digital decision support platform for risk assessment and NbS evaluation across Europe</p>
    <div class="hero-meta">
        <span class="hero-badge">Horizon Europe · Grant 101157448</span>
        <span class="hero-badge">Work Package 2 · Task 2.3</span>
        <span class="hero-badge">University of Rostock</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI BAR ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="kpi-row">
    <div class="kpi-item">
        <span class="kpi-number">6</span>
        <span class="kpi-label">Demo sites<br>across Europe</span>
    </div>
    <div class="kpi-item">
        <span class="kpi-number">12</span>
        <span class="kpi-label">Infrastructure<br>categories</span>
    </div>
    <div class="kpi-item">
        <span class="kpi-number">29</span>
        <span class="kpi-label">Natural hazard<br>types</span>
    </div>
    <div class="kpi-item">
        <span class="kpi-number">20</span>
        <span class="kpi-label">EURO-CORDEX<br>climate indices</span>
    </div>
    <div class="kpi-item">
        <span class="kpi-number">3</span>
        <span class="kpi-label">Assessment<br>levels</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── TOOLS ─────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-label">Platform</p><h2 class="section-heading">Available Tools</h2>', unsafe_allow_html=True)

col_dst, col_clim = st.columns(2, gap="large")

with col_dst:
    st.markdown("""
    <div class="tool-card">
        <span class="tool-card-icon">🌿</span>
        <span class="tool-card-tag">Primary Platform</span>
        <h3 class="tool-card-title">Decision Support Tool</h3>
        <p class="tool-card-desc">
            An integrated web application for multi-level climate risk assessment 
            and Nature-Based Solution recommendation. Covers both pre-configured 
            demonstration sites and free-form analysis for any location across Europe.
        </p>
        <ul class="tool-card-features">
            <li>Specific Site DST for the 6 NATURE-DEMO demonstration sites with expert consensus system</li>
            <li>Custom Site Analysis for any European location via OpenStreetMap extraction</li>
            <li>Three assessment levels: Perceived Risk · Regional Screening · High-Resolution</li>
            <li>Quantitative risk indices (HI, EI, VI, PRI) from EURO-CORDEX climate projections</li>
            <li>NbS ranking engine with SSF, SEI and HIA scoring under RCP4.5 / RCP8.5 scenarios</li>
            <li>AI-generated interpretation reports via Google Gemini</li>
        </ul>
        <a href="/integrated_dst" class="tool-card-btn">Launch Decision Support Tool →</a>
    </div>
    """, unsafe_allow_html=True)

with col_clim:
    st.markdown("""
    <div class="tool-card">
        <span class="tool-card-icon">🌡️</span>
        <span class="tool-card-tag">Companion Tool · IBM Research</span>
        <h3 class="tool-card-title">European Climate Data Visualisation</h3>
        <p class="tool-card-desc">
            An interactive front-end for exploring the EURO-CORDEX climate index dataset 
            that underpins the DST's hazard analysis. Useful for exploring climate trends 
            at any European location before or alongside a full Level 2 assessment.
        </p>
        <ul class="tool-card-features">
            <li>City- and coordinate-based location search across the EURO-CORDEX EUR-11 domain</li>
            <li>Interactive time-series for all 20 climate indices: historical and projected to 2100</li>
            <li>Scenario comparison with ensemble uncertainty bands (RCP4.5 / RCP8.5)</li>
            <li>Powered by the IBM clima-ind-viz API — same data source as the DST Level 2</li>
        </ul>
        <br>
        <a href="https://naturedemo-clima-ind.dic-cloudmate.eu" target="_blank" class="tool-card-btn-outline">Open Climate Visualisation ↗</a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── ABOUT + WORKFLOW ──────────────────────────────────────────────────────────
col_about, col_flow = st.columns([3, 2], gap="large")

with col_about:
    st.markdown('<p class="section-label">Project</p><h2 class="section-heading">About NATURE-DEMO</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="about-strip">
        <p>
            NATURE-DEMO (Nature-Based Solutions for Demonstrating Climate-Resilient Critical Infrastructure) 
            is a Horizon Europe Innovation Action under Grant Agreement No. 101157448. 
            The project develops, validates, and deploys a comprehensive framework for assessing 
            and implementing Nature-Based Solutions (NbS) that protect critical infrastructure 
            against natural hazards and climate change, with a particular focus on the Alpine 
            and peri-Alpine region.
        </p>
        <br>
        <p>
            This Decision Support Tool is the primary software deliverable of Work Package 2, 
            Task 2.3, developed by the University of Rostock (UROS). It consolidates the 
            multi-level risk assessment framework from T2.1 (IHCantabria / FIHAC) and the 
            EURO-CORDEX climate data from T2.2 (IBM Research) into a single operational platform 
            accessible to infrastructure managers, climate risk experts, and project partners.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_flow:
    st.markdown('<p class="section-label">Getting started</p><h2 class="section-heading">How It Works</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="about-strip" style="padding: 1.5rem 2rem;">
        <div class="workflow-step">
            <span class="step-num">1</span>
            <div>
                <p class="step-title">Authenticate</p>
                <p class="step-desc">Log in with your credentials. New users may register and request an expert or viewer role pending admin approval.</p>
            </div>
        </div>
        <div class="workflow-step">
            <span class="step-num">2</span>
            <div>
                <p class="step-title">Select a mode</p>
                <p class="step-desc">Choose a pre-configured demo site for validated assessments, or use the Custom Site Analysis for any European location.</p>
            </div>
        </div>
        <div class="workflow-step">
            <span class="step-num">3</span>
            <div>
                <p class="step-title">Define your scope</p>
                <p class="step-desc">Select infrastructure types, draw a polygon, and extract OSM data and EURO-CORDEX climate indicators automatically.</p>
            </div>
        </div>
        <div class="workflow-step">
            <span class="step-num">4</span>
            <div>
                <p class="step-title">Run the assessment</p>
                <p class="step-desc">Compute HI, EI, VI and PRI risk indices, then rank NbS solutions by RPRI under your chosen climate scenario.</p>
            </div>
        </div>
        <div class="workflow-step">
            <span class="step-num">5</span>
            <div>
                <p class="step-title">Save & share</p>
                <p class="step-desc">Expert users can save named analysis snapshots to the database and reload them at any time.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-wrap">
    <div class="footer-left">
        <strong>NATURE-DEMO</strong> · Horizon Europe Programme · Grant Agreement No. 101157448<br>
        University of Rostock (UROS) · Work Package 2, Task 2.3 · Deliverable D2.3
    </div>
    <div class="eu-badge">
        Funded by the European Union.<br>
        Views expressed are those of the authors only<br>
        and do not reflect those of the EU or CINEA.
    </div>
</div>
""", unsafe_allow_html=True)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    if logo_b64:
        st.markdown(f"""
        <div style="text-align:center; padding: 1rem 0 0.5rem;">
            <a href="https://www.nature-demo.eu" target="_blank">
                <img src="data:image/png;base64,{logo_b64}" width="200"
                     style="filter: brightness(0) invert(1); opacity:0.9;">
            </a>
        </div>""", unsafe_allow_html=True)

    st.markdown('<p class="sidebar-divider"></p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-section">Navigation</p>', unsafe_allow_html=True)

    st.link_button("🌿  Decision Support Tool", "/integrated_dst", use_container_width=True)
    st.link_button("🌡️  Climate Visualisation", "https://naturedemo-clima-ind.dic-cloudmate.eu", use_container_width=True)

    st.markdown('<p class="sidebar-divider"></p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-section">Resources</p>', unsafe_allow_html=True)

    st.markdown("""
    <div style="padding: 0 0.25rem;">
        <a class="link-item" href="https://www.nature-demo.eu" target="_blank">
            <span class="link-icon">🌐</span> Project Website
        </a>
        <a class="link-item" href="https://github.com/NATURE-DEMO/Decision_Support_Tool" target="_blank">
            <span class="link-icon">⌨️</span> GitHub Repository
        </a>
        <a class="link-item" href="https://naturedemo-clima-ind.dic-cloudmate.eu" target="_blank">
            <span class="link-icon">📈</span> Climate Data API
        </a>
        <a class="link-item" href="https://nature-demo.eu/contact" target="_blank">
            <span class="link-icon">📧</span> Contact
        </a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="sidebar-divider"></p>', unsafe_allow_html=True)
    st.markdown("""
    <p style="font-size:0.72rem; color: rgba(200,225,200,0.4) !important;
       line-height:1.6; padding: 0 0.25rem;">
        Horizon Europe · Grant 101157448<br>
        © 2026 NATURE-DEMO Consortium
    </p>
    """, unsafe_allow_html=True)
