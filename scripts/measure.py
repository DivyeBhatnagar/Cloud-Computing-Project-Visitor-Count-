"""Record Docker image sizes and three idle Kubernetes snapshots per phase."""
import argparse
import csv
import json
import re
import statistics
import subprocess
import time
from pathlib import Path

DIRECTORY = Path(__file__).resolve().parents[1] / "cost-analysis"
KUBE = ("kubectl", "--context", "vc-primary")


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def quantity(value, factors):
    number, suffix = re.fullmatch(r"(\d+(?:\.\d+)?)([a-zA-Z]*)", value).groups()
    return float(number) * factors[suffix]


def snapshot():
    pods = json.loads(run(*KUBE, "get", "pod", "-l", "app=visitor", "-o", "json"))["items"]
    rows = run(*KUBE, "top", "pod", "-l", "app=visitor", "--no-headers").splitlines()
    metrics = {row.split()[0]: row.split()[1:] for row in rows}
    names = {pod["metadata"]["name"] for pod in pods}
    if not names or names != metrics.keys() or any(
        pod["metadata"].get("deletionTimestamp") or not any(
            condition["type"] == "Ready" and condition["status"] == "True"
            for condition in pod["status"].get("conditions", [])
        ) for pod in pods
    ):
        raise RuntimeError("Wait for all visitor pods to be Ready and have metrics")
    cpu = {"": 1000, "m": 1, "u": 0.001, "n": 0.000001}
    mem = {"": 1 / 1048576, "Ki": 1 / 1024, "Mi": 1, "Gi": 1024}
    requests = [pod["spec"]["containers"][0]["resources"]["requests"] for pod in pods]
    return {
        "idle_replicas": len(pods),
        "cpu_request_m_per_pod": statistics.mean(quantity(row["cpu"], cpu) for row in requests),
        "memory_request_MiB_per_pod": statistics.mean(quantity(row["memory"], mem) for row in requests),
        "cpu_usage_m_total": sum(quantity(values[0], cpu) for values in metrics.values()),
        "memory_usage_MiB_total": sum(quantity(values[1], mem) for values in metrics.values()),
        "cpu_request_m_total": sum(quantity(row["cpu"], cpu) for row in requests),
        "memory_request_MiB_total": sum(quantity(row["memory"], mem) for row in requests),
    }


def write_csv(path, header, rows):
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def measure(phase):
    tag = {"before": "baseline", "after": "local"}[phase]
    size = int(run("docker", "image", "inspect", f"visitor-counter:{tag}", "--format", "{{.Size}}"))
    samples = []
    expected = 3 if phase == "before" else 1
    for index in range(3):
        sample = snapshot()
        if sample["idle_replicas"] != expected:
            raise RuntimeError(f"Expected {expected} idle replicas: {sample}")
        print(sample, flush=True)
        samples.append(sample)
        if index < 2:
            time.sleep(20)
    fields = list(samples[0])
    write_csv(DIRECTORY / f"{phase}-samples.csv", ["sample", *fields],
              [(index, *(sample[field] for field in fields)) for index, sample in enumerate(samples, 1)])
    values = {field: statistics.median(sample[field] for sample in samples) for field in fields}
    values["image_bytes"] = size
    write_csv(DIRECTORY / f"{phase}.csv", ["metric", "value"], values.items())
    print(f"Image size: {size} bytes")


def compare():
    data = []
    for phase in ("before", "after"):
        with (DIRECTORY / f"{phase}.csv").open(newline="") as handle:
            data.append({row["metric"]: float(row["value"]) for row in csv.DictReader(handle)})
    rows = []
    for metric, before in data[0].items():
        after = data[1][metric]
        change = (after - before) / before * 100 if before else None
        rows.append((metric, f"{before:.15g}", f"{after:.15g}", f"{after - before:.15g}",
                     f"{change:.2f}" if change is not None else "N/A"))
    header = ("Metric", "Before", "After", "After minus before", "Change (%)")
    write_csv(DIRECTORY / "comparison.csv", header, rows)
    table = ["| " + " | ".join(header) + " |", "| --- | ---: | ---: | ---: | ---: |",
             *("| " + " | ".join(row) + " |" for row in rows)]
    (DIRECTORY / "comparison.md").write_text("\n".join(table) + "\n")
    print("\n".join(table))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["before", "after", "compare"])
    phase = parser.parse_args().phase
    if phase == "compare":
        compare()
    else:
        measure(phase)
