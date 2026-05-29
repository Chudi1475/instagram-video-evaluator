"""Build a single multimodal Anthropic request that interleaves the transcript and the
frames in chronological order, then return Claude's evaluation text."""
import base64
import io
from pathlib import Path

import config


def _fmt_ts(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def _encode_image(path: Path) -> str:
    from PIL import Image
    img = Image.open(path).convert("RGB")
    img.thumbnail((config.IMAGE_MAX_DIM, config.IMAGE_MAX_DIM))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    return base64.standard_b64encode(buf.getvalue()).decode("ascii")


def build_content(segments: list[dict], frames: list[tuple[float, Path]]) -> list[dict]:
    """Merge transcript segments and frames into one time-sorted content list so Claude
    sees exactly what was said and shown at each moment, in order."""
    events: list[tuple[float, str, object]] = []
    for seg in segments:
        events.append((seg["start"], "text", seg["text"]))
    for ts, path in frames:
        events.append((ts, "frame", path))
    events.sort(key=lambda e: e[0])

    content: list[dict] = [{
        "type": "text",
        "text": (
            "Below is a chronological reconstruction of an Instagram video. "
            "Lines marked SPOKEN are what the speaker says (with timestamps). "
            "Images are frames captured from the screen at the given timestamp, showing "
            "on-screen text and visuals. Read the spoken words and the on-screen text "
            "together as one coordinated presentation."
        ),
    }]
    for ts, kind, payload in events:
        if kind == "text":
            content.append({"type": "text", "text": f"[{_fmt_ts(ts)}] SPOKEN: {payload}"})
        else:
            content.append({"type": "text", "text": f"[{_fmt_ts(ts)}] ON-SCREEN FRAME:"})
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": _encode_image(payload),
                },
            })
    return content


def evaluate(segments: list[dict], frames: list[tuple[float, Path]],
             eval_prompt: str, system_prompt: str) -> str:
    import anthropic  # pip install anthropic

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    content = build_content(segments, frames)
    content.append({"type": "text", "text": eval_prompt})

    resp = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=config.MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": content}],
    )
    return "".join(block.text for block in resp.content if block.type == "text")
