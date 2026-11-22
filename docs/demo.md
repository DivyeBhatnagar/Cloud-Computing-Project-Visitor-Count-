# Demonstration runbook

Run these commands from the repository root. Use separate terminals for interactive port-forwards, watches and the router.

## A. Docker

```bash
docker build -t visitor-counter:local .
docker compose config
docker compose up -d --build --wait
docker compose ps
docker ps --filter ancestor=visitor-counter:local
docker image inspect visitor-counter:local --format '{{.Architecture}} {{.Size}}'
docker compose logs --tail 20 web redis
python3 scripts/smoke.py http://127.0.0.1:8080
docker compose exec redis redis-cli GET visitor-count
```

The smoke test expects HTTP 200, a visible cluster label and two consecutive counts. Close other browser tabs while running it. Compose wires the full stack and publishes port 8080 on loopback. Use `docker compose down` to stop both services and retain Redis data.

To demonstrate the equivalent standalone workflow on an isolated network:

```bash
docker network create vc-demo-net
docker volume create vc-demo-redis-data
docker run -d --name vc-demo-redis --network vc-demo-net -v vc-demo-redis-data:/data redis:7.4-alpine redis-server --appendonly yes
docker run -d --name vc-demo-web --network vc-demo-net -e REDIS_URL=redis://vc-demo-redis:6379/0 -e CLUSTER_ID=Standalone -p 127.0.0.1:8081:8000 visitor-counter:local
docker inspect vc-demo-web --format '{{.State.Health.Status}}'
docker logs vc-demo-web
python3 scripts/smoke.py http://127.0.0.1:8081
docker stop vc-demo-web vc-demo-redis
docker rm vc-demo-web vc-demo-redis
docker network rm vc-demo-net
```

Wait for a healthy status before running the smoke test. The named demo volume remains available for another run.

## B. Minikube and self-healing

```bash
minikube start -p vc-primary --driver=docker --cpus=2 --memory=2560 --kubernetes-version=v1.37.0
minikube status -p vc-primary
bash scripts/deploy.sh vc-primary
kubectl --context vc-primary get deployments,statefulsets,services,pvc
kubectl --context vc-primary get pods -o wide
```

In a separate terminal run `bash scripts/forward.sh vc-primary`. Open [the primary app](http://127.0.0.1:18081). From the original terminal run:

```bash
python3 scripts/smoke.py http://127.0.0.1:18081
kubectl --context vc-primary get pods -l app=visitor
bash scripts/self-heal.sh vc-primary
python3 scripts/smoke.py http://127.0.0.1:18081
```

Run self-healing before enabling HPA so exactly one Flask pod is replaced. The retrying forward command reconnects after a replacement. If an immediate smoke test fails, wait for the forward terminal to show `Forwarding from` and rerun it. To change image names or tags, update `kustomization.yaml` and load the same image into each profile before applying. When replacing the contents of an existing tag, explicitly restart the Deployment with `kubectl --context vc-primary rollout restart deploy/visitor`.

## C. HPA

```bash
minikube addons enable metrics-server -p vc-primary
kubectl --context vc-primary -n kube-system rollout status deploy/metrics-server --timeout=180s
kubectl --context vc-primary top pod
kubectl --context vc-primary set env deploy/visitor ENABLE_LOAD_TEST=1
kubectl --context vc-primary rollout status deploy/visitor
kubectl --context vc-primary apply -f hpa.yaml
kubectl --context vc-primary get hpa
```

Run `kubectl --context vc-primary get hpa -w` in one terminal and `bash scripts/hpa-load.sh` in another. The Job calls the visitor Service, which can distribute connections across Flask replicas. Capture `kubectl --context vc-primary top pod` and `kubectl --context vc-primary get deploy visitor` while load is running. Observe the deployment return to one ready pod after the Job finishes and the 60-second scale-down stabilization window and control-loop delays elapse. Remove the demo endpoint after capturing evidence.

```bash
kubectl --context vc-primary describe hpa visitor
kubectl --context vc-primary set env deploy/visitor ENABLE_LOAD_TEST-
kubectl --context vc-primary rollout status deploy/visitor
```

If CPU shows unknown, wait for several samples and check `kubectl --context vc-primary get apiservice v1beta1.metrics.k8s.io`, `kubectl --context vc-primary -n kube-system logs deploy/metrics-server` and `kubectl --context vc-primary describe hpa visitor`. CPU utilization uses the requested CPU per pod as the denominator. If load is insufficient, increase the Job worker count or duration and record the adjustment.

## D. Local hybrid cloud simulation

```bash
minikube start -p vc-backup --driver=docker --cpus=2 --memory=2560 --kubernetes-version=v1.37.0
bash scripts/deploy.sh vc-backup
minikube profile list
kubectl config get-contexts
```

Leave the primary forward terminal running. Start `bash scripts/forward.sh vc-backup` and `python3 scripts/router.py` in two more terminals. Open [the router](http://127.0.0.1:8088). Run one line at a time so you can capture the primary, stopped profile, backup and recovered primary states.

```bash
python3 scripts/smoke.py http://127.0.0.1:8088 --route primary
minikube stop -p vc-primary
minikube status -p vc-primary
python3 scripts/smoke.py http://127.0.0.1:8088 --route backup
minikube start -p vc-primary
kubectl --context vc-primary rollout status deploy/visitor --timeout=180s
python3 scripts/smoke.py http://127.0.0.1:8088 --route primary
```

Or run `bash scripts/demo-failover.sh` with both forwards and router already active. The router checks readiness for each request and returns to the primary when it is ready. A request already sent to the primary can fail during the transition. The router avoids replaying a request whose increment may already have committed. Each cluster persists its own Redis counter using a PVC and AOF. Backup visits increment only its counter. Failback can display a different count. The router, Docker Desktop and laptop remain common failure points.

## E. Optimization and cleanup

Use the [cost experiment](../cost-analysis/README.md). Stop router, watches and port-forwards with Ctrl+C. Preserve evidence and data with `minikube stop -p vc-primary`, `minikube stop -p vc-backup` and `docker compose down`. To discard project cluster data after submission, explicitly delete each project profile with `minikube delete -p vc-primary` and `minikube delete -p vc-backup`. For Compose, `docker compose down -v` discards its counter volume.
