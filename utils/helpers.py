# utils/helpers.py
from datetime import datetime

def format_timestamp(timestamp):
    """Format timestamp for display"""
    if isinstance(timestamp, str):
        return timestamp
    elif hasattr(timestamp, 'strftime'):
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return str(timestamp)

def validate_sensor_data(data):
    """Validate sensor data ranges"""
    if not data:
        return False
    
    validations = [
        (0 <= data.get('temperature', 100) <= 60),
        (0 <= data.get('humidity', 100) <= 100),
        (0 <= data.get('soil_moisture', 100) <= 100),
        (data.get('light_intensity', 0) >= 0),
        (data.get('npk_n', 0) >= 0),
        (data.get('npk_p', 0) >= 0),
        (data.get('npk_k', 0) >= 0),
        (data.get('irrigation_needed', 0) in [0, 1])
    ]
    
    return all(validations)