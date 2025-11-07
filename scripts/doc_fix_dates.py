#!/usr/bin/env python3
"""
Automated Date Addition Tool for TOSCA Documentation
Adds "Last Updated" metadata to documentation files that lack dates
"""
import re
from pathlib import Path
from datetime import datetime
import argparse


def add_last_updated_date(filepath: Path, dry_run: bool = False) -> bool:
    """Add Last Updated date to a markdown file if it doesn't have one"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file already has a date
    date_patterns = [
        r'\*\*Last Updated:\*\*\s*\d{4}-\d{2}-\d{2}',
        r'\*\*Generated:\*\*\s*\d{4}-\d{2}-\d{2}',
        r'Last Modified:\s*\d{4}-\d{2}-\d{2}',
    ]

    for pattern in date_patterns:
        if re.search(pattern, content):
            return False  # Already has a date

    # Add date after the first heading
    today = datetime.now().strftime('%Y-%m-%d')
    lines = content.split('\n')

    # Find first heading
    heading_idx = -1
    for i, line in enumerate(lines):
        if re.match(r'^#\s+', line):
            heading_idx = i
            break

    if heading_idx == -1:
        print(f"⚠️  No heading found in {filepath.name}")
        return False

    # Insert date after heading
    new_lines = lines[:heading_idx+1]
    new_lines.append('')
    new_lines.append(f'**Last Updated:** {today}')
    new_lines.extend(lines[heading_idx+1:])

    new_content = '\n'.join(new_lines)

    if dry_run:
        print(f"📝 Would add date to {filepath.name}")
        return True

    # Write updated content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ Added date to {filepath.name}")
    return True


def main():
    parser = argparse.ArgumentParser(description='Add Last Updated dates to documentation')
    parser.add_argument('--base-path', default='.', help='Base path to TOSCA project')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    args = parser.parse_args()

    base_path = Path(args.base_path)

    # Find all markdown files without dates
    docs = []
    docs.extend(base_path.glob('*.md'))
    docs.extend((base_path / 'docs').glob('**/*.md'))

    files_updated = 0
    for doc_path in sorted(docs):
        # Skip certain files
        if doc_path.name in ['CHANGELOG.md', 'LICENSE.md']:
            continue

        if add_last_updated_date(doc_path, dry_run=args.dry_run):
            files_updated += 1

    print(f"\n📊 Summary: {files_updated} files {'would be ' if args.dry_run else ''}updated")


if __name__ == '__main__':
    main()
