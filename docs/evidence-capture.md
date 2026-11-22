# Capturing demonstration evidence

The browser screenshots show the live app on macOS. The numbered command screenshots show authentic recorded output from the successful laptop run in an HTML viewer. Their full corresponding logs are in `evidence/`.

To take original terminal screenshots during a fresh run, use the exact commands listed in [the screenshot checklist](../screenshots/README.md). To regenerate the logged-output screenshots from existing records on a Mac with Chrome installed, run:

```bash
python3 scripts/capture-evidence.py
```

This reads prior logs. To create new logs, start both clusters and build both images as described in the runbook and benchmark guide, then run `bash scripts/record-compose.sh` and `bash scripts/validate-clusters.sh`. The validation script repeats the demonstration and briefly stops the primary profile. Keep other traffic off the project ports while the scripts run.
