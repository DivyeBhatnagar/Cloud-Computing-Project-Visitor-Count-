"""Assert HTTP readiness, two consecutive counter increments and optional routing."""
import argparse
import re
from urllib.request import urlopen


def check(url, route=None):
    with urlopen(url + "/readyz", timeout=5) as response:
        if response.status != 200:
            raise RuntimeError("Readiness probe failed")
    counts = []
    for _ in range(2):
        with urlopen(url + "/", timeout=5) as response:
            if route and response.headers.get("X-Route") != route:
                raise RuntimeError(f"Expected route {route}, got {response.headers.get('X-Route')}")
            page = response.read().decode()
            match = re.search(r'class="count">([\d,]+)<', page)
            if not match:
                raise RuntimeError("Visitor count missing")
            counts.append(int(match[1].replace(",", "")))
            print(f"HTTP {response.status} | {response.headers.get('X-Cluster-ID')} | {response.headers.get('X-Route', 'direct')} | count {counts[-1]}")
    if counts[1] != counts[0] + 1:
        raise RuntimeError(f"Expected one increment in an isolated run, got {counts}")
    print("PASSED readiness and counter increments")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--route", choices=["primary", "backup"])
    args = parser.parse_args()
    check(args.url.rstrip("/"), args.route)
