"""CLI entry point: download -> audio -> transcribe -> frames -> evaluate -> report."""
import sys

# Force UTF-8 on stdout/stderr. Windows consoles default to cp1252, which raises
# UnicodeEncodeError when printing an evaluation that contains emojis or smart quotes
# (the saved report is already written as UTF-8; this only protects the terminal echo).
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

# Load .env into the environment before importing config (which reads os.getenv at
# import time). override=True so .env wins even if a stale/empty var (e.g. an empty
# ANTHROPIC_API_KEY) is already present in the parent environment. Optional dependency:
# if python-dotenv isn't installed, env vars set manually in the shell still work, and
# `python main.py --help` runs with nothing installed.
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

import argparse
from pathlib import Path

import config
import download
import audio
import transcribe
import frames as frames_mod
import evaluate as evaluate_mod
import report


DEFAULT_SYSTEM_PROMPT = (
    "You are a meticulous video analyst. You will receive a chronological mix of "
    "spoken-word transcript lines and on-screen frames from a short video. Comprehend "
    "the full message, treating the spoken words and on-screen text as a single "
    "coordinated presentation. Be precise about what is actually said and shown; do not "
    "invent claims that are not supported by the transcript or the frames."
)

DEFAULT_EVAL_PROMPT = (
    "Do the following:\n"
    "1. Summarize the video's core message in 3-5 sentences.\n"
    "2. List every distinct claim or instruction the speaker makes, in order.\n"
    "3. Note where on-screen text reinforces, adds to, or contradicts what is spoken.\n"
    "4. Give an honest evaluation: is the content accurate, well-supported, and clear? "
    "Flag anything misleading, vague, or unsupported."
)


def run(source, cookies_browser, eval_prompt, system_prompt):
    work = config.WORK_DIR
    work.mkdir(parents=True, exist_ok=True)

    # source can be an Instagram URL or a path to a local video file already on disk.
    src_path = Path(source)
    if src_path.is_file():
        print(f"[1/5] Using local video file: {src_path} ...")
        video_path = src_path
    else:
        print(f"[1/5] Downloading {source} ...")
        video_path = download.download_video(source, work, cookies_browser)

    print("[2/5] Extracting audio ...")
    audio_path = audio.extract_audio(video_path, work)

    print(f"[3/5] Transcribing ({config.TRANSCRIBE_BACKEND}) ...")
    segments = transcribe.transcribe(audio_path)
    print(f"      {len(segments)} transcript segments.")

    print("[4/5] Sampling + de-duplicating frames ...")
    all_frames = frames_mod.extract_frames(video_path, work)
    kept = frames_mod.dedupe_frames(all_frames)
    print(f"      {len(all_frames)} sampled -> {len(kept)} kept.")

    print(f"[5/5] Evaluating with {config.ANTHROPIC_MODEL} ...")
    evaluation = evaluate_mod.evaluate(segments, kept, eval_prompt, system_prompt)

    out_path = work / "evaluation.md"
    report.write_report(source, segments, kept, evaluation, out_path)
    print(f"\nDone. Report written to: {out_path}\n")
    print("=" * 60)
    print(evaluation)
    return out_path


def main():
    p = argparse.ArgumentParser(
        description="Evaluate a video (Instagram URL or local file) using its speech "
                    "and on-screen text."
    )
    p.add_argument("source",
                   help="Instagram Reel/post URL, or path to a local video file "
                        "(mp4, mov, mkv, webm, ...)")
    p.add_argument("--cookies-from-browser", default=None,
                   help="Browser to pull cookies from if the download is blocked "
                        "(chrome/safari/firefox/edge/brave)")
    p.add_argument("--prompt", default=DEFAULT_EVAL_PROMPT, help="Evaluation instructions")
    p.add_argument("--system", default=DEFAULT_SYSTEM_PROMPT, help="System prompt")
    args = p.parse_args()
    run(args.source, args.cookies_from_browser, args.prompt, args.system)


if __name__ == "__main__":
    main()
