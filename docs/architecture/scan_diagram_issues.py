#!/usr/bin/env python3
"""
Scan all markdown files for text-based diagrams that should be converted to
proper formatting or PlantUML diagrams.

This script identifies:
1. ASCII art with arrows (→, ←, ↓, ↑) in code blocks
2. Directory trees with box-drawing characters
3. State machines as text
4. Flowcharts with arrows
5. Large code blocks that are actually diagrams
"""

from pathlib import Path
from typing import List, Dict, Tuple


class DiagramScanner:
    """Scan markdown files for problematic text-based diagrams."""

    def __init__(self):
        self.arrow_chars = ['→', '←', '↓', '↑', '⇒', '⇐', '⇑', '⇓']
        self.box_chars = ['├', '└', '│', '─', '┌', '┐', '┘', '┤', '┬', '┴', '┼']
        self.issues = []

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single markdown file for diagram issues.

        Returns:
            List of issues found, each with: file, line_num, issue_type, content
        """
        file_issues = []

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        in_code_block = False
        code_block_start = 0
        code_block_lines = []

        for i, line in enumerate(lines, start=1):
            # Track code blocks
            if line.strip().startswith('```'):
                if in_code_block:
                    # End of code block - analyze it
                    issues = self._analyze_code_block(
                        file_path, code_block_start, code_block_lines
                    )
                    file_issues.extend(issues)
                    code_block_lines = []
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
                    code_block_start = i
            elif in_code_block:
                code_block_lines.append((i, line))
            else:
                # Check for issues outside code blocks
                if any(char in line for char in self.box_chars):
                    file_issues.append({
                        'file': file_path.name,
                        'line': i,
                        'type': 'box_drawing_outside_code',
                        'content': line.strip()[:80]
                    })

        return file_issues

    def _analyze_code_block(
        self,
        file_path: Path,
        start_line: int,
        lines: List[Tuple[int, str]]
    ) -> List[Dict]:
        """Analyze a code block for diagram-like content."""
        issues = []

        if not lines:
            return issues

        # Combine all lines for analysis
        full_content = ''.join([line for _, line in lines])

        # Check for arrow characters (potential flowchart/state machine)
        arrow_count = sum(full_content.count(char) for char in self.arrow_chars)
        if arrow_count >= 3:
            issues.append({
                'file': file_path.name,
                'line': start_line,
                'type': 'arrow_diagram',
                'content': f'Code block with {arrow_count} arrow characters',
                'details': 'Likely a flowchart or state machine that should be PlantUML'
            })

        # Check for box-drawing characters (potential directory tree)
        box_count = sum(full_content.count(char) for char in self.box_chars)
        if box_count >= 5:
            issues.append({
                'file': file_path.name,
                'line': start_line,
                'type': 'directory_tree',
                'content': f'Code block with {box_count} box-drawing characters',
                'details': 'Likely a directory tree that should use clean indentation'
            })

        # Check for large code blocks (>30 lines) that might be diagrams
        if len(lines) > 30:
            # Check if it looks like a directory structure
            has_paths = sum(1 for _, line in lines if '/' in line or '.py' in line or '.md' in line)
            if has_paths > 10:
                issues.append({
                    'file': file_path.name,
                    'line': start_line,
                    'type': 'large_structure',
                    'content': f'Large code block ({len(lines)} lines) with path-like content',
                    'details': 'Consider condensing or restructuring'
                })

        # Check for state machine patterns
        if 'STATE' in full_content.upper() or 'FAULT' in full_content:
            if arrow_count > 0:
                issues.append({
                    'file': file_path.name,
                    'line': start_line,
                    'type': 'state_machine',
                    'content': 'Code block with STATE keywords and arrows',
                    'details': 'Should be PlantUML state diagram'
                })

        return issues

    def scan_all_files(self, directory: Path = Path('.')) -> Dict:
        """Scan all markdown files in directory.

        Returns:
            Dictionary with summary statistics and detailed issues
        """
        md_files = list(directory.glob('*.md'))

        all_issues = []
        file_summaries = {}

        for md_file in md_files:
            issues = self.scan_file(md_file)
            all_issues.extend(issues)

            if issues:
                file_summaries[md_file.name] = {
                    'count': len(issues),
                    'types': list(set(issue['type'] for issue in issues))
                }

        # Group issues by type
        issues_by_type = {}
        for issue in all_issues:
            issue_type = issue['type']
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)

        return {
            'total_files_scanned': len(md_files),
            'files_with_issues': len(file_summaries),
            'total_issues': len(all_issues),
            'issues_by_type': issues_by_type,
            'file_summaries': file_summaries,
            'all_issues': all_issues
        }

    def print_report(self, results: Dict):
        """Print formatted scan report."""
        print("=" * 80)
        print("MARKDOWN DIAGRAM SCAN REPORT")
        print("=" * 80)
        print()

        print(f"Files scanned: {results['total_files_scanned']}")
        print(f"Files with issues: {results['files_with_issues']}")
        print(f"Total issues found: {results['total_issues']}")
        print()

        if results['total_issues'] == 0:
            print("✅ No issues found! All documents are clean.")
            return

        print("ISSUES BY TYPE:")
        print("-" * 80)
        for issue_type, issues in results['issues_by_type'].items():
            print(f"\n{issue_type.upper().replace('_', ' ')}: {len(issues)} occurrences")
            print()

            for issue in issues:
                print(f"  📄 {issue['file']}:{issue['line']}")
                print(f"     {issue['content'][:70]}")
                if 'details' in issue:
                    print(f"     💡 {issue['details']}")
                print()

        print("=" * 80)
        print("FILES NEEDING ATTENTION:")
        print("-" * 80)
        for filename, summary in sorted(results['file_summaries'].items()):
            print(f"\n{filename}: {summary['count']} issues")
            print(f"  Types: {', '.join(summary['types'])}")


def main():
    """Run the diagram scanner."""
    scanner = DiagramScanner()

    print("Scanning markdown files for diagram issues...")
    print()

    results = scanner.scan_all_files()
    scanner.print_report(results)

    # Save detailed report to file
    if results['total_issues'] > 0:
        report_file = Path('diagram_scan_report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("DETAILED DIAGRAM SCAN REPORT\n")
            f.write("=" * 80 + "\n\n")

            for issue in results['all_issues']:
                f.write(f"File: {issue['file']}\n")
                f.write(f"Line: {issue['line']}\n")
                f.write(f"Type: {issue['type']}\n")
                f.write(f"Content: {issue['content']}\n")
                if 'details' in issue:
                    f.write(f"Details: {issue['details']}\n")
                f.write("\n" + "-" * 80 + "\n\n")

        print(f"\n💾 Detailed report saved to: {report_file}")


if __name__ == '__main__':
    main()
