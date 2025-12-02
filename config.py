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

# API Configuration
TREFLE_API_KEY = "usr-1TsrpZXYG0Ey5xBLnj251QHBxKsZSq4v4RJ6QNyoxgE"
PLANTBOOK_API_KEY = "9fa8c17b3181858f8727a6484e63863b09cd2b07"
PLANTBOOK_CLIENT_ID = "oxtJwxRC1x4BaZjGNnyjpONI9GMERKTBsG6TtQQ9"
PLANTBOOK_CLIENT_SECRET = "EnYbfGF07PHjUNv5KKQpaV7L4DAapRzuIUNhB1D8wP6w2Hm7D04xr6bKLTCVTXI8jxvMmikkzCzhf1rXkzxoZDwsYjVd1eVLfCOpErsA0PyXvn1Eeh2EzhOfkMes1zQK"

# API Endpoints
TREFLE_BASE_URL = "https://trefle.io/api/v1"
PLANTBOOK_BASE_URL = "https://open.plantbook.io/api/v1"