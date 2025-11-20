import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import paho.mqtt.client as mqtt
import json
import ssl
from datetime import datetime
import time
import os

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
if 'last_data_time' not in st.session_state:
    st.session_state.last_data_time = None
if 'connection_attempts' not in st.session_state:
    st.session_state.connection_attempts = 0

# MQTT Callbacks
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        st.session_state.mqtt_connected = True
        st.session_state.connection_attempts = 0
        client.subscribe(TOPIC_SENSOR)
        print("✅ Connected to HiveMQ Cloud - Subscribed to", TOPIC_SENSOR)
    else:
        st.session_state.mqtt_connected = False
        print(f"❌ Connection failed with code {rc}")

def on_message(client, userdata, msg):
    global latest_sensor_data
    try:
        data = json.loads(msg.payload.decode())
        
        # Validate data types
        temperature = float(data.get("temperature", 0))
        humidity = float(data.get("humidity", 0))
        moisture = float(data.get("moisture", 0))
        light = int(data.get("light", 0))
        nitrogen = int(data.get("nitrogen", 0))
        phosphorus = int(data.get("phosphorus", 0))
        potassium = int(data.get("potassium", 0))
        irrigation_prediction = int(data.get("irrigation_prediction", 0))
        plant_health = str(data.get("plant_health_prediction", "unknown"))
        
        # Convert to your CSV format
        latest_sensor_data = {
            "timestamp": datetime.now(),
            "temperature°C": temperature,
            "humidity %": humidity,
            "soil_moisture%": moisture,
            "light_intensitylux": light,
            "npk_n": nitrogen,
            "npk_p": phosphorus,
            "npk_k": potassium,
            "irrigation_needed": irrigation_prediction,
            "plant_health": plant_health,
            "pump_status": "ON" if irrigation_prediction == 1 else "OFF"
        }
        
        st.session_state.last_data_time = datetime.now()
        
        print(f"📥 Received data: Temp={temperature}°C, Humidity={humidity}%, Moisture={moisture}%")
        
        # Save to CSV
        save_to_csv(latest_sensor_data)
        
    except Exception as e:
        print(f"❌ Error processing MQTT message: {e}")
        print(f"Raw message: {msg.payload.decode()}")

def on_disconnect(client, userdata, rc, properties=None):
    st.session_state.mqtt_connected = False
    print("🔌 Disconnected from HiveMQ Cloud")

def save_to_csv(data):
    """Save sensor data to CSV file with size management"""
    try:
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
        else:
            df = pd.DataFrame(columns=[
                "timestamp", "temperature°C", "humidity %", "soil_moisture%",
                "light_intensitylux", "npk_n", "npk_p", "npk_k",
                "irrigation_needed", "plant_health", "pump_status"
            ])
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
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
    
    try:
        df.to_csv(CSV_FILE, index=False)
        print(f"💾 Saved data to CSV (Total records: {len(df)})")
    except Exception as e:
        print(f"❌ Error saving CSV: {e}")

