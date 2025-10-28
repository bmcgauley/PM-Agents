# Required Tools Installation Guide

Complete list of all tools needed for the multi-agent system.

---

## Core Requirements

### 1. Python
**Version**: 3.10 or higher

```bash
# Check installation
python --version
python3 --version

# Install from:
# - Windows: https://www.python.org/downloads/
# - macOS: brew install python@3.11
# - Linux: sudo apt install python3.11
```

### 2. Node.js and npm
**Version**: 18 or 20 (LTS recommended)

```bash
# Check installation
node --version
npm --version

# Install from:
# - All platforms: https://nodejs.org/
# - macOS: brew install node@20
# - Linux: nvm install 20
```

### 3. Git
**Version**: Latest

```bash
# Check installation
git --version

# Install from:
# - Windows: https://git-scm.com/download/win
# - macOS: brew install git
# - Linux: sudo apt install git
```

### 4. Docker
**Version**: Latest

```bash
# Check installation
docker --version

# Install from:
# - All platforms: https://www.docker.com/products/docker-desktop/
```

---

## Python Packages

### Core Agent Dependencies

```bash
# Install all at once
pip install anthropic requests python-dateutil

# Or individually:
pip install anthropic>=0.40.0          # Claude API
pip install requests>=2.31.0           # HTTP requests
pip install python-dateutil>=2.8.2     # Date utilities
```

### Vector Database (Qdrant)

```bash
pip install qdrant-client>=1.7.0       # Qdrant Python client
pip install sentence-transformers      # Text embeddings
```

### Python ML/DL Agent

```bash
# PyTorch (choose based on your system)
# CPU only:
pip install torch torchvision torchaudio

# With CUDA (GPU support):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Additional ML tools:
pip install tensorboard                # Visualization
pip install jupyter jupyterlab         # Notebooks
pip install numpy pandas               # Data manipulation
pip install scikit-learn               # ML utilities
pip install matplotlib seaborn         # Plotting
pip install wandb                      # Experiment tracking (optional)
pip install pytorch-lightning          # Training framework (optional)
```

### Code Quality Tools

```bash
pip install black                      # Python formatter
pip install flake8                     # Linter
pip install mypy                       # Type checker
pip install pytest                     # Testing framework
pip install pytest-cov                 # Test coverage
```

---

## Node.js Packages (MCP Servers)

### Core MCP Servers

```bash
# Install globally
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-brave-search
```

### Frontend Development Tools

```bash
# Install globally (optional but recommended)
npm install -g typescript
npm install -g @types/node
npm install -g eslint
npm install -g prettier
npm install -g vercel                  # Deployment
npm install -g pnpm                    # Fast package manager (alternative to npm)
```

### Project Initialization

```bash
# Specify (spec-kit) for project initialization
npm install -g @specify/cli
```

---

## R Language (for R Analytics Agent)

### R Installation
**Version**: 4.x or higher

```bash
# Check installation
R --version

# Install from:
# - Windows: https://cran.r-project.org/bin/windows/base/
# - macOS: brew install r
# - Linux: sudo apt install r-base
```

### R Packages

```R
# Run in R console or RStudio
install.packages(c(
  # Core tidyverse
  "tidyverse",
  "ggplot2",
  "dplyr",
  "tidyr",
  "readr",
  "purrr",
  "tibble",
  "stringr",
  "forcats",

  # Reporting
  "rmarkdown",
  "knitr",

  # Interactive apps
  "shiny",

  # Modeling
  "caret",
  "tidymodels",

  # Code quality
  "lintr",
  "styler"
), repos = "https://cloud.r-project.org")
```

### RStudio (Optional but Recommended)

```bash
# Download from:
# https://posit.co/download/rstudio-desktop/
```

---

## Vector Database

### Qdrant

**Option 1: Docker (Recommended)**

