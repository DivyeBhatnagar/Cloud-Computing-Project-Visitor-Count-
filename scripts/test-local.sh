#!/usr/bin/env bash
set -euo pipefail
tmp=$(mktemp -d)
redis-server --port 0 --unixsocket "$tmp/redis.sock" --save '' --appendonly no --dir "$tmp" > "$tmp/redis.log" 2>&1 &
pid=$!
trap 'kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; rm -rf "$tmp"' EXIT
for attempt in {1..30}; do
  if redis-cli -s "$tmp/redis.sock" ping >/dev/null 2>&1; then
    TEST_REDIS_URL="unix://$tmp/redis.sock" .venv/bin/python -m unittest discover -s tests -v
    exit
  fi
  sleep 0.2
done
cat "$tmp/redis.log" >&2
exit 1
