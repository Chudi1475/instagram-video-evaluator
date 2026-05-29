"""Central configuration and constants. All values overridable via environment vars."""
import os
from pathlib import Path

WORK_DIR = Path(os.getenv("IGV_WORK_DIR", "work"))

# --- Transcription -----------------------------------------------------------
# "groq" (hosted, fast, needs GROQ_API_KEY) or "local" (faster-whisper, free, offline).
TRANSCRIBE_BACKEND = os.getenv("IGV_TRANSCRIBE_BACKEND", "groq")
GROQ_MODEL = os.getenv("IGV_GROQ_MODEL", "whisper-large-v3-turbo")
LOCAL_WHISPER_SIZE = os.getenv("IGV_LOCAL_WHISPER_SIZE", "base")

# --- Frame sampling ----------------------------------------------------------
FRAME_FPS = float(os.getenv("IGV_FRAME_FPS", "1.0"))          # frames extracted per second
PHASH_THRESHOLD = int(os.getenv("IGV_PHASH_THRESHOLD", "6"))  # higher = more aggressive dedup
MAX_FRAMES = int(os.getenv("IGV_MAX_FRAMES", "30"))           # hard cap on frames sent to Claude
IMAGE_MAX_DIM = int(os.getenv("IGV_IMAGE_MAX_DIM", "1024"))   # px, long edge, before upload

# --- Evaluation (Anthropic) --------------------------------------------------
ANTHROPIC_MODEL = os.getenv("IGV_ANTHROPIC_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = int(os.getenv("IGV_MAX_TOKENS", "4096"))
