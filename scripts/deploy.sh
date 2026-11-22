#!/usr/bin/env bash
set -euo pipefail
case "${1:-}" in
  vc-primary) name="Primary private cloud" ;;
  vc-backup) name="Backup simulated public cloud" ;;
  *) echo "Usage: bash scripts/deploy.sh vc-primary|vc-backup" >&2; exit 2 ;;
esac
minikube -p "$1" image load visitor-counter:local --overwrite=true
kubectl --context "$1" apply -k .
kubectl --context "$1" set env deployment/visitor CLUSTER_ID="$name"
kubectl --context "$1" rollout status statefulset/redis --timeout=180s
kubectl --context "$1" rollout status deployment/visitor --timeout=180s
kubectl --context "$1" get deploy,sts,svc,pods,pvc
