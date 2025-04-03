# detect.py
import random
import time
from datetime import datetime
import json
from collections import Counter

class ThreatDetector:
    def __init__(self, packet_threshold=1000, attempt_threshold=10, ip_repeat_threshold=5):
        self.packet_threshold = packet_threshold
        self.attempt_threshold = attempt_threshold
        self.ip_repeat_threshold = ip_repeat_threshold  # Limite pra IPs repetidos
        self.logs = []
        self.ip_counts = Counter()  # Conta IPs repetidos

    def simulate_log(self):
        """Simula um log de tráfego de rede."""
        # Simula IPs (pra testar repetição, vamos usar alguns IPs fixos)
        possible_ips = ["192.168.1.10", "192.168.1.20", "192.168.1.30", "192.168.1.40"]
        ip_source = random.choice(possible_ips)
        log = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip_source": ip_source,
            "ip_dest": f"192.168.1.{random.randint(1, 255)}",
            "packets": random.randint(50, 2000),
            "attempts": random.randint(0, 15),
            "latency": random.randint(10, 100)
        }
        self.logs.append(log)
        self.ip_counts[ip_source] += 1  # Incrementa contador de IPs
        return log

    def detect_threat(self, log):
        """Detecta ameaças com base no log."""
        threat_detected = False
        threat_type = None

        if log["packets"] > self.packet_threshold:
            threat_detected = True
            threat_type = "Flood Detectado"
        elif log["attempts"] > self.attempt_threshold:
            threat_detected = True
            threat_type = "Tentativa de Intrusão"
        elif self.ip_counts[log["ip_source"]] > self.ip_repeat_threshold:
            threat_detected = True
            threat_type = "Ataque Direcionado (IP Repetido)"

        return {
            "threat_detected": threat_detected,
            "threat_type": threat_type,
            "log": log
        }

    def save_logs(self, filename="logs.json"):
        """Salva os logs num arquivo JSON."""
        with open(filename, "w") as f:
            json.dump(self.logs, f, indent=4)

    def run(self, duration=60):
        """Simula captura de logs por um período (em segundos)."""
        start_time = time.time()
        while time.time() - start_time < duration:
            log = self.simulate_log()
            result = self.detect_threat(log)
            print(f"Log: {log}")
            if result["threat_detected"]:
                print(f"🚨 {result['threat_type']} - {log['timestamp']}")
            time.sleep(1)
        self.save_logs()  # Salva os logs no final

if __name__ == "__main__":
    detector = ThreatDetector()
    detector.run(duration=10)  # Roda por 10 segundos pra testar
