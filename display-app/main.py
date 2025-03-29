from discovery import discover_mqtt
import paho.mqtt.client as mqtt

print("🔍 Scanning for MQTT broker...")
broker_ip = discover_mqtt()
if not broker_ip:
    print("❌ No broker found.")
else:
    print(f"Found broker at: {broker_ip}")
    client = mqtt.Client()
    client.connect(broker_ip, 1883, 60)
    print("📡 Connected to broker")
