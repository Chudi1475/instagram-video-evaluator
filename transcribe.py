"""Transcribe audio to timestamped segments via Groq (hosted) or faster-whisper (local).

Returns: list[dict] with keys start (float secs), end (float secs), text (str).
"""
from pathlib import Path

import config


def transcribe(audio_path: Path) -> list[dict]:
    if config.TRANSCRIBE_BACKEND == "local":
        return _transcribe_local(audio_path)
    return _transcribe_groq(audio_path)


def _transcribe_groq(audio_path: Path) -> list[dict]:
    from groq import Groq  # pip install groq

    client = Groq()  # reads GROQ_API_KEY from the environment
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            file=(audio_path.name, f.read()),
            model=config.GROQ_MODEL,
            response_format="verbose_json",  # includes per-segment timestamps
            temperature=0.0,
        )
    segments = getattr(result, "segments", None) or []
    out = []
    for s in segments:
        # The SDK may return dicts or objects depending on version; handle both.
        start = s["start"] if isinstance(s, dict) else s.start
        end = s["end"] if isinstance(s, dict) else s.end
        text = s["text"] if isinstance(s, dict) else s.text
        out.append({"start": float(start), "end": float(end), "text": text.strip()})
    if not out:  # fallback: one segment with the whole transcript
        text = result["text"] if isinstance(result, dict) else result.text
        out.append({"start": 0.0, "end": 0.0, "text": text.strip()})
    return out


def _transcribe_local(audio_path: Path) -> list[dict]:
    from faster_whisper import WhisperModel  # pip install faster-whisper

    model = WhisperModel(config.LOCAL_WHISPER_SIZE, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(str(audio_path), vad_filter=True)
    return [
        {"start": float(s.start), "end": float(s.end), "text": s.text.strip()}
        for s in segments
    ]
