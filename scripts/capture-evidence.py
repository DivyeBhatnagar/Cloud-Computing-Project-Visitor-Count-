"""Capture PNGs of recorded laptop output using headless Chrome on macOS."""
import html
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def read(name):
    return ANSI.sub("", (ROOT / "evidence" / f"{name}.log").read_text()).strip()


def capture(name, title, output, directory):
    document = directory / "output.html"
    document.write_text(f"""<!doctype html><html lang="en"><meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
body {{ margin: 34px; background: #f0f5f4; color: #192d29; font: 17px system-ui; }}
h1 {{ margin: 0 0 4px; font-size: 26px; }}
p {{ margin: 0 0 20px; color: #3c5850; }}
pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: white; border:
1px solid #afc5bc; border-radius: 10px; padding: 16px; font-size: 14px; line-height: 1.35; }}
</style>
<h1>{html.escape(title)}</h1><p><strong>Divye Bhatnagar</strong> · Recorded command output from the project laptop</p>
<pre>{html.escape(output)}</pre></html>""")
    height = max(340, 165 + len(output.splitlines()) * 22)
    subprocess.run([
        str(CHROME), "--headless", "--disable-gpu", "--no-first-run",
        f"--user-data-dir={directory / 'chrome'}", f"--window-size=1500,{height}",
        f"--screenshot={ROOT / 'screenshots' / (name + '.png')}", document.as_uri(),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def excerpt(name, count, tail=False):
    lines = read(name).splitlines()
    return "\n".join(lines[-count:] if tail else lines[:count])


def select(name, pattern):
    return "\n".join(line for line in read(name).splitlines() if re.search(pattern, line))


def main():
    cost = read("benchmark")
    snapshots = [line for line in cost.splitlines() if line.startswith("{'idle_replicas':")]
    before = "\n".join(line for line in snapshots if line.startswith("{'idle_replicas': 3,"))
    after = "\n".join(line for line in snapshots if line.startswith("{'idle_replicas': 1,"))
    sizes = read("image-sizes").splitlines()
    failover = read("failover")
    groups = [
        ("01-versions", "Installed software", read("versions")),
        ("03-increment", "HTTP 200 and Redis counter increments", read("compose-smoke")),
        ("04-build", "Docker image build", excerpt("optimized-image", 14, True)),
        ("05-containers", "Healthy Docker containers", excerpt("compose-smoke", 3)),
        ("06-compose", "Docker Compose startup", excerpt("compose", 12, True)),
        ("07-minikube", "Minikube cluster readiness", excerpt("clusters", 11)),
        ("08-services", "Deployments, Services and persistent volumes", excerpt("clusters", 28)),
        ("09-pods", "Running Flask and Redis pods", select("clusters", r"NAME .* STATUS|pod/(redis|visitor)")),
        ("10-self-healing", "Flask pod deletion and replacement", read("self-healing")),
        ("11-metrics", "Metrics-server output and CPU utilization", read("metrics-server")),
        ("12-hpa-initial", "Initial HPA replica count and target", excerpt("hpa-up", 11)),
        ("13-load", "Kubernetes load Job", read("load")),
        ("14-scale-up", "HPA scale-up to five ready pods", excerpt("hpa-up", 16, True)),
        ("15-scale-down", "HPA scale-down to one ready pod", excerpt("hpa-down", 16, True)),
        ("16-profiles", "Both local Minikube profiles", excerpt("clusters", 9) + "\n\n" + read("contexts")),
        ("18-primary-stopped", "Primary profile stopped and backup serving",
         "\n".join(line for line in failover.splitlines() if re.search(r"Stopped|stopped|backup", line))),
        ("20-recovery", "Router transitions and primary recovery",
         select("router", r"route .* ->") + "\n" + excerpt("failover", 11, True)),
        ("21-baseline", "Baseline resource measurements",
         before + "\n\nDocker image inspect (ARM64, bytes)\n" + sizes[0]),
        ("22-optimized", "Optimized resource measurements",
         after + "\n\nDocker image inspect (ARM64, bytes)\n" + sizes[1]),
    ]
    with TemporaryDirectory() as tmp:
        for name, title, output in groups:
            if not output.strip():
                raise RuntimeError(f"No recorded evidence for {name}")
            capture(name, title, output, Path(tmp))


if __name__ == "__main__":
    main()
