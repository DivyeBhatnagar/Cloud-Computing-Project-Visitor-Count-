#!/usr/bin/env bash
set -euo pipefail
context=vc-primary
name="visitor-load-$(date +%s)"
kubectl --context "$context" create configmap visitor-load --from-file=scripts/load.py --dry-run=client -o yaml | kubectl --context "$context" apply -f -
kubectl --context "$context" create -f - <<YAML
apiVersion: batch/v1
kind: Job
metadata:
  name: $name
spec:
  ttlSecondsAfterFinished: 900
  backoffLimit: 0
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: load
          image: visitor-counter:local
          imagePullPolicy: Never
          command: ["python", "/load/load.py", "--target", "service", "--seconds", "150", "--workers", "12"]
          volumeMounts:
            - name: script
              mountPath: /load
      volumes:
        - name: script
          configMap:
            name: visitor-load
YAML
kubectl --context "$context" logs -f "job/$name" --pod-running-timeout=90s
kubectl --context "$context" wait "job/$name" --for=condition=complete --timeout=30s
