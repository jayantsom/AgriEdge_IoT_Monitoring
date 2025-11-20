import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import paho.mqtt.client as mqtt
import json
import ssl
from datetime import datetime
import time

# Import configuration
from config import *

# Global variable to store latest sensor data
latest_sensor_data = None

# Initialize session state
if 'mqtt_client' not in st.session_state:
    st.session_state.mqtt_client = None
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False
if 'mqtt_connected' not in st.session_state:
    st.session_state.mqtt_connected = False

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        st.session_state.mqtt_connected = True
        client.subscribe(TOPIC_SENSOR)
        print("✅ Connected to HiveMQ Cloud")
    else:
        st.session_state.mqtt_connected = False
        print(f"❌ Connection failed with code {rc}")

def on_message(client, userdata, msg):
    global latest_sensor_data
    try:
        data = json.loads(msg.payload.decode())
        # Convert to your CSV format
        latest_sensor_data = {
            "timestamp": datetime.now(),
            "temperature°C": data.get("temperature", 0),
            "humidity %": data.get("humidity", 0),
            "soil_moisture%": data.get("moisture", 0),
            "light_intensitylux": data.get("light", 0),
            "npk_n": data.get("nitrogen", 0),
            "npk_p": data.get("phosphorus", 0),
            "npk_k": data.get("potassium", 0),
            "irrigation_needed": data.get("irrigation_prediction", 0),
            "plant_health": data.get("plant_health_prediction", "unknown"),
            "pump_status": "ON" if data.get("irrigation_prediction", 0) == 1 else "OFF"
        }
        
        print(f"📥 Received data: Temp={latest_sensor_data['temperature°C']}, Humidity={latest_sensor_data['humidity %']}")
        
        # Save to CSV
        save_to_csv(latest_sensor_data)
        
    except Exception as e:
        print(f"❌ Error processing MQTT message: {e}")

def save_to_csv(data):
    """Save sensor data to CSV file with size management"""
    try:
        df = pd.read_csv(CSV_FILE)
    except:
        df = pd.DataFrame(columns=[
            "timestamp", "temperature°C", "humidity %", "soil_moisture%",
            "light_intensitylux", "npk_n", "npk_p", "npk_k",
            "irrigation_needed", "plant_health", "pump_status"
        ])
    
    # Add new data
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    
    # Keep only recent data (prevent unlimited growth)
    if len(df) > MAX_DATA_POINTS:
        df = df.tail(MAX_DATA_POINTS)
    
    df.to_csv(CSV_FILE, index=False)

def start_mqtt_client():
    """Initialize and start MQTT client"""
    try:
        client = mqtt.Client()
        client.username_pw_set(USERNAME, PASSWORD)
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
        
        client.on_connect = on_connect
        client.on_message = on_message
        
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()
        return client
    except Exception as e:
        st.error(f"Failed to start MQTT client: {e}")
        return None

def stop_mqtt_client():
    """Stop MQTT client"""
    if st.session_state.mqtt_client:
        st.session_state.mqtt_client.loop_stop()
        st.session_state.mqtt_client.disconnect()
        st.session_state.mqtt_client = None
    st.session_state.monitoring_active = False
    st.session_state.mqtt_connected = False

