"""
PyQt6 Signal/Slot Connection Parser

AST-based parser for analyzing .connect() calls in Python source code
to map signal/slot connections across the TOSCA codebase.

Author: AI Assistant (Task 4.2)
Created: 2025-11-01
"""

import ast
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================


@dataclass
class ParsedConnection:
    """Information about a parsed signal/slot connection."""

    source_file: str  # File where connection is made
    line_number: int  # Line number in source file
    signal_object: str  # Object emitting signal (e.g., "self.button")
    signal_name: str  # Signal name (e.g., "clicked")
    slot_object: str  # Object receiving signal (e.g., "self")
    slot_name: str  # Slot method name (e.g., "on_button_clicked")
    connection_type: str = "direct"  # direct, lambda, partial
    is_lambda: bool = False  # True if slot is a lambda
    raw_code: str = ""  # Original code snippet


@dataclass
class ConnectionReport:
    """Report of all connections found in source files."""

    connections: List[ParsedConnection] = field(default_factory=list)
    files_analyzed: Set[str] = field(default_factory=set)
    total_connections: int = 0
    connections_by_type: Dict[str, int] = field(default_factory=dict)
    connections_by_file: Dict[str, List[ParsedConnection]] = field(default_factory=dict)


# ============================================================================
# AST Connection Parser
# ============================================================================


