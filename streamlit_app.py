import streamlit as st
from data_generator import save_data
import time
import threading
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

monitoring_active = False

st.set_page_config(
    page_title="AgriEdge",
    page_icon="🌱",
    layout="wide"
)

def generate_continuous_data():
    global monitoring_active
    monitoring_active = True
    while monitoring_active:
        save_data()
        time.sleep(2)

st.image("./assets/header1.jpg", use_container_width =True)

st.info("**Select your soil type and crop stage, then click 'Start Monitoring' to begin.**")

col1, col2, col3 = st.columns(3)

with col1:
    soil_type = st.selectbox(
        "**Soil Type**",
        ['Clay', 'Sandy', 'Red', 'Loam', 'Black', 'Alluvial', 'Chalky'],
        help="Select the type of soil in your farm"
    )

with col2:
    crop_stage = st.selectbox(
        "**Crop Stage**",
        ['Flowering', 'Seedling', 'Vegetative Growth', 'Root/Tuber Development',
         'Germination', 'Pollination', 'Fruit/Grain/Bulb Formation', 'Maturation', 'Harvest'],
        help="Select the current growth stage of your crop"
    )

with col3:

    st.markdown("""<style>
                .stButton button {height: 50px;}
                .stSuccess {height: 48px;}
                </style>""", unsafe_allow_html=True)

    btn_col, msg_col = st.columns([1, 2])
    
    with btn_col:
        start_monitoring = st.button(
            "**Start Monitoring**",
            type="primary",
            use_container_width=True
        )
    
    with msg_col:
        if start_monitoring:
            st.success(f"Monitoring started!")
            thread = threading.Thread(target=generate_continuous_data, daemon=True)
            thread.start()

st.markdown("---")
st.header("Real-time Sensor Data")
st.markdown("**Last Updated:** —")

# Row 1: Environmental Sensors
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🌡️ Temperature & Humidity")
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.metric("Temperature", "—", "°C")
    with col_b:
        st.metric("Humidity", "—", "%")

with col2:
    st.subheader("💧 Soil Moisture")
    st.metric("Moisture Level", "—", "%")

with col3:
    st.subheader("☀️ Light Intensity")
    st.metric("Light", "—", "lux")

# Row 2: NPK Values
st.subheader("🧪 Soil Nutrients (NPK)")
npk_col1, npk_col2, npk_col3 = st.columns(3)

with npk_col1:
    st.metric("Nitrogen (N)", "—", "mg/kg")
with npk_col2:
    st.metric("Phosphorus (P)", "—", "mg/kg")
with npk_col3:
    st.metric("Potassium (K)", "—", "mg/kg")

# Row 3: Status Indicators
st.subheader("🔧 System Status")
status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    # Irrigation Needed
    container = st.container(border=True)
    container.markdown("**🔄 Irrigation Needed**")
    container.markdown("<h3 style='color: gray;'>—</h3>", unsafe_allow_html=True)

with status_col2:
    # Plant Health
    container = st.container(border=True)
    container.markdown("**🌱 Plant Health**")
    container.markdown("<h3 style='color: gray;'>—</h3>", unsafe_allow_html=True)

with status_col3:
    # Pump Status
    container = st.container(border=True)
    container.markdown("**🚰 Pump Status**")
    container.markdown("<h3 style='color: gray;'>—</h3>", unsafe_allow_html=True)

st.markdown("---")
st.header("Real-time Monitoring")

# Create two tabs for the graphs
col1, col2 = st.columns(2)

with col1:
    try:
        df = pd.read_csv('sensor_data.csv')
        fig_env = make_subplots(specs=[[{"secondary_y": True}]])
        fig_env.add_trace(go.Scatter(x=df['timestamp'], y=df['temperature°C'], name='Temperature', line=dict(color='red')), secondary_y=False)
        fig_env.add_trace(go.Scatter(x=df['timestamp'], y=df['humidity %'], name='Humidity', line=dict(color='blue')), secondary_y=False)
        fig_env.add_trace(go.Scatter(x=df['timestamp'], y=df['soil_moisture%'], name='Soil Moisture', line=dict(color='brown')), secondary_y=True)
        fig_env.add_trace(go.Scatter(x=df['timestamp'], y=df['light_intensitylux'], name='Light', line=dict(color='orange')), secondary_y=True)
        fig_env.update_layout(title="Environmental Sensors Over Time", xaxis_title="Time")
        fig_env.update_yaxes(title_text="Temp (°C) / Humidity (%)", secondary_y=False)
        fig_env.update_yaxes(title_text="Moisture (%) / Light (lux)", secondary_y=True)
        st.plotly_chart(fig_env, use_container_width=True)
    except:
        st.info("No data available yet. Data will appear after monitoring starts.")

with col2:
    try:
        df = pd.read_csv('sensor_data.csv')
        fig_npk = go.Figure()
        fig_npk.add_trace(go.Scatter(x=df['timestamp'], y=df['npk_n'], name='Nitrogen', line=dict(color='blue')))
        fig_npk.add_trace(go.Scatter(x=df['timestamp'], y=df['npk_p'], name='Phosphorus', line=dict(color='red')))
        fig_npk.add_trace(go.Scatter(x=df['timestamp'], y=df['npk_k'], name='Potassium', line=dict(color='green')))
        fig_npk.update_layout(title="NPK Levels Over Time", xaxis_title="Time", yaxis_title="mg/kg")
        st.plotly_chart(fig_npk, use_container_width=True)
    except:
        st.info("No data available yet. Data will appear after monitoring starts.")

st.markdown("---")
col1, col2, col3 = st.columns(3)
st.markdown("---")
with col2:
    stop_monitoring = st.button("Stop Monitoring", type="primary", use_container_width=True)
    if stop_monitoring:
        monitoring_active = False
        st.warning("Monitoring stopped!")