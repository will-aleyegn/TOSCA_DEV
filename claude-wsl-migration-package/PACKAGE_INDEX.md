# Claude Code WSL Migration Package - Index

**Package Version:** 1.0
**Created:** 2025-11-04
**Source Environment:** Windows 10/11 (Git Bash)
**Target Environment:** WSL2 Ubuntu/Debian

---

## 📦 Package Contents

```
claude-wsl-migration-package/
├── PACKAGE_INDEX.md                    # This file - package manifest
├── MIGRATION_README.md                 # START HERE - Quick start guide
├── MIGRATION_PACKAGE.md                # Complete documentation
├── MEMORY_RESTORE_INSTRUCTIONS.md      # Memory restoration guide
├── migrate_to_wsl.sh                   # Automated setup script
├── settings.json                       # Claude Code settings (ready to use)
├── mcp.json.windows                    # Original Windows MCP config (reference)
└── mcp.json.wsl                        # WSL-ready MCP config (template)
```

---

## 🚀 Quick Start

### Copy Package to WSL

**Option 1: Via Windows filesystem mount**
```bash
# From WSL
cp -r /mnt/c/Users/wille/Desktop/TOSCA-dev/claude-wsl-migration-package ~/
cd ~/claude-wsl-migration-package
```

**Option 2: Via git repository**
```bash
# This package is in your TOSCA-dev/.claude/ directory
# After cloning TOSCA-dev in WSL, the package is already there
cd ~/projects/TOSCA-dev/claude-wsl-migration-package
```

### Run Automated Setup

```bash
cd ~/claude-wsl-migration-package
bash migrate_to_wsl.sh
```

**The script will:**
1. Check dependencies (Node.js v22.15.0, npm, jq, git)
2. Prompt for project path (e.g., `/home/username/projects/TOSCA-dev`)
3. Create `.claude/settings.json` with hooks and permissions
4. Create `.mcp.json` with WSL-compatible MCP server config
5. Test MCP server connectivity
6. Display next steps

---

## 📄 File Descriptions

### Core Documentation

| File | Purpose | Read When |
|------|---------|-----------|
| **MIGRATION_README.md** | Quick start + troubleshooting | Start here first |
| **MIGRATION_PACKAGE.md** | Complete technical docs | Need configuration details |
| **MEMORY_RESTORE_INSTRUCTIONS.md** | Memory MCP restoration | After basic setup complete |
| **PACKAGE_INDEX.md** | This file - package overview | Getting oriented |

### Configuration Files

| File | Purpose | Usage |
|------|---------|-------|
| **settings.json** | Claude Code settings (hooks + permissions) | Auto-copied by script |
| **mcp.json.wsl** | WSL-ready MCP server config | Template for manual setup |
| **mcp.json.windows** | Original Windows config | Reference only |

### Scripts

| File | Purpose | When to Run |
|------|---------|-------------|
| **migrate_to_wsl.sh** | Automated setup | First step after copying to WSL |

---

## 🎯 Migration Workflow

```
┌─────────────────────────────────────────────────────────┐
│ 1. Copy package to WSL                                  │
│    ~/claude-wsl-migration-package/                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Run migrate_to_wsl.sh                                │
│    - Checks dependencies                                │
│    - Creates .claude/settings.json                      │
│    - Creates .mcp.json                                  │
│    - Tests MCP servers                                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Update API keys in .mcp.json                         │
│    - ANTHROPIC_API_KEY (required)                       │
│    - PERPLEXITY_API_KEY (recommended)                   │
│    - Others (optional)                                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Copy TOSCA-dev project files                         │
│    - Git clone or direct copy                           │
│    - Includes all source, docs, configs                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 5. Start Claude Code                                    │
│    cd ~/projects/TOSCA-dev                              │
│    claude                                               │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 6. Restore Memory (optional but recommended)            │
│    See MEMORY_RESTORE_INSTRUCTIONS.md                   │
│    36 entities, 43 relations                            │
└─────────────────────────────────────────────────────────┘
```

---

## 🧠 What Gets Migrated

### Hooks
- ✅ **StatusLine Hook** - Custom status bar (model, directory, Node version)

