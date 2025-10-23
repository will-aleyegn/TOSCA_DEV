# Software Block Diagram - Rendering Instructions

## Files Created

1. **software_block_diagram.mmd** - Mermaid diagram source

## How to Render the Diagram

### Option 1: Online Rendering (Easiest)

1. Go to https://mermaid.live
2. Copy the contents of `software_block_diagram.mmd`
3. Paste into the editor
4. The diagram will render automatically
5. Export options:
   - PNG (for documents, presentations)
   - SVG (for scalable graphics, vector format)
   - PDF (for printing)

### Option 2: GitHub/GitLab

1. Create a markdown file (e.g., `architecture.md`)
2. Add a fenced code block with `mermaid` language identifier:
   ````markdown
   ```mermaid
   [paste contents of software_block_diagram.mmd here]
   ```
   ````
3. GitHub and GitLab will automatically render the diagram

### Option 3: VS Code

1. Install the "Markdown Preview Mermaid Support" extension
2. Open `software_block_diagram.mmd` or create a markdown file with the diagram
3. Use "Markdown: Open Preview" (Ctrl+Shift+V)
4. The diagram will render in the preview pane

### Option 4: Command Line (requires mermaid-cli)

```bash
# Install mermaid-cli (one time)
npm install -g @mermaid-js/mermaid-cli

# Render to PNG
mmdc -i software_block_diagram.mmd -o software_architecture.png

# Render to SVG
mmdc -i software_block_diagram.mmd -o software_architecture.svg

# Render to PDF
mmdc -i software_block_diagram.mmd -o software_architecture.pdf
```

### Option 5: Draw.io / diagrams.net

1. Go to https://app.diagrams.net or open Draw.io desktop
2. File → Import from → Text
3. Select "Mermaid" as the format
4. Paste the contents of `software_block_diagram.mmd`
5. Draw.io will convert it to an editable diagram
6. You can then further customize and export

## Diagram Features

### Visual Elements

- **Color Coding:**
  - Red: Safety Management (highest priority)
  - Blue: Device Control Layer (hardware interfaces)
  - Green: Application Logic Layer
  - Yellow: Data Management Layer
  - Purple: User Interface Layer

- **Arrow Types:**
  - Thick double arrows (═══►): Safety-critical signals with override authority
  - Regular arrows (────►): Operational data flow
  - Dashed arrows (- - -►): Status and monitoring signals

- **Layout:**
  - Safety Management centrally positioned
  - Layered architecture (UI → Logic → Devices → Data)
  - Clear separation of concerns

### Key Highlights

- Safety Management module is visually prominent (red, bold, central position)
- Hardware interlocks explicitly shown in GPIO block
- Camera & Image Processing shown as major subsystem
- Safety override paths clearly indicated
- Module groupings by functional layer

## Recommended Export Settings

For professional documentation:
- **Format:** PNG or PDF
- **Resolution:** 300 DPI minimum
- **Size:** Full page width (6.5 inches for standard 8.5×11" with 1" margins)
- **Background:** White
- **Include:** Legend/key

For presentations:
- **Format:** SVG (scalable) or high-res PNG
- **Resolution:** 150-300 DPI
- **Size:** 1920×1080 for 16:9 slides, 1024×768 for 4:3

For web documentation:
- **Format:** SVG (preferred) or PNG
- **Optimization:** Compress PNG with pngquant or similar
- **Alt text:** "TOSCA Software Architecture Block Diagram showing module relationships and safety-critical paths"

## Customization

The Mermaid source file can be edited to:
- Adjust colors (modify `classDef` statements at bottom)
- Rearrange module positions
- Add or remove connections
- Modify text labels
- Change arrow styles
- Add more subgraphs

Refer to Mermaid documentation: https://mermaid.js.org/intro/

## Integration into Documents

### For Microsoft Word:
1. Render to PNG at 300 DPI
2. Insert → Picture
3. Set size to fit page width
4. Add caption: "Figure 1: TOSCA Software Architecture Block Diagram"

### For LaTeX:
1. Render to PDF or SVG
2. Use `\includegraphics` command
3. Example:
   ```latex
   \begin{figure}[h]
     \centering
     \includegraphics[width=\textwidth]{software_architecture.pdf}
     \caption{TOSCA Software Architecture Block Diagram}
     \label{fig:sw_arch}
   \end{figure}
   ```

### For Markdown:
```markdown
![TOSCA Software Architecture](software_architecture.png)
*Figure 1: TOSCA Software Architecture Block Diagram*
```

---

**Created:** 2025-10-15
**Format:** Mermaid Graph (graph TB - top to bottom flowchart)
**Compatibility:** Mermaid v8.0+
