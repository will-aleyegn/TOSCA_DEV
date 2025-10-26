"""
Test script for the new UI features.
This script demonstrates that all the new components are properly integrated.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        # Test core imports
        from core.session_manager import SessionManager

        print("[OK] SessionManager imported successfully")

        # Check that end_session method exists
        assert hasattr(SessionManager, "end_session"), "end_session method not found"
        print("[OK] SessionManager.end_session() method exists")

        # Test database imports
        from database.db_manager import DatabaseManager

        print("[OK] DatabaseManager imported successfully")

        # Check that get_all_sessions method exists
        assert hasattr(DatabaseManager, "get_all_sessions"), "get_all_sessions method not found"
        print("[OK] DatabaseManager.get_all_sessions() method exists")

        # Test UI imports
        from ui.widgets.subject_widget import SubjectWidget

        print("[OK] SubjectWidget imported successfully")

        # Check new methods exist
        assert hasattr(SubjectWidget, "_on_end_session"), "_on_end_session method not found"
        assert hasattr(SubjectWidget, "_on_view_sessions"), "_on_view_sessions method not found"
        print("[OK] SubjectWidget._on_end_session() method exists")
        print("[OK] SubjectWidget._on_view_sessions() method exists")

        # Test dialog import
        from ui.widgets.view_sessions_dialog import ViewSessionsDialog

        print("[OK] ViewSessionsDialog imported successfully")

        print("\n[SUCCESS] All imports successful!")
        return True

    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False
    except AssertionError as e:
        print(f"[ERROR] Assertion error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False


def test_ui_structure():
    """Test that UI components are properly structured."""
    print("\nTesting UI structure...")

    try:
        from PyQt6.QtWidgets import QApplication

        app = QApplication(sys.argv)

        from ui.widgets.subject_widget import SubjectWidget

        widget = SubjectWidget()

        # Check that new buttons exist
        assert hasattr(widget, "end_session_button"), "end_session_button not found"
        assert hasattr(widget, "view_sessions_button"), "view_sessions_button not found"
        print("[OK] end_session_button exists")
        print("[OK] view_sessions_button exists")

        # Check that new signal exists
        assert hasattr(widget, "session_ended"), "session_ended signal not found"
        print("[OK] session_ended signal exists")

        print("\n[SUCCESS] UI structure validated!")
        app.quit()
        return True

    except Exception as e:
        print(f"[ERROR] Error testing UI structure: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("TOSCA New Features Test")
    print("=" * 50)

    success = True

    # Test imports
    if not test_imports():
        success = False

    # Test UI structure (requires PyQt6)
    try:
        import PyQt6

        if not test_ui_structure():
            success = False
    except ImportError:
        print("\nNote: PyQt6 not installed, skipping UI structure tests")

    print("\n" + "=" * 50)
    if success:
        print("[SUCCESS] All tests passed!")
    else:
        print("[ERROR] Some tests failed")
    print("=" * 50)

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
