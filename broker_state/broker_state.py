# broker_state/broker_state.py
import os
import json
import paho.mqtt.client as mqtt

broker = os.environ.get("BROKER_HOST", "localhost")
TOPIC_REQUEST = "site/request"
TOPIC_RELEASE = "site/release"
TOPIC_STATE = "site/state"

state = {
    "occupied_by": None
}

def publish_state(client):
    client.publish(TOPIC_STATE, json.dumps(state))
    print(f"📣 Published state: {state}")

def on_connect(client, userdata, flags, rc):
    print("🧠 Broker connected.")
    client.subscribe(TOPIC_REQUEST)
    client.subscribe(TOPIC_RELEASE)

def on_message(client, userdata, msg):
    global state
    payload = msg.payload.decode()
    print(f"📥 {msg.topic}: {payload}")

    if msg.topic == TOPIC_REQUEST:
        if not state["occupied_by"]:
            state["occupied_by"] = payload
            print(f"🔐 Reserved by {payload}")
            publish_state(client)
    elif msg.topic == TOPIC_RELEASE:
        if state["occupied_by"] == payload:
            state["occupied_by"] = None
            print(f"🔓 Released by {payload}")
            publish_state(client)

if __name__ == "__main__":
    print(f"🚀 Broker state manager connecting to {broker}...")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker, 1883, 60)
    client.loop_forever()
