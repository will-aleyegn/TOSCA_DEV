#!/usr/bin/env python
"""Simple startup time measurement using existing main.py."""

import statistics
import subprocess
import time


def measure_import_time():
    """Measure just the import time."""
    cmd = [
        "python",
        "-c",
        'import time; start=time.time(); import src.main; print(f"{time.time()-start:.3f}")',
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def main():
    print("TOSCA Import Time Baseline Measurement")
    print("=" * 60)
    print()

    iterations = 10
    print(f"Running {iterations} iterations...")
    print()

    times = []
    for i in range(iterations):
        t = measure_import_time()
        times.append(t)
        print(f"  Run {i+1:2d}: {t:.3f}s")

    print()
    print("=" * 60)
    print("STATISTICS")
    print("=" * 60)
    print(f"Mean:   {statistics.mean(times):.3f}s")
    print(f"Median: {statistics.median(times):.3f}s")
    print(f"StdDev: {statistics.stdev(times):.4f}s")
    print(f"Min:    {min(times):.3f}s")
    print(f"Max:    {max(times):.3f}s")
    print()


if __name__ == "__main__":
    main()
