import sys
import webbrowser
from core.engine import SimulationEngine
from server.api import create_server

def main():
    target_port = 8080
    web_port = 5000

    print(f"[*] Initializing testbed on port {target_port}...")
    engine = SimulationEngine(target_port=target_port)
    engine.start()

    server = create_server(engine, host="0.0.0.0", port=web_port)
    print(f"[+] Web console active: http://localhost:{web_port}")

    try:
        webbrowser.open(f"http://localhost:{web_port}")
    except Exception:
        pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
    finally:
        engine.stop()
        server.shutdown()
        server.server_close()
        print("[+] Cleanup complete.")

if __name__ == "__main__":
    main()
