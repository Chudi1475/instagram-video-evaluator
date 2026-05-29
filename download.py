"""Download an Instagram video (Reel or post) with yt-dlp."""
import subprocess
from pathlib import Path


def download_video(url: str, work_dir: Path, cookies_browser: str | None = None) -> Path:
    work_dir.mkdir(parents=True, exist_ok=True)
    out_template = str(work_dir / "video.%(ext)s")
    cmd = [
        "yt-dlp",
        "-f", "mp4/bestvideo*+bestaudio/best",
        "--merge-output-format", "mp4",
        "-o", out_template,
        url,
    ]
    if cookies_browser:
        # e.g. "chrome", "safari", "firefox", "edge", "brave"
        cmd += ["--cookies-from-browser", cookies_browser]

    subprocess.run(cmd, check=True)

    candidates = sorted(work_dir.glob("video.*"))
    if not candidates:
        raise FileNotFoundError("yt-dlp did not produce a video file.")
    for c in candidates:               # prefer the merged mp4
        if c.suffix.lower() == ".mp4":
            return c
    return candidates[0]
