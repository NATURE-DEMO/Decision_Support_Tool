import streamlit as st

st.set_page_config(
    page_title="NATURE-DEMO — Decision Support Tool",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

LOGO_URL = "https://raw.githubusercontent.com/NATURE-DEMO/Decision_Support_Tool/main/images/main_logo.png"
DOCS_URL = "https://nature-demo.github.io/Decision_Support_Tool/"

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
    margin: 0 0 0.6rem;
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
[data-testid="stSidebar"] { background: #1a3a1a !important; }
[data-testid="stSidebar"] * { color: #c4dcc4 !important; }
[data-testid="stSidebar"] .stLinkButton > a {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(144,200,120,0.2) !important;
    border-radius: 7px !important;
    color: #c4dcc4 !important;
    font-size: 0.82rem !important;
    transition: background 0.18s !important;
}
[data-testid="stSidebar"] .stLinkButton > a:hover {
    background: rgba(144,200,120,0.14) !important;
}
.sb-rule { border: none; border-top: 1px solid rgba(144,200,120,0.15); margin: 0.8rem 0; }
.sb-section {
    font-size: 0.6rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    color: rgba(144,200,120,0.4) !important;
    margin: 0.9rem 0 0.35rem !important;
}
.sb-note {
    font-size: 0.74rem !important;
    font-weight: 300 !important;
    color: rgba(196,220,196,0.55) !important;
    line-height: 1.65 !important;
    padding: 0.6rem 0.75rem !important;
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(144,200,120,0.12) !important;
    border-radius: 7px !important;
    margin-bottom: 0.3rem !important;
}
.sb-note strong { color: rgba(196,220,196,0.8) !important; font-weight: 500 !important; }
.sb-link {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    padding: 0.55rem 0;
    border-bottom: 1px solid rgba(144,200,120,0.1);
    text-decoration: none !important;
    color: #b0ccb0 !important;
    font-size: 0.8rem;
    transition: color 0.15s;
}
.sb-link:last-child { border-bottom: none; }
.sb-link:hover { color: #e0f0e0 !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    try:
        st.image(LOGO_URL, use_container_width=True)
    except Exception:
        st.markdown("**NATURE-DEMO**")

    st.markdown('<hr class="sb-rule">', unsafe_allow_html=True)
    st.markdown('<p class="sb-section">Tools</p>', unsafe_allow_html=True)

    # General DST — no login, main tool
    st.link_button("🌿  General DST", "/General_DST", use_container_width=True)

    st.markdown('<hr class="sb-rule">', unsafe_allow_html=True)
    st.markdown('<p class="sb-section">Extended Access</p>', unsafe_allow_html=True)

    # Integrated DST — login required, with warning
    st.markdown("""
    <div class="sb-note">
        <strong>⚠️ Sign-up required</strong><br>
        The Integrated DST requires an account. Approval may take a few days
        as the administrator is not automatically notified of new registrations.
    </div>
    """, unsafe_allow_html=True)
    st.link_button("🔐  Integrated DST", "/integrated_dst", use_container_width=True)

    st.markdown('<hr class="sb-rule">', unsafe_allow_html=True)
    st.markdown('<p class="sb-section">Resources</p>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="padding: 0 0.1rem;">
        <a class="sb-link" href="{DOCS_URL}" target="_blank">📖&nbsp; Documentation</a>
        <a class="sb-link" href="https://naturedemo-clima-ind.dic-cloudmate.eu" target="_blank">🌡️&nbsp; Climate Data Visualisation</a>
        <a class="sb-link" href="https://www.nature-demo.eu" target="_blank">🌐&nbsp; Project Website</a>
        <a class="sb-link" href="https://github.com/NATURE-DEMO/Decision_Support_Tool" target="_blank">⌨️&nbsp; GitHub</a>
        <a class="sb-link" href="https://nature-demo.eu/contact" target="_blank">📧&nbsp; Contact</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="sb-rule">', unsafe_allow_html=True)
    st.markdown("""
    <p style="font-size:0.66rem; color:rgba(144,200,120,0.3) !important; line-height:1.65; padding:0 0.1rem;">
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
        <a href="/General_DST" class="nd-launch-btn">
            Open the Decision Support Tool &nbsp;→
        </a>
        <div class="nd-docs-row">
            <a class="nd-docs-link" href="{DOCS_URL}" target="_blank">
                📖 Read the documentation
            </a>
            <a class="nd-docs-link" href="/integrated_dst">
                🔐 Integrated DST (sign-up required)
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

    st.markdown(f"""
    <div class="nd-panel" style="margin-bottom:1.25rem;">
        <h2 class="nd-panel-title">About the Decision Support Tool</h2>
        <p>
            NATURE-DEMO is a Horizon Europe Innovation Action (Grant No.&nbsp;101157448) that develops
            and validates Nature-Based Solutions for protecting critical infrastructure against natural
            hazards and climate change, with a focus on Alpine and peri-Alpine regions.
        </p>
        <p>
            The Decision Support Tool — the primary software deliverable of Work Package 2, Task 2.3
            (University of Rostock) — integrates a multi-level risk assessment framework with
            EURO-CORDEX climate projections. Users can explore pre-configured demonstration sites
            or run a custom assessment for any European location, and receive ranked NbS
            recommendations under present and future climate scenarios.
        </p>
        <p>
            <a class="nd-docs-link" href="{DOCS_URL}" target="_blank">
                📖 Full documentation and user guide →
            </a>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="nd-viz-card" style="margin-bottom:1.5rem;">
        <span class="nd-viz-icon">🌡️</span>
        <div class="nd-viz-body">
            <p class="nd-viz-title">European Climate Data Visualisation</p>
            <p class="nd-viz-desc">
                An interactive companion tool — developed by IBM Research — for exploring the
                EURO-CORDEX climate index dataset that underpins the DST's hazard analysis.
                Search any European city or coordinate and visualise historical trends and
                scenario projections (RCP4.5 / RCP8.5) for all 20 climate indices to 2100.
            </p>
            <div class="nd-viz-links">
                <a class="nd-viz-btn"
                   href="https://naturedemo-clima-ind.dic-cloudmate.eu"
                   target="_blank">
                    ↗ Open tool
                </a>
                <a class="nd-viz-btn"
                   href="{DOCS_URL}"
                   target="_blank">
                    📖 Documentation
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
