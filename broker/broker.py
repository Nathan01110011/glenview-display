import asyncio
import json
from gmqtt import Server, Client as MQTTClient

# Global state
occupied_by = None

# Topics
REQUEST_TOPIC = "site/request"
RELEASE_TOPIC = "site/release"
STATE_TOPIC = "site/state"

# Bind to all interfaces so devices can connect
BIND_ADDRESS = "0.0.0.0"
PORT = 1883

class StateManagingBroker(Server):
    def __init__(self):
        super().__init__()
        self.clients = set()

    async def start(self):
        await self.run(host=BIND_ADDRESS, port=PORT)

    async def handle_connect(self, client: MQTTClient):
        self.clients.add(client)
        print(f"🔗 Client connected: {client.client_id}")
        await client.subscribe(REQUEST_TOPIC)
        await client.subscribe(RELEASE_TOPIC)
        # Send current state on connect
        await self.publish_state()

    async def handle_disconnect(self, client: MQTTClient, packet, exc=None):
        self.clients.discard(client)
        print(f"🔌 Client disconnected: {client.client_id}")

    async def handle_message(self, client: MQTTClient, topic: str, payload: bytes, qos, properties):
        global occupied_by
        message = payload.decode()

        if topic == REQUEST_TOPIC:
            print(f"📥 site/request: {message}")
            if occupied_by is None:
                occupied_by = message
                print(f"🔐 Reserved by {message}")
                await self.publish_state()
        elif topic == RELEASE_TOPIC:
            print(f"📥 site/release: {message}")
            if occupied_by == message:
                occupied_by = None
                print(f"🔓 Released by {message}")
                await self.publish_state()

    async def publish_state(self):
        state = json.dumps({"occupied_by": occupied_by})
        print(f"📣 Published state: {state}")
        for client in self.clients:
            await client.publish(STATE_TOPIC, state, qos=1)

async def main():
    broker = StateManagingBroker()
    await broker.start()

if __name__ == "__main__":
    asyncio.run(main())
