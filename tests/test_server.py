import json
import os
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import urlopen

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.server import Handler


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


if __name__ == "__main__":
    unittest.main()
