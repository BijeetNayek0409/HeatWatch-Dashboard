import asyncio
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from src.data_loader import load_historical_data
from src.historical_analysis import get_yearly_trend, get_seasonal_analysis, compare_periods, get_city_comparison
from src.anomaly_detection import calculate_z_scores, get_extreme_events_summary, get_top_extreme_events
from src.live_weather import fetch_current_weather

st.set_page_config(
    page_title="HeatWatch | Historical Analysis",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background-color: #0a0a10;
        background-image: radial-gradient(circle at 50% 0%, #1f1f3a 0%, #0a0a10 70%);
        color: #e2e8f0;
    }
    
    /* Gradient Title */
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff7eb3 0%, #ff758c 50%, #ff9a44 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 1.2rem;
        margin-top: 0px;
        font-weight: 300;
    }
    
    /* Glassmorphism KPI Cards */
    .kpi-container {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px 20px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .kpi-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.2);
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    .kpi-title {
        color: #94a3b8;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 12px;
    }
    .kpi-val {
        color: #ffffff;
        font-size: 38px;
        font-weight: 800;
        text-shadow: 0 0 20px rgba(255,255,255,0.1);
    }
    .kpi-unit {
        font-size: 20px;
        color: #64748b;
        font-weight: 400;
    }
    
    /* Glowing Status Badges */
    .status-badge {
        padding: 8px 16px;
        border-radius: 30px;
        font-weight: 800;
        font-size: 14px;
        color: white;
        display: inline-block;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .status-NORMAL { 
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
    }
    .status-UNUSUAL { 
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.5);
    }
    .status-EXTREME { 
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.5);
    }
    
    /* Sleek Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 32px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .stTabs [data-baseweb="tab"] {
        height: 56px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px 8px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-size: 16px;
        font-weight: 600;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        border-bottom: 3px solid #818cf8;
        color: #818cf8 !important;
        text-shadow: 0 0 15px rgba(129, 140, 248, 0.4);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data():
    df = load_historical_data("weather_data.csv")
    df_scored = calculate_z_scores(df)
    return df, df_scored

def render_kpi(title, value, unit=""):
    st.markdown(f'''
        <div class="kpi-container">
            <div class="kpi-title">{title}</div>
            <div class="kpi-val">{value} <span class="kpi-unit">{unit}</span></div>
        </div>
    ''', unsafe_allow_html=True)

def main():
    try:
        df, df_scored = get_data()
    except Exception as e:
        st.error("Error loading historical dataset (weather_data.csv).")
        return
        
    st.markdown('<h1 class="main-title">🌡️ HEATWATCH</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Historical Weather Trend & Extreme Temperature Analysis</p>', unsafe_allow_html=True)
    st.markdown("*Explore long-term weather patterns and identify unusual temperature events across regions.*")
    
    # Sidebar Controls
    st.sidebar.header("Global Controls")
    
    cities = ["All Cities"] + sorted(df['city'].unique().tolist())
    selected_city = st.sidebar.selectbox("Select City", cities)
    
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    
    year_range = st.sidebar.slider("Select Historical Period (Years)", min_year, max_year, (min_year, max_year))
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Current System Date:**<br>{datetime.now().strftime('%d %B %Y')}", unsafe_allow_html=True)
    
    # Main Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Historical Analysis", "🌐 Live Analysis", "🔥 Extreme Events"])
    
    # -------------------------------------------------------------------------
    # TAB 1: HISTORICAL ANALYSIS
    # -------------------------------------------------------------------------
    with tab1:
        # Filter for tab 1
        mask = (df['year'] >= year_range[0]) & (df['year'] <= year_range[1])
        if selected_city != "All Cities":
            mask = mask & (df['city'] == selected_city)
        t1_df = df[mask]
        
        if t1_df.empty:
            st.warning("No data available for the selected filters.")
        else:
            # KPI Cards
            c1, c2, c3, c4 = st.columns(4)
            avg_max = t1_df['temperature_2m_max'].mean()
            highest_max = t1_df['temperature_2m_max'].max()
            lowest_max = t1_df['temperature_2m_max'].min()
            total_rain = t1_df['precipitation_sum'].sum()
            
            with c1: render_kpi("Average Maximum Temperature", f"{avg_max:.1f}", "°C")
            with c2: render_kpi("Highest Maximum Temperature", f"{highest_max:.1f}", "°C")
            with c3: render_kpi("Lowest Maximum Temperature", f"{lowest_max:.1f}", "°C")
            with c4: render_kpi("Total Rainfall", f"{total_rain:,.0f}", "mm")
            
            # Trend Chart
            st.markdown("### Maximum Temperature Trend")
            trend_df = get_yearly_trend(df, selected_city, year_range[0], year_range[1])
            if not trend_df.empty:
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(x=trend_df['year'], y=trend_df['Average_Max_Temperature'], mode='lines+markers', name='Avg Max Temp', line=dict(color='#ff9f1c', width=3)))
                fig_trend.add_trace(go.Scatter(x=trend_df['year'], y=trend_df['Average_Min_Temperature'], mode='lines+markers', name='Avg Min Temp', line=dict(color='#00b4d8', width=3)))
                fig_trend.update_layout(
                    template="plotly_dark", 
                    xaxis_title="Year", 
                    yaxis_title="Temperature (°C)", 
                    hovermode="x unified",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
                )
                st.plotly_chart(fig_trend, use_container_width=True)
                
            # Compare sections
            col_seas, col_comp = st.columns([3, 2])
            
            with col_seas:
                st.markdown("### Seasonal Analysis")
                st.markdown("*Seasonal analysis helps identify recurring temperature patterns across the year.*")
                seas_df = get_seasonal_analysis(df, selected_city, year_range[0], year_range[1])
                if not seas_df.empty:
                    fig_seas = px.bar(seas_df, x='season', y=['Average_Max_Temperature', 'Average_Min_Temperature'], 
                                      barmode='group', color_discrete_sequence=['#ff9f1c', '#00b4d8'])
                    fig_seas.update_layout(
                        template="plotly_dark", 
                        xaxis_title="Season", 
                        yaxis_title="Temperature (°C)",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
                    )
                    st.plotly_chart(fig_seas, use_container_width=True)
                    
            with col_comp:
                st.markdown("### Recent vs Historical")
                st.markdown(f"Comparing a baseline with recent years.")
                
                # Dynamic mid-point
                mid_year = year_range[0] + (year_range[1] - year_range[0]) // 2
                
                h_avg, r_avg, diff = compare_periods(df, selected_city, year_range[0], mid_year, mid_year+1, year_range[1])
                if h_avg is not None:
                    hc1, hc2 = st.columns(2)
                    with hc1: render_kpi(f"Historical Average<br>({year_range[0]}-{mid_year})", f"{h_avg:.1f}", "°C")
                    with hc2: render_kpi(f"Recent Average<br>({mid_year+1}-{year_range[1]})", f"{r_avg:.1f}", "°C")
                    
                    sign = "+" if diff > 0 else ""
                    color = "#ef4444" if diff > 0 else "#3b82f6"
                    st.markdown(f"""
                    <div style="text-align: center; margin-top: 10px;">
                        <span style="color: #9ca3af; font-size: 14px; text-transform: uppercase;">Observed Difference in this dataset</span><br>
                        <span style="color: {color}; font-size: 36px; font-weight: bold;">{sign}{diff:.1f} °C</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
            if selected_city == "All Cities":
                st.markdown("---")
                st.markdown("### Region-wise Comparison")
                comp_df = get_city_comparison(df, year_range[0], year_range[1])
                
                # Ensure the dataframe fits nicely and doesn't look like a raw dump
                fig_city = px.bar(comp_df, x='Average_Max_Temperature', y='city', orientation='h', 
                                  title="Average Maximum Temperature by City",
                                  color_discrete_sequence=['#818cf8'])
                fig_city.update_layout(
                    template="plotly_dark", 
                    yaxis={'categoryorder':'total ascending'},
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(gridcolor='rgba(255,255,255,0.05)')
                )
                st.plotly_chart(fig_city, use_container_width=True)

    # -------------------------------------------------------------------------
    # TAB 2: LIVE ANALYSIS
    # -------------------------------------------------------------------------
    with tab2:
        st.markdown("### Compare Current Weather to Historical Baseline")
        st.markdown("*View current weather observations and compare them statistically with the historical baseline for this city and month.*")
        
        if selected_city == "All Cities":
            st.warning("Please select a specific city from the sidebar to perform Live Analysis.")
        else:
            if st.button("Fetch Current Weather"):
                with st.spinner(f"Connecting to Live Weather API for {selected_city}..."):
                    try:
                        live_data = fetch_current_weather(selected_city)
                        
                        st.markdown(f"**Data Source:** Live Weather API (Open-Meteo) &nbsp;&nbsp;|&nbsp;&nbsp; **Last Updated:** {live_data['time']}")
                        st.markdown("---")
                        
                        lc1, lc2, lc3, lc4 = st.columns(4)
                        with lc1: render_kpi("Current Temperature", f"{live_data['temperature']:.1f}", "°C")
                        with lc2: render_kpi("Feels Like Temp", f"{live_data['apparent_temperature']:.1f}", "°C")
                        with lc3: render_kpi("Wind Speed", f"{live_data['wind_speed']:.1f}", "km/h")
                        with lc4: render_kpi("Precipitation", f"{live_data['precipitation']:.1f}", "mm")
                        
                        # Statistical Anomaly Comparison
                        st.markdown("### Baseline Comparison")
                        
                        current_month = datetime.now().month
                        city_month_data = df_scored[(df_scored['city'] == selected_city) & (df_scored['month'] == current_month)]
                        
                        if city_month_data.empty:
                            st.error("Insufficient historical data for this city and month to form a baseline.")
                        else:
                            hist_mean = city_month_data['historical_mean'].iloc[0]
                            hist_std = city_month_data['historical_std'].iloc[0]
                            
                            diff = live_data['temperature'] - hist_mean
                            z_score = diff / hist_std if hist_std > 0 else 0
                            abs_z = abs(z_score)
                            
                            if abs_z < 2:
                                status = "NORMAL"
                                explanation = "The current temperature is well within the typical historical range for this time of year."
                            elif 2 <= abs_z < 3:
                                status = "UNUSUAL"
                                explanation = "The current temperature is significantly higher or lower than the historical average."
                            else:
                                status = "EXTREME"
                                explanation = "The current temperature deviates extremely from historical norms (over 3 standard deviations)."
                                
                            col_base1, col_base2, col_base3 = st.columns(3)
                            
                            with col_base1:
                                render_kpi(f"Historical Typical<br>(Month {current_month})", f"{hist_mean:.1f}", "°C")
                            with col_base2:
                                sign = "+" if diff > 0 else ""
                                render_kpi("Difference", f"{sign}{diff:.1f}", "°C")
                            with col_base3:
                                st.markdown(f"""
                                <div class="kpi-container" style="border-color: #6366f1;">
                                    <div class="kpi-title">Statistical Anomaly Indicator</div>
                                    <div style="margin-top: 15px;"><span class="status-badge status-{status}">{status}</span></div>
                                    <div style="color: #9ca3af; font-size: 12px; margin-top: 10px;">Z-Score: {z_score:.2f}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                            st.info(explanation)
                            
                            # Simple Visual Context Chart
                            st.markdown("### Live Temperature Context")
                            # Create a simple bell curve or line to show where today sits
                            fig_context = go.Figure()
                            # Show historical distribution using a box plot
                            hist_temps = df[(df['city'] == selected_city) & (df['month'] == current_month)]['temperature_2m_max']
                            
                            fig_context.add_trace(go.Violin(x=hist_temps, name='Historical Distribution', line_color='#818cf8', fillcolor='#3730a3'))
                            fig_context.add_trace(go.Scatter(x=[live_data['temperature']], y=['Historical Distribution'], mode='markers', marker=dict(color='#ef4444', size=15, symbol='diamond'), name='Current Observation'))
                            
                            fig_context.update_layout(
                                template="plotly_dark", 
                                title="Current Observation vs Historical Pattern for this Month", 
                                xaxis_title="Temperature (°C)", 
                                height=300,
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                yaxis=dict(showgrid=False, showticklabels=False),
                                xaxis=dict(gridcolor='rgba(255,255,255,0.05)')
                            )
                            st.plotly_chart(fig_context, use_container_width=True)
                            
                    except Exception as e:
                        st.error(f"Failed to fetch live API data: {e}")

    # -------------------------------------------------------------------------
    # TAB 3: EXTREME EVENTS
    # -------------------------------------------------------------------------
    with tab3:
        st.markdown("### Identify Unusual Weather Observations")
        st.markdown("*Compare observations with their historical patterns to detect mathematically significant anomalies.*")
        
        mask = (df_scored['year'] >= year_range[0]) & (df_scored['year'] <= year_range[1])
        if selected_city != "All Cities":
            mask = mask & (df_scored['city'] == selected_city)
        t3_df = df_scored[mask]
        
        if not t3_df.empty:
            tot_ext, tot_unu, high_t, max_dev = get_extreme_events_summary(t3_df, year_range[0], year_range[1])
            
            ec1, ec2, ec3, ec4 = st.columns(4)
            with ec1: render_kpi("Total Extreme Events", f"{tot_ext:,}")
            with ec2: render_kpi("Total Unusual Events", f"{tot_unu:,}")
            with ec3: render_kpi("Highest Temperature", f"{high_t:.1f}", "°C")
            with ec4: render_kpi("Max Positive Deviation", f"+{max_dev:.1f}", "°C")
            
            st.markdown("---")
            col_chart, col_top = st.columns([2, 1])
            
            with col_chart:
                st.markdown("### Unusual Temperature Events")
                # Time series chart showing historical mean line and actuals, highlighting anomalies
                # To avoid giant slow plots, we sample or just plot the selected city if selected.
                # If "All Cities", we ask them to select one for the detailed time-series.
                if selected_city == "All Cities":
                    st.info("Select a specific city from the sidebar to view the extreme event time-series chart.")
                else:
                    fig_anom = go.Figure()
                    fig_anom.add_trace(go.Scatter(x=t3_df['date'], y=t3_df['temperature_2m_max'], mode='lines', name='Observed Temp', line=dict(color='#9ca3af', width=1)))
                    fig_anom.add_trace(go.Scatter(x=t3_df['date'], y=t3_df['historical_mean'], mode='lines', name='Historical Average', line=dict(color='#3b82f6', width=2, dash='dot')))
                    
                    # Highlight anomalies
                    ext_pts = t3_df[t3_df['Status'] == 'EXTREME']
                    unu_pts = t3_df[t3_df['Status'] == 'UNUSUAL']
                    
                    fig_anom.add_trace(go.Scatter(x=unu_pts['date'], y=unu_pts['temperature_2m_max'], mode='markers', name='Unusual', marker=dict(color='#f59e0b', size=6)))
                    fig_anom.add_trace(go.Scatter(x=ext_pts['date'], y=ext_pts['temperature_2m_max'], mode='markers', name='Extreme', marker=dict(color='#ef4444', size=8)))
                    
                    fig_anom.update_layout(
                        template="plotly_dark", 
                        xaxis_title="", 
                        yaxis_title="Temperature (°C)", 
                        hovermode="x unified", 
                        height=500,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(showgrid=False),
                        yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
                    )
                    st.plotly_chart(fig_anom, use_container_width=True)
            
            with col_top:
                st.markdown("### Top 10 Most Unusual Temperature Observations")
                top_df = get_top_extreme_events(t3_df, year_range[0], year_range[1])
                
                # Apply styling to status
                def style_status(val):
                    color = '#ef4444' if val == 'EXTREME' else '#f59e0b'
                    return f'color: {color}; font-weight: bold;'
                
                st.dataframe(
                    top_df.style.map(style_status, subset=['Status']),
                    use_container_width=True,
                    hide_index=True
                )
        
    st.markdown("---")
    
    # Bottom Section: How it works & Technical details
    st.markdown("### 🔍 How It Works")
    st.markdown("""
    <div style="background-color: #1f2937; padding: 20px; border-radius: 10px; border-left: 5px solid #6366f1; text-align: center; color: #d1d5db;">
        <b>HISTORICAL WEATHER DATA</b> ➔ <b>TREND & SEASONAL ANALYSIS</b> ➔ <b>HISTORICAL BASELINE</b> ➔ <b>CURRENT OBSERVATION</b> ➔ <b>COMPARE</b> ➔ <b>NORMAL / UNUSUAL / EXTREME</b>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("Technical Details"):
        st.markdown(f"""
        - **Dataset**: Daily weather observations for Indian cities.
        - **Number of records**: {len(df):,}
        - **Number of cities**: {df['city'].nunique()}
        - **Date range**: {df['date'].min().date()} to {df['date'].max().date()}
        - **Columns used**: `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, `city`, `date`.
        - **Anomaly detection method**: Z-score statistical comparison calculated dynamically per city and per month.
        - **Z-score formula**: `Z = (Actual Temperature - Historical Mean) / Historical Standard Deviation`
        - **Thresholds**: Normal (Z < 2), Unusual (2 ≤ Z < 3), Extreme (Z ≥ 3).
        - **Live API source**: Open-Meteo (open-source weather API).
        """)

if __name__ == "__main__":
    main()
