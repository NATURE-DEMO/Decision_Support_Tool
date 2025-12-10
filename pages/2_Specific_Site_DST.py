import streamlit as st
import pandas as pd
import numpy as np
import base64
import requests
import io
import re
import os
import bcrypt
import time
import datetime
from sqlalchemy import text
import leafmap.foliumap as leafmap
import rasterio
from rasterio.io import MemoryFile
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import contextily as cx
import extra_streamlit_components as stx 

# ---------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Decision Support Tool", layout="centered")

st.markdown("""
    <style>
        .justified-text { text-align: justify; display:flex; flex-direction:column; justify-content:flex-end; min-height:100px; }
        
        .custom-link { 
            text-decoration: none; 
            color: white !important; 
            display: block;
        }
        .custom-link:hover {
            color: white !important; 
            text-decoration: none;
        }

        .custom-button-container {
            width: 100%; padding: 10px; margin-bottom: 10px; border-radius: 10px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.2); transition: transform 0.12s;
            background-size: cover; background-position: center; color: white; text-shadow: 1px 1px 2px black;
        }
        .custom-button-container:hover { transform: scale(1.02); box-shadow: 4px 4px 10px rgba(0,0,0,0.25);}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 2. DATABASE & AUTHENTICATION (SAFE MODE - NO CACHING)
# ---------------------------------------------------------------------------

db_url = os.getenv("SUPABASE_URL")
if db_url:
    conn = st.connection("supabase", type="sql", url=db_url)
else:
    conn = st.connection("supabase", type="sql")

def init_db():
    with conn.session as s:
        s.execute(text('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY, 
                password BYTEA, 
                name TEXT, 
                lastname TEXT, 
                email TEXT, 
                job_title TEXT, 
                industry TEXT,
                role TEXT, 
                approved INTEGER
            );
        '''))
        s.execute(text('''
            CREATE TABLE IF NOT EXISTS inputs_v3 (
                site_key TEXT, 
                table_type TEXT, 
                row_name TEXT, 
                column_name TEXT, 
                new_value REAL, 
                username TEXT, 
                role TEXT,
                UNIQUE(site_key, table_type, row_name, column_name, username)
            );
        '''))
        s.commit()

try:
    init_db()
except Exception:
    pass

def run_query(query_str, params=None):
    with conn.session as s:
        result = s.execute(text(query_str), params)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df

def hash_password(password): return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
def check_password(password, hashed): return bcrypt.checkpw(password.encode(), hashed)

def check_password_strength(password):
    score = 0
    if len(password) >= 10: score += 1
    if re.search(r'[A-Z]', password): score += 1
    if re.search(r'[a-z]', password): score += 1
    if re.search(r'[0-9]', password): score += 1
    if re.search(r'[^A-Za-z0-9]', password): score += 1
    if score == 5: return "Strong 💪"
    if score >= 3: return "Good 👍"
    return "Weak ⚠️"

def create_user(username, password, name, lastname, email, job_title, industry, role="viewer"):
    try:
        with conn.session as s:
            s.execute(
                text("INSERT INTO users (username, password, name, lastname, email, job_title, industry, role, approved) VALUES (:u, :p, :n, :l, :e, :j, :i, :r, :a)"),
                params={"u": username, "p": hash_password(password), "n": name, "l": lastname, "e": email, "j": job_title, "i": industry, "r": role, "a": 0}
            )
            s.commit()
        return True
    except Exception:
        return False

def change_user_password(username, old_pw, new_pw):
    try:
        with conn.session as s:
            result = s.execute(text('SELECT password FROM users WHERE username = :u'), params={"u": username})
            row = result.fetchone()
            if row:
                stored_pw = row[0]
                if isinstance(stored_pw, memoryview): stored_pw = bytes(stored_pw)
                
                if check_password(old_pw, stored_pw):
                    new_hashed = hash_password(new_pw)
                    s.execute(text('UPDATE users SET password = :p WHERE username = :u'), params={"p": new_hashed, "u": username})
                    s.commit()
                    return True, "Password updated successfully!"
                else:
                    return False, "Incorrect current password."
        return False, "User error."
    except Exception as e:
        return False, str(e)

def verify_login(username, password):
    try:
        with conn.session as s:
            result = s.execute(text('SELECT password, role, approved, name, lastname FROM users WHERE username = :u'), params={"u": username})
            row = result.fetchone()

        if row:
            stored_pw = row[0]
            if isinstance(stored_pw, memoryview): stored_pw = bytes(stored_pw)
            
            if check_password(password, stored_pw):
                return {"role": row[1], "approved": row[2], "name": row[3], "lastname": row[4]}
    except Exception:
        pass
    return None

def verify_login_status_only(username):
    try:
        with conn.session as s:
            result = s.execute(text('SELECT role, approved, name, lastname FROM users WHERE username = :u'), params={"u": username})
            row = result.fetchone()
        if row:
            return {"role": row[0], "approved": row[1], "name": row[2], "lastname": row[3]}
    except Exception:
        pass
    return None

# ---------------------------------------------------------------------------
# 3. DATA HELPERS
# ---------------------------------------------------------------------------
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/NATURE-DEMO/Decision_Support_Tool/main"
GITHUB_API_BASE = "https://api.github.com/repos/NATURE-DEMO/Decision_Support_Tool/contents/texts"
GITHUB_IMAGE_BASE_URL = f"{GITHUB_RAW_BASE}/images"
GITHUB_TIFF_URL = f"{GITHUB_RAW_BASE}/Koppen/1991-2020/koppen_geiger_0p1.tif"

items = [
    {"name": "Demo site 1-A", "address": "Lattenbach Valley, Austria", "icon_url": f"{GITHUB_IMAGE_BASE_URL}/logo1.jpg", "github_key": "demo1a", "coordinate": [47.148472, 10.499805]},
    {"name": "Demo site 1-B", "address": "Brunntal, Austria", "icon_url": f"{GITHUB_IMAGE_BASE_URL}/logo2.jpg", "github_key": "demo1b", "coordinate": [47.625027, 15.052111]},
    {"name": "Demo site 2", "address": "Brasov City, Romania", "icon_url": f"{GITHUB_IMAGE_BASE_URL}/logo3.jpg", "github_key": "demo2", "coordinate": [45.647078, 25.593030]},
    {"name": "Demo site 3", "address": "Slovenia", "icon_url": f"{GITHUB_IMAGE_BASE_URL}/logo4.jpg", "github_key": "demo3", "coordinate": [46.0345, 14.461]},
    {"name": "Demo site 4", "address": "Zvolen, Slovakia", "icon_url": f"{GITHUB_IMAGE_BASE_URL}/logo5.jpg", "github_key": "demo4", "coordinate": [48.5707, 19.1462]},
    {"name": "Demo site 5", "address": "Globocica, Macedonia", "icon_url": f"{GITHUB_IMAGE_BASE_URL}/logo6.png", "github_key": "demo5", "coordinate": [48.5647, 19.114430]},
]
BACKGROUND_IMAGE_URL = f"{GITHUB_IMAGE_BASE_URL}/main_logo.png"

@st.cache_data(ttl=3600)
def cached_get(url: str) -> bytes: return requests.get(url, timeout=20).content
@st.cache_data(ttl=3600)
def cached_json(url: str): return requests.get(url, timeout=20).json()
@st.cache_data(ttl=3600)
def cached_text(url: str) -> str: return requests.get(url, timeout=20).text
@st.cache_data(ttl=3600)
def cached_base64_image(url: str) -> str | None:
    try: return base64.b64encode(cached_get(url)).decode("utf-8")
    except: return None
@st.cache_data(ttl=3600)
def cached_read_excel(url: str) -> pd.DataFrame | None:
    try: return pd.read_excel(io.BytesIO(cached_get(url)))
    except: return None
@st.cache_data(ttl=600)
def list_github_folder(github_key: str): return cached_json(f"{GITHUB_API_BASE}/{github_key}/level1?ref=main")
@st.cache_data(ttl=600)
def get_sorted_txt_files(github_key: str):
    try:
        items = cached_json(f"{GITHUB_API_BASE}/{github_key}?ref=main")
        txts = [i for i in items if i.get("name", "").endswith(".txt")]
        txts.sort(key=lambda f: int(re.match(r"^(\d+)", f["name"]).group(1)) if re.match(r"^(\d+)", f["name"]) else float("inf"))
        return txts
    except: return []
@st.cache_data(ttl=600)
def download_file_bytes(download_url: str) -> bytes: return cached_get(download_url)
def get_series_display_names():
    return {"CI": "Condition of the infrastructure (CI)", "CIH": "Condition of CI after exposure to hazard (CIH)", "CIHG": "Condition of CI after exposure to hazard but protected by GPI (CIHG)", "CIHN": "Condition of CI after exposure to hazard but protected by NbS (CIHN)", "CIHGN": "Condition of CI after exposure to hazard but protected by both GPI and NBS (CIHGN)"}

# ---------------------------------------------------------------------------
# NEW: reliable Excel downloader using GitHub API listing (fix for Level1)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=600)
def get_excel_from_github(site_key: str, filename: str) -> pd.DataFrame | None:
    """
    List level1 folder via GitHub API and use the provided download_url to fetch the Excel.
    Returns a DataFrame or None.
    """
    try:
        contents = cached_json(f"{GITHUB_API_BASE}/{site_key}/level1?ref=main")
        if not contents:
            return None
        match = next((f for f in contents if f.get("name", "").lower() == filename.lower()), None)
        if match and match.get("download_url"):
            data_bytes = download_file_bytes(match["download_url"])
            return pd.read_excel(io.BytesIO(data_bytes))
    except Exception:
        return None
    return None

# Charts
KOPPEN_COLORS = np.array([[0,0,255], [0,120,255], [70,170,250], [255,0,0], [255,150,150], [245,165,0], [255,220,100], [255,255,0], [200,200,0], [150,150,0], [150,255,150], [100,200,100], [50,150,50], [200,255,80], [100,255,80], [50,200,0], [255,0,255], [200,0,200], [150,50,150], [150,100,150], [170,175,255], [90,120,220], [75,80,180], [50,0,135], [0,255,255], [55,200,255], [0,125,125], [0,70,95], [178,178,178], [102,102,102]]) / 255.0
KOPPEN_CLASSES = {i: c for i, c in enumerate(["Af", "Am", "Aw", "BWh", "BWk", "BSh", "BSk", "Csa", "Csb", "Csc", "Cwa", "Cwb", "Cwc", "Cfa", "Cfb", "Cfc", "Dsa", "Dsb", "Dsc", "Dsd", "Dwa", "Dwb", "Dwc", "Dwd", "Dfa", "Dfb", "Dfc", "Dfd", "ET", "EF"], 1)}

def quick_koppen_map(tif_path, lat, lon):
    try:
        r = requests.get(tif_path)
        if r.status_code != 200: return None
        with rasterio.open(io.BytesIO(r.content)) as src:
            data = src.read(1)
            row_min, col_min = src.index(lon-1, lat+1)
            row_max, col_max = src.index(lon+1, lat-1)
            r_s, r_e = sorted([row_min, row_max])
            c_s, c_e = sorted([col_min, col_max])
            data_cropped = data[r_s:r_e, c_s:c_e]
    except: return None
    data_cropped = np.where(data_cropped == 0, np.nan, data_cropped)
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(data_cropped, cmap=ListedColormap(KOPPEN_COLORS), extent=(lon-1, lon+1, lat-1, lat+1), origin='upper', alpha=0.6, zorder=2)
    cx.add_basemap(ax, crs='EPSG:4326', source=cx.providers.OpenTopoMap, alpha=0.8, zorder=1)
    ax.set_title(f"Koppen-Geiger Climate Map")
    plt.colorbar(im, ticks=range(1, 31), ax=ax, fraction=0.046, pad=0.04).ax.set_yticklabels(list(KOPPEN_CLASSES.values()), fontsize=8)
    return fig

def create_radar_chart_plotly(kpis_df: pd.DataFrame, selected_series: list, title: str):
    df = kpis_df.copy()
    categories = df.iloc[:, 0].astype(str).tolist()
    fig = go.Figure()
    for col in selected_series:
        vals = pd.to_numeric(df[col], errors="coerce").tolist()
        if not vals: continue
        vals_loop = vals + [vals[0]]
        cats_loop = categories + [categories[0]]
        fig.add_trace(go.Scatterpolar(r=vals_loop, theta=cats_loop, fill="toself", name=col))
    fig.update_layout(polar=dict(radialaxis=dict(range=[1,5], tickvals=[1,2,3,4,5])), title=title, height=650)
    return fig

def create_kpi_analysis_plots_plotly(kpis_df: pd.DataFrame, el_df: pd.DataFrame, selected_item_name: str):
    df1 = kpis_df.set_index(kpis_df.columns[0])
    df2 = el_df.set_index(el_df.columns[0])
    figs = []
    max_pairs = min(4, max(0, len(df1.columns)-1), len(df2.columns))
    x_grid = np.linspace(0, 6, 60)
    y_grid = np.linspace(0, 6, 60)
    X, Y = np.meshgrid(x_grid, y_grid)
    Z_heatmap = (X + Y) / 2
    def fmt(l): return f"CI<sub>{l[2:]}</sub>" if isinstance(l, str) and l.startswith("CI") else str(l)
    for i in range(max_pairs):
        col_f1 = df1.columns[i+1] if (i+1) < len(df1.columns) else df1.columns[-1]
        col_f2 = df2.columns[i] if i < len(df2.columns) else df2.columns[-1]
        x = pd.to_numeric(df2[col_f2], errors='coerce')
        y = pd.to_numeric(df1[col_f1], errors='coerce')
        df_plot = pd.DataFrame({"Extent of Loss": x, "Condition": y, "Original_Label": df1.index.map(str)}).dropna()
        df_plot["Display_Label"] = df_plot["Original_Label"].apply(fmt)
        fig = go.Figure()
        fig.add_trace(go.Heatmap(z=Z_heatmap, x=x_grid, y=y_grid, colorscale=[[0,'green'],[0.5,'yellow'],[1,'red']], zmin=1, zmax=5, showscale=False, hoverinfo='none'))
        if not df_plot.empty:
            df_plot["Extent_j"] = df_plot["Extent of Loss"] + np.random.uniform(-0.15, 0.15, size=(len(df_plot),))
            df_plot["Condition_j"] = df_plot["Condition"] + np.random.uniform(-0.15, 0.15, size=(len(df_plot),))
            fig.add_trace(go.Scatter(x=df_plot["Extent_j"], y=df_plot["Condition_j"], mode='markers+text', 
                                     text=df_plot["Display_Label"], textposition=["top right" if i%2==0 else "bottom right" for i in range(len(df_plot))], 
                                     textfont=dict(size=10), marker=dict(size=12, line=dict(width=1, color="black"))))
        fig.update_layout(title=f"<b>{fmt(col_f1)}</b> vs Extent of Loss", xaxis=dict(range=[0, 6]), yaxis=dict(range=[0, 6]), height=450, showlegend=False)
        figs.append(fig)
    return figs

@st.cache_data(ttl=600)
def get_interpretation_text(k):
    try: return cached_text(f"{GITHUB_RAW_BASE}/texts/{k}/level1/interpretation.txt")
    except: return None
@st.cache_data(ttl=600)
def get_climate_report_text(k):
    try: return cached_text(f"{GITHUB_RAW_BASE}/texts/{k}/climate/climate_report.txt")
    except: return None

# ---------------------------------------------------------------------------
# 4. COOKIE & LOGIN GATEKEEPER
# ---------------------------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
    st.session_state['username'] = None
    st.session_state['user_name_full'] = None

cookie_manager = stx.CookieManager(key="cookie_mgr")

query_params = st.query_params
if "item" in query_params:
    st.session_state['selected_site_key'] = query_params["item"]
elif 'selected_site_key' not in st.session_state:
    st.session_state['selected_site_key'] = "demo1a"

if "logout" in query_params:
    cookie_user = None
else:
    cookie_user = cookie_manager.get(cookie="dst_username")

if not st.session_state['logged_in'] and cookie_user:
    user_data = verify_login_status_only(cookie_user)
    if user_data and user_data["approved"]:
        st.session_state['logged_in'] = True
        st.session_state['user_role'] = user_data["role"]
        st.session_state['username'] = cookie_user
        st.session_state['user_name_full'] = f"{user_data['name']} {user_data['lastname']}"
        st.rerun()

if not st.session_state['logged_in']:
    auth_bg_b64 = cached_base64_image(f"{GITHUB_IMAGE_BASE_URL}/background.png")
    if auth_bg_b64:
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{auth_bg_b64}");
                background-size: 100vw 100vh;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            [data-testid="stForm"] {{
                background-color: rgba(255, 255, 255, 0.95);
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            [data-testid="stForm"] label, [data-testid="stForm"] p, [data-testid="stForm"] h1 {{
                color: #000000 !important;
            }}
            [data-testid="stForm"] button {{
                background-color: #ffffff !important; 
                color: #000000 !important;
                border: 2px solid #000000 !important;
                font-weight: bold !important;
            }}
            [data-testid="stForm"] button:hover {{
                background-color: #f0f0f0 !important;
                border-color: #333333 !important;
            }}
            [data-testid="stSidebar"] {{
                display: none;
            }}
            [data-testid="stSidebarCollapsedControl"] {{
                display: none;
            }}
            </style>
            """, unsafe_allow_html=True)
    
    st.title("Decision Support Tool")
    auth_choice = st.radio(
    "Authentication",
    ["Login", "Sign Up"], 
    horizontal=True, 
    label_visibility="collapsed"
)

    if auth_choice == "Login":
        with st.form("login_form"):
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                user_data = verify_login(user, pw)
                if user_data is None: 
                    st.error("Invalid credentials")
                elif not user_data["approved"]: 
                    st.warning("Account waiting for Admin approval.")
                else:
                    expires = datetime.datetime.now() + datetime.timedelta(days=7)
                    cookie_manager.set("dst_username", user, expires_at=expires)
                    st.session_state['logged_in'] = True
                    st.session_state['user_role'] = user_data["role"]
                    st.session_state['username'] = user
                    st.session_state['user_name_full'] = f"{user_data['name']} {user_data['lastname']}"
                    time.sleep(0.5)
                    st.rerun()
                
    elif auth_choice == "Sign Up":
        with st.form("signup_form"):
            new_user = st.text_input("Username")
            new_name = st.text_input("First Name")
            new_last = st.text_input("Last Name")
            new_email = st.text_input("Email Address")
            new_title = st.text_input("Job Title")
            new_industry = st.text_input("Industry")
            new_pw = st.text_input("Password", type="password")
            
            if new_pw:
                strength = check_password_strength(new_pw)
                if strength == "Strong 💪": st.success(f"Password Strength: {strength}")
                elif strength == "Good 👍": st.warning(f"Password Strength: {strength}")
                else: st.error(f"Password requires: 10+ chars, Uppercase, Lowercase, Number, Symbol.")

            req_role = st.selectbox("Requested Role", ["viewer", "expert"]) 
            
            if st.form_submit_button("Create Account"):
                if not all([new_user, new_name, new_last, new_email, new_title, new_industry, new_pw]):
                    st.error("Please fill in all required fields.")
                elif check_password_strength(new_pw) in ["Weak ⚠️", "Good 👍"]:
                     st.error("Password must be Strong 💪 (10+ chars, upper, lower, number, symbol) to register.")
                else:
                    if create_user(new_user, new_pw, new_name, new_last, new_email, new_title, new_industry, req_role): 
                        st.success("Account created! Wait for Admin approval.")
                    else: st.error("Username taken.")

    st.stop()

