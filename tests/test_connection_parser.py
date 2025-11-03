"""
Unit tests for PyQt6 signal/slot connection parser.

Tests AST parsing of .connect() calls, connection extraction,
and report generation.

Author: AI Assistant (Task 4.2)
Created: 2025-11-01
"""

import tempfile
from pathlib import Path

import pytest

from src.utils.connection_parser import (
    ConnectionAnalyzer,
    ConnectionParser,
    ParsedConnection,
    analyze_project_connections,
    parse_connections_in_file,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def simple_connection_code():
    """Simple test code with basic signal/slot connections."""
    return """
from PyQt6.QtWidgets import QPushButton, QWidget
from PyQt6.QtCore import pyqtSignal

class TestWidget(QWidget):
    custom_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.button = QPushButton("Test")

        # Simple connection
        self.button.clicked.connect(self.on_button_clicked)

        # Lambda connection
        self.button.clicked.connect(lambda: print("Clicked"))

        # Custom signal
        self.custom_signal.connect(self.on_value_changed)

    def on_button_clicked(self):
        pass

    def on_value_changed(self, value: int):
        pass
"""


@pytest.fixture
def complex_connection_code():
    """Complex test code with various connection patterns."""
    return """
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

class ComplexWidget(QWidget):
    value_changed = pyqtSignal(int, str)
    status_updated = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Chained attribute connection
        self.child.widget.signal.connect(self.handler)

        # Multiple connections
        self.value_changed.connect(self.on_value_changed)
        self.value_changed.connect(lambda v, s: print(v, s))

        # Global function
        self.status_updated.connect(global_handler)

    def handler(self):
        pass

    def on_value_changed(self, val, status):
        pass

def global_handler():
    pass
"""


@pytest.fixture
def temp_python_file(tmp_path):
    """Create a temporary Python file for testing."""

    def _create_file(content: str, filename: str = "test.py") -> Path:
        file_path = tmp_path / filename
        file_path.write_text(content, encoding="utf-8")
        return file_path

    return _create_file


# ============================================================================
# ConnectionParser Tests
# ============================================================================


def test_parser_initialization():
    """Test ConnectionParser initialization."""
    parser = ConnectionParser("test.py")
    assert parser.source_file == "test.py"
    assert parser.connections == []
    assert parser.current_class is None


def test_parse_simple_connections(temp_python_file, simple_connection_code):
    """Test parsing simple signal/slot connections."""
    file_path = temp_python_file(simple_connection_code)
    parser = ConnectionParser(str(file_path))
    connections = parser.parse_file(str(file_path))

    # Should find 3 connections (clicked -> on_button_clicked, clicked -> lambda, custom_signal -> on_value_changed)
    assert len(connections) >= 3

    # Check first connection (button.clicked -> on_button_clicked)
    direct_conns = [c for c in connections if c.connection_type == "direct"]
    assert len(direct_conns) >= 2

    button_conn = next(c for c in direct_conns if c.signal_name == "clicked")
    assert button_conn.signal_object == "self.button"
    assert button_conn.slot_name == "on_button_clicked"
    assert not button_conn.is_lambda


def test_parse_lambda_connections(temp_python_file, simple_connection_code):
    """Test parsing lambda slot connections."""
    file_path = temp_python_file(simple_connection_code)
    connections = parse_connections_in_file(str(file_path))

    # Find lambda connection
    lambda_conns = [c for c in connections if c.is_lambda]
    assert len(lambda_conns) >= 1

    lambda_conn = lambda_conns[0]
    assert lambda_conn.connection_type == "lambda"
    assert lambda_conn.slot_object == "lambda"
    assert lambda_conn.slot_name == "lambda"


def test_parse_complex_connections(temp_python_file, complex_connection_code):
    """Test parsing complex connection patterns."""
    file_path = temp_python_file(complex_connection_code)
    connections = parse_connections_in_file(str(file_path))

    # Should find multiple connections
    assert len(connections) >= 4

    # Check chained attribute (child.widget.signal)
    chained_conn = next((c for c in connections if "child" in c.signal_object), None)
    assert chained_conn is not None

    # Check global function handler
    global_conn = next((c for c in connections if c.slot_object == "global"), None)
    assert global_conn is not None
    assert global_conn.slot_name == "global_handler"


def test_parse_file_with_syntax_error(temp_python_file):
    """Test parser handles syntax errors gracefully."""
    invalid_code = "def broken syntax here"
    file_path = temp_python_file(invalid_code)

    parser = ConnectionParser(str(file_path))
    connections = parser.parse_file(str(file_path))

    # Should return empty list on syntax error
    assert connections == []


def test_parse_file_not_found():
    """Test parser handles missing files gracefully."""
    parser = ConnectionParser("nonexistent.py")
    connections = parser.parse_file("nonexistent.py")
    assert connections == []


def test_connection_line_numbers(temp_python_file, simple_connection_code):
    """Test that line numbers are correctly captured."""
    file_path = temp_python_file(simple_connection_code)
    connections = parse_connections_in_file(str(file_path))

    # All connections should have valid line numbers
    for conn in connections:
        assert conn.line_number > 0
        assert conn.raw_code != ""


def test_parse_raw_code_extraction(temp_python_file, simple_connection_code):
    """Test extraction of raw code snippets."""
    file_path = temp_python_file(simple_connection_code)
    connections = parse_connections_in_file(str(file_path))

    # Check that raw code contains 'connect'
    for conn in connections:
        assert "connect" in conn.raw_code


# ============================================================================
# ConnectionAnalyzer Tests
# ============================================================================


def test_analyzer_initialization():
    """Test ConnectionAnalyzer initialization."""
    analyzer = ConnectionAnalyzer()
    assert analyzer.report is not None
    assert analyzer.report.total_connections == 0
    assert len(analyzer.report.connections) == 0


def test_analyze_single_file(temp_python_file, simple_connection_code):
    """Test analyzing a single file."""
    file_path = temp_python_file(simple_connection_code)
    analyzer = ConnectionAnalyzer()
    connections = analyzer.analyze_file(str(file_path))

    assert len(connections) >= 3
    assert str(file_path) in analyzer.report.files_analyzed


def test_analyze_directory(tmp_path, simple_connection_code, complex_connection_code):
    """Test analyzing a directory of Python files."""
    # Create multiple test files
    file1 = tmp_path / "test1.py"
    file1.write_text(simple_connection_code, encoding="utf-8")

    file2 = tmp_path / "test2.py"
    file2.write_text(complex_connection_code, encoding="utf-8")

    # Analyze directory
    analyzer = ConnectionAnalyzer()
    report = analyzer.analyze_directory(str(tmp_path))

    # Should find connections from both files
    assert report.total_connections >= 7
    assert len(report.files_analyzed) == 2
    assert str(file1) in report.files_analyzed
    assert str(file2) in report.files_analyzed


def test_analyze_nonexistent_directory():
    """Test analyzer handles nonexistent directories gracefully."""
    analyzer = ConnectionAnalyzer()
    report = analyzer.analyze_directory("/nonexistent/path")

    assert report.total_connections == 0
    assert len(report.files_analyzed) == 0


def test_generate_statistics(temp_python_file, simple_connection_code):
    """Test generation of connection statistics."""
    file_path = temp_python_file(simple_connection_code)
    analyzer = ConnectionAnalyzer()
    analyzer.analyze_file(str(file_path))

    # Check statistics
    assert analyzer.report.total_connections >= 3
    assert "direct" in analyzer.report.connections_by_type
    assert "lambda" in analyzer.report.connections_by_type


def test_generate_markdown_report(temp_python_file, simple_connection_code):
    """Test markdown report generation."""
    file_path = temp_python_file(simple_connection_code)
    analyzer = ConnectionAnalyzer()
    analyzer.analyze_file(str(file_path))

    # Generate report
    markdown = analyzer.generate_markdown_report()

    # Check report content
    assert "# PyQt6 Signal/Slot Connection Analysis Report" in markdown
    assert "Total Connections:" in markdown
    assert "Files Analyzed:" in markdown
    assert "Connection Types" in markdown


def test_save_markdown_report(temp_python_file, simple_connection_code, tmp_path):
    """Test saving markdown report to file."""
    file_path = temp_python_file(simple_connection_code)
    analyzer = ConnectionAnalyzer()
    analyzer.analyze_file(str(file_path))

    # Save report
    output_path = tmp_path / "report.md"
    markdown = analyzer.generate_markdown_report(str(output_path))

    # Check file was created
    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert content == markdown


# ============================================================================
# Real File Tests (Integration)
# ============================================================================


def test_parse_real_main_window():
    """Test parsing the actual TOSCA main_window.py file."""
    main_window_path = "src/ui/main_window.py"

    # Skip if file doesn't exist (running tests outside project)
    if not Path(main_window_path).exists():
        pytest.skip("main_window.py not found (tests running outside TOSCA project)")

    connections = parse_connections_in_file(main_window_path)

    # Main window should have many connections
    assert len(connections) > 20

    # Check for known connections
    signal_names = {c.signal_name for c in connections}
    assert "connection_changed" in signal_names
    assert "clicked" in signal_names
    assert "session_started" in signal_names


def test_parse_real_widgets():
    """Test parsing actual TOSCA widget files."""
    widgets_dir = "src/ui/widgets"

    # Skip if directory doesn't exist
    if not Path(widgets_dir).exists():
        pytest.skip("widgets directory not found (tests running outside TOSCA project)")

    analyzer = ConnectionAnalyzer()
    report = analyzer.analyze_directory(widgets_dir)

    # Widgets should have connections
    assert report.total_connections > 0
    assert len(report.files_analyzed) > 5


# ============================================================================
# Convenience Function Tests
# ============================================================================


def test_parse_connections_in_file_convenience(temp_python_file, simple_connection_code):
    """Test parse_connections_in_file convenience function."""
    file_path = temp_python_file(simple_connection_code)
    connections = parse_connections_in_file(str(file_path))

    assert isinstance(connections, list)
    assert len(connections) >= 3
    assert all(isinstance(c, ParsedConnection) for c in connections)


def test_analyze_project_connections_convenience(tmp_path, simple_connection_code):
    """Test analyze_project_connections convenience function."""
    # Create test file
    file_path = tmp_path / "test.py"
    file_path.write_text(simple_connection_code, encoding="utf-8")

    # Analyze project
    report = analyze_project_connections(str(tmp_path))

    assert report.total_connections >= 3
    assert len(report.files_analyzed) == 1


# ============================================================================
# Edge Case Tests
# ============================================================================


def test_parse_empty_file(temp_python_file):
    """Test parsing an empty Python file."""
    file_path = temp_python_file("")
    connections = parse_connections_in_file(str(file_path))
    assert connections == []


def test_parse_no_connections(temp_python_file):
    """Test parsing a file with no connections."""
    code = """
class Widget:
    def __init__(self):
        self.value = 42

    def method(self):
        return self.value
"""
    file_path = temp_python_file(code)
    connections = parse_connections_in_file(str(file_path))
    assert connections == []


def test_parse_connect_without_args(temp_python_file):
    """Test parsing .connect() call without arguments (malformed)."""
    code = """
from PyQt6.QtWidgets import QPushButton

class Widget:
    def __init__(self):
        button = QPushButton()
        button.clicked.connect()  # Malformed - no slot argument
"""
    file_path = temp_python_file(code)
    connections = parse_connections_in_file(str(file_path))

    # Parser should handle gracefully (either skip or capture as unknown)
    # Should not crash
    assert isinstance(connections, list)
