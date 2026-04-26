import streamlit as st
import pandas as pd
import sqlite3
import folium
from streamlit_folium import folium_static
import plotly.express as px
import os
import datetime
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

def get_last_update_time():
    if os.path.exists(DB_NAME):
        mtime = os.path.getmtime(DB_NAME)
        dt_utc = datetime.datetime.fromtimestamp(mtime, tz=datetime.timezone.utc)
        tw_tz = datetime.timezone(datetime.timedelta(hours=8))
        return dt_utc.astimezone(tw_tz).strftime("%Y-%m-%d %H:%M:%S")
    return "Unknown"

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
st.markdown("<h1 class='gradient-title'>🌤️ Temperature Forecast Web App</h1>", unsafe_allow_html=True)

# Layout: sidebar for controls or main content tabs
with st.sidebar:
    st.header("Data Controls")
    st.write("Source: CWA API (Live)")
    
    # Display last updated time
    st.markdown(f"**Last Updated (Taiwan Time):**<br><span style='color: #28a745; font-weight: 600;'>{get_last_update_time()}</span>", unsafe_allow_html=True)
    st.write("") # spacing
    
    if st.button("Refresh Data"):
        with st.spinner("Fetching latest data from CWA..."):
            data_manager.refresh_data()
            st.success("Successfully Refreshed!")
            df = load_data()

if df.empty:
    st.warning("No data available. Please click 'Refresh Data' to fetch from CWA.")
    st.stop()
    
# Create tabs for the two different views mentioned (HW2-4 vs Complete Prompt Step)
tab1, tab2 = st.tabs(["🗺️ Date Map View (Left/Right)", "📊 Region Trends View"])

with tab1:
    st.subheader("Taiwan Weather Map Forecast")
    
    # Selectors for Date and Overview Region
    sel_col1, sel_col2 = st.columns(2)
    with sel_col1:
        available_dates = df['dataDate'].unique().tolist()
        selected_date = st.selectbox("Select Date", available_dates, key="map_date_select")
        
    with sel_col2:
        available_overview_regions = ["全台灣 (National)"] + sorted(df['regionName'].unique().tolist())
        overview_region = st.selectbox("Select Region for Overview & Advice", available_overview_regions, key="overview_region_select")
    
    # Filter data for selected date (used for Map and Table)
    date_df = df[df['dataDate'] == selected_date].copy()
    date_df['avg_temp'] = (date_df['mint'] + date_df['maxt']) / 2
    
    # Calculate Data Summaries for Metric Cards
    if overview_region == "全台灣 (National)":
        target_df = date_df
        avg_title = "National Avg (°C)"
    else:
        target_df = date_df[date_df['regionName'] == overview_region]
        avg_title = f"{overview_region} Avg (°C)"

    overall_avg = target_df['avg_temp'].mean()
    high_max = target_df['maxt'].max()
    low_min = target_df['mint'].min()
    
    # Going-out Advice Logic
    if overall_avg < 20:
        advice_icon = "🧣"
        advice_text = "天氣偏涼甚至寒冷，建議穿著長袖、毛衣或準備保暖大衣，注意防風。"
    elif 20 <= overall_avg <= 24:
        advice_icon = "🧥"
        advice_text = "天氣舒適帶點涼意，建議洋蔥式穿搭，帶件薄外套或是長袖衣物出門是最佳選擇。"
    elif 24 < overall_avg <= 28:
        advice_icon = "👕"
        advice_text = "氣溫溫暖舒適，穿著短袖或輕薄長袖即可，若太陽大可考慮簡便防曬。"
    else:
        advice_icon = "🕶️"
        advice_text = "天氣相當炎熱！出門請以短袖透氣衣物為主，多補充水分，務必做好防曬以防中暑。"
        
    st.markdown(f"### {overview_region} Overview & Advice")
    m1, m2, m3 = st.columns(3)
    m1.metric("Highest Max Temp (°C)", f"{high_max:.1f}°C")
    m2.metric("Lowest Min Temp (°C)", f"{low_min:.1f}°C")
    m3.metric(avg_title, f"{overall_avg:.1f}°C")
    
    st.info(f"**{advice_icon} 出門穿搭指南**：{advice_text}")
    st.markdown("---")
    
    # Create two columns for left/right layout
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        st.markdown("### Weather Map")
        # Color Legend
        st.markdown("""
        <div style="display: flex; gap: 15px; margin-bottom: 15px; font-size: 0.9em; font-weight: 500; align-items: center;">
            <span style="color: #666;">Map Legend: </span>
            <div><span style="display: inline-block; width: 12px; height: 12px; background-color: #3186cc; border-radius: 50%; opacity: 0.8;"></span> &lt; 20°C</div>
            <div><span style="display: inline-block; width: 12px; height: 12px; background-color: #28a745; border-radius: 50%; opacity: 0.8;"></span> 20~24°C</div>
            <div><span style="display: inline-block; width: 12px; height: 12px; background-color: #ffc107; border-radius: 50%; opacity: 0.8;"></span> 25~29°C</div>
            <div><span style="display: inline-block; width: 12px; height: 12px; background-color: #dc3545; border-radius: 50%; opacity: 0.8;"></span> &ge; 30°C</div>
        </div>
        """, unsafe_allow_html=True)
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
        display_df = date_df[['regionName', 'mint', 'maxt', 'avg_temp']].sort_values(by='avg_temp', ascending=False)
        display_df.rename(columns={'regionName': 'Region', 'mint': 'Min Temp (°C)', 'maxt': 'Max Temp (°C)', 'avg_temp': 'Avg Temp (°C)'}, inplace=True)
        display_df = display_df.reset_index(drop=True)
        st.dataframe(display_df, use_container_width=True)

