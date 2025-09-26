# =========================================================
# COMBINED STREAMLIT APP
# =========================================================

# --- Imports ---
import streamlit as st
import pandas as pd
import base64
import os
import requests
import re
import io
import leafmap.foliumap as leafmap
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import contextily as cx
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# =========================================================
# --- Function Definitions ---
# =========================================================

def get_base64_of_image(image_url):
    """Fetches an image from a URL and returns its Base64-encoded string."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to retrieve image from URL: {e}")
        return None


def quick_koppen_map(tif_path, lat, lon):
    """Ultra-simple Köppen map with fixed settings"""
    
    zoom = 1.0
    koppen_alpha = 0.6
    
    koppen_classes = {
        1: "Af", 2: "Am", 3: "Aw", 4: "BWh", 5: "BWk", 6: "BSh", 7: "BSk", 
        8: "Csa", 9: "Csb", 10: "Csc", 11: "Cwa", 12: "Cwb", 13: "Cwc", 
        14: "Cfa", 15: "Cfb", 16: "Cfc", 17: "Dsa", 18: "Dsb", 19: "Dsc", 
        20: "Dsd", 21: "Dwa", 22: "Dwb", 23: "Dwc", 24: "Dwd", 25: "Dfa", 
        26: "Dfb", 27: "Dfc", 28: "Dfd", 29: "ET", 30: "EF"
    }
    
    colors = [
        [0,0,255], [0,120,255], [70,170,250], [255,0,0], [255,150,150],
        [245,165,0], [255,220,100], [255,255,0], [200,200,0], [150,150,0],
        [150,255,150], [100,200,100], [50,150,50], [200,255,80], [100,255,80],
        [50,200,0], [255,0,255], [200,0,200], [150,50,150], [150,100,150],
        [170,175,255], [90,120,220], [75,80,180], [50,0,135], [0,255,255],
        [55,200,255], [0,125,125], [0,70,95], [178,178,178], [102,102,102]
    ]
    
    cmap = ListedColormap(np.array(colors) / 255.0)
    class_labels = [koppen_classes[i] for i in range(1, 31)]
    
    # Calculate bounds
    min_lon, max_lon = lon - zoom, lon + zoom
    min_lat, max_lat = lat - zoom, lat + zoom
    
    try:
        # Handle TIFF from URL or local
        if tif_path.startswith('http'):
            response = requests.get(tif_path)
            if response.status_code == 200:
                tif_file = io.BytesIO(response.content)
                with rasterio.open(tif_file) as src:
                    data = src.read(1)
                    row_min, col_min = src.index(min_lon, max_lat)
                    row_max, col_max = src.index(max_lon, min_lat)
                    row_start, row_end = sorted([row_min, row_max])
                    col_start, col_end = sorted([col_min, col_max])
                    data_cropped = data[row_start:row_end, col_start:col_end]
            else:
                st.error(f"Failed to download TIFF file from {tif_path}")
                return None
        else:
            with rasterio.open(tif_path) as src:
                data = src.read(1)
                row_min, col_min = src.index(min_lon, max_lat)
                row_max, col_max = src.index(max_lon, min_lat)
                row_start, row_end = sorted([row_min, row_max])
                col_start, col_end = sorted([col_min, col_max])
                data_cropped = data[row_start:row_end, col_start:col_end]
            
    except Exception as e:
        st.error(f"Map error: {e}")
        return None
    
    data_cropped = np.where(data_cropped == 0, np.nan, data_cropped)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(data_cropped, cmap=cmap, extent=(min_lon, max_lon, min_lat, max_lat), 
                   origin='upper', alpha=koppen_alpha, zorder=2)
    
    cx.add_basemap(ax, crs='EPSG:4326', source=cx.providers.OpenTopoMap, alpha=0.8, zorder=1)
    
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)
    ax.set_title(f"Köppen-Geiger Climate Map")
    ax.grid(True, alpha=0.3)
    
    cbar = plt.colorbar(im, ticks=range(1, 31), ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.set_yticklabels(class_labels, fontsize=8)
    
    return fig


def generate_climate_report(lat, lon):
    """
    Fetch climate data for given coordinates and use Gemini to generate a report.
    """
    try:
        # Construct the API URL
        url = f"http://climateapi.scottpinkelman.com/api/v1/location/{lat}/{lon}"
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse API response
        data = response.json()
        climate_data_list = data.get('return_values', [])
        
        if not climate_data_list:
            return "No climate data available for the selected location."
        
        climate_description = climate_data_list[0]['zone_description']
        
        # Create LLM prompt
        report_prompt_template = PromptTemplate(
            input_variables=["climate_description"],
            template=(
                "You are a climate expert. Based on the following climate description: "
                "'{climate_description}', provide a concise four-sentence summary of the region's climate."
            )
        )
        
        # Run through Gemini model
        report_chain = report_prompt_template | llm | StrOutputParser()
        return report_chain.invoke({"climate_description": climate_description})
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching climate data: {e}"
    except Exception as e:
        return f"Error generating report: {e}"


# =========================================================
# --- Streamlit App Setup ---
# =========================================================

# Google API key for Gemini
os.environ["GOOGLE_API_KEY"] = st.secrets["gemini_api_key"]

try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.65,
        max_output_tokens=512
    )
except Exception as e:
    st.error(f"Error initializing Gemini model: {e}")
    st.stop()

# --- Static GitHub Links ---
GITHUB_IMAGE_BASE_URL = "https://raw.githubusercontent.com/saturngreen67/streamlit_tests/main/images"
GITHUB_TIFF_BASE_URL = "https://raw.githubusercontent.com/saturngreen67/streamlit_tests/main/Koppen/1991-2020/koppen_geiger_0p1.tif"

# Sidebar demo sites
items = [
    {"name": "Demo site 1-A", "address": "Lattenbach Valley, Austria", "icon_url": f"{GITHUB_IMAGE_BASE_URL}/logo1.jpg", "github_key": "demo1a", "coordinate": [47.148472, 10.499805]},
    {"name": "Demo site 1-B", "address": "Brunntal, Austria", "icon_url": f"{GITHUB_IMAGE_BASE_URL}/logo2.jpg", "github_key": "demo1b", "coordinate": [47.625027, 15.052111]},
    {"name": "Demo site 2", "address": "Brasov City, Romania", "icon_url": f"{GITHUB_IMAGE_BASE_URL}/logo3.jpg", "github_key": "demo2", "coordinate": [45.647078, 25.593030]},
    {"name": "Demo site 3", "address": "Slovenia", "icon_url": f"{GITHUB_IMAGE_BASE_URL}/logo4.jpg", "github_key": "demo3", "coordinate": [46.0345, 14.461]},
    {"name": "Demo site 4", "address": "Zvolen, Slovakia", "icon_url": f"{GITHUB_IMAGE_BASE_URL}/logo5.jpeg", "github_key": "demo4", "coordinate": [48.5707, 19.1462]},
    {"name": "Demo site 5", "address": "Globocica, Macedonia", "icon_url": f"{GITHUB_IMAGE_BASE_URL}/logo6.jpeg", "github_key": "demo5", "coordinate": [48.5647, 19.114430]},
    {"name": "Testing", "address": "Under construction", "icon_url": f"{GITHUB_IMAGE_BASE_URL}/logo7.jpg", "github_key": "testing", "coordinate": [41.500, 20.5308]},
]

background_image_url = f"{GITHUB_IMAGE_BASE_URL}/main_logo.png"

# =========================================================
# --- Layout ---
# =========================================================

st.set_page_config(page_title="My Data Dashboard", layout="centered")

# Sidebar Logo
background_image_base64 = get_base64_of_image(background_image_url)
if background_image_base64:
    st.sidebar.markdown(
        f'<img src="data:image/png;base64,{background_image_base64}" style="width:100%;">',
        unsafe_allow_html=True
    )

# Sidebar Buttons
st.sidebar.markdown("""
    <style>
        .custom-link {
            text-decoration: none;
            color: inherit;
        }
        .custom-button-container {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 10px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
            transition: transform 0.2s, box-shadow 0.2s;
            background-size: cover;
            background-position: center;
            color: white;
            text-shadow: 1px 1px 2px black;
        }
        .custom-button-container:hover {
            transform: scale(1.02);
            box-shadow: 4px 4px 10px rgba(0,0,0,0.3);
        }
    </style>
