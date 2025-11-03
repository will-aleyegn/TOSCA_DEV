"""
Verify the structure of the newly added code without runtime imports.
"""

import ast
import os


def verify_file_methods(filepath, class_name, expected_methods):
    """Verify that expected methods exist in a class."""
    print(f"\nVerifying {class_name} in {os.path.basename(filepath)}...")

    with open(filepath, "r") as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            method_names = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]

            for method in expected_methods:
                if method in method_names:
                    print(f"  [OK] Method '{method}' exists")
                else:
                    print(f"  [ERROR] Method '{method}' not found")
                    return False
            return True

    print(f"  [ERROR] Class '{class_name}' not found")
    return False


def verify_signal_exists(filepath, class_name, signal_name):
    """Verify that a PyQt signal exists in a class."""
    print(f"\nVerifying signal '{signal_name}' in {class_name}...")

    with open(filepath, "r") as f:
        content = f.read()

    # Simple text search for signal definition
    if f"{signal_name} = pyqtSignal" in content:
        print(f"  [OK] Signal '{signal_name}' exists")
        return True
    else:
        print(f"  [ERROR] Signal '{signal_name}' not found")
        return False


def main():
    """Run all verifications."""
    print("=" * 50)
    print("TOSCA Code Structure Verification")
    print("=" * 50)

    success = True

    # Verify SessionManager
    session_manager_path = "src/core/session_manager.py"
    if not verify_file_methods(session_manager_path, "SessionManager", ["end_session"]):
        success = False

    # Verify DatabaseManager
    db_manager_path = "src/database/db_manager.py"
    if not verify_file_methods(db_manager_path, "DatabaseManager", ["get_all_sessions"]):
        success = False

    # Verify SubjectWidget
    subject_widget_path = "src/ui/widgets/subject_widget.py"
    if not verify_file_methods(
        subject_widget_path, "SubjectWidget", ["_on_end_session", "_on_view_sessions"]
    ):
        success = False

    # Verify signal
    if not verify_signal_exists(subject_widget_path, "SubjectWidget", "session_ended"):
        success = False

    # Check if ViewSessionsDialog file exists
    dialog_path = "src/ui/widgets/view_sessions_dialog.py"
    if os.path.exists(dialog_path):
        print(f"\n[OK] File '{dialog_path}' exists")
        # Verify dialog class
        if not verify_file_methods(
            dialog_path, "ViewSessionsDialog", ["_init_ui", "_load_sessions"]
        ):
            success = False
    else:
        print(f"\n[ERROR] File '{dialog_path}' not found")
        success = False

    # Check button attributes in SubjectWidget
    print("\nVerifying UI elements in SubjectWidget...")
    with open(subject_widget_path, "r") as f:
        content = f.read()

    ui_elements = ["end_session_button", "view_sessions_button"]
    for element in ui_elements:
        if f"self.{element}" in content:
            print(f"  [OK] UI element '{element}' exists")
        else:
            print(f"  [ERROR] UI element '{element}' not found")
            success = False

    print("\n" + "=" * 50)
    if success:
        print("[SUCCESS] All verifications passed!")
    else:
        print("[ERROR] Some verifications failed")
    print("=" * 50)

    return success


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