with tab2:
    st.subheader("Regional Temperature Trends")
    
    # Region Selector
    available_regions = df['regionName'].unique().tolist()
    selected_region = st.selectbox("Select a Region", available_regions, index=available_regions.index("中部地區") if "中部地區" in available_regions else 0)
    
    # Filter Data for Selected Region
    region_df = df[df['regionName'] == selected_region].sort_values(by='dataDate')
    
    st.markdown(f"#### Temperature Trends for {selected_region}")
    
    # Add avg temp to region_df
    region_df['avg'] = (region_df['mint'] + region_df['maxt']) / 2
    
    # Melt dataframe for standard plotly line chart
    melted_df = region_df.melt(id_vars=['dataDate'], value_vars=['mint', 'avg', 'maxt'], var_name='Type', value_name='Temperature')
    melted_df['Type'] = melted_df['Type'].replace({'mint': 'MinT', 'avg': 'AvgT', 'maxt': 'MaxT'})
    
    fig = px.line(melted_df, x="dataDate", y="Temperature", color='Type', markers=True, 
                 labels={'dataDate': 'Date', 'Temperature': 'Temperature (°C)'},
                 color_discrete_map={"MinT": "#00B4D8", "AvgT": "#28a745", "MaxT": "#FF8FA3"})
                 
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"#### Temperature Data for {selected_region}")
    styled_df = region_df[['dataDate', 'mint', 'maxt']].copy()
    styled_df['AvgT'] = (styled_df['mint'] + styled_df['maxt']) / 2
    styled_df = styled_df.rename(columns={'mint': 'MinT', 'maxt': 'MaxT'})
    styled_df = styled_df.reset_index(drop=True)
    st.dataframe(styled_df, use_container_width=True)

# Custom CSS for UI Enhancement
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

html, body, [class*="css"]  {
    font-family: 'Outfit', sans-serif;
}
.gradient-title {
    background: -webkit-linear-gradient(45deg, #FF8FA3, #00B4D8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 3rem;
    padding-bottom: 20px;
}
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(4px);
    border-radius: 10px;
    padding: 15px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 24px 0 rgba(0, 0, 0, 0.3);
}
[data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
[data-testid="stDataFrame"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}
</style>
""", unsafe_allow_html=True)
