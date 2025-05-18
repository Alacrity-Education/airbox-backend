# test_publisher.py
import json
import time
import paho.mqtt.client as mqtt

BROKER = ""
PORT =
TOPIC = ""
USERNAME = ""
PASSWORD = ""

client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)

client.connect(BROKER, PORT)
client.loop_start()

sample_data = {
    "locationName": "Test Location",
    "Location": [51.509865, -0.118092],
    "StationID": "station_test_01",
    "StationNickname": "Tester",
    "SoftwareVersion": "1.0",
    "Modules": ["mod1", "mod2"],
    "Data": [
        {"ModuleId": "mod1", "ModuleName": "Temperature", "Value": 22.5, "Timestamp": "2023-01-01T12:00:00Z"},
        {"ModuleId": "mod2", "ModuleName": "Humidity", "Value": 45.0, "Timestamp": "2023-01-01T12:00:00Z"}
    ]
}

payload = json.dumps(sample_data)
client.publish(TOPIC, payload, qos=2)
print(f"Published test message to {TOPIC}")

time.sleep(2)
client.loop_stop()
client.disconnect()
