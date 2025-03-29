import socket
import threading
import ipaddress
from queue import Queue

def discover_mqtt(port=1883, timeout=0.2, subnet='192.168.1.0/24'):
    subnet = ipaddress.ip_network(subnet, strict=False)
    result_queue = Queue()

    def check_host(ip):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((str(ip), port))
            s.close()
            result_queue.put(str(ip))
        except:
            pass

    threads = []
    for ip in subnet.hosts():
        t = threading.Thread(target=check_host, args=(ip,), daemon=True)
        t.start()
        threads.append(t)

    for t in threads:
        t.join(timeout=timeout + 0.1)

    if not result_queue.empty():
        return result_queue.get()

    return None

# Optional test block
if __name__ == "__main__":
    ip = discover_mqtt()
    if ip:
        print(f"✅ MQTT broker found at {ip}")
    else:
        print("❌ No MQTT broker found on the subnet")