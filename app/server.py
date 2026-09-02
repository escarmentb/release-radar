import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

STARTED = time.time()
REQUESTS = {}
REQUESTS_LOCK = threading.Lock()


def service_metadata():
    return {
        "service": "release-radar",
        "version": os.getenv("APP_VERSION", "dev"),
        "environment": os.getenv("ENVIRONMENT", "local"),
        "region": os.getenv("REGION", "local"),
        "commit": os.getenv("GIT_SHA", "unknown"),
    }


def metric_path(raw_path):
    parsed = urlsplit(raw_path)
    return parsed.path or "/"


def prometheus_label(value):
    return str(value).replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type="application/json", include_body=True):
        request_key = (self.command, metric_path(self.path), status)
        with REQUESTS_LOCK:
            REQUESTS[request_key] = REQUESTS.get(request_key, 0) + 1
        payload = body if isinstance(body, bytes) else body.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if include_body:
            self.wfile.write(payload)

    def do_GET(self):
        path = metric_path(self.path)
        if path == "/":
            metadata = service_metadata()
            self._send(200, json.dumps({
                **metadata,
                "message": "Ship confidently. Observe everything."
            }))
        elif path == "/version":
            self._send(200, json.dumps(service_metadata()))
        elif path == "/health/live":
            self._send(200, '{"status":"alive"}')
        elif path == "/health/ready":
            self._send(200, '{"status":"ready"}')
        elif path == "/metrics":
            lines = [
                "# HELP release_radar_uptime_seconds Process uptime.",
                "# TYPE release_radar_uptime_seconds gauge",
                f"release_radar_uptime_seconds {time.time() - STARTED:.3f}",
                "# HELP release_radar_build_info Release metadata.",
                "# TYPE release_radar_build_info gauge",
                "release_radar_build_info{"
                f'service="{prometheus_label(service_metadata()["service"])}",'
                f'version="{prometheus_label(service_metadata()["version"])}",'
                f'environment="{prometheus_label(service_metadata()["environment"])}",'
                f'region="{prometheus_label(service_metadata()["region"])}",'
                f'commit="{prometheus_label(service_metadata()["commit"])}"'
                "} 1",
                "# HELP release_radar_http_requests_total HTTP requests.",
                "# TYPE release_radar_http_requests_total counter",
            ]
            with REQUESTS_LOCK:
                requests = sorted(REQUESTS.items())
            for (method, path, status), count in requests:
                lines.append(
                    "release_radar_http_requests_total{"
                    f'method="{prometheus_label(method)}",'
                    f'path="{prometheus_label(path)}",'
                    f'status="{prometheus_label(status)}"'
                    f"}} {count}"
                )
            self._send(200, "\n".join(lines) + "\n", "text/plain; version=0.0.4")
        else:
            self._send(404, '{"error":"not found"}')

    def do_HEAD(self):
        path = metric_path(self.path)
        if path in {"/", "/version"}:
            self._send(200, "{}", include_body=False)
        elif path in {"/health/live", "/health/ready"}:
            self._send(200, '{"status":"ok"}', include_body=False)
        elif path == "/metrics":
            self._send(200, "", "text/plain; version=0.0.4", include_body=False)
        else:
            self._send(404, '{"error":"not found"}', include_body=False)

    def log_message(self, fmt, *args):
        print(json.dumps({"time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "message": fmt % args}))


def main():
    port = int(os.getenv("PORT", "8080"))
    print(json.dumps({"event": "startup", "port": port}))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
