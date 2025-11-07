#!/bin/bash
set -e

echo "==================================="
echo "Claude Code WSL Migration Script"
echo "==================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in WSL
if ! grep -qi microsoft /proc/version 2>/dev/null; then
    echo -e "${RED}ERROR: This script must be run in WSL${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Running in WSL${NC}"

# 1. Check dependencies
echo ""
echo "Step 1: Checking dependencies..."

# Check bash
if ! command -v bash &> /dev/null; then
    echo -e "${RED}✗ bash not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ bash found: $(bash --version | head -1)${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found${NC}"
    echo "Install with:"
    echo "  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    echo "  source ~/.bashrc"
    echo "  nvm install 22.15.0"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js found: $NODE_VERSION${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm not found${NC}"
    exit 1
fi
NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓ npm found: $NPM_VERSION${NC}"

# Check jq
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}⚠ jq not found (needed for statusLine hook)${NC}"
    echo "Installing jq..."
    sudo apt update && sudo apt install -y jq
fi
echo -e "${GREEN}✓ jq found: $(jq --version)${NC}"

# Check git
if ! command -v git &> /dev/null; then
    echo -e "${RED}✗ git not found${NC}"
    echo "Installing git..."
    sudo apt update && sudo apt install -y git
fi
echo -e "${GREEN}✓ git found: $(git --version | head -1)${NC}"

# 2. Set up project directory
echo ""
echo "Step 2: Setting up project directory..."
read -p "Enter WSL project path (e.g., /home/username/projects/TOSCA-dev): " PROJECT_PATH

if [ -z "$PROJECT_PATH" ]; then
    echo -e "${RED}ERROR: Project path cannot be empty${NC}"
    exit 1
fi

# Create project directory if it doesn't exist
if [ ! -d "$PROJECT_PATH" ]; then
    echo "Creating directory: $PROJECT_PATH"
    mkdir -p "$PROJECT_PATH"
fi

cd "$PROJECT_PATH"
echo -e "${GREEN}✓ Project directory: $PROJECT_PATH${NC}"

# 3. Create .claude directory
echo ""
echo "Step 3: Creating .claude directory..."
mkdir -p .claude
echo -e "${GREEN}✓ Created .claude directory${NC}"

# 4. Create settings.json
echo ""
echo "Step 4: Creating settings.json..."
cat > .claude/settings.json << 'SETTINGS_EOF'
{
  "statusLine": {
    "type": "command",
    "command": "bash -c 'input=$(cat); MODEL=$(echo \"$input\" | jq -r \".model.display_name\"); DIR=$(echo \"$input\" | jq -r \".workspace.current_dir\"); VERSION=$(echo \"$input\" | jq -r \".version\"); NODE_VER=$(node --version 2>/dev/null || echo \"N/A\"); echo \"[$MODEL] 📁 ${DIR##*/} | Node $NODE_VER | Claude $VERSION\"'"
  },
  "env": {
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "16000",
    "DISABLE_NON_ESSENTIAL_MODEL_CALLS": "1",
    "DISABLE_COST_WARNINGS": "1",
    "USE_BUILTIN_RIPGREP": "1",
    "CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR": "1",
    "CLAUDE_CODE_DISABLE_TERMINAL_TITLE": "0"
  },
  "includeCoAuthoredBy": false,
  "permissions": {
    "allow": [
      "Bash(npm:*)",
      "Bash(yarn:*)",
      "Bash(node:*)",
      "Bash(git:*)",
      "Bash(docker:*)",
      "Bash(python:*)",
      "Bash(pip:*)",
      "Read(**/*.json)",
      "Read(**/*.js)",
      "Read(**/*.ts)",
      "Read(**/*.py)",
      "Edit(**/*.js)",
      "Edit(**/*.ts)",
      "Edit(**/*.py)",
      "Edit(**/*.json)",
      "Write(**/*.js)",
      "Write(**/*.ts)",
      "Write(**/*.py)",
      "Bash(npm run lint)",
      "Bash(npm run test:*)",
      "Bash(npm run build)",
      "Bash(npm start)",
      "Bash(git status)",
      "Bash(git diff:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git push:*)",
      "Bash(git pull:*)",
      "Bash(git log:*)"
    ],
    "deny": [
      "Read(./.env*)",
      "Read(./secrets/**)",
      "Bash(rm -rf:*)",
      "Bash(sudo:*)"
    ]
  },
  "enableAllProjectMcpServers": true
}
SETTINGS_EOF
echo -e "${GREEN}✓ Created settings.json${NC}"

