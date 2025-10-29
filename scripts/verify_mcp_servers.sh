#!/bin/bash

###############################################################################
# PM-Agents MCP Server Verification Script (Linux/macOS)
###############################################################################
#
# This script verifies that all MCP servers are properly installed and functional.
#
# Usage:
#   chmod +x verify_mcp_servers.sh
#   ./verify_mcp_servers.sh
#
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Test MCP server
test_mcp_server() {
    local server_name=$1
    local server_command=$2

    print_info "Testing $server_name..."

    # Test if server responds to tools/list
    if echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | $server_command 2>/dev/null | grep -q "tools"; then
        print_success "$server_name is working"
        return 0
    else
        print_error "$server_name failed to respond"
        return 1
    fi
}

# Main verification
main() {
    print_header "PM-Agents MCP Server Verification"
    echo ""

    local total_tests=0
    local passed_tests=0

    # Test essential MCP servers
    print_header "Testing Essential MCP Servers"

    # filesystem
    ((total_tests++))
    if test_mcp_server "filesystem" "npx -y @modelcontextprotocol/server-filesystem /tmp"; then
        ((passed_tests++))
    fi

    # github (requires GITHUB_TOKEN)
    if [ -n "$GITHUB_TOKEN" ]; then
        ((total_tests++))
        if test_mcp_server "github" "GITHUB_TOKEN=$GITHUB_TOKEN npx -y @modelcontextprotocol/server-github"; then
            ((passed_tests++))
        fi
    else
        print_warning "Skipping github (GITHUB_TOKEN not set)"
    fi

    # brave-search (requires BRAVE_API_KEY)
    if [ -n "$BRAVE_API_KEY" ]; then
        ((total_tests++))
        if test_mcp_server "brave-search" "BRAVE_API_KEY=$BRAVE_API_KEY npx -y @modelcontextprotocol/server-brave-search"; then
            ((passed_tests++))
        fi
    else
        print_warning "Skipping brave-search (BRAVE_API_KEY not set)"
    fi

    # memory
    ((total_tests++))
    if test_mcp_server "memory" "npx -y @modelcontextprotocol/server-memory"; then
        ((passed_tests++))
    fi

    # puppeteer
    ((total_tests++))
    if test_mcp_server "puppeteer" "npx -y @modelcontextprotocol/server-puppeteer"; then
        ((passed_tests++))
    fi

    echo ""

    # Test custom MCP servers (when published)
    print_header "Testing Custom PM-Agents MCP Servers"
    print_warning "Custom MCP servers (@pm-agents/*) not yet published. Skipping tests."

    # Uncomment when published:
    # ((total_tests++))
    # if test_mcp_server "qdrant" "QDRANT_URL=${QDRANT_URL:-http://localhost:6333} npx -y @pm-agents/mcp-qdrant"; then
    #     ((passed_tests++))
    # fi

    # ((total_tests++))
    # if test_mcp_server "tensorboard" "npx -y @pm-agents/mcp-tensorboard"; then
    #     ((passed_tests++))
    # fi

    # ((total_tests++))
    # if test_mcp_server "specify" "npx -y @pm-agents/mcp-specify"; then
    #     ((passed_tests++))
    # fi

    echo ""

    # Test Qdrant availability
    print_header "Testing Qdrant Vector Database"
    if curl -s http://localhost:6333/healthz > /dev/null 2>&1; then
        print_success "Qdrant is accessible at http://localhost:6333"
        ((total_tests++))
        ((passed_tests++))
    else
        print_error "Qdrant is not accessible. Start with: docker run -d -p 6333:6333 qdrant/qdrant"
        ((total_tests++))
    fi

    echo ""

    # Summary
    print_header "Verification Summary"
    echo ""
    echo "Tests passed: $passed_tests / $total_tests"

    if [ $passed_tests -eq $total_tests ]; then
        print_success "All tests passed! ✅"
        echo ""
        echo "Your PM-Agents MCP setup is ready to use."
        exit 0
    else
        failed=$((total_tests - passed_tests))
        print_warning "$failed test(s) failed"
        echo ""
        echo "Some MCP servers are not working correctly."
        echo "Check the errors above and run: ./install_mcp_servers.sh"
        exit 1
    fi
}

main