# Streamlit App Configuration
st.set_page_config(
    page_title="AgriEdge - IoT Agriculture Monitor",
    page_icon="🌱",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stButton button {height: 50px;}
    .stSuccess {height: 48px; display: flex; align-items: center;}
    .status-box {border-radius: 10px; padding: 10px;}
</style>
""", unsafe_allow_html=True)

# Header Section
st.image("./assets/header1.jpg", width='stretch')

# Configuration Section
st.info("**Select your soil type and crop stage, then click 'Start Monitoring' to begin.**")

col1, col2, col3 = st.columns(3)

with col1:
    soil_type = st.selectbox(
        "**Soil Type**",
        SOIL_TYPES,
        help="Select the type of soil in your farm"
    )

with col2:
    crop_stage = st.selectbox(
        "**Crop Stage**",
        CROP_STAGES,
        help="Select the current growth stage of your crop"
    )

with col3:
    btn_col, msg_col = st.columns([1, 2])
    
    with btn_col:
        start_monitoring = st.button(
            "**Start Monitoring**",
            type="primary",
            width='stretch'
        )
    
    with msg_col:
        if start_monitoring and not st.session_state.monitoring_active:
            st.session_state.mqtt_client = start_mqtt_client()
            if st.session_state.mqtt_client:
                st.session_state.monitoring_active = True
                st.success("Monitoring started! Connecting to Raspberry Pi...")
            else:
                st.error("Failed to start monitoring")
        
        if st.session_state.monitoring_active:
            if st.session_state.mqtt_connected:
                st.success("✅ Live monitoring active - Connected to RPi")
            else:
                st.warning("🔄 Connecting to Raspberry Pi...")

# Real-time Sensor Data Section
st.markdown("---")
st.header("Real-time Sensor Data")

# Last updated timestamp
if latest_sensor_data:
    last_updated = latest_sensor_data['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
    connection_status = "✅ Receiving live data"
else:
    last_updated = "—"
    connection_status = "⏳ Waiting for data..."

st.markdown(f"**Last Updated:** {last_updated} | **Status:** {connection_status}")

# Sensor Data Tiles - shows real data
# Row 1: Environmental Sensors
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🌡️ Temperature & Humidity")
    temp_val = latest_sensor_data['temperature°C'] if latest_sensor_data else "—"
    humid_val = latest_sensor_data['humidity %'] if latest_sensor_data else "—"
    st.metric("Temperature", f"{temp_val}", "°C")
    st.metric("Humidity", f"{humid_val}", "%")

with col2:
    st.subheader("💧 Soil Moisture")
    moisture_val = latest_sensor_data['soil_moisture%'] if latest_sensor_data else "—"
    st.metric("Moisture Level", f"{moisture_val}", "%")

with col3:
    st.subheader("☀️ Light Intensity")
    light_val = latest_sensor_data['light_intensitylux'] if latest_sensor_data else "—"
    st.metric("Light", f"{light_val}", "lux")

# Row 2: NPK Values
st.subheader("🧪 Soil Nutrients (NPK)")
npk_col1, npk_col2, npk_col3 = st.columns(3)

with npk_col1:
    n_val = latest_sensor_data['npk_n'] if latest_sensor_data else "—"
    st.metric("Nitrogen (N)", f"{n_val}", "mg/kg")

with npk_col2:
    p_val = latest_sensor_data['npk_p'] if latest_sensor_data else "—"
    st.metric("Phosphorus (P)", f"{p_val}", "mg/kg")

with npk_col3:
    k_val = latest_sensor_data['npk_k'] if latest_sensor_data else "—"
    st.metric("Potassium (K)", f"{k_val}", "mg/kg")

# Row 3: Status Indicators with colors - FIXED: Now shows real data
st.subheader("🔧 System Status")
status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    container = st.container(border=True)
    container.markdown("**🔄 Irrigation Needed**")
    if latest_sensor_data:
        irrigation_val = latest_sensor_data['irrigation_needed']
        color = "red" if irrigation_val == 1 else "green"
        text = "YES" if irrigation_val == 1 else "NO"
        container.markdown(f"<h3 style='color: {color}; text-align: center;'>{text}</h3>", unsafe_allow_html=True)
    else:
        container.markdown("<h3 style='color: gray; text-align: center;'>—</h3>", unsafe_allow_html=True)

with status_col2:
    container = st.container(border=True)
    container.markdown("**🌱 Plant Health**")
    if latest_sensor_data:
        health = latest_sensor_data['plant_health']
        if health == "healthy":
            color = "green"
        elif health == "stressed":
            color = "orange"
        else:
            color = "red"
        container.markdown(f"<h3 style='color: {color}; text-align: center; text-transform: capitalize;'>{health}</h3>", unsafe_allow_html=True)
    else:
        container.markdown("<h3 style='color: gray; text-align: center;'>—</h3>", unsafe_allow_html=True)

with status_col3:
    container = st.container(border=True)
    container.markdown("**🚰 Pump Status**")
    if latest_sensor_data:
        pump_status = latest_sensor_data['pump_status']
        color = "green" if pump_status == "ON" else "red"
        container.markdown(f"<h3 style='color: {color}; text-align: center;'>{pump_status}</h3>", unsafe_allow_html=True)
    else:
        container.markdown("<h3 style='color: gray; text-align: center;'>—</h3>", unsafe_allow_html=True)

# Real-time Graphs Section
st.markdown("---")
st.header("Real-time Monitoring")

# Create two columns for the graphs
col1, col2 = st.columns(2)

with col1:
    try:
        df = pd.read_csv(CSV_FILE)
        if not df.empty and len(df) > 1:
            fig_env = make_subplots(specs=[[{"secondary_y": True}]])
            fig_env.add_trace(go.Scatter(x=df['timestamp'], y=df['temperature°C'], name='Temperature', line=dict(color='red')), secondary_y=False)
            fig_env.add_trace(go.Scatter(x=df['timestamp'], y=df['humidity %'], name='Humidity', line=dict(color='blue')), secondary_y=False)
            fig_env.add_trace(go.Scatter(x=df['timestamp'], y=df['soil_moisture%'], name='Soil Moisture', line=dict(color='brown')), secondary_y=True)
            fig_env.add_trace(go.Scatter(x=df['timestamp'], y=df['light_intensitylux'], name='Light', line=dict(color='orange')), secondary_y=True)
            fig_env.update_layout(title="Environmental Sensors Over Time", xaxis_title="Time", height=400)
            fig_env.update_yaxes(title_text="Temp (°C) / Humidity (%)", secondary_y=False)
            fig_env.update_yaxes(title_text="Moisture (%) / Light (lux)", secondary_y=True)
            st.plotly_chart(fig_env, width='stretch')
        else:
            st.info("Collecting sensor data... Graph will appear shortly.")
    except Exception as e:
        st.info("No data available yet. Data will appear after monitoring starts.")

with col2:
    try:
        df = pd.read_csv(CSV_FILE)
        if not df.empty and len(df) > 1:
            fig_npk = go.Figure()
            fig_npk.add_trace(go.Scatter(x=df['timestamp'], y=df['npk_n'], name='Nitrogen', line=dict(color='blue')))
            fig_npk.add_trace(go.Scatter(x=df['timestamp'], y=df['npk_p'], name='Phosphorus', line=dict(color='red')))
            fig_npk.add_trace(go.Scatter(x=df['timestamp'], y=df['npk_k'], name='Potassium', line=dict(color='green')))
            fig_npk.update_layout(title="NPK Levels Over Time", xaxis_title="Time", yaxis_title="mg/kg", height=400)
            st.plotly_chart(fig_npk, width='stretch')
        else:
            st.info("Collecting sensor data... Graph will appear shortly.")
    except Exception as e:
        st.info("No data available yet. Data will appear after monitoring starts.")

# Stop Monitoring Section
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col2:
    stop_monitoring = st.button("Stop Monitoring", type="secondary", width='stretch')
    if stop_monitoring:
        stop_mqtt_client()
        st.warning("Monitoring stopped!")
        st.rerun()

# Auto-refresh when monitoring is active
if st.session_state.monitoring_active:
    time.sleep(REFRESH_INTERVAL)
    st.rerun()