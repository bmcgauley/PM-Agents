###############################################################################
# PM-Agents MCP Server Verification Script (Windows PowerShell)
###############################################################################
#
# This script verifies that all MCP servers are properly installed and functional.
#
# Usage:
#   .\verify_mcp_servers.ps1
#
###############################################################################

$ErrorActionPreference = "Continue"  # Don't stop on errors during tests

# Colors
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

# Test MCP server
function Test-McpServer {
    param(
        [string]$ServerName,
        [string]$ServerCommand
    )

    Write-Info "Testing $ServerName..."

    try {
        # Create test request
        $testRequest = @{
            jsonrpc = "2.0"
            id = 1
            method = "tools/list"
            params = @{}
        } | ConvertTo-Json

        # Execute server command
        $result = $testRequest | Invoke-Expression $ServerCommand 2>$null

        if ($result -match "tools") {
            Write-Success "$ServerName is working"
            return $true
        }
        else {
            Write-Error "$ServerName failed to respond"
            return $false
        }
    }
    catch {
        Write-Error "$ServerName failed: $_"
        return $false
    }
}

# Main verification
function Main {
    Write-Header "PM-Agents MCP Server Verification"
    Write-Host ""

    $totalTests = 0
    $passedTests = 0

    # Test essential MCP servers
    Write-Header "Testing Essential MCP Servers"

    # filesystem
    $totalTests++
    Write-Info "Testing filesystem..."
    try {
        $testOutput = echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | npx -y @modelcontextprotocol/server-filesystem $env:USERPROFILE 2>$null
        if ($testOutput -match "tools") {
            Write-Success "filesystem is working"
            $passedTests++
        }
        else {
            Write-Error "filesystem failed to respond"
        }
    }
    catch {
        Write-Error "filesystem failed: $_"
    }

    # github (requires GITHUB_TOKEN)
    if ($env:GITHUB_TOKEN) {
        $totalTests++
        Write-Info "Testing github..."
        try {
            $testOutput = echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | npx -y @modelcontextprotocol/server-github 2>$null
            if ($testOutput -match "tools") {
                Write-Success "github is working"
                $passedTests++
            }
            else {
                Write-Error "github failed to respond"
            }
        }
        catch {
            Write-Error "github failed: $_"
        }
    }
    else {
        Write-Warning "Skipping github (GITHUB_TOKEN not set)"
    }

    # brave-search (requires BRAVE_API_KEY)
    if ($env:BRAVE_API_KEY) {
        $totalTests++
        Write-Info "Testing brave-search..."
        try {
            $testOutput = echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | npx -y @modelcontextprotocol/server-brave-search 2>$null
            if ($testOutput -match "tools") {
                Write-Success "brave-search is working"
                $passedTests++
            }
            else {
                Write-Error "brave-search failed to respond"
            }
        }
        catch {
            Write-Error "brave-search failed: $_"
        }
    }
    else {
        Write-Warning "Skipping brave-search (BRAVE_API_KEY not set)"
    }

    # memory
    $totalTests++
    Write-Info "Testing memory..."
    try {
        $testOutput = echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | npx -y @modelcontextprotocol/server-memory 2>$null
        if ($testOutput -match "tools") {
            Write-Success "memory is working"
            $passedTests++
        }
        else {
            Write-Error "memory failed to respond"
        }
    }
    catch {
        Write-Error "memory failed: $_"
    }

    # puppeteer
    $totalTests++
    Write-Info "Testing puppeteer..."
    try {
        $testOutput = echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | npx -y @modelcontextprotocol/server-puppeteer 2>$null
        if ($testOutput -match "tools") {
            Write-Success "puppeteer is working"
            $passedTests++
        }
        else {
            Write-Error "puppeteer failed to respond"
        }
    }
    catch {
        Write-Error "puppeteer failed: $_"
    }

    Write-Host ""

    # Test custom MCP servers (when published)
    Write-Header "Testing Custom PM-Agents MCP Servers"
    Write-Warning "Custom MCP servers (@pm-agents/*) not yet published. Skipping tests."

    # Uncomment when published:
    # $totalTests++
    # if (Test-McpServer "qdrant" "npx -y @pm-agents/mcp-qdrant") {
    #     $passedTests++
    # }

    # $totalTests++
    # if (Test-McpServer "tensorboard" "npx -y @pm-agents/mcp-tensorboard") {
    #     $passedTests++
    # }

    # $totalTests++
    # if (Test-McpServer "specify" "npx -y @pm-agents/mcp-specify") {
    #     $passedTests++
    # }

    Write-Host ""

    # Test Qdrant availability
    Write-Header "Testing Qdrant Vector Database"
    $totalTests++
    try {
        $qdrantResponse = Invoke-WebRequest -Uri "http://localhost:6333/healthz" -Method Get -TimeoutSec 2 2>$null
        if ($qdrantResponse.StatusCode -eq 200) {
            Write-Success "Qdrant is accessible at http://localhost:6333"
            $passedTests++
        }
        else {
            Write-Error "Qdrant is not accessible"
        }
    }
    catch {
        Write-Error "Qdrant is not accessible. Start with: docker run -d -p 6333:6333 qdrant/qdrant"
    }

    Write-Host ""

    # Summary
    Write-Header "Verification Summary"
    Write-Host ""
    Write-Host "Tests passed: $passedTests / $totalTests"

    if ($passedTests -eq $totalTests) {
        Write-Success "All tests passed! ✅"
        Write-Host ""
        Write-Host "Your PM-Agents MCP setup is ready to use."
        exit 0
    }
    else {
        $failed = $totalTests - $passedTests
        Write-Warning "$failed test(s) failed"
        Write-Host ""
        Write-Host "Some MCP servers are not working correctly."
        Write-Host "Check the errors above and run: .\install_mcp_servers.ps1"
        exit 1
    }
}

Main
