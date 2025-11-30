# streamlit_app.py
import streamlit as st
import pandas as pd
from datetime import datetime

from components.header import render_header
from components.sensor_display import render_sensor_tiles
from components.charts import render_charts
from components.status_indicators import render_status_indicators
from config import DATA_FRESHNESS_THRESHOLD, SOIL_TYPES, CROP_STAGES

class Dashboard:
    def __init__(self):
        self.setup_page()
        self.initialize_session_state()
    
    def setup_page(self):
        """Setup page configuration"""
        st.set_page_config(
            page_title="AgriEdge - Smart Farming Dashboard",
            page_icon="🌱",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        self.inject_custom_css()
    
    def inject_custom_css(self):
        """Inject custom CSS for better styling"""
        st.markdown("""
        <style>
            .main-header {
                font-size: 2.5rem;
                color: #2E8B57;
                text-align: center;
                margin-bottom: 1rem;
            }
            .metric-card {
                background-color: #f0f2f6;
                padding: 1rem;
                border-radius: 10px;
                border-left: 4px solid #2E8B57;
            }
            .status-healthy { color: #28a745; }
            .status-warning { color: #ffc107; }
            .status-critical { color: #dc3545; }
            .status-offline { color: #6c757d; }
            div[data-testid="stSidebarNav"] {
                padding-top: 2rem;
            }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        defaults = {
            'monitoring_active': False,
            'mqtt_connected': False,
            'last_data_time': None,
            'soil_type': SOIL_TYPES[0],
            'crop_stage': CROP_STAGES[0],
            'sensor_data': None,
            'connection_attempts': 0
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def is_data_fresh(self):
        """Check if data is still fresh (received recently)"""
        if st.session_state.last_data_time:
            time_diff = datetime.now() - st.session_state.last_data_time
            return time_diff < DATA_FRESHNESS_THRESHOLD
        return False
    
    def render_sidebar(self):
        """Render sidebar with page navigation"""
        with st.sidebar:
            st.title("🌱 AgriEdge")
            st.markdown("---")
            
            # Page Navigation
            st.subheader("📄 Navigation")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Dashboard", use_container_width=True):
                    st.rerun()  # Already on dashboard
            with col2:
                if st.button("👁️ CV Analysis", use_container_width=True):
                    st.switch_page("pages/2_👁️_Computer_Vision.py")
            
            st.markdown("---")
            
            # Configuration Section
            st.subheader("⚙️ Farm Configuration")
            
            st.session_state.soil_type = st.selectbox(
                "**Soil Type**",
                SOIL_TYPES,
                help="Select the type of soil in your farm"
            )
            
            st.session_state.crop_stage = st.selectbox(
                "**Crop Stage**", 
                CROP_STAGES,
                help="Select the current growth stage of your crop"
            )
            
            st.markdown("---")
            
            # Connection Controls
            self.render_connection_controls()
    
    def render_connection_controls(self):
        """Render connection control buttons"""
        st.subheader("🔗 Connection")
        
        # Connection status
        if st.session_state.mqtt_connected:
            if self.is_data_fresh():
                st.success("✅ Live Data")
                if st.session_state.last_data_time:
                    last_update = st.session_state.last_data_time.strftime("%H:%M:%S")
                    st.caption(f"Last: {last_update}")
            else:
                st.warning("🔄 Connected - No Data")
        elif st.session_state.monitoring_active:
            st.warning("🔄 Connecting...")
        else:
            st.info("⏳ Ready to Connect")
        
        # Connection buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if not st.session_state.monitoring_active:
                if st.button("🚀 Start", use_container_width=True, type="primary"):
                    self.start_monitoring()
            else:
                if st.button("🛑 Stop", use_container_width=True, type="secondary"):
                    self.stop_monitoring()
        
        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
    
    def start_monitoring(self):
        """Start monitoring session"""
        st.session_state.monitoring_active = True
        st.session_state.mqtt_connected = True  # Simulate connection for demo
        st.session_state.last_data_time = datetime.now()
        
        # Simulate some initial data
        st.session_state.sensor_data = {
            'temperature': 25.5,
            'humidity': 65.2,
            'soil_moisture': 45.8,
            'light_intensity': 850,
            'npk_n': 25,
            'npk_p': 18,
            'npk_k': 22,
            'irrigation_needed': 1,
            'plant_health': 'Healthy',
            'pump_status': 'ON'
        }
        
        st.success("Monitoring started successfully!")
        st.rerun()
    
    def stop_monitoring(self):
        """Stop monitoring session"""
        st.session_state.monitoring_active = False
        st.session_state.mqtt_connected = False
        st.session_state.last_data_time = None
        st.session_state.sensor_data = None
        st.info("Monitoring stopped")
        st.rerun()
    
    def render_dashboard_header(self):
        """Render dashboard header"""
        render_header()  # This will show the header image
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.title("📊 Live Dashboard")
            st.markdown("Real-time monitoring of your farm sensors and AI predictions")
        
        with col2:
            # Quick status
            if st.session_state.get('monitoring_active', False):
                if self.is_data_fresh():
                    st.success("✅ Live Data Streaming")
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
        self.render_sidebar()
        self.render_dashboard_header()
        self.render_connection_info()
        self.render_real_time_data()
        self.render_historical_data()

# Initialize and run dashboard
if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.run()