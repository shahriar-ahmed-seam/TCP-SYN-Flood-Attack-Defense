import os
import subprocess

class DefenseController:
    def __init__(self, target_port=8080):
        self.target_port = target_port
        self.syncookies = False
        self.iptables = False
        self.synack_retries = 5
        self.iptables_dropped = 0
        self._init_state()

    def _init_state(self):
        try:
            res = subprocess.run(
                ["sysctl", "-n", "net.ipv4.tcp_syncookies"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )
            if res.returncode == 0:
                self.syncookies = (res.stdout.strip() == "1")
        except Exception:
            pass

        try:
            res = subprocess.run(
                ["sysctl", "-n", "net.ipv4.tcp_synack_retries"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )
            if res.returncode == 0:
                self.synack_retries = int(res.stdout.strip())
        except Exception:
            pass

    def set_syncookies(self, enable: bool):
        self.syncookies = enable
        val = "1" if enable else "0"
        try:
            subprocess.run(
                ["sudo", "-n", "sysctl", "-w", f"net.ipv4.tcp_syncookies={val}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass
        return self.syncookies

    def set_iptables(self, enable: bool):
        self.iptables = enable
        port = str(self.target_port)

        try:
            subprocess.run(
                ["sudo", "-n", "iptables", "-D", "INPUT", "-p", "tcp", "--dport", port, "--syn", "-m", "limit", "--limit", "20/s", "--limit-burst", "40", "-j", "ACCEPT"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            subprocess.run(
                ["sudo", "-n", "iptables", "-D", "INPUT", "-p", "tcp", "--dport", port, "--syn", "-j", "DROP"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass

        if enable:
            try:
                subprocess.run(
                    ["sudo", "-n", "iptables", "-I", "INPUT", "1", "-p", "tcp", "--dport", port, "--syn", "-m", "limit", "--limit", "20/s", "--limit-burst", "40", "-j", "ACCEPT"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                subprocess.run(
                    ["sudo", "-n", "iptables", "-I", "INPUT", "2", "-p", "tcp", "--dport", port, "--syn", "-j", "DROP"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass
        return self.iptables

    def get_iptables_drops(self):
        if not self.iptables:
            return 0
        try:
            res = subprocess.run(
                ["sudo", "-n", "iptables", "-L", "INPUT", "-v", "-n"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    if f"dpt:{self.target_port}" in line and "DROP" in line:
                        toks = line.split()
                        if toks:
                            self.iptables_dropped = int(toks[0])
                            return self.iptables_dropped
        except Exception:
            pass
        return self.iptables_dropped

    def reset(self):
        self.set_syncookies(True)
        self.set_iptables(False)

    def stats(self):
        return {
            "syncookies": self.syncookies,
            "iptables": self.iptables,
            "synack_retries": self.synack_retries,
            "iptables_dropped": self.get_iptables_drops()
        }