# ---------------------------------------------------------------------------
# 5. DATA FETCHING LOGIC (POSTGRESQL ADAPTED)
# ---------------------------------------------------------------------------

def get_consensus_data(site_key, table_type, original_df):
    if original_df is None or original_df.empty: return original_df

    final_df = original_df.copy()
    numeric_cols = final_df.select_dtypes(include=np.number).columns
    
    for i in range(len(final_df)):
        row_label = str(final_df.iloc[i, 0])
        for col in numeric_cols:
            try: original_val = float(final_df.at[i, col])
            except: continue

            admin_df = run_query(
                "SELECT new_value FROM inputs_v3 WHERE site_key=:s AND table_type=:t AND row_name=:r AND column_name=:c AND role='admin'",
                params={"s": site_key, "t": table_type, "r": row_label, "c": col}
            )
            
            if not admin_df.empty:
                final_df.at[i, col] = admin_df['new_value'].iloc[0]
            else:

                expert_df = run_query(
                    "SELECT new_value FROM inputs_v3 WHERE site_key=:s AND table_type=:t AND row_name=:r AND column_name=:c AND role='expert'",
                    params={"s": site_key, "t": table_type, "r": row_label, "c": col}
                )
                
                if not expert_df.empty:
                    avg_val = (original_val + expert_df['new_value'].sum()) / (1 + len(expert_df))
                    final_df.at[i, col] = avg_val
    return final_df

