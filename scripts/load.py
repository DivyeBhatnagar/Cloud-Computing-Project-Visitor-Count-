"""Generate bounded traffic against a loopback HPA demo endpoint."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from time import monotonic
from urllib.request import urlopen


def load(duration, workers, url):
    deadline = monotonic() + duration

    def worker():
        successes = failures = 0
        while monotonic() < deadline:
            try:
                with urlopen(url, timeout=4) as response:
                    if response.status != 204:
                        raise ValueError("Unexpected response")
                successes += 1
            except (OSError, ValueError):
                failures += 1
        return successes, failures

    print(f"Generating load for {duration}s with {workers} workers", flush=True)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda _: worker(), range(workers)))
    successes = sum(result[0] for result in results)
    failures = sum(result[1] for result in results)
    print(f"Successful requests: {successes}; failed requests: {failures}")
    return 0 if successes else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, default=180)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--target", choices=["forward", "service"], default="forward")
    args = parser.parse_args()
    if not (1 <= args.seconds <= 600 and 1 <= args.workers <= 32):
        parser.error("Use 1–600 seconds and 1–32 workers")
    host = "127.0.0.1:18081" if args.target == "forward" else "visitor"
    raise SystemExit(load(args.seconds, args.workers, f"http://{host}/demo-load"))
