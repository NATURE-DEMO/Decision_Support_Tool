import streamlit as st

st.set_page_config(
    page_title="NATURE-DEMO — Decision Support Tool",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

LOGO_URL = "https://raw.githubusercontent.com/NATURE-DEMO/Decision_Support_Tool/main/images/main_logo.png"

# ── STYLES ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@300;400;600&family=Inter:wght@300;400;500;600&display=swap');

[data-testid="stSidebarNav"]       { display: none; }
[data-testid="stAppViewContainer"] { background: #f4f6f4; }
[data-testid="stHeader"]           { background: transparent; }
[data-testid="collapsedControl"]   { display: none; }
html, body, [class*="css"]         { font-family: 'Inter', sans-serif; }

/* ── PAGE WRAPPER ── */
.nd-page {
    max-width: 860px;
    margin: 0 auto;
    padding: 2.5rem 1rem 4rem;
}

/* ── LOGO AREA ── */
.nd-logo-wrap {
    text-align: center;
    margin-bottom: 2rem;
}

/* ── HERO ── */
.nd-hero {
    background: #ffffff;
    border: 1px solid #cfdecf;
    border-top: 4px solid #2e6b2e;
    border-radius: 14px;
    padding: 2.75rem 2.5rem 2.5rem;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 12px rgba(30,60,30,0.06);
}
.nd-hero-title {
    font-family: 'Source Serif 4', serif;
    font-size: 2.2rem;
    font-weight: 300;
    color: #1a3a1a;
    line-height: 1.25;
    margin: 0 0 0.65rem;
    letter-spacing: -0.01em;
}
.nd-hero-title strong {
    font-weight: 600;
    color: #2e6b2e;
}
.nd-hero-sub {
    font-size: 0.97rem;
    font-weight: 300;
    color: #587058;
    letter-spacing: 0.01em;
    margin: 0 0 2rem;
    line-height: 1.6;
}

/* ── PRIMARY LAUNCH BUTTON ── */
.nd-launch-btn {
    display: inline-block;
    background: #2e6b2e;
    color: #ffffff !important;
    text-decoration: none !important;
    padding: 0.85rem 2.5rem;
    border-radius: 9px;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    box-shadow: 0 2px 10px rgba(46,107,46,0.30);
    transition: background 0.18s, box-shadow 0.18s, transform 0.15s;
    margin-bottom: 0.65rem;
}
.nd-launch-btn:hover {
    background: #1a3a1a;
    box-shadow: 0 4px 18px rgba(46,107,46,0.35);
    transform: translateY(-1px);
    color: #c4dcc4 !important;
    text-decoration: none !important;
}
.nd-launch-note {
    font-size: 0.74rem;
    color: #8aaa8a;
    margin-top: 0.5rem;
    font-weight: 300;
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
    padding: 0.9rem 0.6rem;
    text-align: center;
}
.nd-cap-num {
    font-family: 'Source Serif 4', serif;
    font-size: 1.6rem;
    font-weight: 600;
    color: #2e6b2e;
    display: block;
    line-height: 1;
    margin-bottom: 0.25rem;
}
.nd-cap-lbl {
    font-size: 0.66rem;
    font-weight: 400;
    color: #7a9a7a;
    line-height: 1.4;
}

/* ── ABOUT PANEL ── */
.nd-about {
    background: #ffffff;
    border: 1px solid #cfdecf;
    border-radius: 12px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 6px rgba(30,60,30,0.04);
}
.nd-about-title {
    font-family: 'Source Serif 4', serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: #1a3a1a;
    margin: 0 0 0.75rem;
}
.nd-about p {
    font-size: 0.85rem;
    font-weight: 300;
    color: #3a5a3a;
    line-height: 1.85;
    margin: 0 0 0.75rem;
}
.nd-about p:last-child { margin-bottom: 0; }

/* ── SECONDARY LINKS ROW ── */
.nd-secondary {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    justify-content: center;
    margin-bottom: 2rem;
}
.nd-sec-link {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.8rem;
    font-weight: 500;
    color: #2e6b2e !important;
    text-decoration: none !important;
    background: #ffffff;
    border: 1px solid #cfdecf;
    border-radius: 8px;
    padding: 0.45rem 0.95rem;
    transition: background 0.15s, border-color 0.15s;
}
.nd-sec-link:hover {
    background: #edf5ed;
    border-color: #90c890;
    color: #1a3a1a !important;
    text-decoration: none !important;
}

/* ── FOOTER ── */
.nd-footer {
    border-top: 1px solid #cfdecf;
    padding-top: 1.25rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 0.75rem;
}
.nd-footer-left {
    font-size: 0.74rem;
    font-weight: 300;
    color: #8aaa8a;
    line-height: 1.7;
}
.nd-footer-left strong {
    color: #587058;
    font-weight: 500;
}
.nd-footer-right {
    font-size: 0.7rem;
    font-weight: 300;
    color: #aac4aa;
    text-align: right;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ── CENTRED NARROW LAYOUT via columns ─────────────────────────────────────────
_, centre, _ = st.columns([1, 3, 1])

with centre:

    # Logo
    try:
        st.image(LOGO_URL, use_container_width=True)
    except Exception:
        st.markdown("<h2 style='text-align:center;color:#2e6b2e;'>NATURE-DEMO</h2>",
                    unsafe_allow_html=True)

    # ── HERO ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="nd-hero">
        <h1 class="nd-hero-title">
            Nature-Based Solutions for<br><strong>Climate-Resilient Infrastructure</strong>
        </h1>
        <p class="nd-hero-sub">
            A Horizon Europe decision support platform for climate risk assessment
            and Nature-Based Solution recommendation across European infrastructure.
        </p>
        <a href="/integrated_dst" class="nd-launch-btn">
            Launch the Decision Support Tool &nbsp;→
        </a>
        <p class="nd-launch-note">Sign-up or log in required &nbsp;·&nbsp; Free for project partners</p>
    </div>
    """, unsafe_allow_html=True)

    # ── CAPABILITIES STRIP ────────────────────────────────────────────────────
    st.markdown("""
    <div class="nd-caps">
        <div class="nd-cap">
            <span class="nd-cap-num">6</span>
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

    # ── ABOUT ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="nd-about">
        <h2 class="nd-about-title">About the platform</h2>
        <p>
            NATURE-DEMO is a Horizon Europe Innovation Action (Grant No.&nbsp;101157448) that develops
            and validates Nature-Based Solutions (NbS) for protecting critical infrastructure
            against natural hazards and climate change, with a focus on Alpine and peri-Alpine regions.
        </p>
        <p>
            This Decision Support Tool — the primary software deliverable of Work Package 2, Task 2.3
            (University of Rostock) — integrates a multi-level risk assessment framework with
            EURO-CORDEX climate projections to help infrastructure managers and project partners
            evaluate and rank NbS interventions under present and future climate scenarios.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── SECONDARY LINKS ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="nd-secondary">
        <a class="nd-sec-link"
           href="https://nature-demo.github.io/Decision_Support_Tool/"
           target="_blank">
            📖&nbsp; Documentation
        </a>
        <a class="nd-sec-link"
           href="https://naturedemo-clima-ind.dic-cloudmate.eu"
           target="_blank">
            🌡️&nbsp; Climate Data Visualisation
        </a>
        <a class="nd-sec-link"
           href="https://www.nature-demo.eu"
           target="_blank">
            🌐&nbsp; Project Website
        </a>
        <a class="nd-sec-link"
           href="https://github.com/NATURE-DEMO/Decision_Support_Tool"
           target="_blank">
            ⌨️&nbsp; GitHub
        </a>
        <a class="nd-sec-link"
           href="https://nature-demo.eu/contact"
           target="_blank">
            📧&nbsp; Contact
        </a>
    </div>
    """, unsafe_allow_html=True)

    # ── FOOTER ────────────────────────────────────────────────────────────────
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
