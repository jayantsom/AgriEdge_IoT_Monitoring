# MQTT Configuration
MQTT_BROKER = "8c70285096fe43429db68ea8e5513422.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
USERNAME = "hivemq.webclient.1763167024884"
PASSWORD = "!A5PgmOd1MS$<7z9X#bf"
TOPIC_SENSOR = "agriedge/sensor"
TOPIC_ADVICE = "agriedge/advice"

# App Configuration
CSV_FILE = "sensor_data.csv"
REFRESH_INTERVAL = 5  # seconds
MAX_DATA_POINTS = 10000  # Keep only last 10000 readings to save space

# Soil Types and Crop Stages
SOIL_TYPES = ['Clay', 'Sandy', 'Red', 'Loam', 'Black', 'Alluvial', 'Chalky']
CROP_STAGES = [
    'Flowering', 'Seedling', 'Vegetative Growth', 'Root/Tuber Development',
    'Germination', 'Pollination', 'Fruit/Grain/Bulb Formation', 'Maturation', 'Harvest'
]