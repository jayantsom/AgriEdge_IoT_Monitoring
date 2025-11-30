# components/sensor_display.py
import streamlit as st

def render_sensor_tiles(sensor_data):
    """Render sensor data tiles in a clean layout"""
    
    # Row 1: Environmental Sensors
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_temperature_humidity(sensor_data)
    
    with col2:
        render_soil_moisture(sensor_data)
    
    with col3:
        render_light_intensity(sensor_data)
    
    # Row 2: NPK Sensors
    st.subheader("🧪 Soil Nutrients (NPK)")
    npk_col1, npk_col2, npk_col3 = st.columns(3)
    
    with npk_col1:
        render_nutrient("Nitrogen (N)", "npk_n", sensor_data, "mg/kg")
    
    with npk_col2:
        render_nutrient("Phosphorus (P)", "npk_p", sensor_data, "mg/kg")
    
    with npk_col3:
        render_nutrient("Potassium (K)", "npk_k", sensor_data, "mg/kg")

def render_temperature_humidity(sensor_data):
    """Render temperature and humidity metrics"""
    st.subheader("🌡️ Temperature & Humidity")
    
    if sensor_data:
        temp_val = sensor_data.get('temperature', 0)
        humid_val = sensor_data.get('humidity', 0)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Temperature", f"{temp_val:.1f}", "°C")
        with col2:
            st.metric("Humidity", f"{humid_val:.1f}", "%")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Temperature", "—", "°C")
        with col2:
            st.metric("Humidity", "—", "%")

def render_soil_moisture(sensor_data):
    """Render soil moisture metric"""
    st.subheader("💧 Soil Moisture")
    
    if sensor_data:
        moisture_val = sensor_data.get('soil_moisture', 0)
        
        # Color code based on moisture level
        if moisture_val < 30:
            delta_color = "off"
            status = "Low"
        elif moisture_val > 70:
            delta_color = "inverse" 
            status = "High"
        else:
            delta_color = "normal"
            status = "Optimal"
            
        st.metric("Moisture Level", f"{moisture_val:.1f}", "%", delta_color=delta_color)
        st.caption(f"Status: {status}")
    else:
        st.metric("Moisture Level", "—", "%")
        st.caption("Status: Unknown")

def render_light_intensity(sensor_data):
    """Render light intensity metric"""
    st.subheader("☀️ Light Intensity")
    
    if sensor_data:
        light_val = sensor_data.get('light_intensity', 0)
        
        # Color code based on light level
        if light_val < 200:
            delta_color = "off"
            status = "Low"
        elif light_val > 800:
            delta_color = "inverse"
            status = "High"
        else:
            delta_color = "normal"
            status = "Optimal"
            
        st.metric("Light", f"{light_val:,}", "lux", delta_color=delta_color)
        st.caption(f"Status: {status}")
    else:
        st.metric("Light", "—", "lux")
        st.caption("Status: Unknown")

def render_nutrient(name, key, sensor_data, unit):
    """Render NPK nutrient metric"""
    if sensor_data:
        value = sensor_data.get(key, 0)
        
        # Color coding for nutrient levels
        if value < 15:
            delta_color = "off"
            status = "Low"
        elif value > 35:
            delta_color = "inverse"
            status = "High" 
        else:
            delta_color = "normal"
            status = "Optimal"
            
        st.metric(name, f"{value}", unit, delta_color=delta_color)
        st.caption(f"Status: {status}")
    else:
        st.metric(name, "—", unit)
        st.caption("Status: Unknown")