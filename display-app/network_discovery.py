import socket
import httpx


def find_server_on_lan(port=8000, timeout=0.2):
    preferred_subnets = ["192.168.1", "192.168.0"]
    for subnet in preferred_subnets:
        print(f"🔍 Scanning {subnet}.100–{subnet}.129...")
        for i in range(100, 130):
            ip = f"{subnet}.{i}"
            try:
                response = httpx.get(f"http://{ip}:{port}/state", timeout=timeout)
                if response.status_code == 200:
                    print(f"✅ Found server at {ip}")
                    return ip
            except (httpx.ConnectTimeout, httpx.ConnectError, httpx.RequestError) as e:
                print(f"🔌 Skipped {ip}: {e}")
    print("❌ No FastAPI server found on common subnets")
    return None


def get_lan_subnet():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            return ".".join(ip.split(".")[:3])
    except OSError as e:
        print("⚠️ Could not determine local subnet:", e)
        return None
