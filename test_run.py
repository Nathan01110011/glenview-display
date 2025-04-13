# localdev.py
import subprocess
import os
import time
import signal


def launch_ui(device_id):
    env = {**os.environ, "DEVICE_ID": device_id, "BROKER_IP": "localhost"}
    return subprocess.Popen(["python3", "display-app/main.py"], env=env)


if __name__ == "__main__":
    print("🚀 Starting full local dev environment...")
    time.sleep(1)

    ui1 = launch_ui("mac_test_frame1")
    ui2 = launch_ui("mac_test_frame2")

    try:
        ui1.wait()
        ui2.wait()
    except KeyboardInterrupt:
        print("🛑 Shutting down...")
    finally:
        for p in [ui1, ui2]:
            p.send_signal(signal.SIGINT)
            p.wait()

        subprocess.run(["docker", "stop", "dev-broker"])
