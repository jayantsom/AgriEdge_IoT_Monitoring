# components/header.py
import streamlit as st
import os

def render_header():
    """Render the application header with image"""
    header_path = "./assets/header1.jpg"
    
    if os.path.exists(header_path):
        st.image(header_path, use_column_width=True)
    else:
        # Fallback header if image not found
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 2rem;">
            <h1 style="color: white; margin: 0; font-size: 2.5rem;">🌱 AgriEdge Smart Farming</h1>
            <p style="color: white; margin: 0.5rem 0 0 0; font-size: 1.2rem;">Real-time IoT Agriculture Monitoring</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")