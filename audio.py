"""Extract a Whisper-friendly audio track with ffmpeg."""
import subprocess
from pathlib import Path


def extract_audio(video_path: Path, work_dir: Path) -> Path:
    out_path = work_dir / "audio.wav"
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",                 # drop the video stream
        "-ar", "16000",        # 16 kHz sample rate (optimal for Whisper)
        "-ac", "1",            # mono
        "-c:a", "pcm_s16le",   # uncompressed 16-bit PCM
        str(out_path),
    ]
    subprocess.run(cmd, check=True)
    return out_path
