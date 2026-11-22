import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

from scripts.router import make_handler


class Backend(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200 if self.server.ready else 503)
        self.send_header("X-Cluster-ID", self.server.cluster)
        self.end_headers()

    def log_message(self, *args):
        pass


class RouterTests(unittest.TestCase):
    def launch(self, handler):
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        task = threading.Thread(target=server.serve_forever, daemon=True)
        task.start()
        self.addCleanup(server.server_close)
        self.addCleanup(task.join)
        self.addCleanup(server.shutdown)
        return server, f"http://127.0.0.1:{server.server_port}"

    def test_primary_backup_recovery_and_total_outage(self):
        primary, p_url = self.launch(Backend)
        backup, b_url = self.launch(Backend)
        primary.cluster, backup.cluster = "private", "public-simulated"
        _, url = self.launch(make_handler(p_url, b_url))
        for state, fallback, route, cluster in [
            (True, True, "primary", "private"),
            (False, True, "backup", "public-simulated"),
            (True, True, "primary", "private"),
        ]:
            primary.ready, backup.ready = state, fallback
            with urlopen(url, timeout=5) as result:
                self.assertEqual(result.headers["X-Route"], route)
                self.assertEqual(result.headers["X-Cluster-ID"], cluster)
        primary.ready = backup.ready = False
        with self.assertRaises(HTTPError) as result:
            urlopen(url, timeout=5)
        self.assertEqual(result.exception.code, 503)
        result.exception.close()
