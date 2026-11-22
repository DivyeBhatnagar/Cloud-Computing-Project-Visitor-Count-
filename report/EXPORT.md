# Export the report

From the repository root, install free Pandoc if needed (`brew install pandoc` on macOS or `sudo apt install pandoc` in WSL). Insert the verified public repository URL and link actual screenshots in the Markdown. The included filter inserts a page break after the cover.

```bash
pandoc report/project-report.md --from=markdown --resource-path=report:. --lua-filter=report/cover.lua -o report/project-report.docx
```

On macOS with Google Chrome installed, `bash scripts/export-report.sh` produces both DOCX and PDF. Open the DOCX in Pages, Word or free LibreOffice and export to PDF. On a machine with LibreOffice CLI available, run `soffice --headless --convert-to pdf --outdir report report/project-report.docx`. Inspect the cover, tables, architecture image and screenshot captions before submission.
