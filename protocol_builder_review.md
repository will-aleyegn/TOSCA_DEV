# TOSCA Protocol Builder - Functionality Review
**Date:** 2025-11-03
**Purpose:** Review current functionality for UX optimization

---

## Overview

The Protocol Builder is a **line-based protocol editor** where each "line" can contain multiple **concurrent actions**:
- **Movement** (actuator positioning)
- **Laser control** (power settings/ramping)
- **Dwell time** (wait/delay)

---

## Current Layout Structure

```
┌────────────────────────────────────────────────────────────────┐
│  🔧 Line-Based Protocol Builder                                │
├────────────────────────────────────────────────────────────────┤
│  Protocol Metadata                                             │
│  Name: [___________]  Loop Count: [1]  Total Duration: 0.0s   │
├─────────────────────┬──────────────────────────────────────────┤
│ Protocol Sequence   │  Line Editor (Contextual)                │
│ (Left 40%)          │  (Right 60%)                             │
│                     │                                          │
│ ┌─────────────┐     │  No line selected - add a line to begin  │
│ │ Line 1      │     │                                          │
│ │ Line 2      │ ◄───┤  ☑ Movement                              │
│ │ Line 3      │     │    ○ Position  ○ Home                    │
│ └─────────────┘     │    Target: [5.00] mm  Speed: [1.00] mm/s │
│                     │                                          │
│ [➕ Add Line]       │  ☑ Laser                                 │
│ [➖ Remove]         │    ○ Set Power  ○ Ramp                   │
│ [⬆ Up] [⬇ Down]     │    Power: [0.50] W                       │
│                     │                                          │
│                     │  ☑ Dwell                                 │
│                     │    Duration: [2.0] s                     │
│                     │                                          │
│                     │  Notes: [_____________________]          │
│                     │                                          │
│                     │  [Apply Changes to Line]                 │
└─────────────────────┴──────────────────────────────────────────┘
│  [📄 New] [💾 Save] [📂 Load]    [▶ Execute Protocol]         │
└────────────────────────────────────────────────────────────────┘
```

---

## Current Buttons & Functions

### Top Section - Protocol Metadata
| Element | Function | Status |
|---------|----------|--------|
| Name input | Protocol name | ✅ Working |
| Loop Count spinner | Repeat protocol N times | ✅ Working |
| Total Duration label | Shows calculated total time | ✅ Working |

### Left Panel - Sequence Controls
| Button | Icon | Function | Status |
|--------|------|----------|--------|
| Add Line | ➕ | Add new line to end of sequence | ✅ Working |
| Remove | ➖ | Delete selected line | ✅ Working |
| Up | ⬆ | Move line up in sequence | ✅ Working |
| Down | ⬇ | Move line down in sequence | ✅ Working |

### Right Panel - Line Editor
| Section | Controls | Function |
|---------|----------|----------|
| **Movement** | ☑ Enable checkbox | Toggle movement for this line |
| | ○ Position / ○ Home | Select movement type |
| | Target (mm) | Absolute position target |
| | Speed (mm/s) | Movement speed |
| **Laser** | ☑ Enable checkbox | Toggle laser for this line |
| | ○ Set Power / ○ Ramp | Fixed power or ramping |
| | Power (W) | Target laser power |
| | Start/End (W) | For ramp mode |
| **Dwell** | ☑ Enable checkbox | Toggle dwell for this line |
| | Duration (s) | Wait time at this line |
| **Notes** | Text input | Optional line description |
| **Apply Changes** | Button | Save editor changes to selected line |

### Bottom Section - Protocol Actions
| Button | Icon | Function | Status |
|--------|------|----------|--------|
| New Protocol | 📄 | Clear and start fresh | ✅ Working |
| Save Protocol | 💾 | Save to JSON file | ✅ Working |
| Load Protocol | 📂 | Load from JSON file | ✅ Working |
| Execute Protocol | ▶ | Send to execution engine | ✅ Working |

---

## User Workflow

### Creating a Protocol

1. **Start**: Click "📄 New Protocol" (or use existing protocol)
2. **Metadata**: Enter protocol name and loop count
3. **Add Lines**: Click "➕ Add Line" for each step
4. **Edit Each Line**:
   - Select line from sequence list (left)
   - Configure actions in editor (right):
     - ☑ Movement: Position/Home + target + speed
     - ☑ Laser: Set/Ramp + power
     - ☑ Dwell: Duration
   - Click "Apply Changes to Line"
5. **Organize**: Use ⬆⬇ to reorder lines
6. **Save**: Click "💾 Save Protocol"
7. **Execute**: Click "▶ Execute Protocol"

### Example Protocol: Laser Line Scan

```
Line 1: Movement (0→5mm, 1mm/s) + Laser (0.5W) + Dwell (0s)
Line 2: Dwell (2s) [laser stays on]
Line 3: Movement (5→0mm, 1mm/s) + Laser (0W) + Dwell (0s)
```

---

## Current Issues & Optimization Opportunities

### 🔴 UX Issues

1. **"Apply Changes to Line" button is confusing**
   - Users expect changes to save automatically
   - Easy to forget to click "Apply" before selecting another line
   - **Suggestion**: Auto-save on selection change (with visual feedback)

2. **Sequence list shows minimal info**
   - Only shows "Line 1", "Line 2", etc.
   - No preview of what each line does
   - **Suggestion**: Show concise summary (e.g., "Move 5mm + 0.5W")

