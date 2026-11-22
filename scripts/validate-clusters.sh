#!/usr/bin/env bash
set -euo pipefail
mkdir -p evidence
k=(kubectl --context vc-primary)
children=()
trap 'for pid in "${children[@]}"; do kill "$pid" 2>/dev/null || true; done' EXIT
collect() {
  minikube profile list
  for profile in vc-primary vc-backup; do
    kubectl --context "$profile" get nodes,deploy,sts,svc,pods,pvc
  done
}
collect | tee evidence/clusters.log
"${k[@]}" apply --dry-run=server -k .
"${k[@]}" apply --dry-run=server -f hpa.yaml
bash scripts/self-heal.sh vc-primary | tee evidence/self-healing.log

"${k[@]}" -n kube-system rollout status deploy/metrics-server --timeout=180s
"${k[@]}" set env deploy/visitor ENABLE_LOAD_TEST=1
"${k[@]}" rollout status deploy/visitor --timeout=180s
"${k[@]}" apply -f hpa.yaml

observe() {
  local minimum=$1
  local maximum=$2
  for attempt in {1..60}; do
    date
    "${k[@]}" get hpa
    "${k[@]}" top pod -l app=visitor || true
    "${k[@]}" get deploy visitor
    local ready
    ready=$("${k[@]}" get deploy visitor -o jsonpath='{.status.readyReplicas}')
    if [[ ${ready:-0} -ge "$minimum" && ${ready:-0} -le "$maximum" ]]; then return; fi
    sleep 5
  done
  return 1
}
bash scripts/hpa-load.sh > evidence/load.log 2>&1 &
children+=("$!")
observe 2 5 | tee evidence/hpa-up.log
wait "${children[0]}"
children=()
observe 1 1 | tee evidence/hpa-down.log
"${k[@]}" set env deploy/visitor ENABLE_LOAD_TEST-
"${k[@]}" rollout status deploy/visitor --timeout=180s

bash scripts/benchmark.sh | tee evidence/benchmark.log

bash scripts/forward.sh vc-primary > evidence/primary-forward.log 2>&1 &
children+=("$!")
bash scripts/forward.sh vc-backup > evidence/backup-forward.log 2>&1 &
children+=("$!")
python3 scripts/router.py > evidence/router.log 2>&1 &
children+=("$!")
for port in 18081 18082; do
  for attempt in {1..30}; do
    if curl -fsS "http://127.0.0.1:$port/readyz"; then break; fi
    sleep 2
  done
  curl -fsS "http://127.0.0.1:$port/readyz"
done
bash scripts/demo-failover.sh | tee evidence/failover.log
