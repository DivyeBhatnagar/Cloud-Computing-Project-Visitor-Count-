#!/usr/bin/env bash
set -euo pipefail
url=http://127.0.0.1:8088
capture() {
  if [[ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]]; then
    bash scripts/capture-browser.sh "$1" || echo "Browser screenshot unavailable" >&2
  fi
}
python3 scripts/smoke.py "$url" --route primary
capture primary
minikube stop -p vc-primary
minikube status -p vc-primary || true
python3 scripts/smoke.py "$url" --route backup
capture backup
minikube start -p vc-primary
kubectl --context vc-primary rollout status statefulset/redis --timeout=180s
kubectl --context vc-primary rollout status deployment/visitor --timeout=180s
for attempt in {1..30}; do
  if python3 scripts/smoke.py "$url" --route primary; then exit 0; fi
  sleep 2
done
exit 1
