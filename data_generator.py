import pandas as pd
import random
from datetime import datetime
import time

def generate_dummy_data():
    # Base values with realistic ranges for Buffalo, USA
    base_temp = random.uniform(1, 28)  # Buffalo climate
    base_humidity = random.uniform(45, 85)
    base_soil_moisture = random.uniform(20, 80)
    base_light = random.uniform(500, 10000)  # lux
    base_n = random.uniform(50, 200)
    base_p = random.uniform(30, 150)
    base_k = random.uniform(100, 300)
    
    # Determine irrigation need (30% probability)
    irrigation_needed = 1 if random.random() < 0.3 else 0
    
    # Determine plant health with 30% probability for each non-healthy state
    health_roll = random.random()
    if health_roll < 0.7:
        plant_health = "healthy"
    elif health_roll < 0.85:
        plant_health = "stressed"
    else:
        plant_health = "diseased"
    
    # Pump status follows irrigation needed
    pump_status = "ON" if irrigation_needed == 1 else "OFF"
    
    return {
        'timestamp': datetime.now(),
        'temperature°C': round(base_temp, 1),
        'humidity %': round(base_humidity, 1),
        'soil_moisture%': round(base_soil_moisture, 1),
        'light_intensitylux': round(base_light),
        'npk_n': round(base_n),
        'npk_p': round(base_p),
        'npk_k': round(base_k),
        'irrigation_needed': irrigation_needed,
        'plant_health': plant_health,
        'pump_status': pump_status
    }

def save_data():
    new_data = generate_dummy_data()
    
    try:
        # Try to read existing data
        df = pd.read_csv('sensor_data.csv')
        # Append new data
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    except FileNotFoundError:
        # Create new dataframe if file doesn't exist
        df = pd.DataFrame([new_data])
    
    # Save to CSV
    df.to_csv('sensor_data.csv', index=False)
    return new_data