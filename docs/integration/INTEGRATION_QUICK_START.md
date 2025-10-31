# Line Protocol Builder - Quick Start Guide 🚀

**Status:** ✅ Integrated into TOSCA
**Location:** Tab 3 - Protocol Builder
**Time to Test:** < 5 minutes

---

## 🎬 Quick Demo

### Step 1: Launch TOSCA

```bash
cd C:\Users\wille\Desktop\TOSCA-dev\src
python main.py
```

### Step 2: Open Protocol Builder

```
Main Window → Tab 3: "Protocol Builder"
```

### Step 3: Load Example Protocol

```
Click "📂 Load Protocol"
→ Navigate to: C:\Users\wille\Desktop\TOSCA-dev\examples\protocols\
→ Select: example_simple_treatment.json
→ Click Open
```

**You should see:**
```
Protocol Metadata:
  Name: Simple Treatment Example
  Loop Count: 1
  Total Duration: 18.3s

Protocol Sequence:
  Line 1: [Move Abs] 5.0mm @ 1.0mm/s | [Laser] Set 2.0W | [Dwell] 3.0s | Duration: 5.0s
  Line 2: [Move Abs] 10.0mm @ 1.5mm/s | [Laser] Ramp 2.0W → 5.0W | [Dwell] 5.0s | Duration: 5.0s
  Line 3: [Home] @ 2.0mm/s | [Laser] Set 0.0W | Duration: 8.3s
```

### Step 4: Edit a Line

```
1. Click "Line 2" in the sequence view
2. Line Editor panel activates
3. Change laser ramp end power: 5.0W → 7.0W
4. Click "✓ Apply Changes to Line"
```

**You should see:**
```
Line 2 summary updates to show:
  [Laser] Ramp 2.0W → 7.0W
```

### Step 5: Add New Line

```
1. Click "➕ Add Line"
2. Enable Movement:
   - Select "Position"
   - Target: 15.0 mm
   - Speed: 2.0 mm/s
   - Type: Absolute
3. Enable Laser:
   - Select "Set Power"
   - Power: 3.5 W
4. Enable Dwell:
   - Duration: 4.0 s
5. Notes: "Final position treatment"
6. Click "✓ Apply Changes to Line"
```

**You should see:**
```
Line 4 added to sequence:
  [Move Abs] 15.0mm @ 2.0mm/s | [Laser] Set 3.5W | [Dwell] 4.0s | Duration: 7.5s

Total Duration updates to: ~25.8s
```

### Step 6: Save Modified Protocol

```
1. Click "💾 Save Protocol"
2. Filename: my_first_protocol.json
3. Click Save
```

**You should see:**
```
Dialog: "Protocol saved successfully: C:\Users\wille\...\my_first_protocol.json"
```

### Step 7: Execute Protocol

```
1. Click "▶ Execute Protocol"
```

**You should see:**
```
Dialog: "Protocol Ready"
  Protocol 'Simple Treatment Example' is ready for execution.
  Lines: 4
  Loop count: 1
  Total duration: 25.8s

  Protocol execution engine integration: TODO

Application automatically switches to:
  Tab 2: "Treatment Workflow"
```

---

## 📊 Available Example Protocols

### 1. Simple Treatment (3 lines)
**File:** `example_simple_treatment.json`
**Description:** Basic move + laser + dwell demonstration
**Duration:** ~18.3s (1 loop)

### 2. Scanning Pattern (4 lines, looped)
**File:** `example_scanning_pattern.json`
**Description:** Multi-position scan with varying laser power
**Duration:** ~45s (3 loops × 15s each)

### 3. Bidirectional Scan (5 lines, looped)
**File:** `example_bidirectional_scan.json`
**Description:** Demonstrates negative position support (-10mm to +10mm)
**Duration:** Variable (2 loops)

---

## 🎨 UI Layout Reference

