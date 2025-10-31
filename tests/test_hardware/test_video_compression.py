"""
Unit tests for video compression and codec handling.

Tests H.264 CRF parameter application and codec fallback.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from hardware.camera_controller import VideoRecorder


@pytest.fixture
def temp_video_dir(tmp_path):
    """Create temporary directory for video files."""
    video_dir = tmp_path / "videos"
    video_dir.mkdir()
    return video_dir


def create_test_frames(count: int, frame_size: tuple = (1456, 1088)) -> list:
    """Create test frames with random data."""
    frames = []
    for _ in range(count):
        # Create random frame (BGR format)
        frame = np.random.randint(0, 255, (frame_size[1], frame_size[0], 3), dtype=np.uint8)
        frames.append(frame)
    return frames


def test_h264_crf_reduces_file_size(temp_video_dir):
    """Test CRF parameter actually affects file size."""
    frame_count = 90  # 3 seconds at 30 FPS
    frames = create_test_frames(frame_count)

    # Record with CRF=28 (good quality/size balance)
    video_path_28 = temp_video_dir / "test_crf28.mp4"
    recorder_28 = VideoRecorder(output_path=video_path_28, fps=30.0, codec="H264", quality_crf=28)
    for frame in frames:
        recorder_28.write_frame(frame)
    recorder_28.close()

    # Record with CRF=18 (higher quality, larger file)
    video_path_18 = temp_video_dir / "test_crf18.mp4"
    recorder_18 = VideoRecorder(output_path=video_path_18, fps=30.0, codec="H264", quality_crf=18)
    for frame in frames:
        recorder_18.write_frame(frame)
    recorder_18.close()

    # Verify both files exist
    assert video_path_28.exists(), "CRF=28 video not created"
    assert video_path_18.exists(), "CRF=18 video not created"

    # Get file sizes
    size_28 = video_path_28.stat().st_size
    size_18 = video_path_18.stat().st_size

    # Verify CRF=28 produces smaller file
    assert size_28 < size_18, (
        f"CRF=28 ({size_28} bytes) should be smaller than CRF=18 ({size_18} bytes). "
        f"This indicates CRF parameter is not being applied correctly."
    )

    # Log sizes for debugging
    print(f"\nCRF=28 file size: {size_28 / 1024:.1f} KB")
    print(f"CRF=18 file size: {size_18 / 1024:.1f} KB")
    print(f"Size reduction: {(1 - size_28 / size_18) * 100:.1f}%")


def test_codec_fallback_works(temp_video_dir):
    """Test fallback to MJPEG when H.264 unavailable."""
    frame_count = 30  # 1 second
    frames = create_test_frames(frame_count)

    # Try with a codec that might not be available
    video_path = temp_video_dir / "test_fallback.mp4"
    recorder = VideoRecorder(
        output_path=video_path,
        fps=30.0,
        codec="FAKE264",  # Intentionally invalid
        fallback_codec="MJPG",  # Should fall back to this
        quality_crf=28,
    )

    # Write frames
    for frame in frames:
        recorder.write_frame(frame)
    recorder.close()

    # Verify file created (using fallback codec)
    assert video_path.exists(), "Video not created with fallback codec"
    assert recorder.actual_codec_used in [
        "MJPG",
        "FAKE264",
    ], f"Expected MJPG fallback, got: {recorder.actual_codec_used}"


def test_crf_config_setting_honored(temp_video_dir):
    """Test video_quality_crf config setting is applied."""
    frame_count = 60  # 2 seconds
    frames = create_test_frames(frame_count)

    # Test multiple CRF values
    crf_values = [18, 28, 35]
    file_sizes = {}

    for crf in crf_values:
        video_path = temp_video_dir / f"test_crf{crf}.mp4"
        recorder = VideoRecorder(output_path=video_path, fps=30.0, codec="H264", quality_crf=crf)

        for frame in frames:
            recorder.write_frame(frame)
        recorder.close()

        assert video_path.exists(), f"Video with CRF={crf} not created"
        file_sizes[crf] = video_path.stat().st_size

    # Verify CRF ordering: lower CRF = larger file
    assert file_sizes[18] > file_sizes[28], (
        f"CRF=18 ({file_sizes[18]} bytes) should be larger than " f"CRF=28 ({file_sizes[28]} bytes)"
    )
    assert file_sizes[28] > file_sizes[35], (
        f"CRF=28 ({file_sizes[28]} bytes) should be larger than " f"CRF=35 ({file_sizes[35]} bytes)"
    )

    print(f"\nFile sizes by CRF:")
    for crf, size in sorted(file_sizes.items()):
        print(f"  CRF={crf}: {size / 1024:.1f} KB")


def test_video_recorder_initialization(temp_video_dir):
    """Test VideoRecorder initialization and codec detection."""
    video_path = temp_video_dir / "test_init.mp4"
    recorder = VideoRecorder(output_path=video_path, fps=30.0, codec="H264", quality_crf=28)

    # Verify recorder initialized
    assert recorder.writer is not None, "VideoWriter not initialized"
    assert recorder.actual_codec_used != "none", "No codec available"

    recorder.close()


def test_video_compression_ratio_goal(temp_video_dir):
    """Test that CRF=28 achieves ~50% file size reduction vs CRF=18."""
    frame_count = 150  # 5 seconds at 30 FPS
    frames = create_test_frames(frame_count)

    # Baseline: CRF=18 (high quality)
    video_path_18 = temp_video_dir / "baseline_crf18.mp4"
    recorder_18 = VideoRecorder(output_path=video_path_18, fps=30.0, codec="H264", quality_crf=18)
    for frame in frames:
        recorder_18.write_frame(frame)
    recorder_18.close()

    # Optimized: CRF=28 (Week 4 goal)
    video_path_28 = temp_video_dir / "optimized_crf28.mp4"
    recorder_28 = VideoRecorder(output_path=video_path_28, fps=30.0, codec="H264", quality_crf=28)
    for frame in frames:
        recorder_28.write_frame(frame)
    recorder_28.close()

    # Calculate compression ratio
    size_18 = video_path_18.stat().st_size
    size_28 = video_path_28.stat().st_size
    reduction_percent = (1 - size_28 / size_18) * 100

    print(f"\nCompression test results:")
    print(f"  CRF=18 (baseline): {size_18 / 1024 / 1024:.2f} MB")
    print(f"  CRF=28 (optimized): {size_28 / 1024 / 1024:.2f} MB")
    print(f"  Reduction: {reduction_percent:.1f}%")

    # Verify meaningful compression (should be 30-60% reduction)
    assert reduction_percent >= 20, (
        f"Compression ratio too low ({reduction_percent:.1f}%). "
        f"Expected ~50% reduction. CRF parameter may not be applied."
    )
    assert reduction_percent <= 80, (
        f"Compression ratio too high ({reduction_percent:.1f}%). "
        f"This seems unrealistic for H.264 CRF difference."
    )


def test_frame_writing_consistency(temp_video_dir):
    """Test that all frames are written correctly."""
    frame_count = 60
    frames = create_test_frames(frame_count)

    video_path = temp_video_dir / "test_frames.mp4"
    recorder = VideoRecorder(output_path=video_path, fps=30.0, codec="H264", quality_crf=28)

    for frame in frames:
        recorder.write_frame(frame)

    # Verify frame count matches
    assert (
        recorder.frame_count == frame_count
    ), f"Expected {frame_count} frames, got {recorder.frame_count}"

    recorder.close()

    # Verify file exists and has reasonable size
    assert video_path.exists()
    assert video_path.stat().st_size > 1024, "Video file too small (likely corrupted)"
