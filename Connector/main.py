import os
import json
from dotenv import load_dotenv
from datetime import datetime
import dateutil.parser
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt

# Load environment variables from .env file
load_dotenv()

def load_config():
    required_vars = [
        'INFLUXDB_URL',
        'INFLUXDB_TOKEN',
        'INFLUXDB_ORG',
        'INFLUXDB_BUCKET',
        'MQTT_BROKER',
        'MQTT_PORT',
        'MQTT_TOPIC',
        'MQTT_USERNAME',
        'MQTT_PASSWORD'
    ]
    cfg = {}
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise ValueError(f"Missing required environment variable: {var}")
        cfg[var] = value
    # Convert port to int
    cfg['MQTT_PORT'] = int(cfg['MQTT_PORT'])
    return cfg

# Load configuration
config = load_config()

# Initialize InfluxDB client
influx_client = InfluxDBClient(
    url=config['INFLUXDB_URL'],
    token=config['INFLUXDB_TOKEN'],
    org=config['INFLUXDB_ORG']
)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# Initialize MQTT client with Callback API v2
client = mqtt.Client(
    protocol=mqtt.MQTTv311,
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)
client.username_pw_set(config['MQTT_USERNAME'], config['MQTT_PASSWORD'])

connected_once = False

# Callback: on successful connection
def on_connect(client, userdata, flags, rc, properties=None):
    global connected_once
    if rc == 0 and not connected_once:
        print("Connected to MQTT broker.")
        client.subscribe(config['MQTT_TOPIC'], qos=2)
        connected_once = True
    elif rc != 0:
        print(f"Failed to connect, return code {rc}")

# Callback: on receiving a message
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        insert_data(data)
    except Exception as e:
        print(f"Error processing message: {e}")

# Attach callbacks
client.on_connect = on_connect
client.on_message = on_message

# Function: insert station and module data into InfluxDB
def insert_data(data):
    points = []

    # 1) Station metadata
    station_point = (
        Point("station_info")
        .tag("StationID", data["StationID"])
        .tag("locationName", data["locationName"])
        .field("latitude", float(data["Location"][0]))
        .field("longitude", float(data["Location"][1]))
        .field("StationNickname", data["StationNickname"])
        .field("SoftwareVersion", data["SoftwareVersion"])
        .time(datetime.utcnow(), WritePrecision.NS)
    )
    points.append(station_point)

    # 2) Module data entries (one field per module name)
    for entry in data.get("Data", []):
        timestamp = dateutil.parser.parse(entry["Timestamp"])
        point = (
            Point("module_data")
            .tag("StationID", data["StationID"])
            .tag("locationName", data["locationName"])
            .time(timestamp, WritePrecision.NS)
            .field(entry["ModuleName"], float(entry["Value"]))
        )
        points.append(point)

    # 3) Write all points in one batch
    write_api.write(
        bucket=config['INFLUXDB_BUCKET'],
        org=config['INFLUXDB_ORG'],
        record=points
    )
    print(f"Inserted {len(points)-1} module entries for station {data['StationID']}")

if __name__ == "__main__":
    try:
        client.connect(config['MQTT_BROKER'], config['MQTT_PORT'])
        print("Starting MQTT loop...")
        client.loop_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        influx_client.close()
