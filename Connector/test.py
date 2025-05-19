# random_mqtt_publisher.py
import os
import logging

logging.basicConfig(level=logging.DEBUG)


import json
import time
import random
from dotenv import load_dotenv
from datetime import datetime
import paho.mqtt.client as mqtt
config = load_dotenv()
# Load MQTT config

BROKER = os.getenv('MQTT_BROKER')
PORT   = int(os.getenv('MQTT_PORT'))
TOPIC  = os.getenv('MQTT_TOPIC')
USER   = os.getenv('MQTT_USERNAME')
PASSWD = os.getenv('MQTT_PASSWORD')

# Connect
client = mqtt.Client()
client.username_pw_set(USER, PASSWD)
client.connect(BROKER, PORT)

# Helper to generate random payloads
def generate_sample(station_id: str):
    return {
        "locationName": "TestSite",
        "Location": [round(random.uniform(-90, 90), 6), round(random.uniform(-180, 180), 6)],
        "StationID": station_id,
        "StationNickname": f"Station_{station_id}",
        "SoftwareVersion": "test",
        "Data": [
            {"ModuleId": "temp", "ModuleName": "Temperature", "Value": round(random.uniform(15, 30), 2), "Timestamp": datetime.utcnow().isoformat() + "Z"},
            {"ModuleId": "hum",  "ModuleName": "Humidity",    "Value": round(random.uniform(30, 90), 2), "Timestamp": datetime.utcnow().isoformat() + "Z"}
        ]
    }

if __name__ == '__main__':
    station_ids = ['station1', 'station2']
    try:
        while True:
            for sid in station_ids:
                payload = json.dumps(generate_sample(sid))
                client.publish(TOPIC, payload, qos=2)
                print(f"Published sample for {sid}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Stopping publisher.")
        client.disconnect()
