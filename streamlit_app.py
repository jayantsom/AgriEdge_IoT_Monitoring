# streamlit_app.py
import streamlit as st
from datetime import datetime
from config import DATA_FRESHNESS_THRESHOLD

class SmartFarmingApp:
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
    
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="AgriEdge - Smart Farming",
            page_icon="🌱",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/your-repo',
                'Report a bug': "https://github.com/your-repo/issues",
                'About': "# AgriEdge Smart Farming Dashboard"
            }
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
            .sidebar .sidebar-content {
                background-color: #f8f9fa;
            }
            .metric-card {
                background-color: #f0f2f6;
                padding: 1rem;
                border-radius: 10px;
                border-left: 4px solid #2E8B57;
            }
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
            'soil_type': 'Black Soil',
            'crop_stage': 'Germination',
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
        """Render sidebar with configuration and status"""
        with st.sidebar:
            st.title("🌱 AgriEdge")
            st.markdown("---")
            
            # Configuration Section
            st.header("⚙️ Configuration")
            
            st.session_state.soil_type = st.selectbox(
                "**Soil Type**",
                ['Black Soil', 'Clay', 'Sandy', 'Red', 'Loam', 'Alluvial', 'Chalky'],
                index=0,
                help="Select the type of soil in your farm"
            )
            
            st.session_state.crop_stage = st.selectbox(
                "**Crop Stage**", 
                ['Germination', 'Seedling', 'Vegetative Growth', 'Flowering', 'Fruit Formation', 'Maturation'],
                index=0,
                help="Select the current growth stage of your crop"
            )
            
            st.markdown("---")
            
            # Connection Status
            self.render_connection_status()
            
            st.markdown("---")
            
            # Navigation Info
            st.caption("💡 Use the hamburger menu to navigate between pages")
    
    def render_connection_status(self):
        """Render connection status in sidebar"""
        st.subheader("🔗 Connection Status")
        
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
        
        # Connection controls
        col1, col2 = st.columns(2)
        
        with col1:
            if not st.session_state.monitoring_active:
                if st.button("🚀 Start", use_container_width=True):
                    self.start_monitoring()
            else:
                if st.button("🛑 Stop", use_container_width=True):
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
    
    def stop_monitoring(self):
        """Stop monitoring session"""
        st.session_state.monitoring_active = False
        st.session_state.mqtt_connected = False
        st.session_state.last_data_time = None
        st.info("Monitoring stopped")
    
    def render_main_content(self):
        """Render main content area"""
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1 style="color: #2E8B57; margin-bottom: 1rem;">🌱 Welcome to AgriEdge</h1>
            <p style="font-size: 1.2rem; color: #666;">
                Smart Farming Dashboard & Computer Vision Analytics
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick Stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active Sessions", "1" if st.session_state.monitoring_active else "0")
        
        with col2:
            st.metric("Data Points", "1,247")
        
        with col3:
            st.metric("System Uptime", "99.8%")
        
        with col4:
            st.metric("Alerts", "0")
        
        st.markdown("---")
        
        # Getting Started Guide
        st.subheader("🚀 Getting Started")
        
        guide_col1, guide_col2 = st.columns(2)
        
        with guide_col1:
            st.markdown("""
            ### 📊 Live Dashboard
            - Real-time sensor monitoring
            - Environmental data visualization  
            - Plant health analytics
            - Irrigation control
            """)
            
            if st.button("Go to Dashboard", type="primary"):
                st.switch_page("pages/1_📊_Live_Dashboard.py")
        
        with guide_col2:
            st.markdown("""
            ### 👁️ Computer Vision
            - Plant disease detection
            - Growth stage analysis
            - Pest identification
            - Yield prediction
            """)
            
            if st.button("Go to Computer Vision"):
                st.switch_page("pages/2_👁️_Computer_Vision.py")
    
    def run(self):
        """Main application runner"""
        self.render_sidebar()
        self.render_main_content()

# Run the application
if __name__ == "__main__":
    app = SmartFarmingApp()
    app.run()