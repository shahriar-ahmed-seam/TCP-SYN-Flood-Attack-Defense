from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json
import os
import urllib.parse

class APIHandler(SimpleHTTPRequestHandler):
    engine = None
    static_dir = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=self.static_dir, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/status":
            self._json(self.engine.snapshot())
            return
        elif parsed.path in ["", "/"]:
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"

        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            payload = {}

        path = parsed.path
        if path == "/api/attack/start":
            rate = int(payload.get("rate_pps", 5000))
            self.engine.trigger_attack(rate_pps=rate)
            self._json({"ok": True})
        elif path == "/api/attack/stop":
            self.engine.stop_attack()
            self._json({"ok": True})
        elif path == "/api/defense/syncookies":
            val = self.engine.toggle_syncookies(bool(payload.get("enable", True)))
            self._json({"ok": True, "syncookies": val})
        elif path == "/api/defense/iptables":
            val = self.engine.toggle_iptables(bool(payload.get("enable", True)))
            self._json({"ok": True, "iptables": val})
        elif path == "/api/config/backlog":
            size = int(payload.get("size", 16))
            self.engine.set_backlog(size)
            self._json({"ok": True, "backlog": size})
        else:
            self.send_response(404)
            self.end_headers()

    def _json(self, data):
        buf = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(buf)))
        self.send_header("Cache-Control", "no-cache, no-store")
        self.end_headers()
        self.wfile.write(buf)

    def log_message(self, format, *args):
        return

def create_server(engine, host="0.0.0.0", port=5000):
    static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
    APIHandler.engine = engine
    APIHandler.static_dir = static_path
    return ThreadingHTTPServer((host, port), APIHandler)
