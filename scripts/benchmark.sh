#!/usr/bin/env bash
set -euo pipefail
k=(kubectl --context vc-primary)
wait_metrics() {
  for attempt in {1..30}; do
    if "${k[@]}" top pod -l app=visitor >/dev/null 2>&1; then return; fi
    sleep 5
  done
  echo "Metrics unavailable" >&2
  return 1
}

"${k[@]}" delete hpa visitor --ignore-not-found
"${k[@]}" set resources deploy/visitor -c web --requests=cpu=250m,memory=128Mi
"${k[@]}" scale deploy/visitor --replicas=3
"${k[@]}" rollout status deploy/visitor --timeout=180s
wait_metrics
sleep 30
python3 scripts/measure.py before

"${k[@]}" set resources deploy/visitor -c web --requests=cpu=100m,memory=64Mi
"${k[@]}" apply -f hpa.yaml
for attempt in {1..45}; do
  if [[ $("${k[@]}" get deploy visitor -o jsonpath='{.status.replicas} {.status.readyReplicas}') == "1 1" ]]; then break; fi
  sleep 5
done
"${k[@]}" rollout status deploy/visitor --timeout=180s
sleep 30
python3 scripts/measure.py after
python3 scripts/measure.py compare
