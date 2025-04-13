import socket
import httpx

import httpx

def find_server_on_lan(port=8000, timeout=0.2):
    preferred_subnets = ["192.168.1", "192.168.0"]
    for subnet in preferred_subnets:
        print(f"🔍 Scanning {subnet}.1–{subnet}.20...")
        for i in range(100, 130):
            ip = f"{subnet}.{i}"
            try:
                r = httpx.get(f"http://{ip}:{port}/state", timeout=timeout)
                if r.status_code == 200:
                    print(f"✅ Found server at {ip}")
                    return ip
            except (httpx.ConnectTimeout, httpx.ConnectError):
                continue
            except Exception as e:
                print(f"⚠️ Error checking {ip}:", e)
    print("❌ No FastAPI server found on common subnets")
    return None


def get_lan_subnet():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ".".join(ip.split(".")[:3])
    except Exception as e:
        print("⚠️ Could not determine local subnet:", e)
        return None