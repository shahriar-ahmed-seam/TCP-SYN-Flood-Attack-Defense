from collections import deque
import threading
import time

from .victim import VictimServer
from .attacker import SynAttacker
from .client import ProbeClient
from .defense import DefenseController

class SimulationEngine:
    def __init__(self, target_port=8080):
        self.target_port = target_port
        self.victim = VictimServer(port=target_port, backlog=16)
        self.attacker = SynAttacker(target_port=target_port)
        self.client = ProbeClient(target_port=target_port, interval=0.35, timeout=0.5)
        self.defense = DefenseController(target_port=target_port)

        self.logs = deque(maxlen=40)
        self.lock = threading.Lock()
        self.running = False
        self.log("SYS", f"Simulation engine initialized on port {target_port}")

    def log(self, source, msg):
        with self.lock:
            self.logs.append({
                "time": time.strftime("%H:%M:%S"),
                "source": source,
                "message": msg
            })

    def start(self):
        self.log("VICTIM", f"Starting TCP listener on :{self.target_port}")
        self.victim.start()
        self.log("CLIENT", "Probing legitimate client traffic")
        self.client.start()
        self.running = True

    def stop(self):
        self.log("SYS", "Stopping engine and resetting rules")
        self.attacker.stop()
        self.client.stop()
        self.victim.stop()
        self.defense.reset()
        self.running = False

    def trigger_attack(self, rate_pps=5000):
        self.log("ATTACK", f"Emitting SYN flood at {rate_pps} pps")
        self.victim.under_attack = True
        self.attacker.start(rate_pps=rate_pps)

    def stop_attack(self):
        self.victim.under_attack = False
        self.attacker.stop()
        self.log("ATTACK", "SYN flood stopped")

    def toggle_syncookies(self, enable: bool):
        val = self.defense.set_syncookies(enable)
        self.victim.syncookies = enable
        state = "enabled" if enable else "disabled"
        self.log("DEFENSE", f"TCP SYN cookies {state}")
        return enable

    def toggle_iptables(self, enable: bool):
        val = self.defense.set_iptables(enable)
        self.victim.iptables = enable
        state = "enabled" if enable else "disabled"
        self.log("DEFENSE", f"iptables rate limiting {state}")
        return enable

    def set_backlog(self, size: int):
        self.victim.set_backlog(size)
        self.log("CONFIG", f"Victim backlog capacity set to {size}")

    def snapshot(self):
        a = self.attacker.stats()
        d = self.defense.stats()

        if a["active"] and d["iptables"]:
            d["iptables_dropped"] += int(a["rate_pps"] * 0.35)

        v = self.victim.stats()
        c = self.client.stats()

        limit = v["backlog_limit"]
        syn_recv = v["syn_recv"]
        saturation = min(100.0, round((syn_recv / limit) * 100.0, 1))

        if a["active"]:
            status = "DEFENDED" if (d["syncookies"] or d["iptables"]) else "ATTACK"
        else:
            status = "HEALTHY"

        with self.lock:
            log_entries = list(self.logs)

        return {
            "timestamp": time.time(),
            "status": status,
            "victim": {
                "port": self.target_port,
                "syn_recv": syn_recv,
                "established": v["established"],
                "backlog_limit": limit,
                "saturation_pct": saturation,
                "handled": v["requests_handled"]
            },
            "attacker": a,
            "client": c,
            "defense": d,
            "logs": log_entries[-20:]
        }
