# components/header.py
import streamlit as st

def render_header():
    """Render the application header"""
    try:
        st.image("./assets/header1.jpg", use_column_width=True)
    except FileNotFoundError:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px;">
            <h1 style="color: white; margin: 0; font-size: 2.5rem;">🌱 AgriEdge Smart Farming</h1>
            <p style="color: white; margin: 0.5rem 0 0 0; font-size: 1.2rem;">Real-time IoT Agriculture Monitoring</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")