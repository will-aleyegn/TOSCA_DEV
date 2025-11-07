# Claude Code WSL Migration Package

**Version:** 1.0
**Generated:** 2025-11-04
**Source:** Windows 10/11 with Git Bash
**Target:** WSL2 Ubuntu/Debian

---

## 📦 Package Contents

This directory contains everything needed to migrate your Claude Code setup from Windows to WSL:

```
.claude/
├── MIGRATION_README.md                 # This file - start here
├── MIGRATION_PACKAGE.md                # Complete migration documentation
├── MEMORY_RESTORE_INSTRUCTIONS.md      # Memory MCP server restoration guide
├── migrate_to_wsl.sh                   # Automated migration script (executable)
├── memory_export_raw.txt               # Memory graph marker file
├── settings.json                       # Claude Code settings (hooks, permissions)
└── (copy to WSL) ../mcp.json          # MCP server configuration

Project root files to copy:
├── .mcp.json                           # MCP server configuration
└── (entire TOSCA-dev directory)       # Your project files
```

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- WSL2 installed (Ubuntu 20.04+ or Debian 11+ recommended)
- Git for Windows (to access these files)

### Step 1: Copy Files to WSL

From Windows Git Bash or PowerShell:

```bash
# Option A: Direct copy (if you can see WSL filesystem)
cp -r /c/Users/wille/Desktop/TOSCA-dev /mnt/c/temp/
# Then from WSL: cp -r /mnt/c/temp/TOSCA-dev ~/projects/

# Option B: Use git (recommended)
# From WSL:
cd ~/projects
git clone https://github.com/will-aleyegn/TOSCA_DEV.git TOSCA-dev
cd TOSCA-dev
```

### Step 2: Copy Migration Package

```bash
# From Windows, copy .claude directory to WSL-accessible location
cp -r .claude /mnt/c/temp/claude-migration/

# From WSL
cd ~/projects/TOSCA-dev
cp -r /mnt/c/temp/claude-migration/.claude .
```

### Step 3: Run Migration Script

```bash
cd ~/projects/TOSCA-dev/.claude
bash migrate_to_wsl.sh
```

The script will:
1. Check all dependencies (Node.js, npm, jq, git)
2. Create `.claude/settings.json` with hooks and permissions
3. Create `.mcp.json` with MCP server configuration
4. Test MCP server connectivity
5. Provide next steps for memory restoration

### Step 4: Update API Keys

```bash
cd ~/projects/TOSCA-dev
nano .mcp.json

# Replace placeholder API keys:
# - ANTHROPIC_API_KEY
# - PERPLEXITY_API_KEY
# - (others as needed)
```

### Step 5: Start Claude Code

```bash
cd ~/projects/TOSCA-dev
claude
```

---

## 📋 Detailed Migration Options

### Option 1: Automated (Recommended)

Use the included `migrate_to_wsl.sh` script (see Quick Start above).

**Pros:**
- Fast (5 minutes)
- Automated dependency checking
- Error handling built-in
- Creates all necessary files

**Cons:**
- Requires bash and standard Unix tools
- May need manual API key updates

### Option 2: Manual Configuration

If you prefer manual setup or need to customize:

1. **Read MIGRATION_PACKAGE.md** - Complete documentation
2. **Follow step-by-step instructions** - Each section has detailed steps
3. **Manually create settings.json** - Copy from template
4. **Manually create .mcp.json** - Convert Windows paths to WSL
5. **Test each MCP server** - Verify connectivity

**Pros:**
- Full control over configuration
- Better understanding of setup
- Can customize for your environment

**Cons:**
- Slower (20-30 minutes)
- More error-prone
- Requires understanding of JSON configuration

### Option 3: Hybrid Approach

1. Run `migrate_to_wsl.sh` to create base configuration
2. Manually customize settings afterward
3. Best of both worlds: automation + customization

---

## 🧠 Memory Migration

Your Windows environment contains **36 entities and 43 relations** in the Memory MCP knowledge graph. This is **critical context** for TOSCA project continuity.

### Memory Restoration Options

#### Option A: Full Restoration (Recommended)
Restore all 36 entities to maintain complete project context.

