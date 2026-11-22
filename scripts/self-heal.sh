#!/usr/bin/env bash
set -euo pipefail
context="${1:-vc-primary}"
pod=$(kubectl --context "$context" get pods -l app=visitor --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')
kubectl --context "$context" wait "pod/$pod" --for=condition=Ready --timeout=90s
kubectl --context "$context" get pods -l app=visitor
kubectl --context "$context" delete "pod/$pod"
for attempt in {1..45}; do
  replacement=$(kubectl --context "$context" get pods -l app=visitor --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
  if [[ -n "$replacement" && "$replacement" != "$pod" ]]; then
    kubectl --context "$context" wait "pod/$replacement" --for=condition=Ready --timeout=90s
    kubectl --context "$context" get pods -l app=visitor
    printf 'PASSED self-healing: %s -> %s\n' "$pod" "$replacement"
    exit 0
  fi
  sleep 2
done
echo "FAILED: no replacement pod became Running" >&2
exit 1
