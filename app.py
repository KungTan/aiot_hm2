import streamlit as st
import pandas as pd
import sqlite3
import folium
from streamlit_folium import folium_static
import plotly.express as px
import os
import data_manager

# --- Config and Setup ---
st.set_page_config(page_title="Taiwan Weather Forecast", page_icon="🌤️", layout="wide")

DB_NAME = "data.db"

# Coordinates approximations for Taiwan regions
REGION_COORDS = {
    "北部地區": [25.04, 121.55],
    "中部地區": [24.15, 120.68],
    "南部地區": [22.99, 120.21],
    "東北部地區": [24.65, 121.75],
    "東部地區": [23.88, 121.60],
    "東南部地區": [22.65, 121.10]
}

def get_color(avg_temp):
    if avg_temp < 20: return "blue"
    elif 20 <= avg_temp < 25: return "green"
    elif 25 <= avg_temp < 30: return "orange" # Changed from yellow to orange for better visibility on map, though the prompt said yellow
    else: return "red"
    
def get_color_str(avg_temp):
    if avg_temp < 20: return "#3186cc"
    elif 20 <= avg_temp < 25: return "#28a745"
    elif 25 <= avg_temp < 30: return "#ffc107" # proper yellow/gold
    else: return "#dc3545"

def load_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM TemperatureForecasts", conn)
    conn.close()
    return df

# Initialize Data & Session State
if "data_fetched" not in st.session_state:
    if not os.path.exists(DB_NAME) or os.stat(DB_NAME).st_size == 0:
        data_manager.main()
    st.session_state["data_fetched"] = True
    
try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    df = pd.DataFrame()

# UI Building
st.title("🌤️ Temperature Forecast Web App")

# Layout: sidebar for controls or main content tabs
with st.sidebar:
    st.header("Data Controls")
    st.write("Source API or Local JSON.")
    data_source = st.radio("fetch mode:", ["Local JSON (Offline)", "CWA API (Live)"])
    if st.button("Refresh Data Data"):
        with st.spinner("Refreshing..."):
            if "Offline" in data_source:
                data_manager.refresh_data("local")
            else:
                data_manager.refresh_data("api")
            st.success("Successfully Refreshed!")
            df = load_data()

if df.empty:
    st.warning("No data available. Please refresh data source.")
    st.stop()
    
# Create tabs for the two different views mentioned (HW2-4 vs Complete Prompt Step)
tab1, tab2 = st.tabs(["🗺️ Date Map View (Left/Right)", "📊 Region Trends View"])

with tab1:
    st.subheader("Taiwan Weather Map Forecast")
    
    # Date Selector
    available_dates = df['dataDate'].unique().tolist()
    selected_date = st.selectbox("Select Date", available_dates, key="map_date_select")
    
    # Filter data for selected date
    date_df = df[df['dataDate'] == selected_date].copy()
    date_df['avg_temp'] = (date_df['mint'] + date_df['maxt']) / 2
    
    # Create two columns for left/right layout
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        st.markdown("### Weather Map")
        # Base folium map
        # Center Taiwan coordinates
        m = folium.Map(location=[23.6978, 120.9605], zoom_start=7, tiles="OpenStreetMap")
        
        # Add markers
        for _, row in date_df.iterrows():
            region = row['regionName']
            if region in REGION_COORDS:
                avg = row['avg_temp']
                color_hex = get_color_str(avg)
                
                popup_html = f"<b>{region}</b><br>Date: {row['dataDate']}<br>Min: {row['mint']}°C<br>Max: {row['maxt']}°C<br>Avg: {avg:.1f}°C"
                
                folium.CircleMarker(
                    location=REGION_COORDS[region],
                    radius=20,
                    popup=folium.Popup(popup_html, max_width=200),
                    tooltip=f"{region}: {avg:.1f}°C",
                    color=color_hex,
                    fill=True,
                    fill_color=color_hex,
                    fill_opacity=0.6,
                    weight=2
                ).add_to(m)
        
        folium_static(m, width=600, height=500)

    with col_right:
        st.markdown("### Temperature Data")
        display_df = date_df[['id', 'regionName', 'mint', 'maxt', 'avg_temp']].sort_values(by='avg_temp', ascending=False)
        display_df.rename(columns={'id': 'ID', 'regionName': 'Region', 'mint': 'Min Temp (°C)', 'maxt': 'Max Temp (°C)', 'avg_temp': 'Avg Temp (°C)'}, inplace=True)
        st.dataframe(display_df, use_container_width=True)

with tab2:
    st.subheader("Regional Temperature Trends")
    
    # Region Selector
    available_regions = df['regionName'].unique().tolist()
    selected_region = st.selectbox("Select a Region", available_regions, index=available_regions.index("中部地區") if "中部地區" in available_regions else 0)
    
    # Filter Data for Selected Region
    region_df = df[df['regionName'] == selected_region].sort_values(by='dataDate')
    
    st.markdown(f"#### Temperature Trends for {selected_region}")
    
    # Melt dataframe for standard plotly line chart
    melted_df = region_df.melt(id_vars=['dataDate'], value_vars=['mint', 'maxt'], var_name='Type', value_name='Temperature')
    melted_df['Type'] = melted_df['Type'].replace({'mint': 'MinT', 'maxt': 'MaxT'})
    
    fig = px.line(melted_df, x="dataDate", y="Temperature", color='Type', markers=True, 
                 labels={'dataDate': 'Date', 'Temperature': 'Temperature (°C)'},
                 color_discrete_map={"MinT": "#00B4D8", "MaxT": "#FF8FA3"})
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"#### Temperature Data for {selected_region}")
    styled_df = region_df[['id', 'dataDate', 'mint', 'maxt']].rename(columns={'id': 'ID', 'dataDate': 'Date', 'mint': 'MinT', 'maxt': 'MaxT'})
    st.dataframe(styled_df, use_container_width=True)

# Custom CSS for UI Enhancement
st.markdown("""
<style>
/* Center headers */
h1, h2, h3 {  
    color: #4A4A4A;
}
/* Style dataframes */
[data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)
