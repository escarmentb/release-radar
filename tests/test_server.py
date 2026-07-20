import json
import os
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.server import Handler, REQUESTS, REQUESTS_LOCK, metric_path, prometheus_label


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_root(self):
        with urlopen(self.base + "/") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.load(response)["service"], "release-radar")

    def test_health_and_metrics(self):
        for path in ("/health/live", "/health/ready", "/metrics"):
            with urlopen(self.base + path) as response:
                self.assertEqual(response.status, 200)

    def test_metrics_normalize_query_strings(self):
        with REQUESTS_LOCK:
            REQUESTS.clear()

        for path in ("/missing?token=one", "/missing?token=two"):
            with self.assertRaises(HTTPError) as error:
                urlopen(self.base + path)
            self.assertEqual(error.exception.code, 404)

        with urlopen(self.base + "/metrics?format=prometheus") as response:
            body = response.read().decode()

        self.assertIn('path="/missing",status="404"} 2', body)
        self.assertNotIn("token=one", body)
        self.assertNotIn("token=two", body)

    def test_metric_helpers(self):
        self.assertEqual(metric_path("/metrics?tenant=abc"), "/metrics")
        self.assertEqual(prometheus_label('a"b\\c\n'), 'a\\"b\\\\c\\n')


if __name__ == "__main__":
    unittest.main()
