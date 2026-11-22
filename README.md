# Visitor Counter on Docker and Kubernetes

A Flask page counts each visit using Redis `INCR`. Docker Compose runs the app and database. Two local Minikube profiles demonstrate Kubernetes recovery, CPU autoscaling and application failover.

- [Laptop setup and troubleshooting](docs/setup.md)
- [Demonstration runbook](docs/demo.md)
- [Architecture diagram](architecture/visitor-counter.svg) and [Mermaid source](architecture/visitor-counter.mmd)
- [Cost experiment](cost-analysis/README.md)
- [Screenshot checklist](screenshots/README.md)
- [Public project report](report/public-report.md)
- [Test outcomes](docs/testing.md)
- [Verification checklist](docs/verification.md)
- [GitHub publication and ZIP](docs/github.md)

## Quick start

```bash
docker compose up -d --build --wait
python3 scripts/smoke.py http://127.0.0.1:8080
```

Open [the Compose app](http://127.0.0.1:8080) and refresh it to observe the next count.

| Setting | Default | Purpose |
| --- | --- | --- |
| `REDIS_URL` | `redis://127.0.0.1:6379/0` | Redis connection |
| `COUNTER_KEY` | `visitor-count` | Redis key shared within a deployment |
| `CLUSTER_ID` | `Local` | Page label and response header |
| `ENABLE_LOAD_TEST` | Disabled | Set to `1` on the primary during the HPA demonstration |

`/healthz` checks the Flask process. `/readyz` also checks Redis. Both are read-only.

## Local Python tests

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
bash scripts/test-local.sh
```

The last command uses a temporary Redis instance and enables the live Redis test. The router test requires local TCP binds. Follow the demonstration runbook for Compose and Kubernetes validation.
