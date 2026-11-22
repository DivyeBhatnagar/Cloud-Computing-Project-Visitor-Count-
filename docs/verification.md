# Final project verification

Practical implementation and validation took place on the project laptop on 22 November 2026. COMPLETE means a deliverable exists or the practical result was observed on this laptop. INCOMPLETE means a required deliverable is still missing. NOT VERIFIED means evidence is still required.

| Requirement | Status | Evidence |
| --- | --- | --- |
| Laptop OS, CPU, RAM, disk and tool versions checked | COMPLETE | [Setup guide](setup.md), [versions log](../evidence/versions.log) |
| Docker Desktop, Compose, Minikube and kubectl installed and working | COMPLETE | [Versions log](../evidence/versions.log), [cluster log](../evidence/clusters.log) |
| Free software and local-only simulation | COMPLETE | [Setup guide](setup.md), [report](../report/project-report.md) |
| A. Flask and Redis containerization | COMPLETE | [Compose log](../evidence/compose.log) |
| Flask, Redis and increasing counter | COMPLETE | [Compose HTTP and Redis assertions](../evidence/compose-smoke.log), [six Python tests](../evidence/python-tests.log) |
| B. Kubernetes Deployment, Services, probes and PVC | COMPLETE | [Cluster resources](../evidence/clusters.log) |
| Kubernetes self-healing | COMPLETE | [Old and replacement pods](../evidence/self-healing.log) |
| C. CPU metrics and HPA scale-up | COMPLETE | [HPA upscale](../evidence/hpa-up.log), [load output](../evidence/load.log) |
| HPA scale-down | COMPLETE | [Return to one ready replica](../evidence/hpa-down.log) |
| D. Two-cluster failover and failback | COMPLETE | [HTTP results and profile stop](../evidence/failover.log), [router transitions](../evidence/router.log) |
| Independent Redis state and failover limitations documented | COMPLETE | [Runbook](demo.md) |
| E. Three measured before-and-after techniques | COMPLETE | [Benchmark log](../evidence/benchmark.log) |
| CSV and comparison table | COMPLETE | [CSV](../cost-analysis/comparison.csv), [table](../cost-analysis/comparison.md) |
| Architecture diagram and Mermaid source | COMPLETE | [SVG](../architecture/visitor-counter.svg), [Mermaid](../architecture/visitor-counter.mmd) |
| Laptop screenshots for deployment, scaling, failover and measurements | COMPLETE | [Browser captures and recorded terminal excerpts](../screenshots/) |
| Public GitHub screenshot | COMPLETE | [Signed-out public repository capture](../screenshots/23-github.png) |
| Markdown report, DOCX and PDF with laptop results | COMPLETE | [Public Markdown](../report/public-report.md), private college exports under `report/` |
| Local Git repository and publishing instructions | COMPLETE | `main` initialized, [publication guide](github.md) |
| Public repository and uploaded files | COMPLETE | [Public repository](https://github.com/DivyeBhatnagar/Cloud-Computing-Project-Visitor-Count-) with `main` as its default branch |
| Verified public URL on the cover or link file | COMPLETE | [Repository link](../github_link.txt) and public report cover |
| GitHub Code → Download ZIP | INCOMPLETE | Pending publication |
