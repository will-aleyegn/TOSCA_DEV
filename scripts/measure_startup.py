#!/usr/bin/env python
"""
Measure TOSCA application startup time.

Measures time from script start to main window display.
Runs multiple iterations for statistical accuracy.
"""

import statistics
import sys
import time
from pathlib import Path

# Add src to path (same as src/main.py does)
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))


def measure_startup():
    """Measure single startup iteration."""
    start_time = time.perf_counter()

    # Import Qt before importing application to suppress warnings
    from PyQt6.QtCore import QTimer
    from PyQt6.QtWidgets import QApplication

    # Import main module (imports are relative to src/ now)
    from ui.main_window import MainWindow

    import_complete = time.perf_counter()

    # Create application (no GUI display for measurement)
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)

    # Create main window but don't show (avoids need for X server)
    window = MainWindow()

    init_complete = time.perf_counter()

    # Clean up
    window.close()
    del window

    end_time = time.perf_counter()

    return {
        "total": end_time - start_time,
        "import_time": import_complete - start_time,
        "init_time": init_complete - import_complete,
        "cleanup_time": end_time - init_complete,
    }


def main():
    """Run multiple measurements and report statistics."""
    print("TOSCA Startup Performance Baseline")
    print("=" * 60)
    print()

    iterations = 5
    print(f"Running {iterations} measurement iterations...")
    print()

    results = []
    for i in range(iterations):
        print(f"Iteration {i+1}/{iterations}...", end=" ", flush=True)
        try:
            result = measure_startup()
            results.append(result)
            print(f"Total: {result['total']:.3f}s")
        except Exception as e:
            print(f"FAILED: {e}")

    if not results:
        print("\nERROR: All measurement iterations failed")
        return 1

    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print()

    # Calculate statistics
    total_times = [r["total"] for r in results]
    import_times = [r["import_time"] for r in results]
    init_times = [r["init_time"] for r in results]

    print(f"Total Startup Time:")
    print(f"  Mean:   {statistics.mean(total_times):.3f}s")
    print(f"  Median: {statistics.median(total_times):.3f}s")
    print(f"  StdDev: {statistics.stdev(total_times):.3f}s")
    print(f"  Min:    {min(total_times):.3f}s")
    print(f"  Max:    {max(total_times):.3f}s")
    print()

    print(f"Import Time:")
    print(f"  Mean:   {statistics.mean(import_times):.3f}s")
    print(f"  Median: {statistics.median(import_times):.3f}s")
    print()

    print(f"Initialization Time:")
    print(f"  Mean:   {statistics.mean(init_times):.3f}s")
    print(f"  Median: {statistics.median(init_times):.3f}s")
    print()

    # Breakdown
    avg_total = statistics.mean(total_times)
    avg_import = statistics.mean(import_times)
    avg_init = statistics.mean(init_times)

    print("Time Breakdown:")
    print(f"  Import:         {avg_import:.3f}s ({avg_import/avg_total*100:.1f}%)")
    print(f"  Initialization: {avg_init:.3f}s ({avg_init/avg_total*100:.1f}%)")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
