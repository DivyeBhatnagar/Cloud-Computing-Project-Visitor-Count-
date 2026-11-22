# Cost and resource optimization

Use the primary profile with metrics-server enabled. Stop traffic and browser refreshes for the full experiment. Keep the same node, Docker architecture, application dependencies, CPU and memory limits, and Redis configuration. The baseline deliberately uses common over-provisioned settings so the comparison can be reproduced.

```bash
docker build --provenance=false --build-arg PYTHON_IMAGE=python:3.12 -t visitor-counter:baseline .
docker build --provenance=false -t visitor-counter:local .
docker image inspect visitor-counter:baseline visitor-counter:local --format '{{.Architecture}} {{.Size}}'
bash scripts/benchmark.sh
```

Run the experiment before starting the failover demonstration or after primary recovery. The benchmark takes three snapshots per phase at 20-second intervals. It records each sample and compares medians. Metrics-server can report the same underlying sample on consecutive snapshots. Startup work can influence CPU after a rollout, so the idle usage figures describe this run's observation window. If metrics are missing for replacement pods, wait for `kubectl --context vc-primary top pod -l app=visitor` to list all ready pods and run the benchmark again.

| Technique | Baseline configuration | Optimized configuration | Measured metric |
| --- | --- | --- | --- |
| Right-size requests | 250m CPU and 128 MiB memory per Flask pod | 100m and 64 MiB | Requests read from live pod specs |
| Reduce idle replicas | Three fixed Flask replicas | HPA converges to one idle replica | Ready pod count, total requests and idle usage |
| Reduce image size | Full Python 3.12 base | Slim Python 3.12 base | Docker image inspect size in bytes |

The script generates `before-samples.csv`, `after-samples.csv`, `before.csv`, `after.csv`, `comparison.csv` and `comparison.md`. Change is after minus before, and percentage change divides that difference by before. The image comparison keeps the Dockerfile and app constant and varies the base. The baseline deployment keeps the same runnable slim app image so changing the base does not confound the pod comparison.

Requests reserve scheduling capacity. `kubectl top` samples observed CPU and memory usage, rounded by kubectl. Total idle usage reflects both pod changes together. Lower requests can reduce scheduling headroom and change HPA sensitivity. One idle replica means pod loss can briefly interrupt service. Slim images omit convenience tools. Image size measures local image metadata and may differ from compressed transfer size or physical space saved with shared layers. All results are local resource observations. No cloud billing was incurred or measured.