**Time:** 15-30 minutes automated, 2-3 hours manual
**See:** MEMORY_RESTORE_INSTRUCTIONS.md

#### Option B: Selective Restoration
Restore only priority entities (project core + hardware modules).

**Time:** 10-15 minutes
**Entities:** ~15 critical entities
**See:** MEMORY_RESTORE_INSTRUCTIONS.md → Priority 1-2 sections

#### Option C: Fresh Start
Start with empty memory and rebuild naturally.

**Time:** 0 minutes (but loses 2+ months of context)
**Recommendation:** At least restore Priority 1-2 entities

### Memory Restoration Process

After Claude Code is running in WSL:

```bash
cd ~/projects/TOSCA-dev
claude

# In Claude Code session:
# "Please help me restore my project memory using the instructions in
#  .claude/MEMORY_RESTORE_INSTRUCTIONS.md"
```

Claude will read the instructions and execute the necessary MCP tool calls.

---

## 🔧 Configuration Deep Dive

### Hooks Configured

#### 1. StatusLine Hook
**Purpose:** Custom status bar showing model, directory, Node version, Claude version

**Command:**
```bash
bash -c 'input=$(cat); MODEL=$(echo "$input" | jq -r ".model.display_name"); DIR=$(echo "$input" | jq -r ".workspace.current_dir"); VERSION=$(echo "$input" | jq -r ".version"); NODE_VER=$(node --version 2>/dev/null || echo "N/A"); echo "[$MODEL] 📁 ${DIR##*/} | Node $NODE_VER | Claude $VERSION"'
```

**Requirements:**
- `jq` (JSON processor)
- `node` (Node.js runtime)

**Output Example:**
```
[Claude Sonnet 4] 📁 TOSCA-dev | Node v22.15.0 | Claude 0.4.0
```

### Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | 16000 | Increase max output length |
| `DISABLE_NON_ESSENTIAL_MODEL_CALLS` | 1 | Reduce API usage |
| `DISABLE_COST_WARNINGS` | 1 | Hide cost warnings |
| `USE_BUILTIN_RIPGREP` | 1 | Use built-in ripgrep |
| `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR` | 1 | Stay in project directory |
| `CLAUDE_CODE_DISABLE_TERMINAL_TITLE` | 0 | Enable terminal title updates |

### Permission Allowlist

**Auto-approved tools:**
- Bash: npm, yarn, node, git, docker, python, pip
- Read: All .json, .js, .ts, .py files
- Edit: All .js, .ts, .py, .json files
- Write: All .js, .ts, .py files
- Git operations: status, diff, add, commit, push, pull, log
- npm scripts: lint, test, build, start

**Denied operations:**
- Reading .env files and secrets/
- `rm -rf` (destructive file removal)
- `sudo` (privilege escalation)

### MCP Servers

| Server | Package | Purpose |
|--------|---------|---------|
| **context7** | @upstash/context7-mcp | Library documentation |
| **memory** | @modelcontextprotocol/server-memory | Knowledge graph |
| **github** | @modelcontextprotocol/server-github | GitHub integration (disabled) |
| **filesystem** | @modelcontextprotocol/server-filesystem | File system access |
| **task-master-ai** | task-master-ai | Task management |

---

## 🐛 Troubleshooting

### Issue: "npx not found"

```bash
# Install Node.js via nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 22.15.0
nvm use 22.15.0
```

### Issue: "jq: command not found"

```bash
sudo apt update
sudo apt install -y jq
```

### Issue: "Memory server timeout"

This is normal on first run as npx downloads the package.

```bash
# Wait 30-60 seconds, then try again
npx -y @modelcontextprotocol/server-memory --version
```

### Issue: "Permission denied" on migrate_to_wsl.sh

```bash
chmod +x .claude/migrate_to_wsl.sh
bash .claude/migrate_to_wsl.sh
```

### Issue: MCP servers not starting

```bash
# Clear npx cache
rm -rf ~/.npm/_npx

# Reinstall MCP servers
npx -y @upstash/context7-mcp --version
npx -y @modelcontextprotocol/server-memory --version
npx -y @modelcontextprotocol/server-filesystem --version
```

### Issue: Windows line endings (CRLF) in WSL

