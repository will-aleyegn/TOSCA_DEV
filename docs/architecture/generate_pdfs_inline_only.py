#!/usr/bin/env python3
"""
Generate PDFs from architecture markdown files with inline diagrams only.

This script:
1. Copies PNG files to temp directory with sanitized names
2. Creates temporary markdown with inline diagram references (no prepending)
3. Generates PDFs using pandoc WITHOUT table of contents or diagram sections
4. Cleans up temporary files

Differences from generate_pdfs.py:
- Does NOT prepend "Architecture Diagrams" section
- Does NOT generate table of contents
- Preserves inline diagram references exactly as written

Usage:
    python generate_pdfs_inline_only.py [--all] [--file <filename>]
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional


class InlinePDFGenerator:
    """Generate PDFs from markdown with inline diagrams only."""

    def __init__(self):
        """Initialize generator."""
        self.base_dir = Path(__file__).parent
        self.diagrams_dir = self.base_dir / "diagrams" / "output" / "png"
        self.pdf_output_dir = self.base_dir / "pdfs"
        self.temp_dir = self.base_dir / ".pdf_temp_inline"

        # Create output directories
        self.pdf_output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)

    def sanitize_filename(self, filename: str) -> str:
        """Convert filename to safe version without spaces."""
        return filename.lower().replace(" ", "_").replace("-", "_")

    def prepare_diagrams(self) -> Dict[str, str]:
        """Copy PNG diagrams to temp directory with sanitized names.

        Returns:
            Mapping of original names to sanitized names
        """
        diagram_map = {}

        if not self.diagrams_dir.exists():
            print(f"Warning: Diagrams directory not found: {self.diagrams_dir}")
            return diagram_map

        for png_file in self.diagrams_dir.glob("*.png"):
            original_name = png_file.name
            sanitized_name = self.sanitize_filename(original_name)

            # Copy to temp directory
            temp_path = self.temp_dir / sanitized_name
            shutil.copy2(png_file, temp_path)

            diagram_map[original_name] = sanitized_name
            print(f"  Copied: {original_name} -> {sanitized_name}")

        return diagram_map

    def create_temp_markdown(self, md_file: Path) -> tuple[Path, Optional[str]]:
        """Create temporary markdown preserving inline diagrams.

        Args:
            md_file: Original markdown file

        Returns:
            Tuple of (Path to temporary markdown file, extracted title or None)
        """
        temp_md = self.temp_dir / md_file.name

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract the first H1 title to use as Pandoc metadata
        lines = content.split('\n')
        extracted_title = None
        title_index = None

        for i, line in enumerate(lines):
            if line.startswith('# '):
                extracted_title = line[2:].strip()
                title_index = i
                break

        # Remove the title from content (Pandoc will add it from metadata)
        if title_index is not None:
            lines.pop(title_index)
            content = '\n'.join(lines)

        # Write temporary file WITHOUT any prepended diagram section
        with open(temp_md, 'w', encoding='utf-8') as f:
            f.write(content)

        return temp_md, extracted_title

    def generate_pdf(self, md_file: Path, output_pdf: Path, title: Optional[str] = None) -> bool:
        """Generate PDF from markdown using pandoc.

        Args:
            md_file: Path to markdown file
            output_pdf: Path for output PDF
            title: Optional document title (will be added as Pandoc metadata)

        Returns:
            True if successful, False otherwise
        """
        pandoc_cmd = [
            'pandoc',
            str(md_file),
            '-o', str(output_pdf),
            '--pdf-engine', 'wkhtmltopdf',
            '--css', str(self.base_dir / 'pdf-styles.css'),
            '-V', 'margin-left=0.75in',
            '-V', 'margin-right=0.75in',
            '-V', 'margin-top=0.75in',
            '-V', 'margin-bottom=0.75in'
        ]

        # Add title as metadata if provided (NO TOC)
        if title:
            pandoc_cmd.extend(['--metadata', f'title={title}'])

        try:
            # Change to temp directory so relative paths work
            result = subprocess.run(
                pandoc_cmd,
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print(f"  ✓ Generated: {output_pdf.name}")
                return True
            else:
                print(f"  ✗ Error generating {output_pdf.name}")
                print(f"    {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"  ✗ Timeout generating {output_pdf.name}")
            return False
        except Exception as e:
            print(f"  ✗ Exception: {e}")
            return False

    def process_file(self, md_filename: str) -> bool:
        """Process a single markdown file to PDF.

        Args:
            md_filename: Name of markdown file (with or without .md)

        Returns:
            True if successful, False otherwise
        """
        # Ensure .md extension
        if not md_filename.endswith('.md'):
            md_filename += '.md'

        md_file = self.base_dir / md_filename

        if not md_file.exists():
            print(f"Error: File not found: {md_file}")
            return False

        print(f"\nProcessing: {md_filename}")

        # Prepare diagram files
        diagram_map = self.prepare_diagrams()

        # Create temporary markdown preserving inline diagrams (extracts title)
        temp_md, extracted_title = self.create_temp_markdown(md_file)

        # Generate PDF with extracted title as metadata
        output_pdf = self.pdf_output_dir / md_file.with_suffix('.pdf').name
        success = self.generate_pdf(temp_md, output_pdf, title=extracted_title)

        return success

    def process_all(self) -> Dict[str, bool]:
        """Process all markdown files in directory.

        Returns:
            Dictionary mapping filenames to success status
        """
        results = {}

        # Get all markdown files
        md_files = sorted(self.base_dir.glob("*.md"))

        print(f"Found {len(md_files)} markdown files")

        for md_file in md_files:
            success = self.process_file(md_file.name)
            results[md_file.name] = success

        return results

    def cleanup(self):
        """Remove temporary files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            print("\nCleaned up temporary files")

    def print_summary(self, results: Dict[str, bool]):
        """Print summary of results."""
        total = len(results)
        successful = sum(1 for v in results.values() if v)
        failed = total - successful

        print("\n" + "="*60)
        print("PDF Generation Summary (Inline Diagrams Only)")
        print("="*60)
        print(f"Total files:      {total}")
        print(f"Successful:       {successful}")
        print(f"Failed:           {failed}")
        print(f"Output directory: {self.pdf_output_dir}")
        print("="*60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate PDFs from markdown with inline diagrams only (no TOC, no prepended diagrams)"
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all markdown files'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Process specific markdown file'
    )
    parser.add_argument(
        '--keep-temp',
        action='store_true',
        help='Keep temporary files for debugging'
    )

    args = parser.parse_args()

    # Create generator
    generator = InlinePDFGenerator()

    try:
        if args.file:
            # Process single file
            success = generator.process_file(args.file)
            results = {args.file: success}
        elif args.all:
            # Process all files
            results = generator.process_all()
        else:
            parser.print_help()
            return 1

        # Print summary
        generator.print_summary(results)

        # Cleanup
        if not args.keep_temp:
            generator.cleanup()

        # Return success code
        return 0 if all(results.values()) else 1

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        generator.cleanup()
        return 130
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
