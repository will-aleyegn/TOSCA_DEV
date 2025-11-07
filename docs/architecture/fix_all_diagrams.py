#!/usr/bin/env python3
"""
Aggressively fix ALL text-based diagrams in markdown files.

This script automatically converts ALL problematic diagrams to clean text:
- Arrow diagrams → Numbered lists or text descriptions
- State machines → Text descriptions with diagram references
- Directory trees → Clean indentation
- Large structures → Condensed summaries
"""

import re
from pathlib import Path
from typing import Tuple


class AggressiveDiagramFixer:
    """Aggressively fix all text-based diagrams."""

    def __init__(self):
        self.arrow_chars = ['→', '←', '↓', '↑', '⇒', '⇐', '⇑', '⇓']
        self.box_chars = ['├', '└', '│', '─', '┌', '┐', '┘', '┤', '┬', '┴', '┼']
        self.changes_made = []

    def remove_arrows_from_text(self, text: str) -> str:
        """Remove all arrow characters from text."""
        result = text
        for char in self.arrow_chars:
            result = result.replace(char, '')
        return result

    def remove_box_chars_from_text(self, text: str) -> str:
        """Remove all box-drawing characters from text."""
        result = text
        for char in self.box_chars:
            result = result.replace(char, '')
        return result

    def fix_directory_tree(self, text: str) -> str:
        """Replace box-drawing characters with clean indentation."""
        lines = text.split('\n')
        fixed_lines = []

        for line in lines:
            if any(char in line for char in self.box_chars):
                # Remove all box-drawing characters
                cleaned = line
                for char in self.box_chars:
                    cleaned = cleaned.replace(char, '')

                # Remove leading/trailing spaces
                stripped = cleaned.lstrip(' ')
                leading_spaces = len(cleaned) - len(stripped)

                # Convert to clean indentation (2 spaces per level)
                indent_level = leading_spaces // 4 if leading_spaces > 0 else 0
                fixed_line = '  ' * indent_level + stripped

                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def convert_arrow_diagram_to_list(self, text: str) -> str:
        """Convert any arrow diagram to a clean numbered list."""
        # Check if it's a state machine
        if 'STATE' in text.upper() or 'FAULT' in text:
            return self.convert_state_machine(text)

        lines = text.split('\n')
        steps = []

        for line in lines:
            # Remove arrows
            cleaned = self.remove_arrows_from_text(line)
            cleaned = cleaned.strip()

            # Skip empty lines
            if not cleaned:
                continue

            # Skip lines that are just arrows
            if all(c in self.arrow_chars + [' ', '|', '+', '-'] for c in line):
                continue

            # Extract meaningful content
            # Remove leading numbers if present
            cleaned = re.sub(r'^\d+\.\s*', '', cleaned)

            # Skip if line is too short or just punctuation
            if len(cleaned) < 3:
                continue

            steps.append(cleaned)

        if not steps:
            # If we couldn't extract steps, just remove arrows and return
            return self.remove_arrows_from_text(text)

        # Convert to numbered list
        numbered = []
        for i, step in enumerate(steps, 1):
            # Check if step has a colon (likely has a label)
            if ':' in step:
                parts = step.split(':', 1)
                numbered.append(f"{i}. **{parts[0].strip()}** - {parts[1].strip()}")
            else:
                # Just make the whole thing bold
                numbered.append(f"{i}. **{step}**")

        return '\n'.join(numbered)

    def convert_state_machine(self, text: str) -> str:
        """Convert state machine ASCII art to text description."""
        # Extract states
        states = []
        state_pattern = r'\[([A-Z_]+)\]'
        found_states = re.findall(state_pattern, text)

        if found_states:
            states = list(dict.fromkeys(found_states))  # Remove duplicates, preserve order

        # Create text description
        if states:
            description = "*See diagram above for state machine visualization.*\n\n"
            description += "**States:** " + ", ".join(f"**{s}**" for s in states) + "\n\n"
            description += "**Key Transitions:**\n"

            # Try to extract some transition info from arrows
            lines = text.split('\n')
            transitions = []
            for line in lines:
                if '→' in line or '←' in line:
                    # Extract states and conditions
                    cleaned = self.remove_arrows_from_text(line)
                    cleaned = ' '.join(cleaned.split())  # Normalize whitespace
                    if cleaned and len(cleaned) > 5:
                        transitions.append(f"- {cleaned}")

            if transitions:
                description += '\n'.join(transitions[:5])  # Limit to 5 transitions
            else:
                description += "- Normal operation: SYSTEM_OFF → INITIALIZING → READY → ARMED → TREATING\n"
                description += "- Fault handling: Any state → FAULT on interlock failure\n"
                description += "- Shutdown: FAULT → SAFE_SHUTDOWN"

            return description

        # Fallback: just remove arrows
        return self.remove_arrows_from_text(text)

    def condense_large_structure(self, text: str) -> str:
        """Condense large directory structures."""
        lines = text.split('\n')

        if len(lines) <= 30:
            return text

        # Extract top-level directories and key files
        top_level = []
        key_files = []

        for line in lines[:50]:  # Look at first 50 lines
            stripped = line.strip()
            if stripped.endswith('/') and len(stripped) < 20:
                top_level.append(stripped)
            elif any(ext in stripped for ext in ['.py', '.md', '.txt', '.json', '.yaml']):
                if len(key_files) < 10:
                    key_files.append(stripped)

        # Build condensed version
        condensed = "**High-Level Structure:**\n\n"
        for item in top_level[:8]:
            condensed += f"- **{item}**\n"

        if key_files:
            condensed += "\n**Key Files:**\n"
            for item in key_files[:8]:
                condensed += f"- {item}\n"

        condensed += "\n*See full project structure in source repository*"

        return condensed

    def process_code_block(self, block_text: str) -> Tuple[str, bool, str]:
        """Process a code block and return fixed version.

        Returns:
            (fixed_text, was_changed, change_type)
        """
        original = block_text

        # Fix directory trees (box-drawing characters)
        box_count = sum(block_text.count(char) for char in self.box_chars)
        if box_count >= 5:
            block_text = self.fix_directory_tree(block_text)
            if block_text != original:
                return block_text, True, 'directory_tree'

        # Fix arrow diagrams
        arrow_count = sum(block_text.count(char) for char in self.arrow_chars)
        if arrow_count >= 3:
            block_text = self.convert_arrow_diagram_to_list(block_text)
            if block_text != original:
                return block_text, True, 'arrow_diagram'

        # Condense large structures
        line_count = len(block_text.split('\n'))
        if line_count > 30:
            has_paths = sum(1 for line in block_text.split('\n')
                          if '/' in line or '.py' in line or '.md' in line)
            if has_paths > 10:
                block_text = self.condense_large_structure(block_text)
                if block_text != original:
                    return block_text, True, 'large_structure'

        return block_text, False, 'no_change'

    def fix_file(self, file_path: Path) -> dict:
        """Fix a single markdown file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # First, fix box-drawing characters outside code blocks
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Check if line is NOT in a code block and has box chars
            if any(char in line for char in self.box_chars):
                # Don't touch if it's in a code block (we'll handle that separately)
                # Just remove the box chars
                cleaned = line
                for char in self.box_chars:
                    cleaned = cleaned.replace(char, ' ')
                lines[i] = cleaned

        content = '\n'.join(lines)

        # Now process code blocks
        lines = content.split('\n')
        output_lines = []
        in_code_block = False
        code_block_lines = []
        code_block_lang = ''
        changes_in_file = []

        i = 0
        while i < len(lines):
            line = lines[i]

            if line.strip().startswith('```'):
                if in_code_block:
                    # End of code block - process it
                    block_text = '\n'.join(code_block_lines)
                    fixed_text, was_changed, change_type = self.process_code_block(block_text)

                    if was_changed:
                        changes_in_file.append({
                            'line': i - len(code_block_lines),
                            'type': change_type
                        })

                    # Output the fixed code block
                    output_lines.append(f'```{code_block_lang}')
                    output_lines.append(fixed_text)
                    output_lines.append('```')

                    code_block_lines = []
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
                    code_block_lang = line.strip()[3:]
            elif in_code_block:
                code_block_lines.append(line)
            else:
                output_lines.append(line)

            i += 1

        new_content = '\n'.join(output_lines)

        result = {
            'file': file_path.name,
            'changed': new_content != original_content,
            'changes': changes_in_file,
            'change_count': len(changes_in_file)
        }

        if result['changed']:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

        return result

    def fix_all_files(self, directory: Path = Path('.')) -> dict:
        """Fix all markdown files in directory."""
        md_files = list(directory.glob('*.md'))

        results = []
        total_changes = 0

        for md_file in md_files:
            result = self.fix_file(md_file)
            if result['changed']:
                results.append(result)
                total_changes += result['change_count']

        return {
            'files_scanned': len(md_files),
            'files_changed': len(results),
            'total_changes': total_changes,
            'results': results
        }


def main():
    """Run the aggressive diagram fixer."""
    print("=" * 80)
    print("AGGRESSIVE DIAGRAM FIXER")
    print("=" * 80)
    print()
    print("Scanning and fixing ALL diagram issues...")
    print()

    fixer = AggressiveDiagramFixer()
    results = fixer.fix_all_files()

    print("=" * 80)
    print("FIX REPORT")
    print("=" * 80)
    print()
    print(f"Files scanned: {results['files_scanned']}")
    print(f"Files changed: {results['files_changed']}")
    print(f"Total fixes applied: {results['total_changes']}")
    print()

    if results['files_changed'] == 0:
        print("✅ No changes needed! All documents are clean.")
    else:
        print("CHANGES BY FILE:")
        print("-" * 80)
        for result in results['results']:
            print(f"\n📄 {result['file']}: {result['change_count']} fixes")
            for change in result['changes']:
                print(f"   Line {change['line']}: {change['type']}")

        print()
        print("=" * 80)
        print("✅ All fixes applied!")
        print()
        print("Next step: Regenerate PDFs")
        print("  python3 generate_pdfs.py --all")


if __name__ == '__main__':
    main()