def get_user_personal_data(site_key, table_type, original_df, username):
    if original_df is None: return None
    personal_df = original_df.copy()
    numeric_cols = personal_df.select_dtypes(include=np.number).columns
    
    for i in range(len(personal_df)):
        row_label = str(personal_df.iloc[i, 0])
        for col in numeric_cols:
            user_data = run_query(
                "SELECT new_value FROM inputs_v3 WHERE site_key=:s AND table_type=:t AND row_name=:r AND column_name=:c AND username=:u",
                params={"s": site_key, "t": table_type, "r": row_label, "c": col, "u": username}
            )
            if not user_data.empty:
                personal_df.at[i, col] = user_data['new_value'].iloc[0]
    return personal_df

def save_user_input(site_key, table_type, edited_df, username, role):
    numeric_cols = edited_df.select_dtypes(include=np.number).columns
    
    with conn.session as s:
        for i in range(len(edited_df)):
            row_label = str(edited_df.iloc[i, 0])
            for col in numeric_cols:
                try:
                    val = float(edited_df.at[i, col])
                    s.execute(
                        text("""
                            INSERT INTO inputs_v3 (site_key, table_type, row_name, column_name, new_value, username, role) 
                            VALUES (:s, :t, :r, :c, :v, :u, :ro)
                            ON CONFLICT (site_key, table_type, row_name, column_name, username) 
                            DO UPDATE SET new_value = EXCLUDED.new_value
                        """),
                        params={"s": site_key, "t": table_type, "r": row_label, "c": col, "v": val, "u": username, "ro": role}
                    )
                except: pass
        s.commit()

