#!/usr/bin/env python3
"""Display presubmit documentation reminder before commits."""
import sys
from pathlib import Path

reminder_file = Path("presubmit/REMINDER.txt")

if reminder_file.exists():
    print(reminder_file.read_text(encoding="utf-8"))
    print()

sys.exit(0)  # Always succeed (don't block commit)
