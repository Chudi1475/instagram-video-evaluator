"""Sample frames with ffmpeg, then drop near-duplicate frames via perceptual hashing.

Returns: list[tuple[float, Path]] of (timestamp_seconds, frame_path), time-sorted.
"""
import subprocess
from pathlib import Path

import config


def extract_frames(video_path: Path, work_dir: Path) -> list[tuple[float, Path]]:
    frames_dir = work_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    out_template = str(frames_dir / "frame_%05d.jpg")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"fps={config.FRAME_FPS}",
        "-q:v", "3",
        out_template,
    ]
    subprocess.run(cmd, check=True)

    paths = sorted(frames_dir.glob("frame_*.jpg"))
    # The fps filter emits frame index i (0-based) at t = i / fps seconds.
    return [(i / config.FRAME_FPS, p) for i, p in enumerate(paths)]


def dedupe_frames(frames: list[tuple[float, Path]]) -> list[tuple[float, Path]]:
    import imagehash      # pip install imagehash
    from PIL import Image  # pip install pillow

    kept: list[tuple[float, Path]] = []
    last_hash = None
    for ts, path in frames:
        h = imagehash.phash(Image.open(path))
        if last_hash is None or (h - last_hash) >= config.PHASH_THRESHOLD:
            kept.append((ts, path))
            last_hash = h
    # Safety cap: if still too many, keep an evenly spaced subset.
    if len(kept) > config.MAX_FRAMES:
        step = len(kept) / config.MAX_FRAMES
        kept = [kept[int(i * step)] for i in range(config.MAX_FRAMES)]
    return kept
