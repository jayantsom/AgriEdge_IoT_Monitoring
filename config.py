# config.py
import os
from datetime import timedelta

# MQTT Configuration (From your friend's agriculture.py)
MQTT_BROKER = "8c70285096fe43429db68ea8e5513422.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
USERNAME = "hivemq.webclient.1763167024884"
PASSWORD = "!A5PgmOd1MS$<7z9X#bf"
TOPIC_SENSOR = "agriedge/sensor"
TOPIC_ADVICE = "agriedge/advice"

# App Configuration
CSV_FILE = "sensor_data.csv"
REFRESH_INTERVAL = 5  # seconds
MAX_DATA_POINTS = 1000
DATA_FRESHNESS_THRESHOLD = timedelta(seconds=30)

# Soil Types and Crop Stages (From your friend's models)
SOIL_TYPES = ['Black Soil', 'Clay', 'Sandy', 'Red', 'Loam', 'Alluvial', 'Chalky']
CROP_STAGES = ['Germination', 'Seedling', 'Vegetative Growth', 'Flowering', 'Fruit Formation', 'Maturation']

# Health Status Mapping
PLANT_HEALTH_COLORS = {
    'Healthy': 'green',
    'Moderate Stress': 'orange', 
    'High Stress': 'red',
    'Unknown': 'gray'
}