""", unsafe_allow_html=True)

for item in items:
    icon_base64 = get_base64_of_image(item['icon_url'])
    if icon_base64:
        link_url = f"?item={item['github_key']}"
        button_html = f"""
        <a href="{link_url}" target="_self" class="custom-link">
            <div class="custom-button-container" style="background-image: url('data:image/png;base64,{icon_base64}');">
                <h4 style="margin: 0; padding: 0; color: white;"><b>{item['name']}</b></h4>
                <p style="margin: 0; padding: 0; font-size: 14px; color: white;">{item['address']}</p>
            </div>
        </a>
        """
        st.sidebar.markdown(button_html, unsafe_allow_html=True)

# Query Parameters
query_params = st.query_params
selected_item_key = query_params.get("item", items[0]['github_key'])
items_map = {item['github_key']: item for item in items}
selected_item = items_map.get(selected_item_key, items[0])

# Map center and zoom
DEFAULT_CENTER = [41.500, 20.5308]
map_center = selected_item.get('coordinate', DEFAULT_CENTER)
map_zoom = 15

# =========================================================
# --- Main Content ---
# =========================================================

if selected_item:
    st.title(f"Risk assessment for {selected_item['name']}: {selected_item['address']}")

    GITHUB_API_URL = f"https://api.github.com/repos/saturngreen67/streamlit_tests/contents/texts/{selected_item['github_key']}?ref=main"

    with st.container():
        with st.expander('Site Information and Maps'):

            # ---------- Site Information ----------
            with st.expander('Site Information'):  
                st.markdown("""
                    <style>
                    .justified-text {
                        text-align: justify;
                        display: flex;
                        flex-direction: column;
                        justify-content: flex-end;
                        min-height: 100px;
                    }
                    </style>
                """, unsafe_allow_html=True)

                def get_file_list():
                    response = requests.get(GITHUB_API_URL)
                    if response.status_code == 200:
                        files = response.json()
                        txt_files = [file for file in files if file['name'].endswith('.txt')]
                        def get_sort_key(file_name):
                            match = re.match(r"(\d+)", file_name)
                            return int(match.group()) if match else float('inf')
                        txt_files.sort(key=lambda x: get_sort_key(x['name']))
                        return txt_files
                    else:
                        st.error(f"Failed to retrieve file list. Status Code: {response.status_code}")
                        return []

                def display_files(files):
                    for file in files:
                        file_name = file['name']
                        display_name = os.path.splitext(file_name)[0]
                        st.markdown(f'<div class="justified-text"><h1 style="font-size: 30px;">{display_name[1:]}</h1></div>', unsafe_allow_html=True)
                        file_response = requests.get(file['download_url'])
                        if file_response.status_code == 200:
                            content = file_response.text
                            st.markdown(f'<div class="justified-text">{content.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                        else:
                            st.error(f"Unable to load {file['name']}")

                files = get_file_list()
                if files:
                    display_files(files)
                else:
                    st.warning("No text files found in the directory.")

            # ---------- Maps ----------
            with st.expander('Maps'):
                # Satellite Map
                m = leafmap.Map(center=map_center, zoom=map_zoom, height="800px")
                m.add_basemap("SATELLITE")
                m.add_marker(map_center, tooltip=selected_item['name'])
                m.to_streamlit()

                # Köppen Map
                st.subheader("Köppen-Geiger Climate Classification")
                fig = quick_koppen_map(GITHUB_TIFF_BASE_URL, map_center[0], map_center[1])
                if fig is not None:
                    st.pyplot(fig)
                else:
                    st.warning("Unable to display Köppen-Geiger Climate Map.")

                # ---------- Climate Report ----------
                st.subheader("Climate Report")
                with st.spinner("Generating climate report..."):
                    report = generate_climate_report(map_center[0], map_center[1])
                st.markdown(report)

        # ---------- Level 1, 2, 3 ----------
        with st.container():
            with st.expander('Level 1'):
                with st.expander('Information tables'):
                    api_url = GITHUB_API_URL
                    response = requests.get(api_url)
                    if response.status_code != 200:
                        st.error(f"Failed to fetch directory: {response.json().get('message', 'Unknown error')}")
                        st.stop()
                    files = response.json()
                    xlsx_files = [f for f in files if isinstance(f, dict) and f.get('name', '').endswith('.xlsx')]
                    def get_order(filename):
                        match = re.match(r'^(\d+)_', filename)
                        return int(match.group(1)) if match else float('inf')
                    xlsx_files.sort(key=lambda f: get_order(f['name']))
                    for file in xlsx_files:
                        full_name = file['name']
                        modified_name = re.sub(r'^\d+_', '', full_name[1:]).replace('.xlsx', '')
                        st.subheader(modified_name)
                        download_url = file['download_url']
                        resp = requests.get(download_url)
                        if resp.status_code == 200:
                            df = pd.read_excel(io.BytesIO(resp.content))
                            st.dataframe(df, hide_index=True)
                        else:
                            st.error(f"Failed to download {full_name}")

                with st.expander('Precieved risk'):
                    st.markdown("Under Construction")

                with st.expander('Interpretation'):
                    st.markdown("Under Construction")

            with st.expander('Level 2'):
                st.markdown("Under Construction")

            with st.expander('Level 3'):
                st.markdown("Under Construction")
