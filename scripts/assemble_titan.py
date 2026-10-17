#!/usr/bin/env python3
"""Assemble TITAN_PRO_V80_NNN_UNIFIED.py from titan_parts/ if needed."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root / "TITAN_PRO_V80_NNN_UNIFIED.py"
parts_dir = root / "titan_parts"
parts = sorted(parts_dir.glob("part_*.txt")) if parts_dir.is_dir() else []

if out.is_file() and out.stat().st_size > 500_000:
    print("already present:", out, out.stat().st_size)
elif parts:
    text = "".join(p.read_text(encoding="utf-8") for p in parts)
    out.write_text(text, encoding="utf-8")
    print("assembled", out, "bytes", out.stat().st_size, "from", len(parts), "parts")
else:
    raise SystemExit(
        "Missing TITAN_PRO_V80_NNN_UNIFIED.py — upload the ~2MB file to the repo root "
        "(GitHub → Add file → Upload files) then re-run the workflow."
    )