```bash
# Convert line endings
dos2unix .claude/migrate_to_wsl.sh

# Or manually
sed -i 's/\r$//' .claude/migrate_to_wsl.sh
```

---

## ✅ Verification Checklist

After migration, verify everything is working:

- [ ] Node.js installed (v22.15.0+)
- [ ] npm installed (v10.9.2+)
- [ ] jq installed
- [ ] git installed
- [ ] `.claude/settings.json` exists and valid
- [ ] `.mcp.json` exists with correct paths
- [ ] API keys updated in `.mcp.json`
- [ ] Claude Code starts without errors
- [ ] StatusLine hook displays correctly
- [ ] MCP servers connect (check with debug mode)
- [ ] Memory server accessible
- [ ] Task Master AI accessible
- [ ] Project files accessible
- [ ] Git repository working

**Full verification:**
```bash
cd ~/projects/TOSCA-dev
claude

# In Claude Code:
# "Please verify my setup by:
#  1. Checking statusLine hook
#  2. Testing memory server with mcp__memory__read_graph
#  3. Testing filesystem server by reading README.md
#  4. Confirming git status works"
```

---

## 📚 Additional Resources

### Documentation Files

| File | Purpose |
|------|---------|
| `MIGRATION_PACKAGE.md` | Complete migration guide with all configuration details |
| `MEMORY_RESTORE_INSTRUCTIONS.md` | Step-by-step memory restoration with entity/relation data |
| `MIGRATION_README.md` | This file - migration overview and quick start |

### External Resources

- **Claude Code Docs:** https://docs.anthropic.com/claude/docs/claude-code
- **MCP Documentation:** https://modelcontextprotocol.io/
- **Task Master AI:** https://github.com/TaskMasterAI/task-master-ai
- **WSL Documentation:** https://docs.microsoft.com/en-us/windows/wsl/

### Project-Specific Resources

- **TOSCA README.md** - Project overview
- **CLAUDE.md** - AI assistant context (auto-loaded)
- **.taskmaster/CLAUDE.md** - Task Master integration guide
- **presubmit/** - Internal development documentation

---

## 🎯 Next Steps After Migration

1. **Restore Memory** (see MEMORY_RESTORE_INSTRUCTIONS.md)
2. **Configure Git:**
   ```bash
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```
3. **Install Python Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Test Hardware Connections** (if applicable):
   ```bash
   # Update COM ports in config.yaml for WSL
   # Windows COM ports may be /dev/ttyS* in WSL
   ```
5. **Run Pre-commit Hooks:**
   ```bash
   pre-commit install
   pre-commit run --all-files
   ```

---

## 🤝 Support

If you encounter issues:

1. **Check troubleshooting section** in this document
2. **Review MIGRATION_PACKAGE.md** for detailed configuration
3. **Check Claude Code logs:** Usually in `~/.claude/logs/`
4. **Test each component individually:** Node, npm, jq, MCP servers
5. **Ask Claude Code for help:** It can debug its own configuration!

---

## 📝 Migration Log Template

Keep track of your migration:

```markdown
## Migration Log

**Date:** 2025-11-04
**Migrated by:** [Your Name]

### Pre-Migration Checklist
- [ ] Backed up Windows .claude directory
- [ ] Backed up .mcp.json
- [ ] Exported API keys
- [ ] Committed all git changes

### Migration Steps
- [ ] Copied files to WSL (Time: ___ mins)
- [ ] Ran migrate_to_wsl.sh (Time: ___ mins)
- [ ] Updated API keys
- [ ] Tested Claude Code startup
- [ ] Restored memory (Time: ___ mins)
- [ ] Verified all MCP servers

### Post-Migration Notes
- Issues encountered: ___
- Resolutions applied: ___
- Configuration changes: ___
- Performance notes: ___

### Verification Results
- StatusLine hook: ✓/✗
- Memory server: ✓/✗
- Task Master: ✓/✗
- Filesystem access: ✓/✗
- Git operations: ✓/✗

**Total migration time:** ___ hours
```

---

**Last Updated:** 2025-11-04
**Package Version:** 1.0
**Estimated Migration Time:** 30-60 minutes (full setup + memory)
**Support:** See troubleshooting section or ask Claude Code for help

Good luck with your migration! 🚀
