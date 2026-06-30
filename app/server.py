import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STARTED = time.time()
REQUESTS = {}


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type="application/json"):
        REQUESTS[(self.command, self.path, status)] = REQUESTS.get((self.command, self.path, status), 0) + 1
        payload = body if isinstance(body, bytes) else body.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/":
            self._send(200, json.dumps({
                "service": "release-radar",
                "version": os.getenv("APP_VERSION", "dev"),
                "environment": os.getenv("ENVIRONMENT", "local"),
                "message": "Ship confidently. Observe everything."
            }))
        elif self.path == "/health/live":
            self._send(200, '{"status":"alive"}')
        elif self.path == "/health/ready":
            self._send(200, '{"status":"ready"}')
        elif self.path == "/metrics":
            lines = [
                "# HELP release_radar_uptime_seconds Process uptime.",
                "# TYPE release_radar_uptime_seconds gauge",
                f"release_radar_uptime_seconds {time.time() - STARTED:.3f}",
                "# HELP release_radar_http_requests_total HTTP requests.",
                "# TYPE release_radar_http_requests_total counter",
            ]
            for (method, path, status), count in REQUESTS.items():
                lines.append(f'release_radar_http_requests_total{{method="{method}",path="{path}",status="{status}"}} {count}')
            self._send(200, "\n".join(lines) + "\n", "text/plain; version=0.0.4")
        else:
            self._send(404, '{"error":"not found"}')

    def log_message(self, fmt, *args):
        print(json.dumps({"time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "message": fmt % args}))


def main():
    port = int(os.getenv("PORT", "8080"))
    print(json.dumps({"event": "startup", "port": port}))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
