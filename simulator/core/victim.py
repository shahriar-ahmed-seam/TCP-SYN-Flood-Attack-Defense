import socket
import threading
import time

class VictimServer:
    def __init__(self, host="0.0.0.0", port=8080, backlog=16):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.sock = None
        self.running = False
        self.thread = None
        self.requests_handled = 0
        self.lock = threading.Lock()

        self.under_attack = False
        self.syncookies = False
        self.iptables = False
        self.syn_recv = 0

    def start(self):
        with self.lock:
            if self.running:
                return
            self.running = True
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.listen(self.backlog)
            self.sock.settimeout(0.5)

            self.thread = threading.Thread(target=self._worker, daemon=True)
            self.thread.start()

    def set_backlog(self, backlog):
        with self.lock:
            self.backlog = backlog

    def _worker(self):
        while self.running:
            try:
                client, _ = self.sock.accept()
                
                if self.under_attack and not self.iptables and not self.syncookies:
                    time.sleep(0.55)
                    try:
                        client.close()
                    except Exception:
                        pass
                    continue

                try:
                    payload = client.recv(512)
                    if payload:
                        client.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nOK")
                        with self.lock:
                            self.requests_handled += 1
                except Exception:
                    pass
                finally:
                    client.close()
            except socket.timeout:
                continue
            except OSError:
                break
            except Exception:
                break

    def stop(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def stats(self):
        if self.under_attack:
            if self.iptables:
                self.syn_recv = min(self.backlog - 1, 3)
            else:
                self.syn_recv = self.backlog
        else:
            self.syn_recv = 0

        return {
            "syn_recv": self.syn_recv,
            "established": 1 if self.requests_handled > 0 else 0,
            "backlog_limit": self.backlog,
            "requests_handled": self.requests_handled
        }
