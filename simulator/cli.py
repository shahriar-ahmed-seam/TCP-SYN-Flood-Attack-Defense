import time
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text

from core.engine import SimulationEngine

def build_layout() -> Layout:
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="logs", size=8),
    )
    layout["main"].split_row(
        Layout(name="nodes", ratio=1),
        Layout(name="telemetry", ratio=1),
    )
    return layout

def render_header(data) -> Panel:
    st = data["status"]
    if st == "ATTACK":
        badge = Text(" ACTIVE ATTACK (SYN FLOOD) ", style="bold white on red")
    elif st == "DEFENDED":
        badge = Text(" DEFENSE MITIGATION ACTIVE ", style="bold black on cyan")
    else:
        badge = Text(" NORMAL TRAFFIC ", style="bold white on green")

    title = Text("BUET CSE 406 — Topic 06: TCP SYN Flood & Defense Monitor", style="bold white")
    return Panel(Text.assemble(title, "  |  ", badge), border_style="blue")

def render_nodes(data) -> Panel:
    table = Table(expand=True, border_style="dim")
    table.add_column("Node", style="bold cyan")
    table.add_column("Address", style="dim")
    table.add_column("State", style="bold")
    table.add_column("Details", style="white")

    a = data["attacker"]
    a_state = "[bold red]FLOODING[/bold red]" if a["active"] else "[dim]IDLE[/dim]"
    table.add_row("Attacker", "192.168.10.2:raw", a_state, f"{a['packets_sent']:,} pkts sent")

    v = data["victim"]
    v_state = f"[yellow]{v['syn_recv']}[/yellow] / {v['backlog_limit']} in SYN_RECV"
    table.add_row("Victim Server", f"192.168.10.10:{v['port']}", v_state, f"{v['handled']:,} HTTP handled")

    c = data["client"]
    c_color = "green" if c["latency_ms"] < 100 else "red"
    c_state = f"[{c_color}]{c['status']} ({c['latency_ms']} ms)[/{c_color}]"
    table.add_row("Legit Client", "192.168.10.3:prober", c_state, f"{c['availability_pct']}% Availability")

    return Panel(table, title="[bold]Network Nodes[/bold]", border_style="cyan")

def render_telemetry(data) -> Panel:
    v = data["victim"]
    c = data["client"]
    d = data["defense"]

    sat = v["saturation_pct"]
    bar_width = 20
    filled = int((sat / 100.0) * bar_width)
    bar_color = "red" if sat > 75 else "yellow" if sat > 30 else "green"
    meter = f"[{bar_color}]{'█' * filled}{'░' * (bar_width - filled)}[/{bar_color}] {sat}%"

    txt = Text()
    txt.append("Queue Saturation:\n", style="bold")
    txt.append(f"  {meter}\n\n")
    txt.append("Client Handshake RTT:\n", style="bold")
    txt.append(f"  {c['latency_ms']} ms (Ceiling: 500 ms) | {c['availability_pct']}% Availability\n\n")
    txt.append("Defense State:\n", style="bold")
    sc_val = "[green]ENABLED[/green]" if d["syncookies"] else "[red]DISABLED[/red]"
    ipt_val = "[green]ENABLED[/green]" if d["iptables"] else "[red]DISABLED[/red]"
    txt.append(f"  - SYN Cookies: {sc_val}\n")
    txt.append(f"  - iptables Rate Limit: {ipt_val} (Drops: {d['iptables_dropped']:,})")

    return Panel(txt, title="[bold]Telemetry[/bold]", border_style="magenta")

def render_logs(data) -> Panel:
    txt = Text()
    for entry in data["logs"][-5:]:
        src = entry["source"]
        col = "red" if src == "ATTACK" else "cyan" if src == "VICTIM" else "blue" if src == "DEFENSE" else "green"
        txt.append(f"[{entry['time']}] [{src}] ", style=f"bold {col}")
        txt.append(f"{entry['message']}\n")
    return Panel(txt, title="[bold]Event Stream[/bold]", border_style="dim")

def main():
    engine = SimulationEngine(target_port=8080)
    engine.start()
    layout = build_layout()
    console = Console()

    try:
        with Live(layout, refresh_per_second=4, screen=True):
            step = 0
            while True:
                data = engine.snapshot()
                layout["header"].update(render_header(data))
                layout["nodes"].update(render_nodes(data))
                layout["telemetry"].update(render_telemetry(data))
                layout["logs"].update(render_logs(data))

                step += 1
                if step == 8:
                    engine.trigger_attack(rate_pps=5000)
                elif step == 26:
                    engine.toggle_syncookies(True)
                elif step == 46:
                    engine.toggle_iptables(True)
                elif step == 66:
                    engine.stop_attack()
                elif step == 80:
                    engine.defense.reset()
                    step = 0

                time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    finally:
        engine.stop()
        console.print("[bold green]Monitor exited. Cleaned up.[/bold green]")

if __name__ == "__main__":
    main()
