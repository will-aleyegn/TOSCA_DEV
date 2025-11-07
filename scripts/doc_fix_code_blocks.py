#!/usr/bin/env python3
"""
Automated Code Block Language Specification Tool
Adds language specifications to code blocks that are missing them
"""
import re
from pathlib import Path
import argparse


def detect_language(code: str) -> str:
    """Attempt to detect programming language from code content"""
    # Python indicators
    if re.search(r'(import |def |class |from .* import|if __name__|self\.)', code):
        return 'python'

    # Bash/Shell indicators
    if re.search(r'(#!/bin/(bash|sh)|echo |export |source |ls |cd )', code):
        return 'bash'

    # JavaScript/TypeScript indicators
    if re.search(r'(function\s+\w+|const |let |var |=>|\bconsole\.log)', code):
        return 'javascript'

    # YAML indicators
    if re.search(r'^[a-z_]+:\s*(.*|\n\s+)', code, re.MULTILINE):
        return 'yaml'

    # JSON indicators
    if re.search(r'^\s*\{[\s\S]*\}\s*$', code.strip()):
        return 'json'

    # Default to text
    return 'text'


def fix_code_blocks(filepath: Path, dry_run: bool = False) -> int:
    """Add language specifications to code blocks in a markdown file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find code blocks without language specification
    pattern = r'```\n([\s\S]*?)```'
    matches = list(re.finditer(pattern, content))

    if not matches:
        return 0

    fixed_count = 0
    new_content = content

    for match in reversed(matches):  # Process in reverse to maintain positions
        code = match.group(1)
        language = detect_language(code)

        # Replace ``` with ```language
        old_block = match.group(0)
        new_block = f'```{language}\n{code}```'

        new_content = new_content[:match.start()] + new_block + new_content[match.end():]
        fixed_count += 1

    if fixed_count == 0:
        return 0

    if dry_run:
        print(f"📝 Would fix {fixed_count} code blocks in {filepath.name}")
        return fixed_count

    # Write updated content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ Fixed {fixed_count} code blocks in {filepath.name}")
    return fixed_count


def main():
    parser = argparse.ArgumentParser(description='Add language specifications to code blocks')
    parser.add_argument('--base-path', default='.', help='Base path to TOSCA project')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    args = parser.parse_args()

    base_path = Path(args.base_path)

    # Find all markdown files
    docs = []
    docs.extend(base_path.glob('*.md'))
    docs.extend((base_path / 'docs').glob('**/*.md'))

    total_fixed = 0
    files_updated = 0

    for doc_path in sorted(docs):
        fixed = fix_code_blocks(doc_path, dry_run=args.dry_run)
        if fixed > 0:
            total_fixed += fixed
            files_updated += 1

    print(f"\n📊 Summary: {total_fixed} code blocks {'would be ' if args.dry_run else ''}fixed in {files_updated} files")


if __name__ == '__main__':
    main()
