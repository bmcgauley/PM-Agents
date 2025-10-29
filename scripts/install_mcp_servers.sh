#!/bin/bash

###############################################################################
# PM-Agents MCP Server Installation Script (Linux/macOS)
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
#   chmod +x install_mcp_servers.sh
#   ./install_mcp_servers.sh
#
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}===================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js not found. Install Node.js 18+ from https://nodejs.org/"
        exit 1
    fi

    NODE_VERSION=$(node -v | cut -d 'v' -f 2 | cut -d '.' -f 1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js 18+ required. Current version: $(node -v)"
        exit 1
    fi
    print_success "Node.js $(node -v) installed"

    # Check npm/npx
    if ! command -v npx &> /dev/null; then
        print_error "npx not found. Install npm: npm install -g npm"
        exit 1
    fi
    print_success "npx available"

    # Check claude CLI
    if ! command -v claude &> /dev/null; then
        print_error "Claude Code CLI not found. Install from https://claude.com/code"
        exit 1
    fi
    print_success "Claude Code CLI installed"

    echo ""
}

# Prompt for API keys
collect_api_keys() {
    print_header "API Key Configuration"

    # GitHub Token
    if [ -z "$GITHUB_TOKEN" ]; then
        echo -e "${YELLOW}GitHub Personal Access Token (required for github MCP server)${NC}"
        echo "Create token at: https://github.com/settings/tokens/new"
        echo "Required scopes: repo, read:org"
        read -p "Enter GITHUB_TOKEN (or press Enter to skip): " GITHUB_TOKEN
    fi

    if [ -n "$GITHUB_TOKEN" ]; then
        print_success "GitHub token configured"
        export GITHUB_TOKEN
    else
        print_warning "GitHub token not provided. 'github' MCP server will be skipped."
    fi

    # Brave Search API Key
    if [ -z "$BRAVE_API_KEY" ]; then
        echo ""
        echo -e "${YELLOW}Brave Search API Key (optional, for research features)${NC}"
        echo "Get API key at: https://api.search.brave.com/app/keys"
        read -p "Enter BRAVE_API_KEY (or press Enter to skip): " BRAVE_API_KEY
    fi

    if [ -n "$BRAVE_API_KEY" ]; then
        print_success "Brave Search API key configured"
        export BRAVE_API_KEY
    else
        print_warning "Brave Search API key not provided. 'brave-search' MCP server will be skipped."
    fi

    # Qdrant URL
    echo ""
    echo -e "${YELLOW}Qdrant Database URL (required for vector search)${NC}"
    read -p "Enter QDRANT_URL [default: http://localhost:6333]: " QDRANT_URL
    QDRANT_URL=${QDRANT_URL:-http://localhost:6333}
    export QDRANT_URL
    print_success "Qdrant URL: $QDRANT_URL"

    echo ""
}

# Install essential MCP servers
install_essential_mcp_servers() {
    print_header "Installing Essential MCP Servers (Global)"

    # filesystem
    print_info "Installing: filesystem"
    WORKSPACE_PATH=${WORKSPACE_PATH:-$HOME}
    if claude mcp add --scope user --transport stdio filesystem -- npx -y @modelcontextprotocol/server-filesystem "$WORKSPACE_PATH"; then
        print_success "filesystem installed (path: $WORKSPACE_PATH)"
    else
        print_error "Failed to install filesystem"
    fi

    # github (if token provided)
    if [ -n "$GITHUB_TOKEN" ]; then
        print_info "Installing: github"
        if claude mcp add --scope user --transport stdio --env GITHUB_TOKEN="$GITHUB_TOKEN" github -- npx -y @modelcontextprotocol/server-github; then
            print_success "github installed"
        else
            print_error "Failed to install github"
        fi
    fi

    # brave-search (if API key provided)
    if [ -n "$BRAVE_API_KEY" ]; then
        print_info "Installing: brave-search"
        if claude mcp add --scope user --transport stdio --env BRAVE_API_KEY="$BRAVE_API_KEY" brave-search -- npx -y @modelcontextprotocol/server-brave-search; then
            print_success "brave-search installed"
        else
            print_error "Failed to install brave-search"
        fi
    fi

    # memory
    print_info "Installing: memory"
    if claude mcp add --scope user --transport stdio memory -- npx -y @modelcontextprotocol/server-memory; then
        print_success "memory installed"
    else
        print_error "Failed to install memory"
    fi

    # puppeteer
    print_info "Installing: puppeteer"
    if claude mcp add --scope user --transport stdio puppeteer -- npx -y @modelcontextprotocol/server-puppeteer; then
        print_success "puppeteer installed"
    else
        print_error "Failed to install puppeteer"
    fi

    echo ""
}

# Install custom PM-Agents MCP servers
install_custom_mcp_servers() {
    print_header "Installing Custom PM-Agents MCP Servers"

    print_warning "Custom MCP servers (@pm-agents/*) are not yet published to npm."
    print_warning "Skipping installation. These will be available after Phase 3 implementation."

    # When published, uncomment:
    # print_info "Installing: @pm-agents/mcp-qdrant"
    # if claude mcp add --scope user --transport stdio --env QDRANT_URL="$QDRANT_URL" qdrant -- npx -y @pm-agents/mcp-qdrant; then
    #     print_success "@pm-agents/mcp-qdrant installed"
    # else
    #     print_error "Failed to install @pm-agents/mcp-qdrant"
    # fi

    # print_info "Installing: @pm-agents/mcp-tensorboard"
    # if claude mcp add --scope user --transport stdio tensorboard -- npx -y @pm-agents/mcp-tensorboard; then
    #     print_success "@pm-agents/mcp-tensorboard installed"
    # else
    #     print_error "Failed to install @pm-agents/mcp-tensorboard"
    # fi

    # print_info "Installing: @pm-agents/mcp-specify"
    # if claude mcp add --scope user --transport stdio specify -- npx -y @pm-agents/mcp-specify; then
    #     print_success "@pm-agents/mcp-specify installed"
    # else
    #     print_error "Failed to install @pm-agents/mcp-specify"
    # fi

    echo ""
}

# Setup Qdrant (Docker)
setup_qdrant() {
    print_header "Setting Up Qdrant Vector Database"

    if ! command -v docker &> /dev/null; then
        print_warning "Docker not found. Install Docker to run Qdrant locally."
        print_info "Alternative: Use Qdrant Cloud at https://cloud.qdrant.io/"
        return
    fi

    print_info "Checking if Qdrant is already running..."
    if docker ps | grep -q qdrant; then
        print_success "Qdrant container already running"
        return
    fi

    print_info "Starting Qdrant container..."
    if docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest; then
        print_success "Qdrant started at http://localhost:6333"
        print_info "Qdrant Dashboard: http://localhost:6333/dashboard"
    else
        print_error "Failed to start Qdrant. Check Docker installation."
    fi

    echo ""
}

# Verify installation
verify_installation() {
    print_header "Verifying MCP Server Installation"

    # List installed MCP servers
    print_info "Installed MCP servers:"
    if claude mcp list; then
        print_success "MCP servers listed successfully"
    else
        print_error "Failed to list MCP servers"
    fi

    echo ""
}

# Generate configuration summary
generate_summary() {
    print_header "Installation Summary"

    cat <<EOF

✅ Installation Complete!

Installed MCP Servers:
  • filesystem      - File operations
  • memory          - Agent memory
  • puppeteer       - Browser automation
EOF

    if [ -n "$GITHUB_TOKEN" ]; then
        echo "  • github          - Repository operations"
    fi

    if [ -n "$BRAVE_API_KEY" ]; then
        echo "  • brave-search    - Web research"
    fi

    if docker ps | grep -q qdrant; then
        echo ""
        echo "Qdrant Vector Database:"
        echo "  • URL: http://localhost:6333"
        echo "  • Dashboard: http://localhost:6333/dashboard"
    fi

    cat <<EOF

Next Steps:
  1. Verify installation: ./scripts/verify_mcp_servers.sh
  2. Run PM-Agents: python pm_coordinator_agent.py
  3. Check documentation: ./docs/ or https://pm-agents.dev

Configuration Files:
  • MCP config: ~/.claude/mcp_servers.json
  • PM-Agents config: ./config/pm-agents.yaml (create if needed)

Troubleshooting:
  • MCP servers not working: claude mcp list
  • Qdrant not accessible: docker ps | grep qdrant
  • API key issues: Check ~/.claude/mcp_servers.json

For support: https://github.com/pm-agents/pm-agents/issues

EOF

    print_success "Setup complete! 🎉"
}

# Main installation flow
main() {
    echo ""
    print_header "PM-Agents MCP Server Installation"
    echo ""

    check_prerequisites
    collect_api_keys
    install_essential_mcp_servers
    install_custom_mcp_servers
    setup_qdrant
    verify_installation
    generate_summary
}

# Run main
main
