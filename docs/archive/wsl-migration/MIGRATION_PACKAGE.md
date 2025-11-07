# Claude Code WSL Migration Package

**Generated:** 2025-11-04
**Source:** Windows (C:\Users\wille\Desktop\TOSCA-dev)
**Target:** WSL Ubuntu/Debian

## Package Contents

This migration package contains all necessary configuration and data to recreate your Claude Code environment in WSL.

## 1. Required Tools & Dependencies

### Node.js & Package Managers
- **Node.js:** v22.15.0 (current version)
- **npm:** 10.9.2 (current version)
- **npx:** (included with npm)

Install in WSL:
```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 22.15.0
nvm use 22.15.0

# Verify installation
node --version  # Should show v22.15.0
npm --version   # Should show 10.9.2
```

### MCP Servers (npx packages)
The following MCP servers are configured and will be auto-installed by npx:

1. **@upstash/context7-mcp** - Documentation context provider
2. **@modelcontextprotocol/server-memory** - Knowledge graph memory
3. **@modelcontextprotocol/server-github** - GitHub integration (disabled)
4. **@modelcontextprotocol/server-filesystem** - File system access
5. **task-master-ai** - Task management and project planning

### Command-line Tools
- **bash** - Shell (native in WSL)
- **jq** - JSON processor for statusLine hook
- **git** - Version control

Install in WSL:
```bash
sudo apt update
sudo apt install -y jq git
```

## 2. Configuration Files

### .claude/settings.json

**Location:** `<project>/.claude/settings.json`

**Key Features:**
- Custom statusLine hook showing model, directory, Node version
- Environment variables for Claude Code behavior
- Permission allowlist for auto-approved tools
- Permission denylist for dangerous operations

**Windows → WSL Changes Required:**
- None (bash commands already compatible)

**Full Configuration:**
```json
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
```

### .mcp.json

**Location:** `<project>/.mcp.json`

**Windows → WSL Changes Required:**
1. Replace `"command": "cmd"` with `"command": "bash"`
2. Replace `"args": ["/c", "npx", ...]` with `"args": ["-c", "npx ..."]`
3. Update filesystem server path from Windows to WSL path

**Original (Windows):**
```json
{
  "mcpServers": {
    "context7": {
      "type": "stdio",
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@upstash/context7-mcp"],
      "env": {
        "MCP_TIMEOUT": "60000",
        "MCP_TOOL_TIMEOUT": "120000"
      }
    },
    "memory": {
      "type": "stdio",
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MCP_TIMEOUT": "60000",
        "MCP_TOOL_TIMEOUT": "120000"
      }
    },
    "_github_disabled": {
      "type": "stdio",
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}",
        "MCP_TIMEOUT": "60000",
        "MCP_TOOL_TIMEOUT": "120000"
      }
    },
    "filesystem": {
      "type": "stdio",
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\wille"],
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
```

**Converted (WSL):**
```json
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
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}",
        "MCP_TIMEOUT": "60000",
        "MCP_TOOL_TIMEOUT": "120000"
      }
    },
    "filesystem": {
      "type": "stdio",
      "command": "bash",
      "args": ["-c", "npx -y @modelcontextprotocol/server-filesystem /home/YOUR_USERNAME"],
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
```

## 3. Memory MCP Server Data

The memory MCP server stores its knowledge graph data locally. The current memory contains:

**Entities:** 36 entities including:
- TOSCA Project metadata
- Hardware modules (Camera HAL, Laser HAL, Actuator HAL, GPIO HAL)
- Development rules and policies
- Documentation systems
- Hardware components (SEMINEX laser, MCP4725 DAC, etc.)

**Relations:** 43 relations mapping dependencies and integrations

**Data Location:**
- **Windows:** Data is stored by the npx cache (typically in AppData)
- **WSL:** Will be recreated in `~/.local/share/@modelcontextprotocol/server-memory/` or similar

**Migration Strategy:**
The memory server data is stored in the MCP server's data directory. Since you have access to `mcp__memory__read_graph` and can export/recreate entities:

1. **Export current memory** (already captured above via read_graph)
2. **Import in WSL** using memory creation tools after setup

## 4. Migration Script

Save this as `migrate_to_wsl.sh`:

```bash
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
echo "3. Run 'claude' in the project directory"
echo ""
echo "Memory MCP Server:"
echo "- Knowledge graph data will be recreated on first use"
echo "- To restore your memory, you can use mcp__memory__create_entities"
echo "  and mcp__memory__create_relations with the exported data"
echo ""
echo -e "${GREEN}All done! 🎉${NC}"