3. **Execute button location**
   - Bottom-right corner, easy to miss
   - Not visually distinct enough for critical action
   - **Suggestion**: Move to prominent location with stronger styling

4. **No visual feedback on unsaved changes**
   - No indication if protocol has been modified
   - No warning when closing with unsaved changes
   - **Suggestion**: Add "Modified *" indicator + save prompt

5. **Movement type toggle is unclear**
   - "Position" vs "Home" radio buttons are cryptic
   - No tooltip explaining difference
   - **Suggestion**: Add tooltips or rename to "Move to Position" / "Return Home"

### 🟡 Layout Issues

6. **Wasted vertical space**
   - Bottom action buttons stretch horizontally
   - Could stack vertically to use space better
   - **Suggestion**: Vertical button column on right edge

7. **Line editor always visible**
   - Takes up space even when no line selected
   - Shows "No line selected" message
   - **Suggestion**: Collapse when empty, or show quick start guide

8. **Loop count buried in metadata**
   - Important feature but easy to miss
   - No visual indication of looping
   - **Suggestion**: Highlight when loop_count > 1

### 🟢 Feature Gaps

9. **No protocol validation feedback**
   - No warning for dangerous combinations
   - No visual indication of safety limit violations
   - **Suggestion**: Add validation icon/color coding per line

10. **No duplicate line function**
    - Have to manually recreate similar lines
    - **Suggestion**: Add "📋 Duplicate Line" button

11. **No line preview/simulation**
    - Can't visualize actuator path
    - Can't see total laser energy
    - **Suggestion**: Add visualization panel (optional)

12. **No undo/redo**
    - Mistakes require manual fixing
    - **Suggestion**: Add undo/redo buttons

---

## Proposed Optimizations

### Priority 1 (Quick Wins)

- ✅ **Auto-save line edits** on selection change
- ✅ **Add line summaries** to sequence list
- ✅ **Add tooltips** to all controls
- ✅ **Add duplicate line button**
- ✅ **Highlight Execute button** (larger, more prominent)

### Priority 2 (UX Improvements)

- 🔲 **Add validation indicators** (⚠️ icons for issues)
- 🔲 **Show modified state** (* in title bar)
- 🔲 **Add keyboard shortcuts** (Ctrl+S save, Ctrl+N new, etc.)
- 🔲 **Improve sequence view** (compact multi-line display)

### Priority 3 (Advanced Features)

- 🔲 **Add undo/redo** (protocol history)
- 🔲 **Add path visualization** (actuator trajectory plot)
- 🔲 **Add protocol templates** (quick start presets)
- 🔲 **Add protocol validation panel** (safety checks)

---

## Recommended Button Layout (Option A - Optimized)

```
┌────────────────────────────────────────────────────────────────┐
│  🔧 Protocol Builder - [Protocol Name] *Modified               │
├────────────────────────────────────────────────────────────────┤
│  Name: [___________]  Loops: [1]  Duration: 0.0s  [💾 Save]  │
├─────────────────────┬──────────────────────────────────────────┤
│ Sequence (Lines)    │  Line Editor                             │
│                     │                                          │
│ ┌─────────────┐     │  ✏️ Editing Line 2                       │
│ │ 1: 5mm @1mm/s│     │  ┌─────────────────────────────────────┐│
│ │    0.5W      │     │  │ ☑ Movement                          ││
│ │ 2: Dwell 2s  │◄────┤  │   ○ Move to Position  ○ Return Home ││
│ │ 3: Home 0W   │     │  │   Target: [5.00] mm                 ││
│ │              │     │  │   Speed: [1.00] mm/s                ││
│ └─────────────┘     │  │                                     ││
│                     │  │ ☑ Laser Control                     ││
│ [➕ Add]            │  │   ○ Fixed Power  ○ Ramp             ││
│ [📋 Dup]            │  │   Power: [0.50] W                   ││
│ [➖ Del]            │  │                                     ││
│ [⬆][⬇]             │  │ ☐ Dwell Time                        ││
│                     │  │   Duration: [0.0] s                 ││
│ ─────────────       │  └─────────────────────────────────────┘│
│ [📄 New]            │  Notes: [Movement with laser on______] │
│ [📂 Load]           │                                          │
│                     │  Changes auto-saved ✓                   │
└─────────────────────┴──────────────────────────────────────────┘
│              [▶▶ EXECUTE PROTOCOL]                             │
└────────────────────────────────────────────────────────────────┘
```

### Changes from Current:
1. ✅ Line summaries in sequence list
2. ✅ Auto-save (no "Apply" button needed)
3. ✅ Duplicate button added
4. ✅ Execute button prominent at bottom
5. ✅ Save button in header for quick access
6. ✅ Modified indicator (* in title)
7. ✅ Better button organization (Add/Dup/Del/Move together)

---

## Questions for Review

1. **Auto-save vs Manual Apply**: Should line edits save immediately or require confirmation?
2. **Sequence Summary Format**: What info should appear in each line summary?
3. **Execute Button**: Bottom (full width) or right column?
4. **Validation**: Real-time (red borders) or on-demand (validate button)?
5. **Templates**: Would pre-built protocol templates be useful?
6. **Keyboard Shortcuts**: Which operations need shortcuts most?

---

## Next Steps

Please review and provide feedback on:
- Current issues identified (agree/disagree?)
- Proposed optimizations (priorities?)
- Button layout preference (Option A, or custom?)
- Any missing functionality?
- Which Priority 1 items to implement first?
