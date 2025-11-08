#!/usr/bin/env python3
"""
TOSCA Documentation Maintenance Automation System
Comprehensive quality assurance, validation, and optimization tools
"""
import re
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple
import argparse


class DocumentationMaintenance:
    """Automated documentation maintenance and quality assurance"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'quality_score': 0,
            'issues': [],
            'recommendations': []
        }

    def run_full_audit(self) -> Dict:
        """Run comprehensive documentation audit"""
        print("🔍 Starting documentation audit...")

        # 1. Discover all documentation files
        docs = self._discover_docs()
        print(f"   Found {len(docs)} documentation files")

        # 2. Analyze each file
        analyses = {}
        for doc_path in docs:
            analyses[str(doc_path.relative_to(self.base_path))] = self._analyze_file(doc_path)

        # 3. Validate links
        link_issues = self._validate_links(docs)
        print(f"   Found {len(link_issues)} link issues")

        # 4. Check style consistency
        style_issues = self._check_style(docs)
        print(f"   Found {len(style_issues)} style issues")

        # 5. Find stale documentation
        stale_docs = self._find_stale_docs(analyses)
        print(f"   Found {len(stale_docs)} stale documents")

        # 6. Calculate quality score
        quality_score = self._calculate_quality_score(analyses, link_issues, style_issues, stale_docs)

        self.results.update({
            'total_files': len(docs),
            'analyses': analyses,
            'link_issues': link_issues,
            'style_issues': style_issues,
            'stale_docs': stale_docs,
            'quality_score': quality_score
        })

        return self.results

    def _discover_docs(self) -> List[Path]:
        """Discover all documentation files"""
        docs = []

        # Root level
        docs.extend(self.base_path.glob('*.md'))

        # Docs directory
        docs_path = self.base_path / 'docs'
        if docs_path.exists():
            docs.extend(docs_path.glob('**/*.md'))

        # Tests/mocks
        tests_mocks = self.base_path / 'tests' / 'mocks'
        if tests_mocks.exists():
            docs.extend(tests_mocks.glob('*.md'))

        return sorted(docs)

    def _analyze_file(self, filepath: Path) -> Dict:
        """Analyze a single documentation file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')

        return {
            'size': len(content),
            'lines': len(lines),
            'word_count': len(content.split()),
            'headings': len(re.findall(r'^#+\s', content, re.MULTILINE)),
            'code_blocks': len(re.findall(r'```', content)) // 2,
            'links_internal': len(re.findall(r'\[([^\]]+)\]\((?!http)([^\)]+)\)', content)),
            'links_external': len(re.findall(r'\[([^\]]+)\]\((https?://[^\)]+)\)', content)),
            'todos': len(re.findall(r'TODO|FIXME|XXX', content, re.IGNORECASE)),
            'last_updated': self._extract_date(content),
            'has_title': bool(re.search(r'^#\s+', content, re.MULTILINE)),
        }

    def _extract_date(self, content: str) -> str:
        """Extract last updated date from content"""
        date_patterns = [
            r'\*\*Last Updated:\*\*\s*(\d{4}-\d{2}-\d{2})',
            r'\*\*Generated:\*\*\s*(\d{4}-\d{2}-\d{2})',
            r'Last Modified:\s*(\d{4}-\d{2}-\d{2})',
        ]
        for pattern in date_patterns:
            if match := re.search(pattern, content):
                return match.group(1)
        return None

    def _validate_links(self, docs: List[Path]) -> List[Dict]:
        """Validate all internal links"""
        issues = []

        for doc_path in docs:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            pattern = r'\[([^\]]+)\]\((?!http)([^\)]+)\)'
            for match in re.finditer(pattern, content):
                link_path = match.group(2).split('#')[0]
                if not link_path:
                    continue

                full_path = (doc_path.parent / link_path).resolve()
                if not full_path.exists():
                    issues.append({
                        'file': str(doc_path.relative_to(self.base_path)),
                        'link': link_path,
                        'severity': 'high'
                    })

        return issues

    def _check_style(self, docs: List[Path]) -> List[Dict]:
        """Check markdown style consistency"""
        issues = []

        for doc_path in docs:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for missing code block languages
            if re.search(r'```\n', content):
                issues.append({
                    'file': str(doc_path.relative_to(self.base_path)),
                    'type': 'missing_code_language',
                    'severity': 'low'
                })

            # Check heading hierarchy
            lines = content.split('\n')
            prev_level = 0
            for i, line in enumerate(lines):
                if match := re.match(r'^(#+)\s+(.+)$', line):
                    level = len(match.group(1))
                    if level > prev_level + 1 and prev_level > 0:
                        issues.append({
                            'file': str(doc_path.relative_to(self.base_path)),
                            'type': 'heading_hierarchy',
                            'line': i + 1,
                            'severity': 'medium'
                        })
                        break
                    prev_level = level

        return issues

    def _find_stale_docs(self, analyses: Dict) -> List[Tuple[str, str]]:
        """Find documentation that needs updating"""
        stale_docs = []
        cutoff = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

        for path, analysis in analyses.items():
            if not analysis['last_updated'] or analysis['last_updated'] < cutoff:
                stale_docs.append((path, analysis['last_updated'] or 'No date'))

        return stale_docs

    def _calculate_quality_score(self, analyses: Dict, link_issues: List,
                                 style_issues: List, stale_docs: List) -> int:
        """Calculate overall documentation quality score (0-100)"""
        total_files = len(analyses)
        if total_files == 0:
            return 0

        # Start with perfect score
        score = 100

        # Deduct for issues
        score -= len(link_issues) * 5  # -5 per broken link
        score -= len(style_issues) * 0.2  # -0.2 per style issue
        score -= len(stale_docs) * 1  # -1 per stale doc

        # Ensure minimum score of 0
        return max(0, int(score))

    def generate_report(self) -> str:
        """Generate comprehensive maintenance report"""
        results = self.results

        report = f"""# TOSCA Documentation Maintenance Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Quality Score:** {results['quality_score']}/100

---

## Executive Summary

**Total Documentation Files:** {results['total_files']}
**Total Word Count:** {sum(a['word_count'] for a in results['analyses'].values()):,}

### Issue Summary

| Category | Count | Severity |
|----------|-------|----------|
| Broken Links | {len(results['link_issues'])} | High |
| Style Issues | {len(results['style_issues'])} | Low-Medium |
| Stale Documents | {len(results['stale_docs'])} | Medium |

---

## Quality Metrics

### Documentation Coverage
- Files with dates: {sum(1 for a in results['analyses'].values() if a['last_updated'])}/{results['total_files']}
- Files with TODOs: {sum(1 for a in results['analyses'].values() if a['todos'] > 0)}
- Average words per file: {sum(a['word_count'] for a in results['analyses'].values()) // results['total_files'] if results['total_files'] > 0 else 0}

### Content Quality
- Total headings: {sum(a['headings'] for a in results['analyses'].values())}
- Total code blocks: {sum(a['code_blocks'] for a in results['analyses'].values())}
- Internal links: {sum(a['links_internal'] for a in results['analyses'].values())}
- External links: {sum(a['links_external'] for a in results['analyses'].values())}

---

## Issues Requiring Attention

### High Priority: Broken Links ({len(results['link_issues'])})

"""
        if results['link_issues']:
            for issue in results['link_issues']:
                report += f"- `{issue['file']}` → `{issue['link']}`\n"
        else:
            report += "*No broken links found!*\n"

        report += f"\n### Medium Priority: Stale Documentation ({len(results['stale_docs'])})\n\n"
        report += "*Documents without dates or >90 days old:*\n\n"

        if results['stale_docs']:
            for path, date in results['stale_docs'][:15]:  # Show first 15
                report += f"- `{path}`: {date}\n"
            if len(results['stale_docs']) > 15:
                report += f"\n*... and {len(results['stale_docs']) - 15} more*\n"
        else:
            report += "*All documentation is current!*\n"

        report += f"""
---

## Recommendations

### Immediate Actions (Priority 1)

1. **Fix Broken Links** ({len(results['link_issues'])} issues)
   - Review and update all broken internal links
   - Verify file paths and directory structure

2. **Update Stale Documentation** ({len(results['stale_docs'])} docs)
   - Add "Last Updated" dates to all documentation
   - Review and refresh content >90 days old

### Short-Term Actions (Priority 2)

3. **Style Consistency** ({len(results['style_issues'])} issues)
   - Add language specifications to code blocks
   - Fix heading hierarchy jumps
   - Standardize list formatting

4. **Content Enhancement**
   - Add table of contents to long documents (>500 lines)
   - Improve cross-referencing between related docs
   - Add missing metadata and frontmatter

### Long-Term Actions (Priority 3)

5. **Automated Maintenance**
   - Schedule monthly documentation audits
   - Implement pre-commit hooks for link validation
   - Set up automated stale documentation alerts

6. **Quality Standards**
   - Establish documentation style guide
   - Create templates for common document types
   - Implement peer review process for major updates

---

## Maintenance Schedule

**Recommended Frequency:**
- Daily: Automated link validation (pre-commit hooks)
- Weekly: Style consistency checks
- Monthly: Full documentation audit
- Quarterly: Comprehensive content review and updates

**Next Scheduled Audit:** {(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}

---

**Report Version:** 1.0
**Tool:** TOSCA Documentation Maintenance System
**Contact:** See project documentation for development guidelines
"""

        return report

    def save_results(self, output_dir: str = 'docs/reports'):
        """Save audit results and report"""
        output_path = self.base_path / output_dir
        output_path.mkdir(parents=True, exist_ok=True)

        # Save JSON results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = output_path / f'doc_audit_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        # Save markdown report
        report = self.generate_report()
        report_file = self.base_path / 'docs' / 'DOCUMENTATION_MAINTENANCE_REPORT.md'
        with open(report_file, 'w') as f:
            f.write(report)

        print(f"\n✅ Results saved:")
        print(f"   JSON: {json_file}")
        print(f"   Report: {report_file}")

        return json_file, report_file


def main():
    parser = argparse.ArgumentParser(description='TOSCA Documentation Maintenance System')
    parser.add_argument('--base-path', default=None, help='Base path to TOSCA project')
    parser.add_argument('--output-dir', default='docs/reports', help='Output directory for reports')
    parser.add_argument('--score-only', action='store_true', help='Print quality score only')

    args = parser.parse_args()

    # Auto-detect project root if not specified
    if args.base_path is None:
        # Try to find project root by looking for pyproject.toml or .git
        current = Path.cwd()
        while current != current.parent:
            if (current / 'pyproject.toml').exists() or (current / '.git').exists():
                args.base_path = str(current)
                break
            current = current.parent
        else:
            # Fallback to current directory
            args.base_path = '.'

    # Run maintenance
    maintenance = DocumentationMaintenance(args.base_path)
    results = maintenance.run_full_audit()

    if args.score_only:
        print(f"Quality Score: {results['quality_score']}/100")
    else:
        # Save results
        maintenance.save_results(args.output_dir)

        # Print summary
        print(f"\n📊 Documentation Quality Score: {results['quality_score']}/100")
        print(f"\n✓ Audit complete!")


if __name__ == '__main__':
    main()
