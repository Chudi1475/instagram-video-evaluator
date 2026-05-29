# Instagram Video Evaluator

## What this is
A CLI tool that downloads an Instagram video, transcribes the speech, captures the
on-screen text via frame sampling, and sends both to the Anthropic API for evaluation.

## Architecture
Pipeline of single-purpose modules, orchestrated by main.py:
download.py (yt-dlp) -> audio.py (ffmpeg) -> transcribe.py (Groq/Whisper)
-> frames.py (ffmpeg + perceptual-hash dedup) -> evaluate.py (Anthropic) -> report.py

The core idea: transcript segments and frames are merged into one time-sorted list in
evaluate.build_content, so Claude sees what was said and what was on screen in order.
Frames go straight to Claude vision (no separate OCR).

## Conventions
- All config lives in config.py and is overridable via IGV_* environment variables.
- Heavy dependencies (groq, anthropic, PIL, imagehash, faster_whisper) are imported
  INSIDE functions, not at module top, so `python main.py --help` works with nothing
  installed. Keep it that way.
- Intermediate artifacts are written to work/ (gitignored).

## Running
python main.py "<instagram_url>"
python main.py "C:\path\to\video.mp4"                            # local file instead of a URL
python main.py "<instagram_url>" --cookies-from-browser chrome   # if download blocked
python main.py "<instagram_url>" --prompt "your custom evaluation question"

The positional arg accepts either an Instagram URL or a path to a local video file.
If it resolves to an existing file (Path.is_file()), the download step is skipped and
the file is used directly; otherwise it's treated as a URL and fetched with yt-dlp.

## Keys
ANTHROPIC_API_KEY (required), GROQ_API_KEY (required unless IGV_TRANSCRIBE_BACKEND=local).

## Gotchas
- yt-dlp breaks when Instagram changes; fix with `pip install -U yt-dlp`.
- Private/age-gated posts need --cookies-from-browser.
- If too many frames inflate cost, raise IGV_PHASH_THRESHOLD or lower IGV_MAX_FRAMES.
