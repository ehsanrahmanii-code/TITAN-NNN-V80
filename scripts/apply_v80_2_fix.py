#!/usr/bin/env python3
from pathlib import Path
root = Path(__file__).resolve().parents[1]
src = root / "TITAN_PRO_V80_NNN_UNIFIED.py"
parts = sorted((root / "patches").glob("v80_2_min_*.py"))
layer = "".join(p.read_text(encoding="utf-8") for p in parts) if parts else ""
text = src.read_text(encoding="utf-8")
marker = "# ===== LAYER: flat/v80_2_real_fix ====="
if marker in text:
    text = text[: text.index(marker)]
for a, b in [
    ("TITAN_REQUIRE_EDGE_SUPPORTED = True       # block LONG/SHORT without historical edge",
     "TITAN_REQUIRE_EDGE_SUPPORTED = False      # V80.2"),
    ('TITAN_SHADOW_TIMEFRAMES = ("15m", "1h")   # score only, force WAIT for publish',
     "TITAN_SHADOW_TIMEFRAMES = ()              # V80.2"),
    ("MIN_DIRECTIONAL_QUALITY = 52  # V75: raise bar, especially for low TFs",
     "MIN_DIRECTIONAL_QUALITY = 48  # V80.2"),
    ("AUTO_SCAN_INTERVAL_SECONDS = 12  # balanced: avoid thrashing while keeping data fresh",
     "AUTO_SCAN_INTERVAL_SECONDS = 25  # V80.2"),
    ("MARKET_CACHE_TTL = 14  # snappier refresh without hammering APIs",
     "MARKET_CACHE_TTL = 20  # V80.2"),
]:
    if a in text:
        text = text.replace(a, b, 1)
if layer.strip():
    text = text.rstrip() + "\n\n" + layer.lstrip() + "\n"
src.write_text(text, encoding="utf-8")
print("applied V80.2", src.stat().st_size, "layer_parts", len(parts))