```bash
# Pull image
docker pull qdrant/qdrant

# Run container
docker run -d -p 6333:6333 -p 6334:6334 \
  --name qdrant \
  -v $(pwd)/qdrant_storage:/qdrant/storage:z \
  qdrant/qdrant

# Windows PowerShell:
docker run -d -p 6333:6333 -p 6334:6334 `
  --name qdrant `
  -v ${PWD}/qdrant_storage:/qdrant/storage `
  qdrant/qdrant
```

**Option 2: Local Installation**

```bash
# macOS
brew install qdrant

# Linux (download binary)
wget https://github.com/qdrant/qdrant/releases/latest/download/qdrant-x86_64-unknown-linux-gnu.tar.gz
tar -xzf qdrant-x86_64-unknown-linux-gnu.tar.gz
./qdrant
```

---

## Database & Backend Services

### Supabase CLI (for Frontend Agent)

```bash
npm install -g supabase

# Check installation
supabase --version
```

---

## API Keys Required

### Anthropic (Claude)

```bash
# Get from: https://console.anthropic.com/

# Set environment variable:
# Linux/macOS:
export ANTHROPIC_API_KEY="your-key-here"

# Windows (Command Prompt):
set ANTHROPIC_API_KEY=your-key-here

# Windows (PowerShell):
$env:ANTHROPIC_API_KEY="your-key-here"
```

### GitHub Personal Access Token

```bash
# Get from: https://github.com/settings/tokens
# Required scopes: repo, read:org

# Set environment variable:
export GITHUB_TOKEN="your-token-here"
```

### Brave Search API (Optional - for web research)

```bash
# Get from: https://brave.com/search/api/

# Set environment variable:
export BRAVE_API_KEY="your-key-here"
```

---

## Frontend Development Stack

### Next.js & React

```bash
# These are project-specific, installed via npm in each project
# Listed here for reference:

# Core
# - next@14+
# - react@18+
# - react-dom@18+
# - typescript@5+

# Styling
# - tailwindcss@3+
# - autoprefixer
# - postcss

# UI Components
# - @radix-ui/react-*
# - class-variance-authority
# - clsx
# - tailwind-merge

# State & Data
# - zustand (state management)
# - @tanstack/react-query (data fetching)
# - @supabase/supabase-js (backend)

# CMS
# - payload
# - @payloadcms/db-mongodb
# - @payloadcms/richtext-slate
```

---

## Testing & Quality Tools

### TypeScript Validator Agent Tools

```bash
# TypeScript
npm install -g typescript

# Linting
npm install -g eslint
npm install -g @typescript-eslint/parser
npm install -g @typescript-eslint/eslint-plugin

# Formatting
npm install -g prettier

# Testing (project-specific, but can install globally)
npm install -g jest
npm install -g vitest
npm install -g @playwright/test
npm install -g cypress
```

---

## Browser Automation (for Browser Agent)

```bash
# Playwright
npm install -g playwright
npx playwright install  # Install browser binaries

# Or Puppeteer
npm install -g puppeteer
```

---

## Optional Tools

### TensorFlow (Alternative to PyTorch)

```bash
pip install tensorflow
pip install tensorflow-datasets
```

### Jupyter Extensions

```bash
pip install ipywidgets          # Interactive widgets
pip install jupyterlab-lsp      # Language server
pip install jupyter-dash        # Dash integration
```

### Database Tools

```bash
# PostgreSQL client (for Supabase)
# macOS: brew install postgresql
# Linux: sudo apt install postgresql-client
# Windows: Download from https://www.postgresql.org/download/windows/
```

### Version Managers (Recommended)

```bash
# Python: pyenv
curl https://pyenv.run | bash

# Node.js: nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Or: fnm (faster node manager)
curl -fsSL https://fnm.vercel.app/install | bash
```

---

## Verification Commands

Run these to verify all installations:

```bash
# Core tools
python --version        # Should be 3.10+
node --version          # Should be v18+ or v20+
npm --version
git --version
docker --version
R --version             # Should be 4.x+

# Python packages
python -c "import anthropic; print('Anthropic OK')"
python -c "import torch; print(f'PyTorch {torch.__version__}')"
python -c "from qdrant_client import QdrantClient; print('Qdrant client OK')"
python -c "import tensorboard; print('TensorBoard OK')"

