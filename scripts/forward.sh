#!/usr/bin/env bash
set -eu
case "${1:-}" in
  vc-primary) port=18081 ;;
  vc-backup) port=18082 ;;
  *) echo "Usage: bash scripts/forward.sh vc-primary|vc-backup" >&2; exit 2 ;;
esac
pid=
trap 'if [[ -n "$pid" ]]; then kill "$pid" 2>/dev/null || true; fi; exit 0' INT TERM
while true; do
  kubectl --context "$1" port-forward --address 127.0.0.1 svc/visitor "$port:80" &
  pid=$!
  wait "$pid" || true
  pid=
  sleep 2
done
