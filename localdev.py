# localdev.py
import subprocess
import os
import time
import signal

def start_broker():
    print("🔌 Starting Mosquitto broker via Docker...")
    return subprocess.Popen([
        "docker", "run", "--rm", "--name", "dev-broker",
        "-p", "1883:1883", "eclipse-mosquitto:2"
    ])

def start_state_manager():
    print("🧠 Starting broker state manager...")
    return subprocess.Popen(["python3", "broker_state/broker_state.py"], env={**os.environ, "BROKER_HOST": "localhost"})

def launch_ui(device_id):
    env = {**os.environ, "DEVICE_ID": device_id, "BROKER_IP": "localhost"}
    return subprocess.Popen(["python3", "display-app/main_ui.py"], env=env)

if __name__ == "__main__":
    print("🚀 Starting full local dev environment...")
    broker_proc = start_broker()
    time.sleep(2)
    state_proc = start_state_manager()
    time.sleep(1)

    ui1 = launch_ui("frame1")
    ui2 = launch_ui("frame2")

    try:
        ui1.wait()
        ui2.wait()
    except KeyboardInterrupt:
        print("🛑 Shutting down...")
    finally:
        for p in [ui1, ui2, state_proc]:
            p.send_signal(signal.SIGINT)
            p.wait()

        subprocess.run(["docker", "stop", "dev-broker"])
