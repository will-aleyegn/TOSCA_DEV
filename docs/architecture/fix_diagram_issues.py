#!/usr/bin/env python3
"""
Automatically fix text-based diagrams in markdown files.

This script:
1. Removes arrow characters from flowcharts and replaces with numbered lists
2. Replaces box-drawing directory trees with clean indentation
3. Identifies state machines that should be PlantUML
"""

import re
from pathlib import Path
from typing import Tuple
import sys


class DiagramFixer:
    """Fix text-based diagrams in markdown files."""

    def __init__(self, backup_dir: str = 'originals'):
        self.arrow_chars = ['→', '←', '↓', '↑', '⇒', '⇐', '⇑', '⇓']
        self.box_chars = ['├', '└', '│', '─', '┌', '┐', '┘', '┤', '┬', '┴', '┼']
        self.backup_dir = Path(backup_dir)
        self.changes_made = []

    def fix_directory_tree(self, text: str) -> str:
        """Replace box-drawing characters with clean indentation."""
        lines = text.split('\n')
        fixed_lines = []

        for line in lines:
            # Check if line has box-drawing chars
            if any(char in line for char in self.box_chars):
                # Remove all box-drawing characters
                cleaned = line
                for char in self.box_chars:
                    cleaned = cleaned.replace(char, '')

                # Count leading spaces (after box chars removed)
                stripped = cleaned.lstrip(' ')
                leading_spaces = len(cleaned) - len(stripped)

                # Convert to clean indentation (2 spaces per level)
                indent_level = leading_spaces // 4 if leading_spaces > 0 else 0
                fixed_line = '  ' * indent_level + stripped

                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def simplify_arrow_flowchart(self, text: str) -> Tuple[str, str]:
        """Convert arrow-based flowchart to numbered list.

        Returns:
            (simplified_text, conversion_type)
        """
        # Check if this looks like a state machine
        if 'STATE' in text.upper() or 'FAULT' in text:
            return text, 'state_machine'  # Don't auto-convert, needs PlantUML

        # Check if it's a simple linear flow (mostly ↓ arrows)
        down_arrows = text.count('↓')
        total_arrows = sum(text.count(char) for char in self.arrow_chars)

        if down_arrows >= total_arrows * 0.6:  # 60% or more are down arrows
            # This is a linear flow - convert to numbered list
            lines = text.split('\n')
            steps = []

            for line in lines:
                # Remove arrows and extract content
                cleaned = line
                for char in self.arrow_chars:
                    cleaned = cleaned.replace(char, '')

                cleaned = cleaned.strip()

                # Skip empty lines and pure arrow lines
                if cleaned and not all(c in self.arrow_chars + [' '] for c in line):
                    # Check if line starts with a number (already numbered)
                    if re.match(r'^\d+\.', cleaned):
                        steps.append(cleaned)
                    else:
                        steps.append(cleaned)

            # Convert to numbered list with bold items
            if steps:
                numbered = []
                for i, step in enumerate(steps, 1):
                    # Make first phrase bold if not already
                    if not step.startswith('**'):
                        # Find first sentence or phrase
                        parts = step.split(':', 1)
                        if len(parts) == 2:
                            numbered.append(f"{i}. **{parts[0]}** - {parts[1].strip()}")
                        else:
                            numbered.append(f"{i}. **{step}**")
                    else:
                        numbered.append(f"{i}. {step}")

                return '\n'.join(numbered), 'flowchart'

        return text, 'complex_diagram'

    def process_code_block(self, block_text: str, block_type: str) -> Tuple[str, bool, str]:
        """Process a code block and return fixed version.

        Returns:
            (fixed_text, was_changed, change_type)
        """
        # Check for box-drawing characters (directory tree)
        box_count = sum(block_text.count(char) for char in self.box_chars)
        if box_count >= 5:
            fixed = self.fix_directory_tree(block_text)
            if fixed != block_text:
                return fixed, True, 'directory_tree'

        # Check for arrow diagrams
        arrow_count = sum(block_text.count(char) for char in self.arrow_chars)
        if arrow_count >= 3:
            fixed, conv_type = self.simplify_arrow_flowchart(block_text)
            if conv_type == 'flowchart' and fixed != block_text:
                return fixed, True, 'flowchart'
            elif conv_type == 'state_machine':
                return block_text, False, 'state_machine_skipped'

        return block_text, False, 'no_change'

    def fix_file(self, file_path: Path, dry_run: bool = False) -> dict:
        """Fix a single markdown file.

        Args:
            file_path: Path to markdown file
            dry_run: If True, don't write changes, just report what would change

        Returns:
            Dictionary with fix statistics
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        lines = content.split('\n')
        output_lines = []

        in_code_block = False
        code_block_start = 0
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
                    fixed_text, was_changed, change_type = self.process_code_block(
                        block_text, code_block_lang
                    )

                    if was_changed:
                        changes_in_file.append({
                            'line': code_block_start,
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
                    code_block_start = i + 1
                    code_block_lang = line.strip()[3:]  # Get language specifier
                    # Don't add the ``` line yet, we'll add it when we output the block
            elif in_code_block:
                code_block_lines.append(line)
            else:
                # Regular line outside code block
                output_lines.append(line)

            i += 1

        new_content = '\n'.join(output_lines)

        result = {
            'file': file_path.name,
            'changed': new_content != original_content,
            'changes': changes_in_file,
            'change_count': len(changes_in_file)
        }

        if result['changed'] and not dry_run:
            # Write the fixed file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

        return result

    def fix_all_files(self, directory: Path = Path('.'), dry_run: bool = False) -> dict:
        """Fix all markdown files in directory.

        Args:
            directory: Directory containing markdown files
            dry_run: If True, don't write changes, just report

        Returns:
            Dictionary with overall statistics
        """
        md_files = [f for f in directory.glob('*.md') if f.name not in ['CLEANUP_SUMMARY.md', 'PDF_WORKFLOW_GUIDE.md']]

        results = []
        total_changes = 0

        for md_file in md_files:
            result = self.fix_file(md_file, dry_run=dry_run)
            if result['changed']:
                results.append(result)
                total_changes += result['change_count']

        return {
            'files_scanned': len(md_files),
            'files_changed': len(results),
            'total_changes': total_changes,
            'results': results
        }

    def print_report(self, results: dict, dry_run: bool = False):
        """Print formatted fix report."""
        print("=" * 80)
        if dry_run:
            print("DIAGRAM FIX REPORT (DRY RUN - NO CHANGES MADE)")
        else:
            print("DIAGRAM FIX REPORT")
        print("=" * 80)
        print()

        print(f"Files scanned: {results['files_scanned']}")
        print(f"Files changed: {results['files_changed']}")
        print(f"Total fixes applied: {results['total_changes']}")
        print()

        if results['files_changed'] == 0:
            print("✅ No changes needed! All documents are clean.")
            return

        print("CHANGES BY FILE:")
        print("-" * 80)

        for result in results['results']:
            print(f"\n📄 {result['file']}: {result['change_count']} fixes")
            for change in result['changes']:
                print(f"   Line {change['line']}: {change['type']}")


def main():
    """Run the diagram fixer."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Fix text-based diagrams in markdown files'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Fix a single file instead of all files'
    )

    args = parser.parse_args()

    fixer = DiagramFixer()

    print("Scanning and fixing diagram issues...")
    print()

    if args.file:
        # Fix single file
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ Error: File not found: {args.file}")
            sys.exit(1)

        result = fixer.fix_file(file_path, dry_run=args.dry_run)

        print("=" * 80)
        print(f"FIXED: {result['file']}")
        print("=" * 80)
        print(f"Changes: {result['change_count']}")

        for change in result['changes']:
            print(f"  Line {change['line']}: {change['type']}")

    else:
        # Fix all files
        results = fixer.fix_all_files(dry_run=args.dry_run)
        fixer.print_report(results, dry_run=args.dry_run)

        if not args.dry_run and results['files_changed'] > 0:
            print()
            print("✅ Files have been updated!")
            print()
            print("Next steps:")
            print("  1. Review changes with: git diff")
            print("  2. Regenerate PDFs: python3 generate_pdfs.py --all")


if __name__ == '__main__':
    main()
