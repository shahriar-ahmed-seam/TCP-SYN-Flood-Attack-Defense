import os
import subprocess

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Common styling
BASE_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
        width: 100%;
        height: 100%;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        scrollbar-width: none !important;
        -ms-overflow-style: none !important;
    }
    ::-webkit-scrollbar {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        background: transparent !important;
    }
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #ffffff;
        color: #1e293b;
        -webkit-font-smoothing: antialiased;
    }
    .mono { font-family: 'JetBrains Mono', monospace; }
</style>
"""

def render_html_to_png(html_content, output_png, width, height):
    temp_html = output_png.replace(".png", ".html")
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    cmd = [
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={width},{height}",
        "--force-device-scale-factor=2",
        f"--screenshot={output_png}",
        temp_html
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[+] Rendered: {output_png} ({width}x{height} @2x)")
    finally:
        if os.path.exists(temp_html):
            os.remove(temp_html)

# -------------------------------------------------------------------------
# 1. TIMING DIAGRAMS
# -------------------------------------------------------------------------
def generate_timing_diagrams():
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
{BASE_STYLE}
<style>
    body {{ padding: 18px 20px; width: 1200px; height: 740px; overflow: hidden !important; }}
    .container {{
        display: grid;
        grid-template-columns: 1fr 1.2fr;
        gap: 20px;
        height: 100%;
        overflow: hidden;
    }}
    .panel {{
        border: 2px solid #e2e8f0;
        border-radius: 14px;
        padding: 16px 18px;
        background: #fafafa;
        position: relative;
        overflow: hidden;
    }}
    .panel.left {{ border-color: #3b82f6; }}
    .panel.right {{ border-color: #ef4444; }}
    .title {{
        font-size: 16.5px;
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .title.left {{ color: #1d4ed8; }}
    .title.right {{ color: #b91c1c; }}
    
    .badge {{
        font-size: 11px;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
    }}
    .badge-blue {{ background: #dbeafe; color: #1e40af; }}
    .badge-red {{ background: #fee2e2; color: #991b1b; }}

    svg {{
        width: 100%;
        height: 560px;
    }}
    .actor-line {{ stroke: #94a3b8; stroke-width: 2; stroke-dasharray: 4,4; }}
    .actor-box {{ fill: #ffffff; stroke-width: 1.5; rx: 8px; }}
    .actor-text {{ font-size: 13px; font-weight: 600; text-anchor: middle; }}
    
    .msg-line {{ stroke-width: 2; marker-end: url(#arrow); }}
    .msg-blue {{ stroke: #2563eb; }}
    .msg-green {{ stroke: #059669; }}
    .msg-red {{ stroke: #dc2626; }}
    .msg-dashed {{ stroke: #dc2626; stroke-dasharray: 5,4; }}
    
    .msg-label {{
        font-size: 11px;
        font-weight: 600;
        fill: #334155;
    }}
    .state-box {{
        rx: 6px;
        stroke-width: 1;
    }}
    .state-text {{
        font-size: 10.5px;
        font-weight: 600;
        text-anchor: middle;
    }}
</style>
</head>
<body>
<div class="container">
    <!-- PART A -->
    <div class="panel left">
        <div class="title left">
            <span>Part A: Standard TCP 3-Way Handshake</span>
            <span class="badge badge-blue">RFC 793 Compliant</span>
        </div>
        <svg viewBox="0 0 480 590">
            <defs>
                <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                    <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/>
                </marker>
                <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                    <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669"/>
                </marker>
                <marker id="arrow-dark" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                    <path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/>
                </marker>
            </defs>

            <!-- Lifelines -->
            <line x1="100" y1="50" x2="100" y2="560" class="actor-line"/>
            <line x1="380" y1="50" x2="380" y2="560" class="actor-line"/>

            <!-- Actor Headers -->
            <rect x="20" y="10" width="160" height="36" class="actor-box" stroke="#3b82f6"/>
            <text x="100" y="33" class="actor-text" fill="#1e40af">Client (192.168.10.3)</text>

            <rect x="300" y="10" width="160" height="36" class="actor-box" stroke="#3b82f6"/>
            <text x="380" y="33" class="actor-text" fill="#1e40af">Server (192.168.10.10)</text>

            <!-- 1. SYN -->
            <line x1="100" y1="110" x2="372" y2="145" stroke="#2563eb" stroke-width="2" marker-end="url(#arrow-blue)"/>
            <text x="130" y="98" class="msg-label mono" fill="#1e40af">1. SYN [seq=1000, Flags=SYN]</text>

            <!-- Server State: TCB Allocated -->
            <rect x="255" y="160" width="210" height="32" class="state-box" fill="#fef2f2" stroke="#f87171"/>
            <text x="360" y="180" class="state-text" fill="#991b1b">Allocates TCB -> SYN_RCVD</text>

            <!-- 2. SYN-ACK -->
            <line x1="380" y1="225" x2="108" y2="260" stroke="#059669" stroke-width="2" marker-end="url(#arrow-green)"/>
            <text x="140" y="213" class="msg-label mono" fill="#065f46">2. SYN-ACK [seq=5000, ack=1001]</text>

            <!-- Client State: Established -->
            <rect x="15" y="275" width="170" height="28" class="state-box" fill="#ecfdf5" stroke="#34d399"/>
            <text x="100" y="293" class="state-text" fill="#065f46">State: ESTABLISHED</text>

            <!-- 3. ACK -->
            <line x1="100" y1="335" x2="372" y2="370" stroke="#2563eb" stroke-width="2" marker-end="url(#arrow-blue)"/>
            <text x="130" y="323" class="msg-label mono" fill="#1e40af">3. ACK [seq=1001, ack=5001]</text>

            <!-- Server State: Moved to Accept Queue -->
            <rect x="250" y="385" width="220" height="32" class="state-box" fill="#eff6ff" stroke="#60a5fa"/>
            <text x="360" y="405" class="state-text" fill="#1e40af">ESTABLISHED -> Accept Queue</text>

            <!-- 4. HTTP Data -->
            <line x1="100" y1="450" x2="372" y2="485" stroke="#475569" stroke-width="2" marker-end="url(#arrow-dark)"/>
            <text x="130" y="438" class="msg-label mono" fill="#334155">4. HTTP GET /index.html</text>

            <line x1="380" y1="515" x2="108" y2="550" stroke="#475569" stroke-width="2" marker-end="url(#arrow-dark)"/>
            <text x="140" y="503" class="msg-label mono" fill="#334155">5. HTTP 200 OK (Payload Data)</text>
        </svg>
    </div>

    <!-- PART B -->
    <div class="panel right">
        <div class="title right">
            <span>Part B: SYN Flood Denial of Service Saturation</span>
            <span class="badge badge-red">Queue Starvation Attack</span>
        </div>
        <svg viewBox="0 0 580 590">
            <defs>
                <marker id="arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                    <path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626"/>
                </marker>
                <marker id="arrow-red-dash" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                    <path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626"/>
                </marker>
            </defs>

            <!-- Lifelines -->
            <line x1="70" y1="50" x2="70" y2="560" class="actor-line"/>
            <line x1="280" y1="50" x2="280" y2="560" class="actor-line"/>
            <line x1="490" y1="50" x2="490" y2="560" class="actor-line"/>

            <!-- Actor Headers -->
            <rect x="5" y="10" width="130" height="36" class="actor-box" stroke="#ef4444"/>
            <text x="70" y="33" class="actor-text" fill="#b91c1c">Attacker Node</text>

            <rect x="215" y="10" width="130" height="36" class="actor-box" stroke="#3b82f6"/>
            <text x="280" y="33" class="actor-text" fill="#1e40af">Victim Server</text>

            <rect x="425" y="10" width="130" height="36" class="actor-box" stroke="#10b981"/>
            <text x="490" y="33" class="actor-text" fill="#047857">Legit Client</text>

            <!-- Spoofed SYN #1 -->
            <line x1="70" y1="105" x2="272" y2="125" stroke="#dc2626" stroke-width="2" marker-end="url(#arrow-red)"/>
            <text x="75" y="96" class="msg-label mono" fill="#b91c1c">Spoofed SYN #1 [Src: 10.4.1.2]</text>

            <!-- Spoofed SYN #2 -->
            <line x1="70" y1="145" x2="272" y2="165" stroke="#dc2626" stroke-width="2" marker-end="url(#arrow-red)"/>
            <text x="75" y="136" class="msg-label mono" fill="#b91c1c">Spoofed SYN #2 [Src: 172.16.8.9]</text>

            <!-- Torrent stream -->
            <line x1="70" y1="185" x2="272" y2="205" stroke="#dc2626" stroke-width="2.5" marker-end="url(#arrow-red)"/>
            <text x="75" y="176" class="msg-label mono" fill="#b91c1c">Flood Stream (>388k SYNs/sec)</text>

            <!-- Server Saturated Badge -->
            <rect x="180" y="218" width="200" height="42" class="state-box" fill="#fee2e2" stroke="#ef4444" stroke-width="1.5"/>
            <text x="280" y="236" class="state-text" fill="#991b1b" font-weight="700">SYN BACKLOG FULL (128/128)</text>
            <text x="280" y="251" class="state-text" fill="#7f1d1d" font-size="9.5px">Victim SYN-ACKs unanswered</text>

            <!-- Legit Client attempts connection -->
            <line x1="490" y1="285" x2="288" y2="310" stroke="#059669" stroke-width="2" marker-end="url(#arrow-green)"/>
            <text x="315" y="278" class="msg-label mono" fill="#065f46">Valid SYN [seq=2000]</text>

            <!-- Silent Drop Box -->
            <rect x="200" y="325" width="160" height="32" class="state-box" fill="#450a0a" stroke="#b91c1c"/>
            <text x="280" y="345" class="state-text" fill="#fecaca">QUEUE FULL -> DROP</text>

            <!-- Legit client retransmits -->
            <line x1="490" y1="385" x2="288" y2="410" stroke="#dc2626" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#arrow-red-dash)"/>
            <text x="305" y="378" class="msg-label mono" fill="#991b1b">SYN Retransmit (T_timeout)</text>

            <!-- Second Silent Drop -->
            <rect x="200" y="425" width="160" height="32" class="state-box" fill="#450a0a" stroke="#b91c1c"/>
            <text x="280" y="445" class="state-text" fill="#fecaca">NO RESPONSE -> DROP</text>

            <!-- Starvation Conclusion -->
            <rect x="360" y="480" width="210" height="54" class="state-box" fill="#fff1f2" stroke="#e11d48" stroke-width="1.5"/>
            <text x="465" y="502" class="state-text" fill="#be123c" font-weight="700">Connection Timed Out!</text>
            <text x="465" y="522" class="state-text" fill="#881337" font-size="10px">100% Denial of Service (DoS)</text>
        </svg>
    </div>
</div>
</body>
</html>
"""
    out_png = os.path.join(OUTPUT_DIR, "timing_diagrams.png")
    render_html_to_png(html, out_png, 1200, 740)

