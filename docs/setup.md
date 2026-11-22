# Environment setup

## This laptop

The initial inspection found macOS 26.6.2 on Apple M4 (ARM64), 10 CPU cores, 16 GB RAM and 32 GiB available. Docker Desktop 4.77.0 started successfully. Docker Engine 29.5.3 reported Linux ARM64, 10 CPUs and 8,321,515,520 bytes of VM RAM. Compose v5.1.4, Python 3.14.6, Git 2.50.1, Minikube 1.39.0 and kubectl 1.37.2 were available after setup. Running the Docker engine verified that its Linux VM could start.

## macOS

Install the Apple silicon or Intel edition as appropriate from the [Docker Desktop macOS installer](https://docs.docker.com/desktop/setup/install/mac-install/). Docker Desktop is available at no charge for education under Docker's terms. Open the app and finish its initial setup. Use an existing Homebrew installation or follow [Homebrew installation](https://brew.sh/).

```bash
brew install minikube kubectl
# Install only as needed.
brew install python git gh redis
open -a Docker
uname -sm
system_profiler SPHardwareDataType | grep -E 'Chip|Processor|Cores|Memory'
df -h .
python3 --version
git --version
docker version
docker compose version
minikube version
kubectl version --client
docker info --format 'CPUs={{.NCPU}} RAM_bytes={{.MemTotal}}'
docker run --rm hello-world
```

Expect your architecture, available disk space, versions for each tool, both Docker client and server sections, and a successful hello-world message. If the Docker CLI is missing, enable CLI tool installation in Docker Desktop settings or prepend `/Applications/Docker.app/Contents/Resources/bin` to your shell PATH. If the Docker daemon is unavailable, check Docker Desktop has finished starting and use `docker context ls` to identify its context.

## Windows

Use WSL 2 with Docker Desktop integration and run the project commands from Ubuntu Bash. Check firmware virtualization under Task Manager → Performance → CPU, enable it in firmware if disabled, and restart after installing WSL if Windows prompts you. See [Docker Desktop WSL backend](https://docs.docker.com/desktop/features/wsl/).

```powershell
wsl --install -d Ubuntu
wsl --update
wsl --list --verbose
winget install Docker.DockerDesktop
```

After Docker Desktop starts, enable the WSL 2 engine and Ubuntu integration. In Ubuntu Bash, use the Linux binary installation steps for [Minikube](https://minikube.sigs.k8s.io/docs/start/) and [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) matching `uname -m`. Keep kubectl within one minor release of your Kubernetes server.

```bash
sudo apt update
sudo apt install python3 python3-venv git redis-server gh
uname -sm
nproc
free -h
df -h .
python3 --version
git --version
docker version
docker compose version
minikube version
kubectl version --client
docker info --format 'CPUs={{.NCPU}} RAM_bytes={{.MemTotal}}'
docker run --rm hello-world
```

Expect Ubuntu to be listed as version 2 and Docker to print both client and server details. If Docker works in PowerShell only, check WSL integration for Ubuntu.

## Capacity and troubleshooting

The project starts each Minikube profile with two CPUs and 2,560 MiB RAM. Allow about 8 GiB for Docker Desktop and keep at least 20 GiB available for the two profiles, base layers and build cache. Check available storage again after creating both clusters. If Minikube reports a memory shortage, stop unrelated containers and give the Docker VM more RAM within the physical host budget. Use `docker system df` to see disk usage and `minikube logs -p vc-primary` to diagnose startup. Check browser ports with `lsof -nP -iTCP:8080 -sTCP:LISTEN` on macOS or `ss -ltn` in WSL.
