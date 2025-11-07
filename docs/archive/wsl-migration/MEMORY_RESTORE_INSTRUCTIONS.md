# Memory MCP Server Restoration Guide

**Source:** Windows Claude Code Environment
**Target:** WSL Claude Code Environment
**Memory Entities:** 36 entities, 43 relations
**Generated:** 2025-11-04

## Overview

The Memory MCP Server stores a knowledge graph with entities and relations that provide context continuity across Claude Code sessions. This guide explains how to restore your Windows memory data in WSL.

## Memory Server Storage Location

The memory server stores data locally in:
- **Windows:** `%LOCALAPPDATA%\npm-cache\_npx\*\node_modules\@modelcontextprotocol\server-memory\`
- **WSL:** `~/.local/share/@modelcontextprotocol/server-memory/` or `~/.npm/_npx/*/node_modules/@modelcontextprotocol/server-memory/`

## Restoration Methods

### Method 1: Automated Batch Import (Recommended)

After setting up Claude Code in WSL, create a restoration script:

```bash
#!/bin/bash
# restore_memory.sh

# Navigate to your WSL project directory
cd /path/to/your/TOSCA-dev

# Start Claude Code in headless mode and execute memory restoration
claude -p "Please restore the TOSCA project memory by creating the following entities and relations using the mcp__memory__create_entities and mcp__memory__create_relations tools. I will provide the data in the next message."

# Then paste the entity and relation data from the sections below
```

### Method 2: Manual Recreation via Claude Code

1. Start Claude Code in your WSL project directory:
   ```bash
   cd /path/to/your/TOSCA-dev
   claude
   ```

2. Ask Claude to restore memory:
   ```
   Please use mcp__memory__create_entities to recreate my project memory.
   Create the entities from the exported data in .claude/MEMORY_RESTORE_INSTRUCTIONS.md
   ```

3. Claude will read this file and execute the necessary MCP tool calls.

### Method 3: Interactive Restoration

If you prefer to rebuild memory gradually as you work:

1. Start fresh with empty memory in WSL
2. As you work on the project, key context will be naturally added
3. After major milestones, use `mcp__memory__add_observations` to update entities

## Key Entities to Restore

The most critical entities for TOSCA project continuity:

### Priority 1: Project Core
- **TOSCA Project** - Main project metadata, phase status, repository info
- **Git Content Policy** - Public repository content restrictions
- **Hardware API Usage Rule** - Critical development rule

### Priority 2: Hardware Modules
- **Camera HAL** - Allied Vision camera integration
- **Laser Controller HAL** - Arroyo laser/TEC controllers
- **Actuator Controller HAL** - Xeryon linear stage
- **GPIO HAL** - Arduino safety interlocks

### Priority 3: Development Infrastructure
- **Coding Standards** - Development rules and pre-commit hooks
- **Development Workflow** - Before/during/after work checklists
- **Key Documentation Files** - Navigation to critical docs
- **Presubmit Folder** - Documentation system structure

### Priority 4: Hardware Components (New as of Nov 2025)
- **SEMINEX-2CM-004-189** - Dual-wavelength laser unit
- **MCP4725_DAC** - I2C DAC for aiming beam control
- **LDD200_Driver** - 200mA laser driver
- **Arduino_I2C_Bus** - Shared I2C architecture

### Priority 5: Lessons Learned
- **VmbPy API Quirks** - Camera API gotchas
- **Arduino GPIO Migration** - FT232H → Arduino Nano
- **Code Review Findings** - Historical quality improvements
- **Motor Vibration Calibration** - Calibration data (0.8g threshold)

## Entity Data Structure

Each entity follows this format:

```json
{
  "name": "Entity Name",
  "entityType": "Type",
  "observations": [
    "Observation 1",
    "Observation 2"
  ]
}
```

## Relation Data Structure

Each relation follows this format:

```json
{
  "from": "Source Entity",
  "to": "Target Entity",
  "relationType": "relationship type"
}
```

## Quick Restore Script

Save this as `quick_restore_memory.md` and paste into Claude Code:

````markdown
Please restore my TOSCA project memory using the following data.

Use mcp__memory__create_entities with this data (create in batches of 10 entities):

**Batch 1 - Project Core:**
1. TOSCA Project (entityType: "Project")
2. Git Content Policy (entityType: "Policy")
3. Hardware API Usage Rule (entityType: "Development Rule")
4. Coding Standards (entityType: "Development Rule")
5. Development Workflow (entityType: "Process")
6. Key Documentation Files (entityType: "Documentation")
7. Presubmit Folder (entityType: "Documentation System")
8. Manufacturer Documentation System (entityType: "Documentation")
9. TodoWrite Workflow (entityType: "Development Tool")
10. AI Tool Usage (entityType: "Development Practice")

**Batch 2 - Hardware Modules:**
1. Camera HAL (entityType: "Module")
2. Laser Controller HAL (entityType: "Module")
3. Actuator Controller HAL (entityType: "Module")
4. GPIO HAL (entityType: "Module")
5. Safety System (entityType: "Module")
6. Session Management (entityType: "Module")
7. Event Logging System (entityType: "Module")

**Batch 3 - Hardware Components:**
1. TOSCA Motor Control System (entityType: "hardware_system")
2. MPU6050 Accelerometer Integration (entityType: "hardware_system")
3. SEMINEX-2CM-004-189 (entityType: "hardware_component")
4. MCP4725_DAC (entityType: "hardware_component")
5. LDD200_Driver (entityType: "hardware_component")
6. Arduino_I2C_Bus (entityType: "hardware_architecture")

**Batch 4 - Lessons & Firmware:**
1. VmbPy API Quirks (entityType: "Lessons Learned")
2. Arduino GPIO Migration (entityType: "Lessons Learned")
3. Code Review Findings (2025-10-24) (entityType: "Lessons Learned")
4. Critical Motor-First Sequence Bug (entityType: "bug_fix")
5. Watchdog Timing Bug Fix (entityType: "bug_fix")
6. Motor Vibration Calibration (entityType: "calibration_data")
7. Arduino Watchdog Firmware v2.1 (entityType: "firmware")

**Batch 5 - UI & Tools:**
1. MotorWidget PyQt6 Component (entityType: "gui_component")
2. TOSCA GUI Treatment Tab (entityType: "gui_component")
3. GPIO Controller Extensions (entityType: "software_module")
4. Hardware Test Results Oct 27 (entityType: "test_report")
5. Serial Communication Protocol (entityType: "protocol")
6. GPIO Module Review (entityType: "code_review")

**Batch 6 - Additional Context:**
1. UI Redesign Code Review 2025-10-27 (entityType: "Code Review")
2. File Writing Protocol (entityType: "Best Practice")
3. User Communication Preferences (entityType: "preference")
4. Tool Workflow Patterns (entityType: "Development Practice")
5. Required vs Optional Tools (entityType: "Development Practice")
6. Hardware_Documentation_Upgrade_2025-11-04 (entityType: "project_milestone")

For each entity, refer to the full observation data in the MIGRATION_PACKAGE.md file.
After creating entities, create relations using mcp__memory__create_relations.
````

## Post-Restoration Verification

After restoration, verify memory with:

```bash
# In Claude Code session
Please verify the memory restoration by:
1. Using mcp__memory__search_nodes with query "TOSCA"
2. Checking that key entities exist (TOSCA Project, Camera HAL, Safety System)
3. Verifying relations are properly linked
```

Expected results:
- 36 entities should be found
- 43 relations should be established
- Search for "TOSCA" should return the main Project entity

## Incremental Restoration Strategy

If batch restoration seems overwhelming:

1. **Week 1:** Restore project core + hardware modules (Priority 1-2)
2. **Week 2:** Add development infrastructure (Priority 3)
3. **Week 3:** Add hardware components (Priority 4)
4. **Week 4:** Add lessons learned (Priority 5)

This gradual approach lets you verify functionality at each stage.

## Troubleshooting

### Memory Server Not Starting

```bash
# Check if npx can access the memory server
npx -y @modelcontextprotocol/server-memory --version

# Clear npx cache if needed
rm -rf ~/.npm/_npx
```

### Entity Creation Failures

- Create entities in smaller batches (5 instead of 10)
- Check entity names for special characters
- Ensure entityType is a valid string

### Relation Creation Failures

- Verify both "from" and "to" entities exist first
- Check for typos in entity names (case-sensitive)
- Create relations after ALL entities are created

## Alternative: Fresh Start

If restoration seems too complex, you can start with a fresh memory in WSL:

**Pros:**
- Clean slate, no migration complexity
- Memory will rebuild naturally as you work
- Good opportunity to refine what's stored

**Cons:**
- Lose 2+ months of accumulated context
- Need to re-learn project patterns
- May miss critical lessons learned

**Recommendation:** Restore at least Priority 1-2 entities (project core + hardware modules) for critical context continuity.

---

## Full Entity List

Below is the complete list of entities from the Windows environment:

1. TOSCA Project
2. Git Content Policy
3. Hardware API Usage Rule
4. Camera HAL
5. Laser Controller HAL
6. Actuator Controller HAL
7. Coding Standards
8. Key Documentation Files
9. VmbPy API Quirks
10. Development Workflow
11. GPIO HAL
12. Safety System
13. Session Management
14. Event Logging System
15. Arduino GPIO Migration
16. Code Review Findings (2025-10-24)
17. Presubmit Folder
18. TodoWrite Workflow
19. Manufacturer Documentation System
20. AI Tool Usage
21. Tool Workflow Patterns
22. Required vs Optional Tools
23. TOSCA Motor Control System
24. MPU6050 Accelerometer Integration
25. Arduino Watchdog Firmware v2.1
26. MotorWidget PyQt6 Component
27. GPIO Controller Extensions
28. Hardware Test Results Oct 27
29. Critical Motor-First Sequence Bug
30. Watchdog Timing Bug Fix
31. TOSCA GUI Treatment Tab
32. Serial Communication Protocol
33. GPIO Module Review
34. Motor Vibration Calibration
35. UI Redesign Code Review 2025-10-27
36. File Writing Protocol
37. User Communication Preferences
38. SEMINEX-2CM-004-189
39. MCP4725_DAC
40. LDD200_Driver
41. Arduino_I2C_Bus
42. Hardware_Documentation_Upgrade_2025-11-04

For the complete observation data for each entity, see the full memory graph export in the MIGRATION_PACKAGE.md documentation.

---

**Last Updated:** 2025-11-04
**Restore Time Estimate:** 15-30 minutes (automated) or 2-3 hours (manual)