# Node packages
npx @modelcontextprotocol/server-filesystem --version
supabase --version

# R packages
R -e "library(tidyverse); print('tidyverse OK')"

# Docker services
curl http://localhost:6333/collections  # Qdrant (if running)

# API keys
echo $ANTHROPIC_API_KEY    # Should show your key
echo $GITHUB_TOKEN         # Should show your token
```

---

## Installation Script

Save this as `install_tools.sh` (Linux/macOS) or `install_tools.ps1` (Windows):

### Linux/macOS

```bash
#!/bin/bash

echo "Installing Python packages..."
pip install anthropic requests python-dateutil qdrant-client sentence-transformers
pip install torch torchvision torchaudio tensorboard jupyter jupyterlab
pip install numpy pandas scikit-learn matplotlib seaborn
pip install black flake8 mypy pytest pytest-cov

echo "Installing Node.js packages..."
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-brave-search
npm install -g typescript eslint prettier
npm install -g @specify/cli supabase
npm install -g playwright

echo "Installing Playwright browsers..."
npx playwright install

echo "Starting Qdrant..."
docker run -d -p 6333:6333 -p 6334:6334 --name qdrant qdrant/qdrant

echo "Done! Please install R packages manually in R console."
```

### Windows PowerShell

```powershell
# install_tools.ps1

Write-Host "Installing Python packages..."
pip install anthropic requests python-dateutil qdrant-client sentence-transformers
pip install torch torchvision torchaudio tensorboard jupyter jupyterlab
pip install numpy pandas scikit-learn matplotlib seaborn
pip install black flake8 mypy pytest pytest-cov

Write-Host "Installing Node.js packages..."
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-brave-search
npm install -g typescript eslint prettier
npm install -g @specify/cli supabase
npm install -g playwright

Write-Host "Installing Playwright browsers..."
npx playwright install

Write-Host "Starting Qdrant..."
docker run -d -p 6333:6333 -p 6334:6334 --name qdrant qdrant/qdrant

Write-Host "Done! Please install R packages manually in R console."
```

---

## Quick Reference Checklist

- [ ] Python 3.10+
- [ ] Node.js 18+ or 20+
- [ ] Git
- [ ] Docker
- [ ] R 4.x (if using R Analytics Agent)
- [ ] Python packages (anthropic, torch, qdrant-client, etc.)
- [ ] MCP servers (filesystem, github, brave-search)
- [ ] Qdrant running on port 6333
- [ ] API keys set (ANTHROPIC_API_KEY, GITHUB_TOKEN, BRAVE_API_KEY)
- [ ] R packages (tidyverse, ggplot2, rmarkdown, etc.)
- [ ] Frontend tools (typescript, eslint, prettier)
- [ ] Testing tools (jest/vitest, playwright)
- [ ] Supabase CLI

---

## Troubleshooting

### Python package conflicts

```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Node.js permission errors

```bash
# Fix npm permissions (Linux/macOS)
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
export PATH=~/.npm-global/bin:$PATH

# Or use nvm (recommended)
```

### Qdrant connection issues

```bash
# Check if running
docker ps | grep qdrant

# View logs
docker logs qdrant

# Restart
docker restart qdrant
```

### PyTorch CUDA issues

```bash
# Check CUDA availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# If False, reinstall with correct CUDA version:
# https://pytorch.org/get-started/locally/
```

---

## System Requirements

### Minimum

- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 20 GB free
- **OS**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)

### Recommended

- **CPU**: 8+ cores
- **RAM**: 16 GB+ (32 GB for ML/DL work)
- **Storage**: 50 GB+ SSD
- **GPU**: NVIDIA GPU with 8GB+ VRAM (for PyTorch training)
- **OS**: Latest stable version

---

## Next Steps

After installing all tools:

1. Follow [claudcodesetup.md](claudcodesetup.md) for configuration
2. Run verification commands above
3. Set up MCP servers
4. Initialize Qdrant collections
5. Start building with the agents!
