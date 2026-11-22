#!/usr/bin/env bash
set -euo pipefail
pandoc report/project-report.md --from=markdown --resource-path=report:. \
  --lua-filter=report/cover.lua -o report/project-report.docx
chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [[ -x "$chrome" ]]; then
  tmp=$(mktemp -d)
  trap 'rm -rf "$tmp"' EXIT
  pandoc report/project-report.md --from=markdown --standalone --embed-resources \
    --resource-path=report:. --metadata pagetitle="Cloud Computing Small Project" \
    --css=report/print.css -o "$tmp/report.html"
  "$chrome" --headless --disable-gpu --no-first-run --no-pdf-header-footer \
    --user-data-dir="$tmp/chrome" --print-to-pdf="$PWD/report/project-report.pdf" \
    "file://$tmp/report.html"
fi
