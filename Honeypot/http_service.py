# http_service.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

import config
import logger

INDEX_HTML = """<!DOCTYPE html>
<html>
  <head><title>Embedded Device</title></head>
  <body>
    <h1>Embedded Device Web Interface</h1>
    <p>For administration, visit <a href="/admin/login">/admin/login</a>.</p>
  </body>
</html>
"""

ADMIN_LOGIN_HTML = """<!DOCTYPE html>
<html>
  <head><title>Admin Login</title></head>
  <body>
    <h1>Admin Login</h1>
    <form method="POST" action="/admin/login">
      <label>Username: <input name="username" type="text" /></label><br/>
      <label>Password: <input name="password" type="password" /></label><br/>
      <input type="submit" value="Login" />
    </form>
    <p>Hint: default credentials have been changed.</p>
  </body>
</html>
"""


class HoneypotHTTPRequestHandler(BaseHTTPRequestHandler):
    # Disable built-in console logging
    def log_message(self, format, *args):
        return

    def _log_http_event(self, event_type, extra=None, body=None):
        if extra is None:
            extra = {}

        src_ip, src_port = self.client_address
        base = {
            "service": "http",
            "src_ip": src_ip,
            "src_port": src_port,
            "dst_port": config.HTTP_PORT,
            "method": getattr(self, "command", None),
            "path": getattr(self, "path", None),
        }
        base.update(extra)

        if body is not None:
            base["body"] = body

        logger.log_event(event_type, **base)

    def do_GET(self):
        self._log_http_event("http_request", extra={
            "headers": dict(self.headers),
        })

        if self.path.startswith("/admin"):
            body = ADMIN_LOGIN_HTML.encode()
        else:
            body = INDEX_HTML.encode()

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        body_bytes = self.rfile.read(length) if length > 0 else b""
        body_text = body_bytes.decode(errors="replace")

        self._log_http_event(
            "http_post",
            extra={"headers": dict(self.headers)},
            body=body_text,
        )

        # Always "fail" the login
        resp = b"<!DOCTYPE html><html><body><h1>Login failed</h1></body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)


def run_http_service():
    """
    Run HTTP server that uses HoneypotHTTPRequestHandler.
    """
    server = HTTPServer((config.BIND_ADDR, config.HTTP_PORT), HoneypotHTTPRequestHandler)

    logger.log_event(
        "service_started",
        service="http",
        port=config.HTTP_PORT,
        bind_addr=config.BIND_ADDR,
    )

    print(f"[http] listening on {config.BIND_ADDR}:{config.HTTP_PORT}")

    # Run in current thread (we'll wrap it in a thread from run_honeypot.py)
    server.serve_forever()

