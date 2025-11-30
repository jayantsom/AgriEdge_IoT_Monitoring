# components/status_indicators.py
import streamlit as st

def render_status_indicators(sensor_data):
    """Render system status indicators"""
    st.subheader("🔧 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_irrigation_status(sensor_data)
    
    with col2:
        render_plant_health_status(sensor_data)
    
    with col3:
        render_pump_status(sensor_data)

def render_irrigation_status(sensor_data):
    """Render irrigation needed status"""
    container = st.container(border=True)
    container.markdown("**🔄 Irrigation Needed**")
    
    if sensor_data:
        irrigation_val = sensor_data.get('irrigation_needed', 0)
        
        if irrigation_val == 1:
            status_text = "YES"
            status_color = "red"
            status_emoji = "💧"
            help_text = "Plants need water - Irrigation recommended"
        else:
            status_text = "NO" 
            status_color = "green"
            status_emoji = "✅"
            help_text = "Soil moisture is adequate"
            
        container.markdown(
            f"<h3 style='color: {status_color}; text-align: center; margin: 0;'>{status_emoji} {status_text}</h3>",
            unsafe_allow_html=True
        )
        container.caption(help_text)
    else:
        container.markdown("<h3 style='color: gray; text-align: center;'>—</h3>", unsafe_allow_html=True)
        container.caption("No data available")

def render_plant_health_status(sensor_data):
    """Render plant health status"""
    container = st.container(border=True)
    container.markdown("**🌱 Plant Health**")
    
    if sensor_data:
        health = sensor_data.get('plant_health', 'Unknown')
        health_lower = health.lower()
        
        # Map health status to colors and emojis
        health_config = {
            'healthy': {'color': 'green', 'emoji': '🌿', 'desc': 'Plants are healthy'},
            'moderate stress': {'color': 'orange', 'emoji': '🌱', 'desc': 'Plants show moderate stress'},
            'high stress': {'color': 'red', 'emoji': '🍂', 'desc': 'Plants are under high stress'},
        }
        
        config = health_config.get(health_lower, {'color': 'gray', 'emoji': '❓', 'desc': 'Unknown status'})
        
        container.markdown(
            f"<h3 style='color: {config['color']}; text-align: center; margin: 0;'>{config['emoji']} {health.title()}</h3>",
            unsafe_allow_html=True
        )
        container.caption(config['desc'])
    else:
        container.markdown("<h3 style='color: gray; text-align: center;'>—</h3>", unsafe_allow_html=True)
        container.caption("No data available")

def render_pump_status(sensor_data):
    """Render pump status"""
    container = st.container(border=True)
    container.markdown("**🚰 Pump Status**")
    
    if sensor_data:
        irrigation_val = sensor_data.get('irrigation_needed', 0)
        pump_status = "ON" if irrigation_val == 1 else "OFF"
        color = "green" if pump_status == "ON" else "red"
        emoji = "💦" if pump_status == "ON" else "⏸️"
        help_text = "Pump is currently active" if pump_status == "ON" else "Pump is idle"
        
        container.markdown(
            f"<h3 style='color: {color}; text-align: center; margin: 0;'>{emoji} {pump_status}</h3>",
            unsafe_allow_html=True
        )
        container.caption(help_text)
    else:
        container.markdown("<h3 style='color: gray; text-align: center;'>—</h3>", unsafe_allow_html=True)
        container.caption("No data available")