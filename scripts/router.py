"""Loopback-only, primary-first router for the local hybrid simulation."""
import argparse
import logging
from http.client import HTTPException
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from urllib.error import HTTPError
from urllib.request import urlopen


def make_handler(primary, backup):
    lock = Lock()
    active = None

    class Router(BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal active
            for name, upstream in (("primary", primary), ("backup", backup)):
                try:
                    with urlopen(upstream + "/readyz", timeout=1) as probe:
                        if probe.status != 200:
                            continue
                except HTTPError as error:
                    error.close()
                    continue
                except (OSError, HTTPException):
                    continue

                with lock:
                    if active != name:
                        logging.info("route %s -> %s", active, name)
                        active = name

                # Forward exactly once. A timeout can occur after Redis commits INCR.
                try:
                    try:
                        response = urlopen(upstream + self.path, timeout=3)
                    except HTTPError as error:
                        response = error
                    with response:
                        payload = response.read()
                        status = response.code
                        headers = response.headers
                except (OSError, HTTPException):
                    self.send_error(502, "Upstream request failed; refresh to retry")
                    return

                self.send_response(status)
                for header in ("Content-Type", "Cache-Control", "X-Cluster-ID"):
                    if header in headers:
                        self.send_header(header, headers[header])
                self.send_header("X-Route", name)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            with lock:
                if active is not None:
                    logging.warning("route %s -> unavailable", active)
                    active = None
            self.send_error(503, "Neither cluster is ready")

    return Router


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8088)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    handler = make_handler("http://127.0.0.1:18081", "http://127.0.0.1:18082")
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
        logging.info("Local hybrid simulation listening on port %s", args.port)
        server.serve_forever()
