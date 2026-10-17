#!/usr/bin/env python3
"""Assemble TITAN_PRO_V80_NNN_UNIFIED.py from gzip base64 parts or plain parts."""
from __future__ import annotations

import base64
import gzip
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root / "TITAN_PRO_V80_NNN_UNIFIED.py"

if out.is_file() and out.stat().st_size > 500_000:
    print("already present:", out, out.stat().st_size)
    raise SystemExit(0)

gz_dir = root / "titan_gz_parts"
gz_parts = sorted(gz_dir.glob("gz_*.b64")) if gz_dir.is_dir() else []
if gz_parts:
    b64 = "".join(p.read_text(encoding="ascii").strip() for p in gz_parts)
    raw = base64.b64decode(b64)
    data = gzip.decompress(raw)
    out.write_bytes(data)
    print("assembled from gzip parts:", out, out.stat().st_size, "parts", len(gz_parts))
    raise SystemExit(0)

parts_dir = root / "titan_parts"
parts = sorted(parts_dir.glob("part_*.txt")) if parts_dir.is_dir() else []
if parts:
    text = "".join(p.read_text(encoding="utf-8") for p in parts)
    out.write_text(text, encoding="utf-8")
    print("assembled from text parts:", out, out.stat().st_size, "parts", len(parts))
    raise SystemExit(0)

raise SystemExit(
    "Missing TITAN_PRO_V80_NNN_UNIFIED.py — need titan_gz_parts/ or full file at repo root."
)
