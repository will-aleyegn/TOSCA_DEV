#!/usr/bin/env python3
"""
Fix directory tree structures in markdown files.
Replaces Unicode box-drawing characters with simple indentation.
"""

from pathlib import Path

def fix_directory_tree(text):
    """Replace Unicode box-drawing characters with simple indentation."""
    lines = text.split('\n')
    fixed_lines = []
    in_code_block = False

    for line in lines:
        # Track code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            fixed_lines.append(line)
            continue

        # Only process lines inside code blocks that have box-drawing chars
        if in_code_block and any(char in line for char in '├│└─'):
            # Count leading spaces before box-drawing chars
            leading_spaces = len(line) - len(line.lstrip())

            # Remove box-drawing characters
            cleaned = line.replace('├──', '').replace('└──', '').replace('│', '').replace('─', '')

            # Calculate indentation level from remaining content
            content = cleaned.lstrip()
            if content:
                # Count spaces after removal
                spaces_after = len(cleaned) - len(content)
                # Convert to simple indentation (2 spaces per level)
                indent_level = spaces_after // 4 if spaces_after > 0 else 0
                fixed_line = '  ' * indent_level + content
                fixed_lines.append(fixed_line)
            else:
                # Empty line or only had box chars
                fixed_lines.append('')
        else:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)

def main():
    # Find all markdown files
    arch_dir = Path('/mnt/c/Users/wille/Desktop/TOSCA-dev/docs/architecture')
    md_files = list(arch_dir.glob('*.md'))

    print(f"Found {len(md_files)} markdown files")

    for md_file in md_files:
        # Skip README and other meta files
        if md_file.name in ['README.md', 'PDF_GENERATION_GUIDE.md']:
            continue

        print(f"\nProcessing: {md_file.name}")

        # Read content
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if it has box-drawing characters
        if any(char in content for char in '├│└─'):
            print(f"  Found box-drawing characters, fixing...")
            fixed_content = fix_directory_tree(content)

            # Write back
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)

            print(f"  ✓ Fixed")
        else:
            print(f"  No box-drawing characters found")

if __name__ == '__main__':
    main()