### MCP Servers (5 total)
- ✅ **context7** - Library documentation lookup
- ✅ **memory** - Knowledge graph (36 entities, 43 relations)
- ✅ **filesystem** - File system access
- ✅ **task-master-ai** - Task management
- ⚠️ **github** - GitHub integration (disabled, can enable later)

### Permissions
- ✅ **Auto-approved tools** - npm, git, python, read/write JS/TS/PY
- ✅ **Denied operations** - .env files, rm -rf, sudo

### Environment Variables
- ✅ **6 Claude Code settings** - Output tokens, cost warnings, ripgrep, etc.

### Memory Knowledge Graph
- ✅ **36 entities** - Project, modules, hardware, documentation
- ✅ **43 relations** - Dependencies and integrations
- ℹ️ **Restoration required** - See MEMORY_RESTORE_INSTRUCTIONS.md

---

## 🔧 Dependencies Required in WSL

The migration script will check for these:

| Dependency | Version | Required | Install Command |
|------------|---------|----------|-----------------|
| **Node.js** | v22.15.0+ | Yes | `nvm install 22.15.0` |
| **npm** | v10.9.2+ | Yes | Included with Node.js |
| **jq** | Latest | Yes | `sudo apt install jq` |
| **git** | Latest | Yes | `sudo apt install git` |
| **bash** | v4.0+ | Yes | Built-in to WSL |

---

## 📊 Package Statistics

- **Total files:** 8 files
- **Documentation:** 4 files (12,000+ words)
- **Configuration:** 3 files (JSON + shell script)
- **Package size:** ~150 KB (text only)
- **Migration time:** 30-60 minutes (including memory restoration)

---

## ✅ Pre-Migration Checklist

Before copying to WSL:

- [ ] All files present in package (8 files)
- [ ] migrate_to_wsl.sh is executable (`chmod +x`)
- [ ] Have API keys ready (ANTHROPIC_API_KEY minimum)
- [ ] Know target WSL username
- [ ] WSL2 installed and updated
- [ ] Have Git credentials ready for TOSCA-dev clone

---

## 📋 Post-Migration Checklist

After running migrate_to_wsl.sh:

- [ ] Node.js v22.15.0+ installed
- [ ] npm v10.9.2+ installed
- [ ] jq installed
- [ ] git installed
- [ ] `.claude/settings.json` created
- [ ] `.mcp.json` created
- [ ] API keys updated in `.mcp.json`
- [ ] Claude Code starts without errors
- [ ] StatusLine hook displays correctly
- [ ] MCP servers connect
- [ ] Memory restoration completed (optional)

---

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| "npx not found" | Install Node.js via nvm (see MIGRATION_README.md) |
| "jq not found" | `sudo apt install jq` |
| "Permission denied" on script | `chmod +x migrate_to_wsl.sh` |
| MCP server timeout | Normal on first run, wait 60 seconds |
| Windows line endings | `dos2unix migrate_to_wsl.sh` |

For detailed troubleshooting, see MIGRATION_README.md.

---

## 📚 Reading Order

**First time migrating?** Read in this order:

1. **PACKAGE_INDEX.md** (this file) - 5 minutes
2. **MIGRATION_README.md** - 10 minutes
3. **Run migrate_to_wsl.sh** - 5 minutes
4. **MIGRATION_PACKAGE.md** (if needed) - Reference
5. **MEMORY_RESTORE_INSTRUCTIONS.md** - 15 minutes

**Total time:** 35 minutes reading + 30 minutes doing = ~1 hour

---

## 🔗 External Resources

- **Claude Code Docs:** https://docs.anthropic.com/claude/docs/claude-code
- **MCP Protocol:** https://modelcontextprotocol.io/
- **Task Master AI:** https://github.com/TaskMasterAI/task-master-ai
- **WSL Installation:** https://docs.microsoft.com/en-us/windows/wsl/install
- **nvm (Node Version Manager):** https://github.com/nvm-sh/nvm

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-04 | Initial package creation |

---

## 🤝 Support

1. **Check MIGRATION_README.md** troubleshooting section
2. **Review MIGRATION_PACKAGE.md** for technical details
3. **Ask Claude Code for help** - It can debug its own setup!
4. **Check Claude Code logs** - Usually in `~/.claude/logs/`

---

**Package ready for WSL migration** ✓

**Next step:** Copy this entire folder to WSL and run `bash migrate_to_wsl.sh`
