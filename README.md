# CSE 406: Computer Security Sessional
## Design & Implementation Report — Topic 06: TCP SYN Flood + DoS Attack & Defense Mechanisms

**Team Members:**
- **Shahriar Ahmed Seam** (Student ID: 2005093)
- **Hozifa Rahman Hamim** (Student ID: 1705083)

**Institution:** Department of Computer Science and Engineering, Bangladesh University of Engineering and Technology (BUET)  
**Course:** CSE 406 (Computer Security Sessional)  

---

### Project Overview
This repository contains the design, mathematical modeling, custom low-level C implementation, and defense evaluations for **Topic 06: TCP SYN Flood + DoS Attack and Defense Mechanisms**.

In strict conformance with course policy, zero third-party attack frameworks (`hping3`, `Scapy`, `nping`) were utilized. The core attack engine is written from scratch in standard C utilizing POSIX Raw Sockets (`AF_INET`, `SOCK_RAW`, `IP_HDRINCL`) with manual serialization of Layer 3 (IPv4) and Layer 4 (TCP) headers, dynamic source IP and ephemeral port randomization, and RFC 1071 / RFC 793 16-bit one's complement checksum algorithms.

---

### Directory & File Structure
```
.
├── report.pdf              # Compiled 23-page comprehensive academic design report
├── report.tex              # Complete LaTeX source code for the design report
├── compile_report.py       # Python compilation script (tectonic engine)
├── syn_flood.c             # Custom standalone C raw socket attack engine
├── run_live_experiments.py # Automated virtual network testbed and defense evaluation harness
├── Makefile                # Build automation for compilation, testing, and UI launch
├── figures/                # High-resolution architectural diagrams and empirical graphs
│   ├── network_topology.png
│   ├── timing_diagrams.png
│   ├── packet_structure.png
│   ├── syn_cookie_architecture.png
│   └── empirical_results.png
├── simulator/              # Network attack & defense telemetry console
│   ├── app.py              # Web console entry point (http://localhost:5000)
│   ├── cli.py              # Terminal telemetry monitor
│   ├── Makefile            # Module build rules
│   ├── core/               # Simulation engine (victim, attacker, client, defense)
│   ├── server/             # Standard library REST/HTTP server
│   └── static/             # Telemetry dashboard UI (HTML5 Canvas charts, SVG topology)
└── README.md               # Documentation and reproduction guide
```

---

### Prerequisites & Dependencies
* Linux environment (Ubuntu / Debian / Arch / Fedora) with `gcc`, `make`, and `python3`.
* Standard POSIX networking headers (`<sys/socket.h>`, `<netinet/ip.h>`, `<netinet/tcp.h>`, `<arpa/inet.h>`).
* Optional root privileges for raw socket injection and iptables/sysctl manipulation.

---

### Building and Running

#### 1. Compile the Attack Tool
```bash
make
# Alternatively:
gcc -O2 -Wall syn_flood.c -o syn_flood
```

#### 2. Execute the Standalone Attack Engine
```bash
sudo ./syn_flood <Target_IP> <Target_Port> [Duration_Seconds]

# Example: Flood local port 8080 for 10 seconds (or 0 for continuous)
sudo ./syn_flood 127.0.0.1 8080 10
```

#### 3. Run the Automated Live Experiment Harness
```bash
make test
# Alternatively:
python3 run_live_experiments.py
```

#### 4. Launch the Web Telemetry Dashboard
To launch the real-time telemetry console in the browser:
```bash
make web
# Or directly:
python3 simulator/app.py
```
* Opens `http://localhost:5000` in your browser.
* Real-time RTT latency chart, queue saturation tracking, and defense toggles.
* Zero external pip dependencies.

#### 5. Launch the Terminal Monitor (CLI Mode)
To monitor metrics directly inside the terminal:
```bash
make cli
# Or directly:
python3 simulator/cli.py
```

#### 6. Recompile the LaTeX Design Report
```bash
make report
# Or directly:
python3 compile_report.py
```

---

### Defenses Implemented & Benchmarked
1. **Stateless Cryptographic TCP SYN Cookies (`tcp_syncookies = 1`):** Eliminates server-side half-open state allocation, achieving 90–100% client recovery under flood conditions.
2. **Ingress Firewall Rate Limiting (`iptables -m limit`):** Drops ~84.7% of attack packets at kernel ingress, protecting socket queues.
3. **Netfilter SYN Proxy (`SYNPROXY`):** Shields application backends behind an ingress proxy firewall.
4. **Kernel Parameter Hardening:** Tuned `net.ipv4.tcp_synack_retries` and expanded `tcp_max_syn_backlog`.

