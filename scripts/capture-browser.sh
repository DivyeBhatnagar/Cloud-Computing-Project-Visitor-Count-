#!/usr/bin/env bash
set -euo pipefail
chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
target="${1:-compose}"
case "$target" in
  compose) port=8080; filename=02-flask.png ;;
  primary) port=8088; filename=17-primary.png ;;
  backup) port=8088; filename=19-backup.png ;;
  *) exit 2 ;;
esac
profile=$(mktemp -d)
trap 'rm -rf "$profile"' EXIT
"$chrome" --headless --disable-gpu --no-first-run --user-data-dir="$profile" \
  --window-size=1280,820 --screenshot="$PWD/screenshots/$filename" "http://127.0.0.1:$port/"