# ---------------------------------------------------------------------------
# 6. SIDEBAR
# ---------------------------------------------------------------------------
with st.sidebar:

    logo_b64 = cached_base64_image(f"{GITHUB_IMAGE_BASE_URL}/main_logo.png")
    if logo_b64:
        st.markdown(f'<div style="text-align: center; margin-bottom: 20px;"><img src="data:image/png;base64,{logo_b64}" style="width: 100%;"></div>', unsafe_allow_html=True)
    
    if st.session_state.get('user_name_full'):
        st.markdown(f"**{st.session_state['user_name_full']}**")
        st.markdown(f"Role: **{st.session_state.get('user_role', 'None')}**")
        
        with st.expander("🔐 Change Password"):
            curr_pass = st.text_input("Current Password", type="password", key="cp_curr")
            new_pass = st.text_input("New Password", type="password", key="cp_new")
            conf_pass = st.text_input("Confirm New Password", type="password", key="cp_conf")
            
            if st.button("Update Password"):
                if new_pass != conf_pass:
                    st.error("New passwords do not match.")
                elif check_password_strength(new_pass) == "Weak ⚠️":
                    st.error("New password is too weak.")
                else:
                    success, msg = change_user_password(st.session_state['username'], curr_pass, new_pass)
                    if success: st.success(msg)
                    else: st.error(msg)
        
        st.divider()
    else:
        st.markdown(f"User: **{st.session_state.get('username', 'Unknown')}** ({st.session_state.get('user_role', 'None')})")

    if st.button("Logout"):
        try:
            cookie_manager.delete("dst_username")
        except KeyError:
            pass
        st.session_state.clear()
        st.query_params["logout"] = "true" 
        time.sleep(0.5)
        st.rerun()


    if st.session_state.get('user_role') == 'admin':
        with st.expander("🛡️ Admin Panel", expanded=True):

            users = run_query("SELECT username, role, approved, name, lastname, email, job_title, industry FROM users")
            pending = users[users['approved'] == 0]
            active = users[users['approved'] == 1]
            st.markdown("### ⏳ Pending")
            if not pending.empty:
                st.error(f"{len(pending)} Requests")
                target = st.selectbox("User", pending['username'], key="p_sel")
                
                user_info = pending[pending['username'] == target].iloc[0]
                with st.container(border=True):
                    st.caption("Request Details")
                    st.markdown(f"**Name:** {user_info['name']} {user_info['lastname']}")
                    st.markdown(f"**Email:** {user_info['email']}")
                    st.markdown(f"**Job:** {user_info['job_title']}")
                    st.markdown(f"**Industry:** {user_info['industry']}")

                curr_role = pending.loc[pending['username']==target, 'role'].iloc[0]
                new_role = st.selectbox("Assign Role", ["viewer", "expert", "admin"], index=["viewer", "expert", "admin"].index(curr_role) if curr_role in ["viewer", "expert", "admin"] else 0, key="r_sel")
                action = st.radio("Action", ["Approve", "Reject/Delete"], key="act_rad")
                if st.button("Process"):
                    with conn.session as s:
                        if action == "Approve":
                            s.execute(text("UPDATE users SET approved=1, role=:r WHERE username=:u"), params={"r": new_role, "u": target})
                            st.success(f"Approved {target}")
                        else:
                            s.execute(text("DELETE FROM users WHERE username=:u"), params={"u": target})
                            st.warning(f"Deleted {target}")
                        s.commit()
                    time.sleep(0.5)
                    st.rerun()
            else: st.success("No pending.")

            st.divider()
            st.markdown("### 📋 Audit")
            audit_df = run_query("SELECT * FROM inputs_v3 ORDER BY site_key, table_type")
            if not audit_df.empty:
                st.download_button("📥 Download Audit CSV", data=audit_df.to_csv(index=False).encode('utf-8'), file_name="expert_inputs_audit.csv", mime="text/csv")
            
            st.divider()
            st.markdown("### ✅ Active Users")
            st.dataframe(active[['username', 'role', 'name', 'lastname']], hide_index=True)
            if not active.empty:
                with st.popover("Delete User"):
                    target_del = st.selectbox("User", active['username'], key="del_act")
                    if target_del != st.session_state['username']:
                        if st.button("Confirm Delete"):
                            with conn.session as s:
                                s.execute(text("DELETE FROM users WHERE username=:u"), params={"u": target_del})
                                s.commit()
                            st.rerun()

    st.divider()
    
    st.write("### Select Site")
    for it in items:
        b64 = cached_base64_image(it["icon_url"])
        if b64:
            u = f"?item={it['github_key']}"
            h = f'''<a href="{u}" target="_self" class="custom-link"><div class="custom-button-container" style="background-image: url('data:image/png;base64,{b64}');"><h4 style="margin:0; padding:0; color:white;"><b>{it["name"]}</b></h4><p style="margin:0; padding:0; font-size:14px; color:white;">{it["address"]}</p></div></a>'''
            st.markdown(h, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 7. MAIN CONTENT
# ---------------------------------------------------------------------------
selected_key = st.session_state['selected_site_key']
items_map = {it["github_key"]: it for it in items}
selected_item = items_map.get(selected_key, items[0])
DEFAULT_CENTER = [41.500, 20.5308]
map_center = selected_item.get("coordinate", DEFAULT_CENTER)

st.title(f"Risk assessment for {selected_item['name']}: {selected_item['address']}")


with st.container():
    with st.expander("Site Information and Maps"):
        with st.expander("Site Information"):
            for f in get_sorted_txt_files(selected_item["github_key"]):
                st.markdown(f'<div class="justified-text"><h1 style="font-size:30px;">{os.path.splitext(f["name"])[0][1:]}</h1></div>', unsafe_allow_html=True)
                try: st.markdown(f'<div class="justified-text">{download_file_bytes(f["download_url"]).decode("utf-8").replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                except: pass
        
        with st.expander("Maps"):
            m = leafmap.Map(center=map_center, zoom=15, height="700px")
            m.add_basemap("SATELLITE")
            m.add_marker(map_center, tooltip=selected_item["name"])
            m.to_streamlit()
            
            st.subheader("Climate Classification")
            fig = quick_koppen_map(GITHUB_TIFF_URL, map_center[0], map_center[1])
            if fig: st.pyplot(fig)
            report = get_climate_report_text(selected_item["github_key"])
            if report: st.markdown(report)


with st.container():
    with st.expander("Level 1"):
        

        kpis_original = get_excel_from_github(selected_key, "1KPIs.xlsx")
        el_original   = get_excel_from_github(selected_key, "2el.xlsx")
        

        if kpis_original is None:
            st.error(f"⚠️ Failed to download 1KPIs.xlsx from GitHub. Check your internet connection or GitHub repo structure.")
        if el_original is None:
            st.warning(f"⚠️ Failed to download 2el.xlsx from GitHub.")


        kpis_consensus = get_consensus_data(selected_key, "KPI", kpis_original)
        el_consensus = get_consensus_data(selected_key, "EL", el_original)

        def render_table_and_editor(label, table_type, consensus_df, original_df):
            if consensus_df is None: 
                st.warning(f"No data available for {label}")
                return
            st.subheader(label)
            st.dataframe(consensus_df, width='stretch')
            
            user_role = st.session_state.get('user_role')
            if user_role in ['expert', 'admin']:
                personal_df = get_user_personal_data(selected_key, table_type, original_df, st.session_state['username'])
                
                with st.expander(f"✏️ Edit {label} ({st.session_state['username']})"):
                    st.info("Edit your personal values below. Changes are held until you click Save.")
                    

                    with st.form(key=f"form_{table_type}_{selected_key}"):
                        

                        edited = st.data_editor(personal_df, key=f"edit_{table_type}_{selected_key}")
                        

                        submit_button = st.form_submit_button(f"Save {label}")
                        
                        if submit_button:
                            save_user_input(selected_key, table_type, edited, st.session_state['username'], user_role)
                            st.success("Values Saved! Consensus updated.")
                            time.sleep(0.5)
                            st.rerun()

        with st.expander("Information tables"):
            render_table_and_editor("KPIs", "KPI", kpis_consensus, kpis_original)
            render_table_and_editor("Extent of Loss", "EL", el_consensus, el_original)

        with st.expander("Perceived risk"):
            st.subheader("KPI Radar Chart")
            if kpis_consensus is not None:
                sel = [s for s in kpis_consensus.columns[1:] if st.checkbox(get_series_display_names().get(s,s), value=True, key=f"chk_{s}")]
                if sel: st.plotly_chart(create_radar_chart_plotly(kpis_consensus, sel, f"Radar Chart of {selected_item['name']}"), width='stretch')
            else:
                st.warning("KPI data is missing, cannot generate Radar Chart.")

            st.subheader("KPI Analysis")
            if kpis_consensus is not None and el_consensus is not None:
                for f in create_kpi_analysis_plots_plotly(kpis_consensus, el_consensus, selected_item["name"]): st.plotly_chart(f, width='stretch')
            else:
                st.warning("Both KPI and Extent of Loss data are required for analysis plots.")

        with st.expander("Interpretation"):
            interp = get_interpretation_text(selected_item["github_key"])
            if interp: st.markdown(interp)
            else: st.warning("Interpretation text not found.")


with st.container():
    with st.expander("Level 2"):
        st.write("Under Construction")


with st.container():
    with st.expander("Level 3"):
        st.write("Under Construction")

