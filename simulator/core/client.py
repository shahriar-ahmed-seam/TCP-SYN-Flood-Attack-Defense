from collections import deque
import socket
import threading
import time

class ProbeClient:
    def __init__(self, target_ip="127.0.0.1", target_port=8080, interval=0.3, timeout=0.5):
        self.target_ip = target_ip
        self.target_port = target_port
        self.interval = interval
        self.timeout = timeout
        
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        
        self.history = deque(maxlen=40)
        self.total_probes = 0
        self.total_success = 0
        self.total_fail = 0
        self.last_latency = 0.0
        self.last_status = "IDLE"

    def start(self):
        with self.lock:
            if self.running:
                return
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self):
        with self.lock:
            self.running = False

    def _run(self):
        while self.running:
            t0 = time.perf_counter()
            ok = False
            status = "FAILED"
            rtt = 0.0

            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(self.timeout)
                s.connect((self.target_ip, self.target_port))
                s.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
                _ = s.recv(128)
                s.close()
                rtt = (time.perf_counter() - t0) * 1000.0
                ok = True
                status = "OK"
            except socket.timeout:
                rtt = self.timeout * 1000.0
                status = "TIMEOUT"
            except ConnectionRefusedError:
                rtt = (time.perf_counter() - t0) * 1000.0
                status = "REFUSED"
            except Exception:
                rtt = self.timeout * 1000.0
                status = "ERR"

            with self.lock:
                self.total_probes += 1
                if ok:
                    self.total_success += 1
                else:
                    self.total_fail += 1
                self.last_latency = round(rtt, 2)
                self.last_status = status
                self.history.append({
                    "time": time.time(),
                    "rtt_ms": self.last_latency,
                    "success": ok,
                    "status": status
                })

            time.sleep(self.interval)

    def stats(self):
        with self.lock:
            records = list(self.history)
            cnt = len(records)
            ok_cnt = sum(1 for r in records if r["success"])
            avail = round((ok_cnt / cnt * 100.0), 1) if cnt > 0 else 100.0

            return {
                "latency_ms": self.last_latency,
                "status": self.last_status,
                "availability_pct": avail,
                "total_probes": self.total_probes,
                "total_success": self.total_success,
                "total_fail": self.total_fail,
                "history": records[-25:]
            }
