# components/charts.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from config import CSV_FILE

def render_charts():
    """Render historical data charts"""
    
    # Create sample data if no CSV exists (for demo)
    if not os.path.exists(CSV_FILE):
        create_sample_data()
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_environmental_chart()
    
    with col2:
        render_npk_chart()

def create_sample_data():
    """Create sample data for demonstration"""
    try:
        import numpy as np
        from datetime import datetime, timedelta
        
        # Generate sample data
        dates = [datetime.now() - timedelta(hours=i) for i in range(24, 0, -1)]
        
        sample_data = {
            'timestamp': dates,
            'temperature': np.random.normal(25, 3, 24).round(1),
            'humidity': np.random.normal(65, 10, 24).round(1),
            'soil_moisture': np.random.normal(45, 15, 24).round(1),
            'light_intensity': np.random.randint(200, 900, 24),
            'npk_n': np.random.randint(15, 35, 24),
            'npk_p': np.random.randint(10, 30, 24),
            'npk_k': np.random.randint(20, 40, 24),
            'irrigation_needed': np.random.randint(0, 2, 24),
            'plant_health': np.random.choice(['Healthy', 'Moderate Stress', 'High Stress'], 24),
            'pump_status': ['ON' if x == 1 else 'OFF' for x in np.random.randint(0, 2, 24)]
        }
        
        df = pd.DataFrame(sample_data)
        df.to_csv(CSV_FILE, index=False)
        print("📊 Created sample data for demonstration")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

def render_environmental_chart():
    """Render environmental sensors chart"""
    try:
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            
            if not df.empty and len(df) > 1:
                # Convert timestamp if needed
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                # Primary Y-axis: Temperature and Humidity
                if 'temperature' in df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df['timestamp'], 
                            y=df['temperature'],
                            name='Temperature',
                            line=dict(color='red', width=2),
                            opacity=0.8
                        ), 
                        secondary_y=False
                    )
                
                if 'humidity' in df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df['timestamp'], 
                            y=df['humidity'],
                            name='Humidity', 
                            line=dict(color='blue', width=2),
                            opacity=0.8
                        ), 
                        secondary_y=False
                    )
                
                # Secondary Y-axis: Moisture and Light
                if 'soil_moisture' in df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df['timestamp'], 
                            y=df['soil_moisture'],
                            name='Soil Moisture',
                            line=dict(color='brown', width=2),
                            opacity=0.8
                        ), 
                        secondary_y=True
                    )
                
                if 'light_intensity' in df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df['timestamp'], 
                            y=df['light_intensity'],
                            name='Light Intensity',
                            line=dict(color='orange', width=2),
                            opacity=0.8
                        ), 
                        secondary_y=True
                    )
                
                fig.update_layout(
                    title="Environmental Sensors Over Time",
                    xaxis_title="Time",
                    height=400,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                fig.update_yaxes(title_text="Temperature (°C) / Humidity (%)", secondary_y=False)
                fig.update_yaxes(title_text="Moisture (%) / Light (lux)", secondary_y=True)
                
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.info("📊 Collecting sensor data... Chart will appear shortly.")
        else:
            st.info("📊 No historical data found.")
            
    except Exception as e:
        st.error(f"❌ Error loading environmental data: {e}")

def render_npk_chart():
    """Render NPK levels chart"""
    try:
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            
            if not df.empty and len(df) > 1:
                # Convert timestamp if needed
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                fig = go.Figure()
                
                # NPK traces
                nutrients = [
                    ('npk_n', 'Nitrogen', 'blue'),
                    ('npk_p', 'Phosphorus', 'red'), 
                    ('npk_k', 'Potassium', 'green')
                ]
                
                for nutrient_key, nutrient_name, color in nutrients:
                    if nutrient_key in df.columns:
                        fig.add_trace(go.Scatter(
                            x=df['timestamp'],
                            y=df[nutrient_key],
                            name=nutrient_name,
                            line=dict(color=color, width=2),
                            opacity=0.8
                        ))
                
                fig.update_layout(
                    title="NPK Nutrient Levels Over Time",
                    xaxis_title="Time",
                    yaxis_title="Concentration (mg/kg)",
                    height=400,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.info("📊 Collecting NPK data... Chart will appear shortly.")
        else:
            st.info("📊 No historical data found.")
            
    except Exception as e:
        st.error(f"❌ Error loading NPK data: {e}")