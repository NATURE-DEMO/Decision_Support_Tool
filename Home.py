import streamlit as st
import base64
import requests

st.set_page_config(
    page_title="NATURE DEMO - Decision Support Tool",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# GitHub logo URL
LOGO_URL = "https://raw.githubusercontent.com/NATURE-DEMO/Decision_Support_Tool/main/images/main_logo.png"


@st.cache_data(ttl=3600)
def get_logo_base64(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return base64.b64encode(response.content).decode()
    except Exception:
        return None


# Custom CSS
st.markdown("""
    <style>
    /* Hide default Streamlit page navigation in sidebar */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f8ff;
        border-left: 5px solid #2e7d32;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .feature-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .feature-card h4 {
        color: #2e7d32;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .feature-card ul {
        list-style-type: none;
        padding-left: 0;
    }
    .feature-card li {
        padding: 0.25rem 0;
    }
    .cta-button {
        background-color: #2e7d32;
        color: white;
        padding: 0.75rem 2rem;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        margin: 1rem 0;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    .cta-button:hover {
        background-color: #1b5e20;
        color: white;
        text-decoration: none;
    }
    </style>
""", unsafe_allow_html=True)

# Display Logo
logo_b64 = get_logo_base64(LOGO_URL)
if logo_b64:
    st.markdown(f"""
        <div class="logo-container">
        <a href="https://www.nature-demo.eu" target="_blank">
            <img src="data:image/png;base64,{logo_b64}" width="400">
        </a>
        </div>
    """, unsafe_allow_html=True)

# Main Header
st.markdown("""
    <div class="main-header">
        <h1>🌿 NATURE DEMO Decision Support Tool</h1>
        <p style="font-size: 1.2rem; color: #666;">
            Empowering Climate Resilience through Nature-Based Solutions
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# About Section
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
        <div class="info-box">
            <h2>📖 About the NATURE DEMO Project</h2>
            <p>
                The NATURE DEMO project demonstrates innovative nature-based solutions (NbS) 
                for critical infrastructure protection across Europe. This tool suite helps 
                stakeholders assess climate risks, evaluate infrastructure resilience, and 
                make informed decisions about protective measures.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        ### 🎯 Key Objectives
        
        - **Risk Assessment**: Evaluate infrastructure vulnerability to natural hazards
        - **NbS Evaluation**: Compare nature-based solutions with traditional grey infrastructure
        - **Decision Support**: Provide data-driven insights for climate adaptation planning
        - **Stakeholder Engagement**: Facilitate participatory risk assessment processes
    """)

with col2:
    st.markdown("""
        <div class="feature-card">
            <h3>🔗 Quick Links</h3>
            <ul style="list-style: none; padding: 0;">
                <li>🌐 <a href="https://nature-demo.eu" target="_blank">Project Website</a></li>
                <li>📚 <a href="https://github.com/NATURE-DEMO/Decision_Support_Tool" target="_blank">GitHub Repository</a></li>
                <li>📧 <a href="https://nature-demo.eu/contact" target="_blank">Contact Us</a></li>
                <li>📄 <a href="https://nature-demo.eu/work-packages/work-package-2" target="_blank">Documentation</a></li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Applications Overview
st.markdown("## 🛠️ Available Applications")

col_app1, col_app2, col_app3 = st.columns(3)

with col_app1:
    st.markdown("""
        <div class="feature-card">
            <h3> <a href="/General_DST"> 📊 General Decision Support Tool </a></h3>
            <p><strong>Purpose:</strong> Analyze any geographical area for infrastructure risk assessment</p>
            <h4>Features:</h4>
            <ul>
                <li>🗺️ Interactive map selection and polygon drawing</li>
                <li>🏗️ OpenStreetMap infrastructure extraction</li>
                <li>🌡️ Köppen-Geiger climate classification</li>
                <li>🤖 AI-powered contextual reports (via Google Gemini)</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col_app2:
    st.markdown("""
        <div class="feature-card">
            <h3> <a href="/Specific_Site_DST_v2"> 🗺️ Specific Site Decision Support Tool </a></h3>
            <p><strong>Purpose:</strong> Detailed analysis of pre-configured NATURE DEMO sites</p>
            <h4>Features:</h4>
            <ul>
                <li>📍 Pre-configured demo sites across Europe</li>
                <li>📋 Site-specific infrastructure inventories</li>
                <li>📊 Multi-level risk assessment (Levels 1-3)</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col_app3:
    st.markdown("""
        <div class="feature-card">
            <h3> <a href="https://naturedemo-clima-ind.dic-cloudmate.eu"> 🌡️ European Climate Data Visualization </a></h3>
            <p><strong>Purpose:</strong> Interactive climate indices analysis across European cities</p>
            <h4>Features:</h4>
            <ul>
                <li>📍 Search cities across Europe</li>
                <li>📊 Climate indices visualization</li>
                <li>📈 Future scenario projections</li>
            </ul>
            <h4>Best For:</h4>
            <p>Analyzing historical and projected climate data for European locations.</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# How to Use Section
st.markdown("## 📖 How to Use This Tool")

st.markdown("""
### Getting Started

1. **Choose Your Application**  
   Use the sidebar navigation buttons to access different tools:
   - 📊 General DST - For exploring any location
   - 🗺️ Specific Site DST - For NATURE DEMO demo sites
   - 🌡️ Climate Visualization - For European climate data

2. **General DST Workflow**
   - Search for a location or draw a polygon on the map
   - Select infrastructure types to extract
   - Generate AI-powered reports and climate analysis
   - Input risk ratings and generate visualizations

3. **Specific Site DST Workflow**
   - Select a demo site from the sidebar
   - Review site information and maps
   - Navigate through assessment levels
   - Analyze pre-configured risk data and interpretations

4. **Export Results**
   - Download generated reports
   - Save visualizations and data tables
   - Share insights with stakeholders
""")

st.markdown("---")

# Technical Information
with st.expander("⚙️ Technical Information"):
    st.markdown("""
    ### System Requirements
    
    - **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)
    - **Internet Connection**: Required for map tiles and AI features
    - **API Keys**: Gemini API key required for AI report generation (configured on deployment)
    
    ### Data Sources
    
    - **Infrastructure Data**: OpenStreetMap (via Overpass API)
    - **Climate Data**: Köppen-Geiger Climate Classification (1991-2020)
    - **Basemaps**: CartoDB, OpenTopoMap, Esri
    - **AI Analysis**: Google Gemini 2.5 Flash with Google Search integration
    
    ### Privacy & Data
    
    - No personal data is collected or stored
    - All analysis is performed in real-time
    - Geographic queries are sent to public APIs (OSM, Nominatim)
    - AI features use Google Gemini API (subject to Google's privacy policy)
    """)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p>
            <strong>NATURE DEMO</strong> | 
            Horizon Europe Project | 
            Grant Agreement No. 101037525
        </p>
        <p style="font-size: 0.9rem;">
            © 2025 NATURE DEMO Consortium | 
            <a href="https://nature-demo.eu/privacy" target="_blank">Privacy Policy</a> | 
            <a href="https://nature-demo.eu/terms" target="_blank">Terms of Use</a>
        </p>
    </div>
""", unsafe_allow_html=True)


# ============= SIDEBAR =============
with st.sidebar:
    st.markdown(f"""
        <a href="https://www.nature-demo.eu" target="_blank">
            <img src="https://raw.githubusercontent.com/NATURE-DEMO/Decision_Support_Tool/main/images/main_logo.png" width="250" />
        </a>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Sidebar Instructions
    st.success("👇 Select an application to get started!")

    st.markdown("### 🚀 Quick Navigation")

    # Navigation buttons
    # if st.button("📊 General DST", use_container_width=True, type="primary"):
    #     st.switch_page("pages/General_DST.py")

    # if st.button("🗺️ Specific Site DST", use_container_width=True, type="primary"):
    #     st.switch_page("pages/Specific_Site_DST.py")
    st.link_button("📊 General DST",
                   "/General_DST", use_container_width=True)
    st.link_button("🗺️ Specific Site DST",
                   "/Specific_Site_DST_v2", use_container_width=True)
    st.link_button("🌡️ Climate Visualization",
                   "https://naturedemo-clima-ind.dic-cloudmate.eu", use_container_width=True)

    st.markdown("---")

    st.markdown("""
        ### 💡 Quick Tips
        
        - **General DST**: Best for exploring new locations
        - **Specific Site DST**: Best for detailed demo site analysis
        - **Climate Viz**: Analyze European climate indices
        - Both tools support risk assessment and visualization
        - AI features require internet connection
    """)
