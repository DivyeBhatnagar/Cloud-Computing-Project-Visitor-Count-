#!/usr/bin/env bash
set -euo pipefail
mkdir -p evidence
{
  uname -sm
  python3 --version
  git --version
  docker version
  docker compose version
  minikube version
  kubectl version --client
} | tee evidence/versions.log
docker compose up -d --build --wait 2>&1 | tee evidence/compose.log
{
  docker compose ps
  docker image inspect visitor-counter:local --format '{{.Architecture}} {{.Size}}'
  python3 scripts/smoke.py http://127.0.0.1:8080
  docker compose exec -T redis redis-cli GET visitor-count
} | tee evidence/compose-smoke.log
bash scripts/test-local.sh 2>&1 | tee evidence/python-tests.log