```
┌────────────────────────────────────────────────────────────────┐
│  TOSCA Main Window                                              │
├────────────────────────────────────────────────────────────────┤
│  [Hardware & Diagnostics] [Treatment Workflow] [Protocol Builder] │
│                                                    ^              │
│                                              Click Tab 3          │
├────────────────────────────────────────────────────────────────┤
│  🔧 Line-Based Protocol Builder                                 │
├────────────────────────────────────────────────────────────────┤
│  Protocol Metadata                                              │
│  Name: [                    ]  Loop: [1]  Duration: 0.0s        │
├────────────────────────┬───────────────────────────────────────┤
│  Protocol Sequence     │  Line Editor                          │
│  ┌──────────────────┐  │  ┌─────────────────────────────────┐ │
│  │ (empty)          │  │  │ No line selected - add a line   │ │
│  │                  │  │  │ to begin                        │ │
│  │                  │  │  │                                 │ │
│  │                  │  │  │ [✓] Movement                    │ │
│  │                  │  │  │   ○ Position  ○ Home            │ │
│  │                  │  │  │   Target: [     ] mm            │ │
│  │                  │  │  │   Speed: [     ] mm/s           │ │
│  │                  │  │  │                                 │ │
│  │                  │  │  │ [✓] Laser                       │ │
│  │                  │  │  │   ○ Set Power  ● Ramp Power    │ │
│  │                  │  │  │   Start: [    ] W               │ │
│  │                  │  │  │   End: [    ] W                 │ │
│  │                  │  │  │   Duration: [    ] s            │ │
│  │                  │  │  │                                 │ │
│  │                  │  │  │ [✓] Dwell (Wait)                │ │
│  │                  │  │  │   Duration: [    ] s            │ │
│  │                  │  │  │                                 │ │
│  │                  │  │  │ Notes: [                    ]   │ │
│  │                  │  │  │                                 │ │
│  │                  │  │  │ [✓ Apply Changes to Line]       │ │
│  └──────────────────┘  │  └─────────────────────────────────┘ │
│                        │                                      │
│  [➕ Add] [➖ Remove]   │                                      │
│  [⬆ Up] [⬇ Down]      │                                      │
├────────────────────────┴───────────────────────────────────────┤
│  [📄 New] [💾 Save] [📂 Load]              [▶ Execute Protocol]│
└────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Features Demo

### Feature 1: Concurrent Actions
Each line combines multiple actions simultaneously:
```
Line 1: Move to 5mm AND Set laser to 2W AND Hold for 3s
        → Duration = MAX(5s move, 0s laser, 3s dwell) = 5s
```

### Feature 2: Laser Power Ramping
Gradual power increase over time:
```
Line 2: Ramp laser from 2W to 5W over 10 seconds
        → Power increases linearly: 2W → 3W → 4W → 5W
```

### Feature 3: Bidirectional Movement
Negative positions supported:
```
Line 1: Move to -10mm (left of home)
Line 2: Move to 0mm (home center)
Line 3: Move to +10mm (right of home)
```

### Feature 4: Protocol Looping
Repeat entire protocol multiple times:
```
Loop Count: 3
→ Executes all lines 3 times
→ Total duration = Single loop duration × 3
```

### Feature 5: Safety Validation
Pre-execution checks:
```
✅ Power within limits (0-10W)
✅ Position within limits (-20mm to +20mm)
✅ Speed within limits (0.1-5.0 mm/s)
✅ Duration within limits (0.1-300s)
```

---

## 🐛 Troubleshooting

### Problem: "No line selected" message
**Solution:** Click "➕ Add Line" first to create a line

### Problem: "Validation Error" when applying changes
**Solution:** Check that all values are within safety limits:
- Power: 0-10W
- Position: -20mm to +20mm
- Speed: 0.1-5.0 mm/s
- Duration: 0.1-300s

### Problem: Can't save protocol
**Solution:** Ensure at least one line exists and protocol name is not empty

### Problem: Execute button does nothing
**Solution:** Current implementation shows confirmation dialog only.
Full execution engine: TODO (next development phase)

---

## 📞 Support

**Documentation:** `docs/architecture/LINE_PROTOCOL_BUILDER.md`
**Examples:** `examples/protocols/`
**Integration:** `INTEGRATION_COMPLETE.md`
**Summary:** `LINE_PROTOCOL_BUILDER_SUMMARY.md`

---

**You're ready to build line-based protocols in TOSCA!** 🎉

Start with loading an example, then try creating your own custom treatment protocol.
