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
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import contextily as cx
import seaborn as sns
from adjustText import adjust_text
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
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    cbar = plt.colorbar(im, ticks=range(1, 31), ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.set_yticklabels(class_labels, fontsize=8)
    
    return fig


def get_climate_report_from_github(github_key):
    """
    Fetch climate report from the climate_report.txt file in the climate folder
    for the given demo site from GitHub.
    """
    try:
        # Construct the URL to the climate_report.txt file
        climate_report_url = f"https://raw.githubusercontent.com/saturngreen67/streamlit_tests/main/texts/{github_key}/climate/climate_report.txt"
        
        response = requests.get(climate_report_url)
        response.raise_for_status()
        
        return response.text
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching climate report from GitHub: {e}"
    except Exception as e:
        return f"Error reading climate report: {e}"


def generate_climate_report_with_gemini(lat, lon):
    """
    Fetch climate data for given coordinates and use Gemini to generate a report.
    Only used for the Testing section.
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


def get_series_display_names():
    """
    Returns a mapping of column names to display names for the checkboxes.
    """
    return {
        "CI": "Condition of the infrastructure (CI)",
        "CIH": "Condition of CI after exposure to hazard (CIH)",
        "CIHG": "Condition of CI after exposure to hazard but protected by GPI (CIHG)",
        "CIHN": "Condition of CI after exposure to hazard but protected by NbS (CIHN)",
        "CIHGN": "Condition of CI after exposure to hazard but protected by both GPI and NBS (CIHGN)"
    }


def create_radar_chart_from_kpis(kpis_data, selected_series=None):
    """
    Create a radar chart from KPIs data with interactive series selection.
    Handles missing values and non-numeric data.
    Fixed axis limits from 1 to 5 with integer ticks.
    """
    try:
        # Clean the data - remove rows with missing or invalid values
        cleaned_data = kpis_data.copy()
        
        # Convert numeric columns, coerce errors to NaN
        for col in cleaned_data.columns[1:]:  # Skip the first column (categories)
            cleaned_data[col] = pd.to_numeric(cleaned_data[col], errors='coerce')
        
        # Remove rows where all values are NaN (except category)
        numeric_cols = cleaned_data.columns[1:]
        cleaned_data = cleaned_data.dropna(subset=numeric_cols, how='all')
        
        if len(cleaned_data) == 0:
            st.warning("No valid numeric data found for radar chart.")
            return None
        
        # Get categories and series data
        categories = cleaned_data.iloc[:, 0].tolist()
        
        # Prepare series data
        series_data = {}
        for col in numeric_cols:
            series_values = cleaned_data[col].dropna().tolist()
            # Only include series that have valid data
            if len(series_values) == len(categories):
                series_data[col] = series_values
        
        if not series_data:
            st.warning("No complete series found for radar chart.")
            return None
        
        # Filter series based on selected checkboxes
        if selected_series:
            series_data = {k: v for k, v in series_data.items() if k in selected_series}
        
        if not series_data:
            st.warning("No series selected for radar chart.")
            return None
        
        N = len(categories)
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Define colors for different series
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
        
        # Plot each series
        for i, (series_name, values) in enumerate(series_data.items()):
            color = colors[i % len(colors)]
            
            # Complete the circle
            values_complete = values + values[:1]
            angles_complete = angles + angles[:1]
            
            # Plot the series
            ax.plot(angles_complete, values_complete, 'o-', linewidth=2, 
                   label=series_name, color=color)
            ax.fill(angles_complete, values_complete, alpha=0.25, color=color)
        
        # Customize the chart
        ax.set_xticks(angles)
        ax.set_xticklabels(categories, fontweight="bold")
        
        # Fixed axis limits from 1 to 5 with integer ticks
        ax.set_ylim(1, 5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(['1', '2', '3', '4', '5'])
        
        ax.grid(True)
        
        # Use display names in legend
        display_names = get_series_display_names()
        legend_labels = [display_names.get(series_name, series_name) for series_name in series_data.keys()]
        plt.legend(legend_labels, loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        plt.title(f'Radar Chart of {selected_item["name"]} infrastructure', size=15, y=1.05, fontweight='bold')
        
        plt.tight_layout()
        return fig
        
    except Exception as e:
        st.error(f"Error creating radar chart: {e}")
        return None


def get_kpis_data(github_key):
    """
    Fetch KPIs.xlsx file from the level1 folder for the given demo site.
    """
    try:
        # Construct the URL to the KPIs.xlsx file in level1 folder
        kpis_url = f"https://raw.githubusercontent.com/saturngreen67/streamlit_tests/main/texts/{github_key}/level1/KPIs.xlsx"
        
        response = requests.get(kpis_url)
        response.raise_for_status()
        
        # Read the Excel file
        kpis_data = pd.read_excel(io.BytesIO(response.content))
        return kpis_data
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching KPIs data from GitHub: {e}")
        return None
    except Exception as e:
        st.error(f"Error reading KPIs data: {e}")
        return None


def get_el_data(github_key):
    """
    Fetch el.xlsx file from the level1 folder for the given demo site.
    """
    try:
        # Construct the URL to the el.xlsx file in level1 folder
        el_url = f"https://raw.githubusercontent.com/saturngreen67/streamlit_tests/main/texts/{github_key}/level1/el.xlsx"
        
        response = requests.get(el_url)
        response.raise_for_status()
        
        # Read the Excel file
        el_data = pd.read_excel(io.BytesIO(response.content))
        return el_data
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching EL data from GitHub: {e}")
        return None
    except Exception as e:
        st.error(f"Error reading EL data: {e}")
        return None


def format_label(label):
    """Format labels for display, especially CI labels."""
    if label.startswith('CI'):
        return r'CI$_{' + label[2:] + '}$'
    return label


def plot_kpi_analysis(kpis_data, el_data):
    """
    Create KPI analysis plots comparing Condition vs Extent of Loss.
    """
    try:
        # Set indices
        df1 = kpis_data.set_index(kpis_data.columns[0])
        df2 = el_data.set_index(el_data.columns[0])
        
        plot_pairs = [
            (df1.columns[1], df2.columns[0]),
            (df1.columns[2], df2.columns[1]),
            (df1.columns[3], df2.columns[2]),
            (df1.columns[4], df2.columns[3]) 
        ]

        plt.style.use('default')
        sns.set_palette("husl")
        
        colors = ['#2E8B57', '#7CFC00', '#FFD700', '#FF8C00', '#FF4500', '#8B0000']
        cmap = LinearSegmentedColormap.from_list('quality_map', colors, N=256)
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 14))
        axes = axes.flatten()

        background_colors = ['#F8F9FA', '#F8F9FA', '#F8F9FA', '#F8F9FA']

        for i, (col_f1, col_f2) in enumerate(plot_pairs):
            axes[i].set_facecolor(background_colors[i])
            
            x_data = df2[col_f2].copy()  
            y_data = df1[col_f1].copy()  

            x_data = pd.to_numeric(x_data, errors='coerce')
            y_data = pd.to_numeric(y_data, errors='coerce')
            
            valid_mask = ~(x_data.isna() | y_data.isna())
            
            if not valid_mask.any():
                axes[i].text(0.5, 0.5, 'No valid data', transform=axes[i].transAxes, 
                            ha='center', va='center', fontsize=14, style='italic')
                continue
                
            x_data_clean = x_data[valid_mask]
            y_data_clean = y_data[valid_mask]
            
            row_names = df2.index[valid_mask]

            jitter_amount = 0.25
            x_jittered = x_data_clean + np.random.uniform(-jitter_amount, jitter_amount, len(x_data_clean))
            y_jittered = y_data_clean + np.random.uniform(-jitter_amount, jitter_amount, len(y_data_clean))

            xx, yy = np.meshgrid(np.linspace(0.5, 5.5, 500), np.linspace(0.5, 5.5, 1500))
            quality_score = (xx + yy) / 10
            contour = axes[i].contourf(xx, yy, quality_score, levels=200, cmap=cmap, alpha=0.7)
            
            scatter_size = 150
            scatter = axes[i].scatter(
                x_jittered, y_jittered, 
                alpha=1, 
                s=scatter_size, 
                edgecolors='black', 
                linewidth=1.5, 
                c='blue',
                marker='o'
            )
            
            texts = []
            for idx, (x, y, row_name) in enumerate(zip(x_jittered, y_jittered, row_names)):
                formatted_name = format_label(str(row_name))
                text = axes[i].text(
                    x, y, formatted_name, 
                    fontsize=9, 
                    ha='center', 
                    va='center', 
                    fontweight='bold', 
                    color='darkblue',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.9, edgecolor='none')
                )
                texts.append(text)

            adjust_text(texts, 
                       ax=axes[i],
                       expand_points=(1.5, 1.5),
                       expand_text=(1.2, 1.2),
                       arrowprops=dict(arrowstyle='-', color='gray', lw=0.5, alpha=0.7),
                       force_points=0.5,
                       force_text=0.8)

            formatted_col = format_label(col_f1)
            axes[i].set_title(formatted_col, fontsize=16, fontweight='bold', pad=20, color='#2C3E50')
            axes[i].set_xlabel('Extent of Loss', fontsize=13, fontweight='semibold', labelpad=10, color='#34495E')
            axes[i].set_ylabel(formatted_col + ' Condition', fontsize=13, fontweight='semibold', labelpad=10, color='#34495E')

            axes[i].set_xticks(np.arange(1, 6))
            axes[i].set_yticks(np.arange(1, 6))
            axes[i].tick_params(axis='both', which='major', labelsize=11, length=6, width=1.5)
            
            axes[i].set_xlim(0.5, 5.5)
            axes[i].set_ylim(0.5, 5.5)
            
            for spine in axes[i].spines.values():
                spine.set_visible(True)
                spine.set_linewidth(1.5)
                spine.set_color('#BDC3C7')
            
            axes[i].grid(False)

        plt.suptitle(f'KPI Analysis: Condition vs Extent of Loss - {selected_item["name"]}', 
                     fontsize=20, fontweight='bold', y=0.98, color='#2C3E50')
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.93)
        return fig
        
    except Exception as e:
        st.error(f"Error creating KPI analysis plots: {e}")
        return None


def get_interpretation_text(github_key):
    """
    Fetch interpretation text from interpretation.txt file in level1 folder.
    """
    try:
        # Construct the URL to the interpretation.txt file
        interpretation_url = f"https://raw.githubusercontent.com/saturngreen67/streamlit_tests/main/texts/{github_key}/level1/interpretation.txt"
        
        response = requests.get(interpretation_url)
        response.raise_for_status()
        
        return response.text
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching interpretation text from GitHub: {e}"
    except Exception as e:
        return f"Error reading interpretation text: {e}"


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
    {"name": "Demo site 4", "address": "Zvolen, Slovakia", "icon_url": f"{GITHUB_IMAGE_BASE_URL}/logo5.jpg", "github_key": "demo4", "coordinate": [48.5707, 19.1462]},
    {"name": "Demo site 5", "address": "Globocica, Macedonia", "icon_url": f"{GITHUB_IMAGE_BASE_URL}/logo6.png", "github_key": "demo5", "coordinate": [48.5647, 19.114430]},
    {"name": "Testing", "address": "", "icon_url": f"{GITHUB_IMAGE_BASE_URL}/logo7.jpg", "github_key": "testing", "coordinate": [41.500, 20.5308]},
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
                
                # Check if this is a Demo site or Testing site
                if selected_item['github_key'] == 'testing':
                    # Use Gemini for Testing section
                    with st.spinner("Generating climate report with Gemini..."):
                        report = generate_climate_report_with_gemini(map_center[0], map_center[1])
                else:
                    # Fetch from GitHub for Demo sites
                    with st.spinner("Fetching climate report from GitHub..."):
                        report = get_climate_report_from_github(selected_item['github_key'])
                
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

                with st.expander('Perceived risk'):
                    # Fetch and display KPIs radar chart
                    st.subheader("KPI Radar Chart")
                    
                    # Get KPIs data from level1 folder
                    kpis_data = get_kpis_data(selected_item['github_key'])
                    
                    if kpis_data is not None and not kpis_data.empty:
                        st.dataframe(kpis_data)
                        
                        # Get available series (columns except the first one)
                        available_series = kpis_data.columns[1:].tolist()
                        
                        # Create checkboxes for series selection with display names
                        st.subheader("Select the CI conditions that you want to plot:")
                        selected_series = []
                        
                        # Get display names mapping
                        display_names = get_series_display_names()
                        
                        # Create mapping from display name back to original column name
                        reverse_mapping = {v: k for k, v in display_names.items()}
                        
                        # Create checkboxes with display names
                        for series in available_series:
                            display_name = display_names.get(series, series)
                            if st.checkbox(display_name, value=True, key=f"checkbox_{series}"):
                                selected_series.append(series)
                        
                        # Create and display radar chart with selected series
                        if selected_series:
                            radar_fig = create_radar_chart_from_kpis(kpis_data, selected_series)
                            if radar_fig is not None:
                                st.pyplot(radar_fig)
                            else:
                                st.warning("Could not generate radar chart from the selected data.")
                        else:
                            st.warning("Please select at least one series to display.")
                    else:
                        st.warning("No KPIs data found in the level1 folder.")
                    
                    # KPI Analysis Plots
                    st.subheader("KPI Analysis: Extent of Loss vs. CI Condition")
                    
                    # Get EL data from level1 folder
                    el_data = get_el_data(selected_item['github_key'])
                    
                    if kpis_data is not None and el_data is not None and not kpis_data.empty and not el_data.empty:

                        st.dataframe(el_data)
                        
                        # Create and display KPI analysis plots
                        kpi_fig = plot_kpi_analysis(kpis_data, el_data)
                        if kpi_fig is not None:
                            st.pyplot(kpi_fig)
                        else:
                            st.warning("Could not generate KPI analysis plots from the available data.")
                    else:
                        st.warning("Both KPIs.xlsx and el.xlsx files are required for KPI analysis plots.")

                with st.expander('Interpretation'):
                    # Fetch and display interpretation text from GitHub
                    with st.spinner("Loading interpretation..."):
                        interpretation_text = get_interpretation_text(selected_item['github_key'])
                    
                    if interpretation_text and not interpretation_text.startswith("Error"):
                        st.markdown(interpretation_text)
                    else:
                        st.warning("No interpretation text found or error loading interpretation.")
                        st.info("The interpretation text should be located at:")
                        st.code(f"https://raw.githubusercontent.com/saturngreen67/streamlit_tests/main/texts/{selected_item['github_key']}/level1/interpretation.txt")

            with st.expander('Level 2'):
                st.markdown("Under Construction")

            with st.expander('Level 3'):
                st.markdown("Under Construction")