class ConnectionParser(ast.NodeVisitor):
    """
    AST visitor for parsing PyQt6 signal/slot connections.

    Analyzes .connect() method calls to extract signal and slot information.
    """

    def __init__(self, source_file: str):
        """
        Initialize connection parser.

        Args:
            source_file: Path to source file being parsed
        """
        self.source_file = source_file
        self.connections: List[ParsedConnection] = []
        self.current_class: Optional[str] = None
        self.source_lines: List[str] = []

    def parse_file(self, file_path: str) -> List[ParsedConnection]:
        """
        Parse a Python file to extract signal/slot connections.

        Args:
            file_path: Path to Python file to parse

        Returns:
            List of ParsedConnection objects found in the file
        """
        self.connections = []
        self.source_file = file_path

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
                self.source_lines = source_code.splitlines()

            # Parse AST
            tree = ast.parse(source_code, filename=file_path)
            self.visit(tree)

            logger.info(f"Parsed {file_path}: Found {len(self.connections)} connections")
            return self.connections

        except SyntaxError as e:
            logger.error(f"Syntax error parsing {file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return []

    def visit_ClassDef(self, node: ast.ClassDef):
        """Track current class for context."""
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_Call(self, node: ast.Call):
        """
        Visit Call nodes to find .connect() method calls.

        Handles patterns like:
        - signal.connect(slot_method)
        - self.button.clicked.connect(self.on_clicked)
        - widget.signal.connect(lambda: ...)
        """
        # Check if this is a .connect() call
        if isinstance(node.func, ast.Attribute) and node.func.attr == "connect":
            self._parse_connection(node)

        # Continue visiting child nodes
        self.generic_visit(node)

    def _parse_connection(self, node: ast.Call):
        """
        Parse a .connect() call to extract connection information.

        Args:
            node: AST Call node for .connect() method
        """
        try:
            # Extract signal object and name
            signal_expr = node.func.value  # The signal (e.g., self.button.clicked)
            signal_object, signal_name = self._extract_signal_info(signal_expr)

            # Extract slot information from first argument
            if len(node.args) == 0:
                logger.warning(f"connect() call with no arguments at line {node.lineno}")
                return

            slot_arg = node.args[0]
            slot_object, slot_name, is_lambda = self._extract_slot_info(slot_arg)

            # Determine connection type
            connection_type = "lambda" if is_lambda else "direct"

            # Get raw code snippet
            raw_code = self._get_raw_code(node.lineno)

            # Create connection record
            connection = ParsedConnection(
                source_file=self.source_file,
                line_number=node.lineno,
                signal_object=signal_object,
                signal_name=signal_name,
                slot_object=slot_object,
                slot_name=slot_name,
                connection_type=connection_type,
                is_lambda=is_lambda,
                raw_code=raw_code,
            )

            self.connections.append(connection)
            logger.debug(
                f"Found connection at line {node.lineno}: "
                f"{signal_object}.{signal_name} -> {slot_object}.{slot_name}"
            )

        except Exception as e:
            logger.warning(f"Could not parse connection at line {node.lineno}: {e}")

    def _extract_signal_info(self, signal_expr: ast.expr) -> Tuple[str, str]:
        """
        Extract signal object and name from signal expression.

        Args:
            signal_expr: AST expression for signal (e.g., self.button.clicked)

        Returns:
            Tuple of (signal_object, signal_name)
        """
        if isinstance(signal_expr, ast.Attribute):
            # signal_name is the attribute (e.g., "clicked")
            signal_name = signal_expr.attr

            # signal_object is the object chain (e.g., "self.button")
            signal_object = self._ast_to_string(signal_expr.value)

            return signal_object, signal_name

        # Fallback for complex expressions
        return self._ast_to_string(signal_expr), "unknown"

    def _extract_slot_info(self, slot_expr: ast.expr) -> Tuple[str, str, bool]:
        """
        Extract slot object, method name, and lambda status from slot expression.

        Args:
            slot_expr: AST expression for slot (e.g., self.on_clicked or lambda: ...)

        Returns:
            Tuple of (slot_object, slot_name, is_lambda)
        """
        # Lambda function
        if isinstance(slot_expr, ast.Lambda):
            return "lambda", "lambda", True

        # Method attribute (e.g., self.on_clicked)
        if isinstance(slot_expr, ast.Attribute):
            slot_name = slot_expr.attr
            slot_object = self._ast_to_string(slot_expr.value)
            return slot_object, slot_name, False

        # Name reference (e.g., some_function)
        if isinstance(slot_expr, ast.Name):
            return "global", slot_expr.id, False

        # Fallback
        return "unknown", self._ast_to_string(slot_expr), False

    def _ast_to_string(self, node: ast.expr) -> str:
        """
        Convert AST expression to string representation.

        Args:
            node: AST expression node

        Returns:
            String representation of the expression
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            base = self._ast_to_string(node.value)
            return f"{base}.{node.attr}"
        elif isinstance(node, ast.Call):
            func = self._ast_to_string(node.func)
            return f"{func}(...)"
        else:
            return ast.unparse(node) if hasattr(ast, "unparse") else "unknown"

    def _get_raw_code(self, line_number: int) -> str:
        """
        Get raw code snippet for a given line number.

        Args:
            line_number: Line number (1-indexed)

        Returns:
            Code snippet string
        """
        if 1 <= line_number <= len(self.source_lines):
            return self.source_lines[line_number - 1].strip()
        return ""


# ============================================================================
# Connection Analyzer
# ============================================================================


class ConnectionAnalyzer:
    """
    Analyzes signal/slot connections across multiple source files.

    Combines AST parsing with runtime introspection to validate connections.
    """

    def __init__(self):
        """Initialize connection analyzer."""
        self.report = ConnectionReport()
        logger.info("ConnectionAnalyzer initialized")

    def analyze_directory(self, directory: str, pattern: str = "*.py") -> ConnectionReport:
        """
        Analyze all Python files in a directory for signal/slot connections.

        Args:
            directory: Directory path to analyze
            pattern: File pattern to match (default: "*.py")

        Returns:
            ConnectionReport with all found connections
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            logger.error(f"Directory does not exist: {directory}")
            return self.report

        # Find all matching files
        files = list(dir_path.rglob(pattern))
        logger.info(f"Analyzing {len(files)} Python files in {directory}")

        # Parse each file
        for file_path in files:
            self.analyze_file(str(file_path))

        # Generate statistics
        self._generate_statistics()

        return self.report

    def analyze_file(self, file_path: str) -> List[ParsedConnection]:
        """
        Analyze a single Python file for connections.

        Args:
            file_path: Path to Python file

        Returns:
            List of ParsedConnection objects found in file
        """
        parser = ConnectionParser(file_path)
        connections = parser.parse_file(file_path)

        # Add to report
        self.report.connections.extend(connections)
        self.report.files_analyzed.add(file_path)
        self.report.connections_by_file[file_path] = connections

        # Update statistics
        self._generate_statistics()

        return connections

    def _generate_statistics(self):
        """Generate summary statistics for the report."""
        self.report.total_connections = len(self.report.connections)

        # Count by connection type
        type_counts: Dict[str, int] = {}
        for conn in self.report.connections:
            type_counts[conn.connection_type] = type_counts.get(conn.connection_type, 0) + 1

        self.report.connections_by_type = type_counts

        logger.info(f"Analysis complete: {self.report.total_connections} total connections")
        logger.info(f"  Files analyzed: {len(self.report.files_analyzed)}")
        logger.info(f"  By type: {type_counts}")

    def generate_markdown_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate markdown report of all connections.

        Args:
            output_file: Optional file path to save report

        Returns:
            Markdown-formatted report string
        """
        lines = []
        lines.append("# PyQt6 Signal/Slot Connection Analysis Report")
        lines.append("")
        lines.append(f"**Total Connections:** {self.report.total_connections}")
        lines.append(f"**Files Analyzed:** {len(self.report.files_analyzed)}")
        lines.append("")

        # Summary by type
        lines.append("## Connection Types")
        lines.append("")
        for conn_type, count in sorted(self.report.connections_by_type.items()):
            lines.append(f"- **{conn_type}**: {count} connections")
        lines.append("")

        # Connections by file
        lines.append("## Connections by File")
        lines.append("")

        for file_path in sorted(self.report.connections_by_file.keys()):
            connections = self.report.connections_by_file[file_path]
            if len(connections) == 0:
                continue

            lines.append(f"### {Path(file_path).name}")
            lines.append(f"*File: `{file_path}`*")
            lines.append("")
            lines.append("| Line | Signal | Slot | Type |")
            lines.append("|------|--------|------|------|")

            for conn in sorted(connections, key=lambda c: c.line_number):
                signal = f"{conn.signal_object}.{conn.signal_name}"
                slot = f"{conn.slot_object}.{conn.slot_name}"
                lines.append(
                    f"| {conn.line_number} | `{signal}` | `{slot}` | {conn.connection_type} |"
                )

            lines.append("")

        report = "\n".join(lines)

        # Save to file if requested
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"Report saved to {output_file}")

        return report


# ============================================================================
# Convenience Functions
# ============================================================================


def parse_connections_in_file(file_path: str) -> List[ParsedConnection]:
    """
    Convenience function to parse connections in a single file.

    Args:
        file_path: Path to Python file

    Returns:
        List of ParsedConnection objects
    """
    parser = ConnectionParser(file_path)
    return parser.parse_file(file_path)


def analyze_project_connections(
    project_dir: str, output_file: Optional[str] = None
) -> ConnectionReport:
    """
    Convenience function to analyze all connections in a project.

    Args:
        project_dir: Root directory of project
        output_file: Optional path to save markdown report

    Returns:
        ConnectionReport with all found connections
    """
    analyzer = ConnectionAnalyzer()
    report = analyzer.analyze_directory(project_dir)

    if output_file:
        analyzer.generate_markdown_report(output_file)

    return report


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example: Analyze connections in TOSCA widgets
    analyzer = ConnectionAnalyzer()
    report = analyzer.analyze_directory("src/ui/widgets")

    # Print summary
    print(f"\n=== Connection Analysis Summary ===")
    print(f"Total connections: {report.total_connections}")
    print(f"Files analyzed: {len(report.files_analyzed)}")
    print(f"\nBy type:")
    for conn_type, count in report.connections_by_type.items():
        print(f"  {conn_type}: {count}")

    # Generate markdown report
    markdown = analyzer.generate_markdown_report("connection_report.md")
    print(f"\nReport saved to connection_report.md")
