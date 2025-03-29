import os
import paho.mqtt.client as mqtt
from threading import Thread

DEVICE_ID = os.getenv("DEVICE_ID", "frame1")
BROKER_IP = os.getenv("BROKER_IP", "localhost")

class MQTTClient:
    def __init__(self, on_state_change):
        self.on_state_change = on_state_change
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self):
        print(f"📡 Connecting to MQTT broker at {BROKER_IP}...")
        self.client.connect(BROKER_IP, 1883, 60)
        Thread(target=self.client.loop_forever, daemon=True).start()

    def on_connect(self, client, userdata, flags, rc):
        print("✅ Connected to broker!")
        self.client.subscribe("yard/state")
        print("📥 Subscribed to yard/state")

    def on_message(self, client, userdata, msg):
        state = msg.payload.decode()
        print(f"📨 UI ({DEVICE_ID}) received state: {state}")
        self.on_state_change(state)

    def request_access(self):
        print(f"🟢 UI ({DEVICE_ID}) requesting access...")
        self.client.publish("yard/request", DEVICE_ID)

    def release_access(self):
        print(f"🔴 UI ({DEVICE_ID}) releasing access...")
        self.client.publish("yard/release", DEVICE_ID)
