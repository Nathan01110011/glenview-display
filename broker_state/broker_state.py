import asyncio
import os
import json
from gmqtt import Client as MQTTClient

BROKER_HOST = os.getenv("BROKER_HOST", "127.0.0.1")
STATE_TOPIC = "site/state"
REQUEST_TOPIC = "site/request"
RELEASE_TOPIC = "site/release"

occupied_by = None
client = MQTTClient("state_manager")

# -- MQTT Event Handlers --

def on_connect(client, flags, rc, properties):
    print("✅ Connected to MQTT broker")
    client.subscribe(REQUEST_TOPIC)
    client.subscribe(RELEASE_TOPIC)

def on_message(client, topic, payload, qos, properties):
    global occupied_by
    decoded = payload.decode()
    print(f"📥 Message on {topic}: {decoded}")

    if topic == REQUEST_TOPIC:
        if occupied_by is None:
            occupied_by = decoded
            print(f"🔐 Reserved by {decoded}")
            publish_state()
        else:
            print(f"⛔ Ignored request from {decoded}, already reserved by {occupied_by}")
    elif topic == RELEASE_TOPIC:
        if occupied_by == decoded:
            print(f"🔓 Released by {decoded}")
            occupied_by = None
            publish_state()

def publish_state():
    state_json = json.dumps({"occupied_by": occupied_by})
    print(f"📣 Publishing state: {state_json}")
    client.publish(STATE_TOPIC, state_json, qos=1, retain=True)

def on_disconnect(client, packet, exc=None):
    print("🔌 Disconnected")

def on_subscribe(client, mid, qos, properties):
    print("📡 Subscribed successfully")

# -- Assign Callbacks --

client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe

# -- Main Async Setup --

async def run_broker_state():
    await client.connect(BROKER_HOST)
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_broker_state())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("🛑 Interrupted by user")
    finally:
        loop.stop()
