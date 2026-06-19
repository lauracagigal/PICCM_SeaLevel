#!/usr/bin/env python3
"""Regenerate aggregated_CIndRA_markdowns.md from all assistant markdown sources."""

from datetime import date
from pathlib import Path

ASSISTANT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = ASSISTANT_DIR / "aggregated_CIndRA_markdowns.md"

SOURCE_FILES = [
    ASSISTANT_DIR / "CIndRA_role.md",
    ASSISTANT_DIR / "skills" / "site_setup.md",
    ASSISTANT_DIR / "skills" / "trend_analysis.md",
    ASSISTANT_DIR / "skills" / "anomaly_analysis.md",
    ASSISTANT_DIR / "skills" / "flood_frequency.md",
    ASSISTANT_DIR / "skills" / "rankings.md",
    ASSISTANT_DIR / "skills" / "functions_api.md",
    ASSISTANT_DIR / "skills" / "output_conventions.md",
    ASSISTANT_DIR / "skills" / "data_sources.md",
    ASSISTANT_DIR / "README.md",
]


def build() -> Path:
    parts = [
        "# CIndRA — Aggregated Training Material\n",
        f"\nSingle-file concatenation of all CIndRA assistant markdowns. "
        f"Generated on {date.today().isoformat()}. "
        f"Source files live in `assistant/` and `assistant/skills/`; "
        f"regenerate with `python assistant/build_aggregated_CIndRA.py`.\n",
    ]

    for path in SOURCE_FILES:
        rel = path.relative_to(ASSISTANT_DIR.parent).as_posix()
        content = path.read_text().rstrip() + "\n"
        parts.append(f"\n---\n\n<!-- SOURCE: {rel} -->\n\n")
        parts.append(content)

    OUTPUT_FILE.write_text("".join(parts))
    return OUTPUT_FILE


if __name__ == "__main__":
    out = build()
    print(f"Wrote {out} ({out.stat().st_size} bytes, {len(SOURCE_FILES)} sections)")