def start_mqtt_client():
    """Initialize and start MQTT client"""
    try:
        # Use Callback API Version 2
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.username_pw_set(USERNAME, PASSWORD)
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
        
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        
        # Set last will testament
        client.will_set(TOPIC_SENSOR, json.dumps({"status": "offline"}), qos=1)
        
        print(f"🔗 Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()
        
        # Wait a bit for connection to establish
        time.sleep(2)
        return client
    except Exception as e:
        st.session_state.connection_attempts += 1
        st.error(f"❌ Failed to start MQTT client (Attempt {st.session_state.connection_attempts}): {e}")
        return None

def stop_mqtt_client():
    """Stop MQTT client"""
    if st.session_state.mqtt_client:
        try:
            st.session_state.mqtt_client.loop_stop()
            st.session_state.mqtt_client.disconnect()
            print("🛑 MQTT client stopped")
        except Exception as e:
            print(f"❌ Error stopping MQTT client: {e}")
        st.session_state.mqtt_client = None
    
    st.session_state.monitoring_active = False
    st.session_state.mqtt_connected = False
    st.session_state.last_data_time = None

def check_data_freshness():
    """Check if data is still being received"""
    if st.session_state.last_data_time:
        time_diff = (datetime.now() - st.session_state.last_data_time).total_seconds()
        return time_diff < 30  # Data is fresh if less than 30 seconds old
    return False

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
    .stWarning {height: 48px; display: flex; align-items: center;}
    .status-box {border-radius: 10px; padding: 10px;}
    .data-fresh {color: green;}
    .data-stale {color: orange;}
    .data-none {color: gray;}
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
                st.success("🚀 Monitoring started! Connecting to Raspberry Pi...")
            else:
                st.error("❌ Failed to start monitoring - Check MQTT credentials")
        
        if st.session_state.monitoring_active:
            if st.session_state.mqtt_connected:
                if check_data_freshness():
                    st.success("✅ Live monitoring active - Receiving data from RPi")
                else:
                    st.warning("🔄 Connected to RPi - Waiting for sensor data...")
            else:
                st.warning("🔄 Connecting to Raspberry Pi...")

# Real-time Sensor Data Section
st.markdown("---")
st.header("📊 Real-time Sensor Data")

# Connection and data status
if latest_sensor_data and check_data_freshness():
    last_updated = latest_sensor_data['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
    connection_status = "✅ Receiving live data"
    status_class = "data-fresh"
elif st.session_state.mqtt_connected:
    last_updated = "—"
    connection_status = "🔄 Connected - Waiting for data"
    status_class = "data-stale"
else:
    last_updated = "—"
    connection_status = "⏳ Not connected"
    status_class = "data-none"

st.markdown(f"**Last Updated:** <span class='{status_class}'>{last_updated}</span> | **Status:** <span class='{status_class}'>{connection_status}</span>", unsafe_allow_html=True)

# Data freshness warning
if st.session_state.monitoring_active and st.session_state.mqtt_connected and not check_data_freshness():
    st.warning("⚠️ No data received from Raspberry Pi recently. Check if RPi is running and sensors are active.")

# Sensor Data Tiles
# Row 1: Environmental Sensors
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🌡️ Temperature & Humidity")
    if latest_sensor_data:
        temp_val = latest_sensor_data['temperature°C']
        humid_val = latest_sensor_data['humidity %']
        st.metric("Temperature", f"{temp_val:.1f}", "°C")
        st.metric("Humidity", f"{humid_val:.1f}", "%")
    else:
        st.metric("Temperature", "—", "°C")
        st.metric("Humidity", "—", "%")

with col2:
    st.subheader("💧 Soil Moisture")
    if latest_sensor_data:
        moisture_val = latest_sensor_data['soil_moisture%']
        st.metric("Moisture Level", f"{moisture_val:.1f}", "%")
    else:
        st.metric("Moisture Level", "—", "%")

with col3:
    st.subheader("☀️ Light Intensity")
    if latest_sensor_data:
        light_val = latest_sensor_data['light_intensitylux']
        st.metric("Light", f"{light_val}", "lux")
    else:
        st.metric("Light", "—", "lux")

# Row 2: NPK Values
st.subheader("🧪 Soil Nutrients (NPK)")
npk_col1, npk_col2, npk_col3 = st.columns(3)

with npk_col1:
    if latest_sensor_data:
        n_val = latest_sensor_data['npk_n']
        st.metric("Nitrogen (N)", f"{n_val}", "mg/kg")
    else:
        st.metric("Nitrogen (N)", "—", "mg/kg")

with npk_col2:
    if latest_sensor_data:
        p_val = latest_sensor_data['npk_p']
        st.metric("Phosphorus (P)", f"{p_val}", "mg/kg")
    else:
        st.metric("Phosphorus (P)", "—", "mg/kg")

with npk_col3:
    if latest_sensor_data:
        k_val = latest_sensor_data['npk_k']
        st.metric("Potassium (K)", f"{k_val}", "mg/kg")
    else:
        st.metric("Potassium (K)", "—", "mg/kg")

# Row 3: Status Indicators with colors
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
        if health.lower() == "healthy":
            color = "green"
        elif health.lower() == "stressed":
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
st.header("📈 Real-time Monitoring")

# Create two columns for the graphs
col1, col2 = st.columns(2)

with col1:
    try:
        if os.path.exists(CSV_FILE):
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
                st.info("📊 Collecting sensor data... Graph will appear shortly.")
        else:
            st.info("📊 No data file found. Start monitoring to collect data.")
    except Exception as e:
        st.error(f"❌ Error loading environmental data: {e}")

with col2:
    try:
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            if not df.empty and len(df) > 1:
                fig_npk = go.Figure()
                fig_npk.add_trace(go.Scatter(x=df['timestamp'], y=df['npk_n'], name='Nitrogen', line=dict(color='blue')))
                fig_npk.add_trace(go.Scatter(x=df['timestamp'], y=df['npk_p'], name='Phosphorus', line=dict(color='red')))
                fig_npk.add_trace(go.Scatter(x=df['timestamp'], y=df['npk_k'], name='Potassium', line=dict(color='green')))
                fig_npk.update_layout(title="NPK Levels Over Time", xaxis_title="Time", yaxis_title="mg/kg", height=400)
                st.plotly_chart(fig_npk, width='stretch')
            else:
                st.info("📊 Collecting sensor data... Graph will appear shortly.")
        else:
            st.info("📊 No data file found. Start monitoring to collect data.")
    except Exception as e:
        st.error(f"❌ Error loading NPK data: {e}")

# Stop Monitoring Section
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col2:
    stop_monitoring = st.button("Stop Monitoring", type="primary", width='stretch')
    if stop_monitoring:
        stop_mqtt_client()
        st.warning("🛑 Monitoring stopped!")
        st.stop()

# Auto-refresh when monitoring is active
if st.session_state.monitoring_active:
    time.sleep(REFRESH_INTERVAL)
    st.rerun()

# Debug information (hidden by default)
with st.expander("🔧 Debug Information"):
    st.write("**Session State:**")
    st.json({
        "monitoring_active": st.session_state.monitoring_active,
        "mqtt_connected": st.session_state.mqtt_connected,
        "connection_attempts": st.session_state.connection_attempts,
        "last_data_time": str(st.session_state.last_data_time),
        "data_freshness": check_data_freshness()
    })
    
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            st.write(f"**CSV Data:** {len(df)} records")
            if not df.empty:
                st.dataframe(df.tail(3))
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
    else:
        st.write("**CSV Data:** File not found")