import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

# Set page configuration
st.set_page_config(page_title="Green DevOps Dashboard", layout="wide")

# Path to the database
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "green_metrics.db")

def load_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM carbon_logs ORDER BY timestamp DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def calculate_green_grade(smells, energy):
    """Calculates a sustainability grade from A+ to F."""
    score = 100
    # Deduct points for high energy usage
    if energy > 0.000005: score -= 20
    elif energy > 0.000002: score -= 10
    
    # Deduct points for bad code practices
    score -= (smells * 15)
    
    if score >= 90: return "A+ 🏆"
    elif score >= 80: return "A 🟢"
    elif score >= 70: return "B 🟡"
    elif score >= 60: return "C 🟠"
    else: return "F 🔴"

st.title("🌱 Green DevOps Sustainability Dashboard")
st.markdown("### Real-time Carbon Tracking for your CI/CD Pipeline")

data = load_data()

if data.empty:
    st.warning("No data found. Please run the green_analyzer.py script first to generate logs.")
else:
    # Top Metrics Row (Now with 4 columns!)
    col1, col2, col3, col4 = st.columns(4)
    latest_run = data.iloc[0]
    
    with col1:
        st.metric("Latest Carbon Impact", f"{latest_run['co2_mg']} mg CO2")
    with col2:
        st.metric("Code Smells", int(latest_run['smell_count']))
    with col3:
        avg_energy = round(data['energy_kwh'].mean(), 8)
        st.metric("Avg Energy per Run", f"{avg_energy} kWh")
    with col4:
        grade = calculate_green_grade(latest_run['smell_count'], latest_run['energy_kwh'])
        st.metric("Sustainability Grade", grade)

    st.divider()

    # Graphs Row
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Carbon Emission Trend")
        fig_carbon = px.line(data, x='timestamp', y='co2_mg', markers=True, 
                             labels={'co2_mg': 'CO2 (mg)', 'timestamp': 'Time'})
        st.plotly_chart(fig_carbon, use_container_width=True)

    with col_b:
        st.subheader("Energy Consumption Distribution")
        fig_energy = px.bar(data, x='timestamp', y='energy_kwh', color='co2_mg',
                            labels={'energy_kwh': 'Energy (kWh)'})
        st.plotly_chart(fig_energy, use_container_width=True)

    # Detailed Log Table
    st.subheader("📜 Detailed Audit History")
    st.dataframe(data, use_container_width=True)