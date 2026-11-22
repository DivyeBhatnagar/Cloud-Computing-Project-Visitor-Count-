# Public GitHub repository and ZIP

The local Git repository uses branch `main`. For an extracted copy without Git metadata, run `git init -b main`. Before a new commit, check `git var GIT_AUTHOR_IDENT` and set your GitHub noreply email locally with `git config user.email YOUR_GITHUB_NOREPLY_ADDRESS` if needed. Check the exact files before staging. The project ignores the filled college report and its exports because the cover contains student identifiers. The publishable Markdown is `report/public-report.md`. Review the staged files before committing. Review screenshots for any personal details.

```bash
git status --short
git add .
git diff --cached --stat
git diff --cached --check
git diff --cached
git commit -m "Build and document the visitor counter cloud project"
gh auth status
gh auth login --hostname github.com --web
gh repo create visitor-counter-cloud-project --public --source=. --remote=origin --push
gh repo view --json url,visibility --jq '.visibility + " " + .url'
```

If the initial commit already exists and the tree is clean, continue at the authentication check. Run the login command if authentication is invalid. Run the create command only once. If you already created an empty public repository manually, add it with `git remote add origin <verified-HTTPS-repository-URL>` and run `git push -u origin main`.

Confirm the repository visibility reads `PUBLIC` and open it in a private browser window signed out. Copy its verified URL into `github_link.txt` and both report covers. Regenerate the private export for your submission and push the public Markdown update. Stage evidence screenshots after reviewing their contents.

```bash
git add github_link.txt report/public-report.md screenshots
git commit -m "Add the verified public link and project evidence"
git push
```

On the verified repository page select **Code → Download ZIP**. Unzip a copy and check the application, Dockerfile, Kubernetes and HPA manifests, measured CSV, architecture diagram, report and screenshots. Download again after the final push if files changed.