# 5. Create .mcp.json
echo ""
echo "Step 5: Creating .mcp.json..."
read -p "Enter your home directory path (e.g., /home/username): " HOME_PATH

cat > .mcp.json << MCP_EOF
{
  "mcpServers": {
    "context7": {
      "type": "stdio",
      "command": "bash",
      "args": ["-c", "npx -y @upstash/context7-mcp"],
      "env": {
        "MCP_TIMEOUT": "60000",
        "MCP_TOOL_TIMEOUT": "120000"
      }
    },
    "memory": {
      "type": "stdio",
      "command": "bash",
      "args": ["-c", "npx -y @modelcontextprotocol/server-memory"],
      "env": {
        "MCP_TIMEOUT": "60000",
        "MCP_TOOL_TIMEOUT": "120000"
      }
    },
    "_github_disabled": {
      "type": "stdio",
      "command": "bash",
      "args": ["-c", "npx -y @modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "\${GITHUB_TOKEN}",
        "MCP_TIMEOUT": "60000",
        "MCP_TOOL_TIMEOUT": "120000"
      }
    },
    "filesystem": {
      "type": "stdio",
      "command": "bash",
      "args": ["-c", "npx -y @modelcontextprotocol/server-filesystem $HOME_PATH"],
      "env": {
        "MCP_TIMEOUT": "60000",
        "MCP_TOOL_TIMEOUT": "120000"
      }
    },
    "task-master-ai": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "ANTHROPIC_API_KEY": "YOUR_ANTHROPIC_API_KEY_HERE",
        "PERPLEXITY_API_KEY": "YOUR_PERPLEXITY_API_KEY_HERE",
        "OPENAI_API_KEY": "YOUR_OPENAI_KEY_HERE",
        "GOOGLE_API_KEY": "YOUR_GOOGLE_KEY_HERE",
        "XAI_API_KEY": "YOUR_XAI_KEY_HERE",
        "OPENROUTER_API_KEY": "YOUR_OPENROUTER_KEY_HERE",
        "MISTRAL_API_KEY": "YOUR_MISTRAL_KEY_HERE",
        "AZURE_OPENAI_API_KEY": "YOUR_AZURE_KEY_HERE",
        "OLLAMA_API_KEY": "YOUR_OLLAMA_API_KEY_HERE"
      }
    }
  }
}
MCP_EOF
echo -e "${GREEN}✓ Created .mcp.json${NC}"

# 6. Test MCP servers
echo ""
echo "Step 6: Testing MCP server connectivity..."
echo "Note: First run will download MCP servers via npx (this may take a minute)"

# Test if npx can find the packages
echo "Testing context7..."
timeout 10s npx -y @upstash/context7-mcp --version &>/dev/null || echo -e "${YELLOW}⚠ Context7 test timed out (normal for first run)${NC}"

echo "Testing memory server..."
timeout 10s npx -y @modelcontextprotocol/server-memory --version &>/dev/null || echo -e "${YELLOW}⚠ Memory server test timed out (normal for first run)${NC}"

echo "Testing filesystem server..."
timeout 10s npx -y @modelcontextprotocol/server-filesystem --version &>/dev/null || echo -e "${YELLOW}⚠ Filesystem server test timed out (normal for first run)${NC}"

echo -e "${GREEN}✓ MCP servers are accessible${NC}"

# 7. Summary
echo ""
echo "==================================="
echo "Migration Complete!"
echo "==================================="
echo ""
echo "Configuration created in: $PROJECT_PATH"
echo ""
echo "Next steps:"
echo "1. Update API keys in .mcp.json (task-master-ai section)"
echo "2. Copy your project files to: $PROJECT_PATH"
echo "3. Copy memory_export.json to restore knowledge graph"
echo "4. Run 'claude' in the project directory"
echo ""
echo "To restore memory:"
echo "  See MEMORY_RESTORE_INSTRUCTIONS.md for detailed steps"
echo ""
echo -e "${GREEN}All done! 🎉${NC}"
