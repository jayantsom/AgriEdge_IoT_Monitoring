# pages/1_📊_Live_Dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime

from components.header import render_header
from components.sensor_display import render_sensor_tiles
from components.charts import render_charts
from components.status_indicators import render_status_indicators
from config import DATA_FRESHNESS_THRESHOLD

class LiveDashboard:
    def __init__(self):
        self.setup_page()
    
    def setup_page(self):
        """Setup page configuration"""
        st.set_page_config(
            page_title="Live Dashboard - AgriEdge",
            page_icon="📊",
            layout="wide"
        )
    
    def is_data_fresh(self):
        """Check if data is still fresh"""
        if 'last_data_time' in st.session_state and st.session_state.last_data_time:
            time_diff = datetime.now() - st.session_state.last_data_time
            return time_diff < DATA_FRESHNESS_THRESHOLD
        return False
    
    def render_dashboard_header(self):
        """Render dashboard header"""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.title("📊 Live Dashboard")
            st.markdown("Real-time monitoring of your farm sensors and AI predictions")
        
        with col2:
            # Quick status
            if st.session_state.get('monitoring_active', False):
                if self.is_data_fresh():
                    st.success("✅ Live Data")
                else:
                    st.warning("🔄 No Recent Data")
            else:
                st.info("⏳ Monitoring Paused")
    
    def render_connection_info(self):
        """Render connection information"""
        st.info(f"**Active Configuration:** Soil Type: {st.session_state.get('soil_type', 'Black Soil')} | Crop Stage: {st.session_state.get('crop_stage', 'Germination')}")
    
    def render_real_time_data(self):
        """Render real-time data section"""
        st.markdown("---")
        st.header("📊 Real-time Sensor Data")
        
        # Get current sensor data
        sensor_data = st.session_state.get('sensor_data', None)
        
        # Render sensor tiles
        render_sensor_tiles(sensor_data)
        
        # Render status indicators
        render_status_indicators(sensor_data)
    
    def render_historical_data(self):
        """Render historical data charts"""
        st.markdown("---")
        st.header("📈 Historical Trends")
        render_charts()
    
    def run(self):
        """Run the dashboard"""
        self.render_dashboard_header()
        self.render_connection_info()
        self.render_real_time_data()
        self.render_historical_data()

# Initialize and run dashboard
if __name__ == "__main__":
    dashboard = LiveDashboard()
    dashboard.run()