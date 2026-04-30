import streamlit as st

st.set_page_config(
    page_title="NATURE-DEMO — Decision Support Tool",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

LOGO_URL = "https://raw.githubusercontent.com/NATURE-DEMO/Decision_Support_Tool/main/images/main_logo.png"
DOCS_URL = "https://nature-demo.github.io/Decision_Support_Tool/"
CLIMA_DOCS_URL = "https://nature-demo.github.io/clima-data/indicators/"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@300;400;600&family=Inter:wght@300;400;500;600&display=swap');

[data-testid="stSidebarNav"]       { display: none; }
[data-testid="stAppViewContainer"] { background: #f4f6f4; }
[data-testid="stHeader"]           { background: transparent; }
html, body, [class*="css"]         { font-family: 'Inter', sans-serif; }

/* ── HERO ── */
.nd-hero {
    background: #ffffff;
    border: 1px solid #cfdecf;
    border-top: 4px solid #2e6b2e;
    border-radius: 14px;
    padding: 2.5rem 2.5rem 2.25rem;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 12px rgba(30,60,30,0.06);
}
.nd-hero-title {
    font-family: 'Source Serif 4', serif;
    font-size: 2.15rem;
    font-weight: 300;
    color: #1a3a1a;
    line-height: 1.25;
    margin: 0 0 0.6rem;
    letter-spacing: -0.01em;
}
.nd-hero-title strong { font-weight: 600; color: #2e6b2e; }
.nd-hero-sub {
    font-size: 0.95rem;
    font-weight: 300;
    color: #587058;
    margin: 0 0 1.75rem;
    line-height: 1.65;
}

/* ── ABOUT BLURB ── */
.nd-hero-about {
    font-size: 0.85rem;
    font-weight: 300;
    color: #4a6a4a;
    line-height: 1.75;
    max-width: 680px;
    margin: 0 auto 1.75rem;
    text-align: left;
    background: #f3f8f3;
    border: 1px solid #cfdecf;
    border-radius: 10px;
    padding: 1rem 1.4rem;
}
.nd-hero-about strong {
    font-weight: 600;
    color: #2e6b2e;
}
.nd-hero-about-title {
    font-family: 'Source Serif 4', serif;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #587058;
    margin-bottom: 0.5rem;
}

/* ── PRIMARY BUTTON ── */
.nd-launch-btn {
    display: inline-block;
    background: #2e6b2e;
    color: #ffffff !important;
    text-decoration: none !important;
    padding: 0.85rem 2.4rem;
    border-radius: 9px;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    box-shadow: 0 2px 10px rgba(46,107,46,0.28);
    transition: background 0.18s, transform 0.15s;
    margin-bottom: 0.75rem;
}
.nd-launch-btn:hover {
    background: #1a3a1a;
    transform: translateY(-1px);
    color: #c4dcc4 !important;
    text-decoration: none !important;
}

/* ── DOCS LINK BELOW BUTTON ── */
.nd-docs-row {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 0.6rem;
}
.nd-docs-link {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.8rem;
    font-weight: 500;
    color: #2e6b2e !important;
    text-decoration: none !important;
    border-bottom: 1px solid #90c890;
    padding-bottom: 1px;
    transition: color 0.15s, border-color 0.15s;
}
.nd-docs-link:hover {
    color: #1a3a1a !important;
    border-color: #2e6b2e;
    text-decoration: none !important;
}

/* ── CAPABILITIES STRIP ── */
.nd-caps {
    display: flex;
    gap: 1px;
    background: #cfdecf;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #cfdecf;
    margin-bottom: 1.5rem;
}
.nd-cap {
    flex: 1;
    background: #ffffff;
    padding: 0.85rem 0.5rem;
    text-align: center;
}
.nd-cap-num {
    font-family: 'Source Serif 4', serif;
    font-size: 1.55rem;
    font-weight: 600;
    color: #2e6b2e;
    display: block;
    line-height: 1;
    margin-bottom: 0.25rem;
}
.nd-cap-lbl { font-size: 0.65rem; color: #7a9a7a; line-height: 1.4; }

/* ── ABOUT PANEL ── */
.nd-panel {
    background: #ffffff;
    border: 1px solid #cfdecf;
    border-radius: 12px;
    padding: 1.5rem 1.75rem;
    box-shadow: 0 1px 6px rgba(30,60,30,0.04);
}
.nd-panel-title {
    font-family: 'Source Serif 4', serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: #1a3a1a;
    margin: 0 0 0.7rem;
}
.nd-panel p {
    font-size: 0.84rem;
    font-weight: 300;
    color: #3a5a3a;
    line-height: 1.85;
    margin: 0 0 0.65rem;
}
.nd-panel p:last-child { margin-bottom: 0; }

/* ── CLIMATE VIZ CARD ── */
.nd-viz-card {
    background: #f8fbf8;
    border: 1px solid #cfdecf;
    border-left: 4px solid #7ab87a;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}
.nd-viz-icon {
    font-size: 1.6rem;
    line-height: 1;
    flex-shrink: 0;
    margin-top: 0.1rem;
}
.nd-viz-body {}
.nd-viz-title {
    font-family: 'Source Serif 4', serif;
    font-size: 1rem;
    font-weight: 600;
    color: #1a3a1a;
    margin: 0 0 0.35rem;
}
.nd-viz-desc {
    font-size: 0.81rem;
    font-weight: 300;
    color: #4a6a4a;
    line-height: 1.7;
    margin: 0 0 0.5rem;
}
.nd-viz-indicators {
    font-size: 0.78rem;
    font-weight: 300;
    color: #4a6a4a;
    line-height: 1.7;
    margin: 0 0 0.6rem;
    background: #eef5ee;
    border: 1px solid #c0d8c0;
    border-radius: 7px;
    padding: 0.6rem 0.85rem;
}
.nd-viz-indicators strong {
    font-weight: 600;
    color: #2e6b2e;
    display: block;
    margin-bottom: 0.25rem;
    font-size: 0.76rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}
.nd-viz-indicators ul {
    margin: 0;
    padding-left: 1.15rem;
}
.nd-viz-indicators ul li {
    margin-bottom: 0.1rem;
}
.nd-viz-links {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
}
.nd-viz-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.76rem;
    font-weight: 500;
    color: #2e6b2e !important;
    text-decoration: none !important;
    background: #ffffff;
    border: 1px solid #90c890;
    border-radius: 6px;
    padding: 0.3rem 0.7rem;
    transition: background 0.15s;
}
.nd-viz-btn:hover {
    background: #edf5ed;
    color: #1a3a1a !important;
    text-decoration: none !important;
}

/* ── FOOTER ── */
.nd-footer {
    border-top: 1px solid #cfdecf;
    padding-top: 1.1rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 0.6rem;
}
.nd-footer-left {
    font-size: 0.72rem;
    font-weight: 300;
    color: #8aaa8a;
    line-height: 1.7;
}
.nd-footer-left strong { color: #587058; font-weight: 500; }
.nd-footer-right {
    font-size: 0.68rem;
    font-weight: 300;
    color: #aac4aa;
    text-align: right;
    line-height: 1.6;
}

/* ── SIDEBAR ── */
/* ── SIDEBAR ── */
[data-testid="stSidebar"] { 
    /* Gradient starts at Gray (#707070) and ends at your Green (#3a6e3a) */
    background: linear-gradient(180deg, #707070 0%, #3a6e3a 100%) !important; 
    background-attachment: fixed !important;
}

[data-testid="stSidebar"] * { 
    /* Brightened text for better contrast against the gray top */
    color: #fdfdfd !important; 
}

[data-testid="stSidebar"] .stLinkButton > a {
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 7px !important;
    color: #ffffff !important;
    font-size: 0.82rem !important;
    transition: background 0.18s !important;
}

[data-testid="stSidebar"] .stLinkButton > a:hover {
    background: rgba(255,255,255,0.25) !important;
}

.sb-rule { 
    border: none; 
    border-top: 1px solid rgba(255,255,255,0.2); 
    margin: 0.8rem 0; 
}

.sb-section {
    font-size: 0.6rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    color: rgba(255,255,255,0.6) !important;
    margin: 0.9rem 0 0.35rem !important;
}

.sb-doc-link {
    display: block;
    text-align: center;
    text-decoration: none !important;
    color: rgba(255,255,255,0.85) !important;
    font-size: 0.8rem;
    font-weight: 400;
    padding: 0.45rem 0 0.6rem;
    transition: color 0.15s;
    letter-spacing: 0.01em;
}

.sb-doc-link:hover {
    color: #ffffff !important;
}

.sb-link {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    padding: 0.55rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.12);
    text-decoration: none !important;
    color: #e0eee0 !important;
    font-size: 0.8rem;
    transition: color 0.15s;
}
.sb-link:last-child { border-bottom: none; }
.sb-link:hover { color: #ffffff !important; }
[data-testid="stSidebar"] .stLinkButton > a {
    background: rgba(255,255,255,0.10) !important;
    border: 1px solid rgba(180,230,160,0.3) !important;
    border-radius: 7px !important;
    color: #e0f0e0 !important;
    font-size: 0.82rem !important;
    transition: background 0.18s !important;
}
[data-testid="stSidebar"] .stLinkButton > a:hover {
    background: rgba(180,230,160,0.18) !important;
}
.sb-rule { border: none; border-top: 1px solid rgba(180,230,160,0.2); margin: 0.8rem 0; }
.sb-section {
    font-size: 0.6rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    color: rgba(180,230,160,0.55) !important;
    margin: 0.9rem 0 0.35rem !important;
}
.sb-doc-link {
    display: block;
    text-align: center;
    text-decoration: none !important;
    color: rgba(210,240,210,0.85) !important;
    font-size: 0.8rem;
    font-weight: 400;
    padding: 0.45rem 0 0.6rem;
    transition: color 0.15s;
    letter-spacing: 0.01em;
}
.sb-doc-link:hover {
    color: #e8f6e8 !important;
    text-decoration: none !important;
}
.sb-link {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    padding: 0.55rem 0;
    border-bottom: 1px solid rgba(180,230,160,0.12);
    text-decoration: none !important;
    color: #c8e0c8 !important;
    font-size: 0.8rem;
    transition: color 0.15s;
}
.sb-link:last-child { border-bottom: none; }
.sb-link:hover { color: #e8f6e8 !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    try:
        st.image(LOGO_URL, use_container_width=True)
    except Exception:
        st.markdown("**NATURE-DEMO**")

    st.markdown('<hr class="sb-rule">', unsafe_allow_html=True)
    st.markdown('<p class="sb-section">Tools</p>', unsafe_allow_html=True)

    # Main DST button — Integrated DST (has documentation)
    st.link_button("🌿  NATURE-DEMO's DST", "/integrated_dst",
                   use_container_width=True)
    st.markdown(f"""
    <a class="sb-doc-link" href="{DOCS_URL}" target="_blank">
        📖&nbsp; Documentation
    </a>
    """, unsafe_allow_html=True)

    # Climate Data Visualisation button + docs
    st.link_button("🌡️  Climate Data Visualisation",
                   "https://naturedemo-clima-ind.dic-cloudmate.eu", use_container_width=True)
    st.markdown(f"""
    <a class="sb-doc-link" href="{CLIMA_DOCS_URL}" target="_blank">
        📖&nbsp; Documentation
    </a>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="sb-rule">', unsafe_allow_html=True)
    st.markdown('<p class="sb-section">Resources</p>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="padding: 0 0.1rem;">
        <a class="sb-link" href="https://www.nature-demo.eu" target="_blank">🌐&nbsp; Project Website</a>
        <a class="sb-link" href="https://github.com/NATURE-DEMO/Decision_Support_Tool" target="_blank">⌨️&nbsp; GitHub</a>
        <a class="sb-link" href="https://nature-demo.eu/contact" target="_blank">📧&nbsp; Contact</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="sb-rule">', unsafe_allow_html=True)
    st.markdown("""
    <p style="font-size:0.66rem; color:rgba(180,230,160,0.4) !important; line-height:1.65; padding:0 0.1rem;">
        Horizon Europe · Grant 101157448<br>© 2026 NATURE-DEMO Consortium
    </p>
    """, unsafe_allow_html=True)

_, centre, _ = st.columns([1, 4, 1])

with centre:

    _, lc, _ = st.columns([1, 2, 1])
    with lc:
        try:
            st.image(LOGO_URL, use_container_width=True)
        except Exception:
            st.empty()

    st.markdown(f"""
    <div class="nd-hero">
        <h1 class="nd-hero-title">
            Nature-Based Solutions for<br><strong>Climate-Resilient Infrastructure</strong>
        </h1>
        <p class="nd-hero-sub">
            A Horizon Europe decision support platform for climate risk assessment
            and Nature-Based Solution recommendation across European infrastructure.
        </p>
        <div class="nd-hero-about">
            <div class="nd-hero-about-title">About the Decision Support Tool</div>
            <strong>NATURE-DEMO</strong> is a Horizon Europe Innovation Action (Grant No. 101157448)
            that develops and validates Nature-Based Solutions for protecting critical infrastructure
            against natural hazards and climate change, with a focus on Alpine and peri-Alpine regions.
            <br><br>
            The Decision Support Tool — the primary software deliverable of Work Package 2, Task 2.3
            (University of Rostock) — integrates a multi-level risk assessment framework with
            EURO-CORDEX climate projections. Users can explore pre-configured demonstration sites or
            run a custom assessment for any European location, and receive ranked NbS recommendations
            under present and future climate scenarios.
        </div>
        <a href="/General_DST" class="nd-launch-btn">
            Open the Decision Support Tool &nbsp;→
        </a>
        <div class="nd-docs-row">
            <a class="nd-viz-btn"
                   href="{DOCS_URL}"
                   target="_blank">
                    📖 Tool's full documentation
                </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="nd-caps">
        <div class="nd-cap">
            <span class="nd-cap-num">5</span>
            <span class="nd-cap-lbl">Demo sites<br>across Europe</span>
        </div>
        <div class="nd-cap">
            <span class="nd-cap-num">12</span>
            <span class="nd-cap-lbl">Infrastructure<br>categories</span>
        </div>
        <div class="nd-cap">
            <span class="nd-cap-num">29</span>
            <span class="nd-cap-lbl">Natural hazard<br>types</span>
        </div>
        <div class="nd-cap">
            <span class="nd-cap-num">23</span>
            <span class="nd-cap-lbl">EURO-CORDEX<br>climate indices</span>
        </div>
        <div class="nd-cap">
            <span class="nd-cap-num">3</span>
            <span class="nd-cap-lbl">Assessment<br>levels</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # st.markdown(f"""
    # <div class="nd-panel" style="margin-bottom:1.25rem;">
    #     <h2 class="nd-panel-title">About the Decision Support Tool</h2>
    #     <p>
    #         NATURE-DEMO is a Horizon Europe Innovation Action (Grant No.&nbsp;101157448) that develops
    #         and validates Nature-Based Solutions for protecting critical infrastructure against natural
    #         hazards and climate change, with a focus on Alpine and peri-Alpine regions.
    #     </p>
    #     <p>
    #         The Decision Support Tool — the primary software deliverable of Work Package 2, Task 2.3
    #         (University of Rostock) — integrates a multi-level risk assessment framework with
    #         EURO-CORDEX climate projections. Users can explore pre-configured demonstration sites
    #         or run a custom assessment for any European location, and receive ranked NbS
    #         recommendations under present and future climate scenarios.
    #     </p>
    # </div>
    # """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="nd-viz-card" style="margin-bottom:1.5rem;">
        <span class="nd-viz-icon">🌡️</span>
        <div class="nd-viz-body">
            <p class="nd-viz-title">European Climate Data Visualisation</p>
            <p class="nd-viz-desc">
                An interactive companion tool — developed by IBM Research — for exploring the
                EURO-CORDEX climate index dataset that underpins the DST's hazard analysis.
                Search any European city or coordinate and visualise historical trends and
                scenario projections (RCP4.5 / RCP8.5) for all 23 climate indices to 2100.
            </p>
            <div class="nd-viz-indicators">
                <strong>📊 Available Climate Indicators</strong>
                <ul>
                    <li><b>Temperature</b> — mean, min, max, diurnal range, growing degree days, frost/ice/tropical days, warm/cold spells</li>
                    <li><b>Precipitation</b> — total, heavy rainfall days (R10mm / R20mm), consecutive dry/wet days, max 1-day &amp; 5-day precipitation</li>
                    <li><b>Wind &amp; Humidity</b> — wind speed indices, relative humidity extremes</li>
                    <li><b>Scenarios</b> — RCP4.5 and RCP8.5 projections to 2100 · Historical baseline from 1971</li>
                </ul>
                <a class="nd-docs-link" href="{CLIMA_DOCS_URL}" target="_blank" style="font-size:0.76rem; margin-top:0.35rem; display:inline-flex;">
                    📖 Full indicator documentation →
                </a>
            </div>
            <div class="nd-viz-links">
                <a class="nd-viz-btn"
                   href="https://naturedemo-clima-ind.dic-cloudmate.eu"
                   target="_blank">
                    ↗ Open tool
                </a>
                <a class="nd-viz-btn"
                   href="{CLIMA_DOCS_URL}"
                   target="_blank">
                    📖 Indicators documentation
                </a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="nd-footer">
        <div class="nd-footer-left">
            <strong>NATURE-DEMO</strong> · Horizon Europe · Grant Agreement No. 101157448<br>
            University of Rostock (UROS) · WP2 Task 2.3 · Deliverable D2.3
        </div>
        <div class="nd-footer-right">
            Funded by the European Union.<br>
            Views are those of the authors only<br>
            and do not reflect those of the EU or CINEA.
        </div>
    </div>
    """, unsafe_allow_html=True)