# -------------------------------------------------------------------------
# 2. SYN COOKIE ARCHITECTURE
# -------------------------------------------------------------------------
def generate_syn_cookie_architecture():
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
{BASE_STYLE}
<style>
    body {{ padding: 20px 24px; width: 1200px; height: 630px; overflow: hidden !important; }}
    .title {{
        font-size: 20px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 24px;
        text-align: center;
    }}
    .register-container {{
        background: #f8fafc;
        border: 2px solid #cbd5e1;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 28px;
    }}
    .reg-title {{
        font-size: 14px;
        font-weight: 700;
        color: #334155;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
    }}
    .bit-indices {{
        display: flex;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 4px;
    }}
    .bit-bar {{
        display: flex;
        height: 52px;
        border-radius: 8px;
        overflow: hidden;
        border: 2px solid #475569;
    }}
    .bit-seg {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        font-weight: 600;
        font-size: 12.5px;
        border-right: 1.5px solid #475569;
        padding: 0 8px;
    }}
    .bit-seg:last-child {{ border-right: none; }}
    
    .seg-mss {{ width: 14%; background: #dcfce7; color: #166534; }}
    .seg-time {{ width: 20%; background: #e0f2fe; color: #075985; }}
    .seg-hash {{ width: 66%; background: #fee2e2; color: #991b1b; }}
    
    .cards {{
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 20px;
    }}
    .card {{
        border-radius: 12px;
        border: 1.5px solid #cbd5e1;
        padding: 20px;
        background: #ffffff;
    }}
    .card.c1 {{ border-top: 5px solid #10b981; }}
    .card.c2 {{ border-top: 5px solid #0284c7; }}
    .card.c3 {{ border-top: 5px solid #f59e0b; }}
    
    .card-title {{
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 12px;
    }}
    .c1 .card-title {{ color: #047857; }}
    .c2 .card-title {{ color: #0369a1; }}
    .c3 .card-title {{ color: #b45309; }}
    
    .card-list {{
        list-style: none;
        font-size: 12.5px;
        color: #334155;
        line-height: 1.6;
    }}
    .card-list li {{
        margin-bottom: 6px;
        position: relative;
        padding-left: 14px;
    }}
    .card-list li::before {{
        content: "•";
        position: absolute;
        left: 0;
        font-weight: bold;
    }}
    .c1 .card-list li::before {{ color: #10b981; }}
    .c2 .card-list li::before {{ color: #0284c7; }}
    .c3 .card-list li::before {{ color: #f59e0b; }}
    
    .card-footer {{
        margin-top: 14px;
        padding-top: 10px;
        border-top: 1px dashed #e2e8f0;
        font-size: 12px;
        font-weight: 700;
    }}
    .alert-success {{ color: #059669; }}
    .alert-danger {{ color: #dc2626; }}
</style>
</head>
<body>
    <div class="title">Stateless TCP SYN Cookie Architecture & ISN Encoding (D. J. Bernstein)</div>
    
    <div class="register-container">
        <div class="reg-title">
            <span>32-Bit Initial Sequence Number (ISN_cookie) Field Allocation</span>
            <span class="mono">sizeof(uint32_t) = 4 Bytes</span>
        </div>
        <div class="bit-indices">
            <span style="width: 14%;">Bit 0 .. 2 (3 bits)</span>
            <span style="width: 20%;">Bit 3 .. 7 (5 bits)</span>
            <span style="width: 66%;">Bit 8 .. 31 (24 bits)</span>
        </div>
        <div class="bit-bar">
            <div class="bit-seg seg-mss">
                <span>MSS Index</span>
                <span class="mono" style="font-size: 10.5px;">8 MSS table values</span>
            </div>
            <div class="bit-seg seg-time">
                <span>Timestamp &tau; (mod 32)</span>
                <span class="mono" style="font-size: 10.5px;">Coarse time (t &gt;&gt; 6)</span>
            </div>
            <div class="bit-seg seg-hash">
                <span>Keyed Cryptographic Hash: SipHash(SrcIP, SrcPort, DstIP, DstPort, SecretKey, &tau;)</span>
                <span class="mono" style="font-size: 10.5px;">24-bit truncated keyed message authentication code (MAC)</span>
            </div>
        </div>
    </div>
    
    <div class="cards">
        <div class="card c1">
            <div class="card-title">1. Inbound SYN Arrival</div>
            <ul class="card-list">
                <li>Client sends standard TCP SYN packet.</li>
                <li>SYN Backlog reaches maximum capacity (<span class="mono">128/128</span>).</li>
                <li>Kernel activates SYN Cookies fallback automatically.</li>
                <li>Normal TCB allocation is explicitly skipped.</li>
            </ul>
            <div class="card-footer alert-danger">
                Memory Allocated: 0 Bytes
            </div>
        </div>

        <div class="card c2">
            <div class="card-title">2. Stateless Computation</div>
            <ul class="card-list">
                <li>Kernel computes 24-bit hash over 4-tuple and secret key.</li>
                <li>Encodes client MSS into lower 3 bits.</li>
                <li>Embeds result into 32-bit Initial Sequence Number.</li>
                <li>Transmits SYN-ACK (<span class="mono">seq = ISN_cookie</span>) to client.</li>
            </ul>
            <div class="card-footer alert-success">
                Server Retains Zero State
            </div>
        </div>

        <div class="card c3">
            <div class="card-title">3. Validation on ACK Arrival</div>
            <ul class="card-list">
                <li>Legitimate client returns ACK (<span class="mono">ack = ISN_cookie + 1</span>).</li>
                <li>Server subtracts 1 and recalculates expected hash.</li>
                <li>Checks timestamp freshness (&tau; within valid window).</li>
                <li>Allocates real socket/TCB only after validation passes.</li>
            </ul>
            <div class="card-footer alert-success">
                Spoofed SYNs Discarded (No Memory Leak)
            </div>
        </div>
    </div>
</body>
</html>
"""
    out_png = os.path.join(OUTPUT_DIR, "syn_cookie_architecture.png")
    render_html_to_png(html, out_png, 1200, 630)

# -------------------------------------------------------------------------
# 3. NETWORK TOPOLOGY
# -------------------------------------------------------------------------
def generate_network_topology():
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
{BASE_STYLE}
<style>
    body {{ padding: 16px 20px; width: 1200px; height: 660px; overflow: hidden !important; }}
    .title {{
        font-size: 19px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 16px;
        text-align: center;
    }}
    .testbed-box {{
        border: 2px dashed #94a3b8;
        border-radius: 14px;
        padding: 16px 18px;
        margin-top: 14px;
        background: #f8fafc;
        position: relative;
    }}
    .subnet-tag {{
        position: absolute;
        top: -12px;
        left: 32px;
        background: #1e293b;
        color: white;
        padding: 2px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}
    svg {{
        width: 100%;
        height: 490px;
    }}
    .bridge-box {{
        fill: #1e293b;
        stroke: #0f172a;
        stroke-width: 2;
        rx: 10px;
    }}
    .bridge-text {{ fill: #ffffff; font-weight: 700; font-size: 15px; text-anchor: middle; }}
    .bridge-sub {{ fill: #94a3b8; font-size: 12px; text-anchor: middle; font-family: monospace; }}

    .node-box {{
        stroke-width: 2;
        rx: 12px;
        fill: #ffffff;
    }}
    .node-att {{ stroke: #ef4444; }}
    .node-vic {{ stroke: #2563eb; }}
    .node-cli {{ stroke: #10b981; }}

    .node-title {{ font-size: 15px; font-weight: 700; text-anchor: middle; }}
    .node-ip {{ font-size: 13px; font-weight: 600; text-anchor: middle; font-family: monospace; }}
    .node-detail {{ font-size: 11.5px; fill: #475569; }}

    .cable {{
        stroke-width: 3;
        stroke-linecap: round;
    }}
    .cable-att {{ stroke: #ef4444; }}
    .cable-vic {{ stroke: #2563eb; }}
    .cable-cli {{ stroke: #10b981; }}

    .port-badge {{
        fill: #ffffff;
        stroke-width: 1.5;
        rx: 4px;
    }}
    .port-text {{
        font-size: 10.5px;
        font-weight: 600;
        font-family: monospace;
        text-anchor: middle;
    }}
</style>
</head>
<body>
    <div class="title">Isolated Virtual Testbed Network Architecture (Linux Namespaces + Bridge)</div>
    
    <div class="testbed-box">
        <div class="subnet-tag">SUBNET: 192.168.10.0/24 (ISOLATED L2 BROADCAST DOMAIN)</div>
        
        <svg viewBox="0 0 1100 500">
            <!-- Virtual Bridge -->
            <rect x="400" y="14" width="300" height="84" class="bridge-box"/>
            <text x="550" y="46" class="bridge-text">Virtual Bridge (br-sec)</text>
            <text x="550" y="72" class="bridge-sub" fill="#93c5fd">IP: 192.168.10.1 &bull; Linux Software Switch</text>

            <!-- Cables from bridge to nodes -->
            <path d="M 460 98 L 460 160 L 190 160 L 190 230" fill="none" class="cable cable-att"/>
            <path d="M 550 98 L 550 230" fill="none" class="cable cable-vic"/>
            <path d="M 640 98 L 640 160 L 910 160 L 910 230" fill="none" class="cable cable-cli"/>

            <!-- Port Badges on Bridge -->
            <rect x="430" y="108" width="60" height="20" class="port-badge" stroke="#ef4444"/>
            <text x="460" y="122" class="port-text" fill="#ef4444">br-att</text>

            <rect x="520" y="108" width="60" height="20" class="port-badge" stroke="#2563eb"/>
            <text x="550" y="122" class="port-text" fill="#2563eb">br-vic</text>

            <rect x="610" y="108" width="60" height="20" class="port-badge" stroke="#10b981"/>
            <text x="640" y="122" class="port-text" fill="#10b981">br-cli</text>

            <!-- Port Badges on Nodes -->
            <rect x="160" y="200" width="60" height="20" class="port-badge" stroke="#ef4444"/>
            <text x="190" y="214" class="port-text" fill="#ef4444">veth-att</text>

            <rect x="520" y="200" width="60" height="20" class="port-badge" stroke="#2563eb"/>
            <text x="550" y="214" class="port-text" fill="#2563eb">veth-vic</text>

            <rect x="880" y="200" width="60" height="20" class="port-badge" stroke="#10b981"/>
            <text x="910" y="214" class="port-text" fill="#10b981">veth-cli</text>

            <!-- NODE 1: ATTACKER -->
            <rect x="40" y="230" width="300" height="220" class="node-box node-att"/>
            <text x="190" y="265" class="node-title" fill="#b91c1c">Attacker Node (ns-attacker)</text>
            <text x="190" y="285" class="node-ip" fill="#dc2626">192.168.10.2 / 24</text>
            <line x1="60" y1="295" x2="320" y2="295" stroke="#fecaca" stroke-width="1"/>
            <text x="60" y="320" class="node-detail">• Custom Standalone C Binary (syn_flood)</text>
            <text x="60" y="342" class="node-detail">• POSIX AF_INET / SOCK_RAW with IP_HDRINCL</text>
            <text x="60" y="364" class="node-detail">• Privilege: CAP_NET_RAW (Layer 3/4 crafting)</text>
            <text x="60" y="386" class="node-detail">• Random Spoofed Source IPs & Ports</text>
            <text x="60" y="408" class="node-detail">• Injection Rate: >388,000 packets/sec</text>

            <!-- NODE 2: VICTIM SERVER -->
            <rect x="400" y="230" width="300" height="220" class="node-box node-vic"/>
            <text x="550" y="265" class="node-title" fill="#1d4ed8">Victim Server (ns-victim)</text>
            <text x="550" y="285" class="node-ip" fill="#2563eb">192.168.10.10 / 24</text>
            <line x1="420" y1="295" x2="680" y2="295" stroke="#bfdbfe" stroke-width="1"/>
            <text x="420" y="320" class="node-detail">• Web Service: HTTP on TCP Port 8080</text>
            <text x="420" y="342" class="node-detail">• SYN Backlog Queue: 16 to 128 slots</text>
            <text x="420" y="364" class="node-detail">• Privilege: CAP_NET_ADMIN (sysctl & iptables)</text>
            <text x="420" y="386" class="node-detail">• Baseline: tcp_syncookies = 0 (Vulnerable)</text>
            <text x="420" y="408" class="node-detail">• Hardened: SYN Cookies, iptables Rate Limit</text>

            <!-- NODE 3: LEGITIMATE CLIENT -->
            <rect x="760" y="230" width="300" height="220" class="node-box node-cli"/>
            <text x="910" y="265" class="node-title" fill="#047857">Legit Client (ns-client)</text>
            <text x="910" y="285" class="node-ip" fill="#059669">192.168.10.3 / 24</text>
            <line x1="780" y1="295" x2="1040" y2="295" stroke="#a7f3d0" stroke-width="1"/>
            <text x="780" y="320" class="node-detail">• Python Telemetry Socket Prober & curl</text>
            <text x="780" y="342" class="node-detail">• Standard Kernel 3-Way Handshake</text>
            <text x="780" y="364" class="node-detail">• Probes Port 8080 at Periodic Intervals</text>
            <text x="780" y="386" class="node-detail">• Measures Round Trip Time (RTT) Latency</text>
            <text x="780" y="408" class="node-detail">• Records Timeout Drops & Connection Failures</text>
        </svg>
    </div>
</body>
</html>
"""
    out_png = os.path.join(OUTPUT_DIR, "network_topology.png")
    render_html_to_png(html, out_png, 1200, 660)

# -------------------------------------------------------------------------
# 4. PACKET STRUCTURE
# -------------------------------------------------------------------------
def generate_packet_structure():
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
{BASE_STYLE}
<style>
    body {{ padding: 18px 24px; width: 1200px; height: 750px; overflow: hidden !important; }}
    .title {{
        font-size: 20px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 14px;
        text-align: center;
    }}
    .header-card {{
        border-radius: 12px;
        border: 2px solid #cbd5e1;
        overflow: hidden;
        margin-bottom: 16px;
    }}
    .header-top {{
        padding: 10px 16px;
        font-weight: 700;
        font-size: 13.5px;
        display: flex;
        justify-content: space-between;
    }}
    .header-top.ip {{ background: #eff6ff; color: #1e40af; border-bottom: 2px solid #bfdbfe; }}
    .header-top.tcp {{ background: #fffbeb; color: #b45309; border-bottom: 2px solid #fde68a; }}

    table.grid {{
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
    }}
    table.grid th {{
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        padding: 4px;
        font-size: 10.5px;
        color: #64748b;
        font-family: 'JetBrains Mono', monospace;
    }}
    table.grid td {{
        border: 1px solid #cbd5e1;
        padding: 8px 10px;
        text-align: center;
        font-weight: 500;
        background: #ffffff;
    }}
    .f-name {{ font-weight: 700; font-size: 12px; }}
    .f-val {{ font-size: 11px; color: #475569; font-family: 'JetBrains Mono', monospace; margin-top: 2px; }}
    
    .hl-red {{ background: #fee2e2 !important; color: #991b1b !important; border: 2px solid #ef4444 !important; }}
    .hl-blue {{ background: #dbeafe !important; color: #1e40af !important; border: 2px solid #3b82f6 !important; }}
    .hl-green {{ background: #dcfce7 !important; color: #166534 !important; }}
</style>
</head>
<body>
    <div class="title">Bitwise Network Frame & Transport Segment Header Layouts</div>

    <!-- IPv4 Header -->
    <div class="header-card">
        <div class="header-top ip">
            <span>Layer 3: IPv4 Header (20 Bytes - User Constructed via IP_HDRINCL)</span>
            <span class="mono">sizeof(struct iphdr) = 20B</span>
        </div>
        <table class="grid">
            <tr>
                <th style="width: 12.5%;">Bit 0 .. 3</th>
                <th style="width: 12.5%;">Bit 4 .. 7</th>
                <th style="width: 25%;">Bit 8 .. 15</th>
                <th style="width: 50%;">Bit 16 .. 31</th>
            </tr>
            <tr>
                <td><div class="f-name">Version</div><div class="f-val">4 (IPv4)</div></td>
                <td><div class="f-name">IHL</div><div class="f-val">5 (20 Bytes)</div></td>
                <td><div class="f-name">Type of Service</div><div class="f-val">0x00 (Routine)</div></td>
                <td><div class="f-name">Total Length</div><div class="f-val">40 Bytes (IP + TCP)</div></td>
            </tr>
            <tr>
                <td colspan="2"><div class="f-name">Identification</div><div class="f-val">rand() % 65535</div></td>
                <td><div class="f-name">Flags</div><div class="f-val">0x4000 (DF = 1)</div></td>
                <td><div class="f-name">Fragment Offset</div><div class="f-val">0</div></td>
            </tr>
            <tr>
                <td colspan="2"><div class="f-name">TTL</div><div class="f-val">64 Hops</div></td>
                <td><div class="f-name">Protocol</div><div class="f-val">6 (IPPROTO_TCP)</div></td>
                <td><div class="f-name">Header Checksum</div><div class="f-val">RFC 1071 16-bit 1's Complement</div></td>
            </tr>
            <tr>
                <td colspan="4" class="hl-red">
                    <div class="f-name" style="font-size: 13.5px; color: #b91c1c;">SOURCE IP ADDRESS: RANDOM SPOOFED [32 Bits]</div>
                    <div class="f-val" style="color: #7f1d1d;">Random IPv4 Address per Packet (Generates Distinct Inactive Subnets)</div>
                </td>
            </tr>
            <tr>
                <td colspan="4" class="hl-blue">
                    <div class="f-name" style="font-size: 13px;">DESTINATION IP ADDRESS: 192.168.10.10 [32 Bits]</div>
                    <div class="f-val" style="color: #1e3a8a;">Victim Server Target Interface (Subnet 192.168.10.0/24)</div>
                </td>
            </tr>
        </table>
    </div>

    <!-- TCP Header -->
    <div class="header-card">
        <div class="header-top tcp">
            <span>Layer 4: TCP Segment Header (20 Bytes - Crafted SYN Segment)</span>
            <span class="mono">sizeof(struct tcphdr) = 20B</span>
        </div>
        <table class="grid">
            <tr>
                <th style="width: 50%;">Bit 0 .. 15</th>
                <th style="width: 50%;">Bit 16 .. 31</th>
            </tr>
            <tr>
                <td class="hl-red">
                    <div class="f-name">SOURCE PORT: RANDOM (1024 - 65535)</div>
                    <div class="f-val">Diversifies 4-Tuple Connections</div>
                </td>
                <td class="hl-blue">
                    <div class="f-name">DESTINATION PORT: 8080</div>
                    <div class="f-val">Target Listening Web Service</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="f-name">Sequence Number (seq)</div>
                    <div class="f-bits">32 bits &bull; Random Initial Sequence Number</div>
                    <div class="f-val">rand() (Unpredictable RFC 793 ISN)</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="f-name">Acknowledgment Number (ack_seq)</div>
                    <div class="f-bits">32 bits &bull; Initial SYN Handshake</div>
                    <div class="f-val">0 (No Previous State Exists)</div>
                </td>
            </tr>
            <tr>
                <td>
                    <div style="display: flex; justify-content: space-around;">
                        <div>
                            <div class="f-name">Data Offset</div>
                            <div class="f-bits">4 bits</div>
                            <div class="f-val">5 (20 B)</div>
                        </div>
                        <div>
                            <div class="f-name">Reserved</div>
                            <div class="f-bits">4 bits</div>
                            <div class="f-val">0</div>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="f-name">Control Flags (6 bits active)</div>
                    <div class="flag-group" style="margin-top: 4px;">
                        <span class="flag-badge flag-off">URG:0</span>
                        <span class="flag-badge flag-off">ACK:0</span>
                        <span class="flag-badge flag-off">PSH:0</span>
                        <span class="flag-badge flag-off">RST:0</span>
                        <span class="flag-badge flag-on">SYN:1</span>
                        <span class="flag-badge flag-off">FIN:0</span>
                    </div>
                </td>
            </tr>
            <tr>
                <td>
                    <div class="f-name">Window Size</div>
                    <div class="f-bits">16 bits</div>
                    <div class="f-val">htons(5840) (Linux Default Advertised)</div>
                </td>
                <td>
                    <div class="f-name">Checksum</div>
                    <div class="f-bits">16 bits</div>
                    <div class="f-val" style="color: #b91c1c;">csum(pseudo_header + tcphdr)</div>
                </td>
            </tr>
            <tr>
                <td>
                    <div class="f-name">Options & Padding</div>
                    <div class="f-val">None (Minimum 20 Bytes Header)</div>
                </td>
                <td>
                    <div class="f-name">Urgent Pointer</div>
                    <div class="f-val">0 (Not Used)</div>
                </td>
            </tr>
        </table>
    </div>
</body>
</html>
"""
    out_png = os.path.join(OUTPUT_DIR, "packet_structure.png")
    render_html_to_png(html, out_png, 1200, 750)

# -------------------------------------------------------------------------
# 5. EMPIRICAL RESULTS
# -------------------------------------------------------------------------
def generate_empirical_results():
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
{BASE_STYLE}
<style>
    body {{ padding: 20px 24px; width: 1200px; height: 610px; overflow: hidden !important; }}
    .title {{
        font-size: 20px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 24px;
        text-align: center;
    }}
    .charts-grid {{
        display: grid;
        grid-template-columns: 1.15fr 1fr;
        gap: 28px;
        height: 500px;
    }}
    .chart-box {{
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        background: #ffffff;
        display: flex;
        flex-direction: column;
    }}
    .chart-header {{
        font-size: 15px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 20px;
        text-align: center;
    }}
    
    /* Bar Graph SVG */
    .axis-line {{ stroke: #64748b; stroke-width: 1.5; }}
    .grid-line {{ stroke: #f1f5f9; stroke-width: 1; stroke-dasharray: 4,4; }}
    .tick-text {{ font-size: 11px; fill: #64748b; font-family: 'JetBrains Mono', monospace; }}
    .bar-val {{ font-size: 12px; font-weight: 700; text-anchor: middle; }}
    .bar-sub {{ font-size: 10px; font-weight: 600; text-anchor: middle; }}
    .bar-lbl {{ font-size: 11.5px; font-weight: 600; text-anchor: middle; fill: #334155; }}
</style>
</head>
<body>
    <div class="title">Empirical Verification Metrics from Isolated Testbed Benchmarks</div>

    <div class="charts-grid">
        <!-- Chart 1: Latency -->
        <div class="chart-box">
            <div class="chart-header">Legitimate Client Handshake Latency (ms) across Test Phases</div>
            <svg viewBox="0 0 540 380">
                <!-- Y-Axis Grid Lines -->
                <line x1="60" y1="40" x2="510" y2="40" class="grid-line"/>
                <text x="50" y="44" class="tick-text" text-anchor="end">500</text>

                <line x1="60" y1="110" x2="510" y2="110" class="grid-line"/>
                <text x="50" y="114" class="tick-text" text-anchor="end">375</text>

                <line x1="60" y1="180" x2="510" y2="180" class="grid-line"/>
                <text x="50" y="184" class="tick-text" text-anchor="end">250</text>

                <line x1="60" y1="250" x2="510" y2="250" class="grid-line"/>
                <text x="50" y="254" class="tick-text" text-anchor="end">125</text>

                <line x1="60" y1="320" x2="510" y2="320" class="axis-line"/>
                <text x="50" y="324" class="tick-text" text-anchor="end">0</text>

                <line x1="60" y1="30" x2="60" y2="320" class="axis-line"/>

                <!-- Bar 1: Baseline -->
                <rect x="95" y="318" width="55" height="2" fill="#10b981" rx="4"/>
                <text x="122" y="310" class="bar-val" fill="#047857">0.09 ms</text>
                <text x="122" y="340" class="bar-lbl">Baseline</text>
                <text x="122" y="356" class="bar-sub" fill="#059669">[No Attack]</text>

                <!-- Bar 2: SYN Flood -->
                <rect x="200" y="40" width="55" height="280" fill="#ef4444" rx="4"/>
                <text x="227" y="30" class="bar-val" fill="#b91c1c">500.54 ms</text>
                <text x="227" y="340" class="bar-lbl">SYN Flood</text>
                <text x="227" y="356" class="bar-sub" fill="#dc2626">[Total DoS]</text>

                <!-- Bar 3: SYN Cookies -->
                <rect x="305" y="292" width="55" height="28" fill="#0284c7" rx="4"/>
                <text x="332" y="284" class="bar-val" fill="#0369a1">50.09 ms</text>
                <text x="332" y="340" class="bar-lbl">SYN Cookies</text>
                <text x="332" y="356" class="bar-sub" fill="#0284c7">[90-100% Ok]</text>

                <!-- Bar 4: iptables -->
                <rect x="410" y="317" width="55" height="3" fill="#f59e0b" rx="4"/>
                <text x="437" y="310" class="bar-val" fill="#b45309">0.15 ms</text>
                <text x="437" y="340" class="bar-lbl">iptables Limit</text>
                <text x="437" y="356" class="bar-sub" fill="#d97706">[Shielded]</text>
            </svg>
        </div>

        <!-- Chart 2: Netfilter Packet Distribution -->
        <div class="chart-box">
            <div class="chart-header">Netfilter Ingress Packet Distribution (300 Injected SYNs)</div>
            <svg viewBox="0 0 460 380">
                <!-- Y-Axis Grid Lines -->
                <line x1="60" y1="40" x2="420" y2="40" class="grid-line"/>
                <text x="50" y="44" class="tick-text" text-anchor="end">300</text>

                <line x1="60" y1="110" x2="420" y2="110" class="grid-line"/>
                <text x="50" y="114" class="tick-text" text-anchor="end">225</text>

                <line x1="60" y1="180" x2="420" y2="180" class="grid-line"/>
                <text x="50" y="184" class="tick-text" text-anchor="end">150</text>

                <line x1="60" y1="250" x2="420" y2="250" class="grid-line"/>
                <text x="50" y="254" class="tick-text" text-anchor="end">75</text>

                <line x1="60" y1="320" x2="420" y2="320" class="axis-line"/>
                <text x="50" y="324" class="tick-text" text-anchor="end">0</text>

                <line x1="60" y1="30" x2="60" y2="320" class="axis-line"/>

                <!-- Bar 1: Dropped Packets -->
                <rect x="120" y="83" width="80" height="237" fill="#dc2626" rx="6"/>
                <text x="160" y="72" class="bar-val" fill="#991b1b" font-size="14px">254 pkts</text>
                <text x="160" y="200" class="bar-val" fill="#ffffff" font-size="16px">84.7%</text>
                <text x="160" y="342" class="bar-lbl" fill="#b91c1c" font-weight="700">DROPPED</text>
                <text x="160" y="358" class="bar-sub" fill="#7f1d1d">Attack Spoofed SYNs</text>

                <!-- Bar 2: Accepted Packets -->
                <rect x="270" y="277" width="80" height="43" fill="#16a34a" rx="6"/>
                <text x="310" y="267" class="bar-val" fill="#15803d" font-size="14px">46 pkts</text>
                <text x="310" y="302" class="bar-val" fill="#ffffff" font-size="13px">15.3%</text>
                <text x="310" y="342" class="bar-lbl" fill="#15803d" font-weight="700">ACCEPTED</text>
                <text x="310" y="358" class="bar-sub" fill="#14532d">Token Bucket Admitted</text>
            </svg>
        </div>
    </div>
</body>
</html>
"""
    out_png = os.path.join(OUTPUT_DIR, "empirical_results.png")
    render_html_to_png(html, out_png, 1200, 610)

if __name__ == "__main__":
    print("[*] Generating clean preview figures into:", OUTPUT_DIR)
    generate_timing_diagrams()
    generate_syn_cookie_architecture()
    generate_network_topology()
    generate_packet_structure()
    generate_empirical_results()
    print("[✓] All 5 preview figures generated successfully!")
