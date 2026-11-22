# Test outcomes

| Check | Result | Method |
| --- | --- | --- |
| Flask increment, health, readiness, Redis outage and opt-in load endpoint | PASSED | Four Flask test-client tests |
| Shared count between two Flask app instances | PASSED | Temporary live Redis server and atomic increment assertions |
| Router preference, failover, failback and total outage | PASSED | Loopback HTTP backend fixtures |
| Initial sandboxed socket test attempt | FAILED | Local sockets were blocked by sandbox permissions. The subsequent authorized run passed all six tests. |
| Live Redis test in a plain unittest run without a test Redis URL | SKIPPED by design | `bash scripts/test-local.sh` sets the URL and exercises the integration test |
| Compose containers, HTTP readiness and count | PASSED | `docker compose up -d --build --wait`, `docker compose ps` and `scripts/smoke.py` |
| Kubernetes API validation and live workload readiness | PASSED | `kubectl apply --dry-run=server`, rollout status, pods and PVCs |
| Kubernetes self-healing | PASSED | Delete the single web pod and wait for its distinct replacement |
| HPA load and scaling | PASSED | Load Job recorded 4,864 successful HTTP requests and seven failed requests. Ready replicas changed 1 → 5 → 1. |
| Live primary outage, backup availability and primary recovery | PASSED | Stop the primary Minikube profile, require HTTP 200 and backup route header, restart and verify return to the primary |
| Three optimization measurements and comparison generation | PASSED | Pod specs, replica counts, metrics-server snapshots and .Size from Docker image inspect |
| Windows/WSL verification | NOT RUN | Setup instructions provided. Practical validation used macOS ARM64. |
| Standalone Docker workflow | NOT RUN | Commands provided. The complete container deployment was tested through Compose. |
| Public GitHub and downloaded ZIP | NOT RUN | Requires a valid authenticated GitHub session and public publication. |

Recorded output is under [evidence](../evidence). Re-run the local suite with `bash scripts/test-local.sh` and the complete cluster exercise with `bash scripts/validate-clusters.sh` after deploying both profiles and building both image variants.
