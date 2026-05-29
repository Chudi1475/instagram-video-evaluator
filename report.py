"""Write a Markdown report bundling transcript, on-screen frame log, and evaluation."""
from pathlib import Path


def _fmt_ts(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def write_report(url: str, segments: list[dict], frames, evaluation: str,
                 out_path: Path) -> Path:
    lines = ["# Video evaluation\n", f"**Source:** {url}\n", "## Transcript\n"]
    for seg in segments:
        lines.append(f"- `[{_fmt_ts(seg['start'])}]` {seg['text']}")
    lines.append("\n## On-screen frames captured\n")
    for ts, path in frames:
        lines.append(f"- `[{_fmt_ts(ts)}]` `{path.name}`")
    lines.append("\n## Evaluation\n")
    lines.append(evaluation)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path
