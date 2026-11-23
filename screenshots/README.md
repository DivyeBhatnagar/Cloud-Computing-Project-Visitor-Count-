# Screenshot checklist

All published evidence carries the attribution **Divye Bhatnagar**. Browser evidence is presented inside a clearly labeled attribution frame, and command captures show the name above the recorded output. Original browser captures are retained locally in the ignored `screenshots/originals/` directory. The framing identifies the author while preserving the captured evidence.

Capture these on the project laptop during the [demonstration](../docs/demo.md). Use Shift–Command–4 on macOS or Win–Shift–S on Windows. Save PNGs with the listed prefixes. Crop to the app or terminal and remove account credentials, tokens, notifications and unrelated windows. Retain the commands and their genuine output. Capture screenshots during scaling and failover before the state changes.

| File prefix | What to show | Command or action |
| --- | --- | --- |
| 01-versions | Installed versions and Docker engine | `python3 --version; git --version; docker version; docker compose version; minikube version; kubectl version --client` |
| 02-flask | Counter page | Open `http://127.0.0.1:8080` |
| 03-increment | Two increasing counts | `python3 scripts/smoke.py http://127.0.0.1:8080` |
| 04-build | Successful image build | `docker build --progress=plain -t visitor-counter:local .` |
| 05-containers | Two healthy containers | `docker compose ps` |
| 06-compose | Compose startup output | `docker compose up -d --build --wait` |
| 07-minikube | Primary control plane running | `minikube status -p vc-primary` |
| 08-services | Deployments, Services and PVC | `kubectl --context vc-primary get deploy,sts,svc,pvc` |
| 09-pods | Ready Flask and Redis pods | `kubectl --context vc-primary get pods -o wide` |
| 10a-before and 10b-after | Old pod name and new ready pod | `kubectl --context vc-primary get pods -l app=visitor`; then `bash scripts/self-heal.sh vc-primary` |
| 11-metrics | Metrics-server and measured CPU | `kubectl --context vc-primary -n kube-system get deploy metrics-server`; `kubectl --context vc-primary top pod` |
| 12-hpa-initial | CPU target and one initial replica | `kubectl --context vc-primary get hpa` |
| 13-load | Active/completed load Job | `bash scripts/hpa-load.sh` |
| 14-scale-up | CPU and multiple ready web pods | `kubectl --context vc-primary get hpa,deploy,pods` |
| 15-scale-down | One replica again | `kubectl --context vc-primary get hpa,deploy,pods` after load |
| 16-profiles | Both profiles and contexts | `minikube profile list`; `kubectl config get-contexts` |
| 17-primary | Primary badge and route | Open `http://127.0.0.1:8088`; `python3 scripts/smoke.py http://127.0.0.1:8088 --route primary` |
| 18-primary-stopped | Primary failure | `minikube stop -p vc-primary`; `minikube status -p vc-primary` |
| 19-backup | Backup badge and route | Refresh the router URL and run `python3 scripts/smoke.py http://127.0.0.1:8088 --route backup` |
| 20-recovery | Router transitions and restored primary | `minikube start -p vc-primary`; rerun primary smoke test and capture the router terminal |
| 21-baseline | Three pods, baseline requests, CPU/memory samples and full image | Run `bash scripts/benchmark.sh` and capture its before samples; `docker image inspect visitor-counter:baseline --format '{{.Size}}'` |
| 22-optimized | One pod, reduced requests, CPU/memory samples and slim image | Capture after samples and table; `docker image inspect visitor-counter:local --format '{{.Size}}'` |
| 23-github | Public repository and files | Open the verified GitHub URL in a private browser window while signed out |

For fleeting states, replay the appropriate authentic local log with its timestamps visible, or rerun the demonstration. Add each captured PNG to the report with a caption identifying the state and outcome.

The Compose and routed app PNGs are actual browser captures. The numbered command-output PNGs show excerpts from the original laptop logs in a browser document. See [raw logs](../evidence). To reproduce browser capture on macOS with Chrome installed, use `bash scripts/capture-browser.sh compose` and `python3 scripts/capture-evidence.py` after recording the demonstration. The public GitHub screenshot requires a verified public repository.
