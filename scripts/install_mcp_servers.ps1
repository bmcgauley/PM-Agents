###############################################################################
# PM-Agents MCP Server Installation Script (Windows PowerShell)
###############################################################################
#
# This script installs and configures all MCP servers required by PM-Agents:
# - Essential (global): filesystem, github, brave-search, memory, puppeteer
# - Custom: @pm-agents/mcp-qdrant, @pm-agents/mcp-tensorboard, @pm-agents/mcp-specify
# - Optional: supabase (for frontend projects)
#
# Prerequisites:
# - Node.js 18+ installed
# - npm or npx available
# - Claude Code installed
# - API keys ready (GITHUB_TOKEN, BRAVE_API_KEY)
#
# Usage:
#   .\install_mcp_servers.ps1
#   (or: powershell -ExecutionPolicy Bypass -File install_mcp_servers.ps1)
#
###############################################################################

# Enable strict mode
$ErrorActionPreference = "Stop"

# Colors for output
function Write-Header {
    param([string]$Message)
    Write-Host "===================================================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "===================================================================" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

# Check prerequisites
function Test-Prerequisites {
    Write-Header "Checking Prerequisites"

    # Check Node.js
    try {
        $nodeVersion = node -v
        $versionNumber = [int]($nodeVersion -replace 'v', '' -split '\.')[0]

        if ($versionNumber -lt 18) {
            Write-Error "Node.js 18+ required. Current version: $nodeVersion"
            exit 1
        }
        Write-Success "Node.js $nodeVersion installed"
    }
    catch {
        Write-Error "Node.js not found. Install Node.js 18+ from https://nodejs.org/"
        exit 1
    }

    # Check npx
    try {
        $null = npx --version
        Write-Success "npx available"
    }
    catch {
        Write-Error "npx not found. Install npm: npm install -g npm"
        exit 1
    }

    # Check claude CLI
    try {
        $null = claude --version
        Write-Success "Claude Code CLI installed"
    }
    catch {
        Write-Error "Claude Code CLI not found. Install from https://claude.com/code"
        exit 1
    }

    Write-Host ""
}

# Collect API keys
function Get-ApiKeys {
    Write-Header "API Key Configuration"

    # GitHub Token
    $global:GITHUB_TOKEN = $env:GITHUB_TOKEN
    if (-not $global:GITHUB_TOKEN) {
        Write-Host "GitHub Personal Access Token (required for github MCP server)" -ForegroundColor Yellow
        Write-Host "Create token at: https://github.com/settings/tokens/new"
        Write-Host "Required scopes: repo, read:org"
        $global:GITHUB_TOKEN = Read-Host "Enter GITHUB_TOKEN (or press Enter to skip)"
    }

    if ($global:GITHUB_TOKEN) {
        Write-Success "GitHub token configured"
        $env:GITHUB_TOKEN = $global:GITHUB_TOKEN
    }
    else {
        Write-Warning "GitHub token not provided. 'github' MCP server will be skipped."
    }

    # Brave Search API Key
    $global:BRAVE_API_KEY = $env:BRAVE_API_KEY
    if (-not $global:BRAVE_API_KEY) {
        Write-Host ""
        Write-Host "Brave Search API Key (optional, for research features)" -ForegroundColor Yellow
        Write-Host "Get API key at: https://api.search.brave.com/app/keys"
        $global:BRAVE_API_KEY = Read-Host "Enter BRAVE_API_KEY (or press Enter to skip)"
    }

    if ($global:BRAVE_API_KEY) {
        Write-Success "Brave Search API key configured"
        $env:BRAVE_API_KEY = $global:BRAVE_API_KEY
    }
    else {
        Write-Warning "Brave Search API key not provided. 'brave-search' MCP server will be skipped."
    }

    # Qdrant URL
    Write-Host ""
    Write-Host "Qdrant Database URL (required for vector search)" -ForegroundColor Yellow
    $qdrantInput = Read-Host "Enter QDRANT_URL [default: http://localhost:6333]"
    $global:QDRANT_URL = if ($qdrantInput) { $qdrantInput } else { "http://localhost:6333" }
    $env:QDRANT_URL = $global:QDRANT_URL
    Write-Success "Qdrant URL: $global:QDRANT_URL"

    Write-Host ""
}

# Install essential MCP servers
function Install-EssentialMcpServers {
    Write-Header "Installing Essential MCP Servers (Global)"

    # filesystem
    Write-Info "Installing: filesystem"
    $workspacePath = if ($env:WORKSPACE_PATH) { $env:WORKSPACE_PATH } else { $env:USERPROFILE }

    try {
        claude mcp add --scope user --transport stdio filesystem -- npx -y @modelcontextprotocol/server-filesystem $workspacePath
        Write-Success "filesystem installed (path: $workspacePath)"
    }
    catch {
        Write-Error "Failed to install filesystem: $_"
    }

    # github (if token provided)
    if ($global:GITHUB_TOKEN) {
        Write-Info "Installing: github"
        try {
            claude mcp add --scope user --transport stdio --env GITHUB_TOKEN=$global:GITHUB_TOKEN github -- npx -y @modelcontextprotocol/server-github
            Write-Success "github installed"
        }
        catch {
            Write-Error "Failed to install github: $_"
        }
    }

    # brave-search (if API key provided)
    if ($global:BRAVE_API_KEY) {
        Write-Info "Installing: brave-search"
        try {
            claude mcp add --scope user --transport stdio --env BRAVE_API_KEY=$global:BRAVE_API_KEY brave-search -- npx -y @modelcontextprotocol/server-brave-search
            Write-Success "brave-search installed"
        }
        catch {
            Write-Error "Failed to install brave-search: $_"
        }
    }

    # memory
    Write-Info "Installing: memory"
    try {
        claude mcp add --scope user --transport stdio memory -- npx -y @modelcontextprotocol/server-memory
        Write-Success "memory installed"
    }
    catch {
        Write-Error "Failed to install memory: $_"
    }

    # puppeteer
    Write-Info "Installing: puppeteer"
    try {
        claude mcp add --scope user --transport stdio puppeteer -- npx -y @modelcontextprotocol/server-puppeteer
        Write-Success "puppeteer installed"
    }
    catch {
        Write-Error "Failed to install puppeteer: $_"
    }

    Write-Host ""
}

# Install custom PM-Agents MCP servers
function Install-CustomMcpServers {
    Write-Header "Installing Custom PM-Agents MCP Servers"

    Write-Warning "Custom MCP servers (@pm-agents/*) are not yet published to npm."
    Write-Warning "Skipping installation. These will be available after Phase 3 implementation."

    # When published, uncomment:
    # Write-Info "Installing: @pm-agents/mcp-qdrant"
    # try {
    #     claude mcp add --scope user --transport stdio --env QDRANT_URL=$global:QDRANT_URL qdrant -- npx -y @pm-agents/mcp-qdrant
    #     Write-Success "@pm-agents/mcp-qdrant installed"
    # }
    # catch {
    #     Write-Error "Failed to install @pm-agents/mcp-qdrant: $_"
    # }

    # Write-Info "Installing: @pm-agents/mcp-tensorboard"
    # try {
    #     claude mcp add --scope user --transport stdio tensorboard -- npx -y @pm-agents/mcp-tensorboard
    #     Write-Success "@pm-agents/mcp-tensorboard installed"
    # }
    # catch {
    #     Write-Error "Failed to install @pm-agents/mcp-tensorboard: $_"
    # }

    # Write-Info "Installing: @pm-agents/mcp-specify"
    # try {
    #     claude mcp add --scope user --transport stdio specify -- npx -y @pm-agents/mcp-specify
    #     Write-Success "@pm-agents/mcp-specify installed"
    # }
    # catch {
    #     Write-Error "Failed to install @pm-agents/mcp-specify: $_"
    # }

    Write-Host ""
}

# Setup Qdrant (Docker)
function Initialize-Qdrant {
    Write-Header "Setting Up Qdrant Vector Database"

    # Check if Docker is installed
    try {
        $null = docker --version
    }
    catch {
        Write-Warning "Docker not found. Install Docker Desktop to run Qdrant locally."
        Write-Info "Alternative: Use Qdrant Cloud at https://cloud.qdrant.io/"
        return
    }

    Write-Info "Checking if Qdrant is already running..."
    $qdrantRunning = docker ps | Select-String "qdrant"

    if ($qdrantRunning) {
        Write-Success "Qdrant container already running"
        return
    }

    Write-Info "Starting Qdrant container..."
    try {
        docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
        Write-Success "Qdrant started at http://localhost:6333"
        Write-Info "Qdrant Dashboard: http://localhost:6333/dashboard"
    }
    catch {
        Write-Error "Failed to start Qdrant. Check Docker installation: $_"
    }

    Write-Host ""
}

# Verify installation
function Test-Installation {
    Write-Header "Verifying MCP Server Installation"

    # List installed MCP servers
    Write-Info "Installed MCP servers:"
    try {
        claude mcp list
        Write-Success "MCP servers listed successfully"
    }
    catch {
        Write-Error "Failed to list MCP servers: $_"
    }

    Write-Host ""
}

# Generate configuration summary
function Show-Summary {
    Write-Header "Installation Summary"

    Write-Host ""
    Write-Host "✅ Installation Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Installed MCP Servers:"
    Write-Host "  • filesystem      - File operations"
    Write-Host "  • memory          - Agent memory"
    Write-Host "  • puppeteer       - Browser automation"

    if ($global:GITHUB_TOKEN) {
        Write-Host "  • github          - Repository operations"
    }

    if ($global:BRAVE_API_KEY) {
        Write-Host "  • brave-search    - Web research"
    }

    $qdrantRunning = docker ps 2>$null | Select-String "qdrant"
    if ($qdrantRunning) {
        Write-Host ""
        Write-Host "Qdrant Vector Database:"
        Write-Host "  • URL: http://localhost:6333"
        Write-Host "  • Dashboard: http://localhost:6333/dashboard"
    }

    Write-Host ""
    Write-Host "Next Steps:"
    Write-Host "  1. Verify installation: .\scripts\verify_mcp_servers.ps1"
    Write-Host "  2. Run PM-Agents: python pm_coordinator_agent.py"
    Write-Host "  3. Check documentation: .\docs\ or https://pm-agents.dev"
    Write-Host ""
    Write-Host "Configuration Files:"
    Write-Host "  • MCP config: $env:USERPROFILE\.claude\mcp_servers.json"
    Write-Host "  • PM-Agents config: .\config\pm-agents.yaml (create if needed)"
    Write-Host ""
    Write-Host "Troubleshooting:"
    Write-Host "  • MCP servers not working: claude mcp list"
    Write-Host "  • Qdrant not accessible: docker ps | Select-String qdrant"
    Write-Host "  • API key issues: Check $env:USERPROFILE\.claude\mcp_servers.json"
    Write-Host ""
    Write-Host "For support: https://github.com/pm-agents/pm-agents/issues"
    Write-Host ""

    Write-Success "Setup complete! 🎉"
}

# Main installation flow
function Main {
    Write-Host ""
    Write-Header "PM-Agents MCP Server Installation"
    Write-Host ""

    Test-Prerequisites
    Get-ApiKeys
    Install-EssentialMcpServers
    Install-CustomMcpServers
    Initialize-Qdrant
    Test-Installation
    Show-Summary
}

# Run main
Main
