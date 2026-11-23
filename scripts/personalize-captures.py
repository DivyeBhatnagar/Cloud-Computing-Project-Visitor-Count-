"""Frame original browser evidence with an explicit student attribution."""
import base64
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    for filename in ("02-flask.png", "17-primary.png", "19-backup.png", "23-github.png"):
        target = ROOT / "screenshots" / filename
        original = ROOT / "screenshots" / "originals" / filename
        original.parent.mkdir(exist_ok=True)
        if not original.exists():
            original.write_bytes(target.read_bytes())
        encoded = base64.b64encode(original.read_bytes()).decode()
        page = directory / "capture.html"
        page.write_text(
            '<html><meta charset="utf-8"><style>body{margin:0;background:#10251f;color:#fff;'
            'font-family:system-ui}header{padding:18px 28px;font-size:24px}small{font-size:14px;'
            'display:block;color:#bed5ca}img{display:block;width:100%}</style>'
            '<header>Divye Bhatnagar<small>Original project browser evidence · attributed presentation</small>'
            f'</header><img src="data:image/png;base64,{encoded}"></html>'
        )
        height = 1340 if filename == "23-github.png" else 1000
        subprocess.run([
            CHROME, "--headless", "--disable-gpu", "--no-first-run",
            f"--user-data-dir={directory / 'profile'}",
            f"--window-size=1440,{height}", f"--screenshot={target}", page.as_uri()
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
