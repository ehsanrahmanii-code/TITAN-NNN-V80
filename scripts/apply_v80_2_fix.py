#!/usr/bin/env python3
"""Apply V80.2 constant tweaks + append real-fix layer to TITAN source."""
from pathlib import Path
root = Path(__file__).resolve().parents[1]
src = root / "TITAN_PRO_V80_NNN_UNIFIED.py"
layer_path = root / "patches" / "v80_2_real_fix.py"
part_a = root / "patches" / "v80_2_real_fix_a.py"
part_b = root / "patches" / "v80_2_real_fix_b.py"
if part_a.is_file() and part_b.is_file():
    layer_path.write_text(part_a.read_text(encoding="utf-8") + part_b.read_text(encoding="utf-8"), encoding="utf-8")
elif not layer_path.is_file():
    raise SystemExit("missing V80.2 patch layer")
text = src.read_text(encoding="utf-8")
marker = "# ===== LAYER: flat/v80_2_real_fix ====="
if marker in text:
    text = text[:text.index(marker)]
replacements = [
    ("TITAN_REQUIRE_EDGE_SUPPORTED = True       # block LONG/SHORT without historical edge",
     "TITAN_REQUIRE_EDGE_SUPPORTED = False      # V80.2: allow directional publish when live TA is clear"),
    ("TITAN_SHADOW_TIMEFRAMES = (\"15m\", \"1h\")   # score only, force WAIT for publish",
     "TITAN_SHADOW_TIMEFRAMES = ()              # V80.2: all TFs can publish real direction"),
    ("MIN_DIRECTIONAL_QUALITY = 52  # V75: raise bar, especially for low TFs",
     "MIN_DIRECTIONAL_QUALITY = 48  # V80.2: slightly lower so real edges surface"),
    ("AUTO_SCAN_INTERVAL_SECONDS = 12  # balanced: avoid thrashing while keeping data fresh",
     "AUTO_SCAN_INTERVAL_SECONDS = 25  # V80.2: complete full scans before next queue"),
    ("MARKET_CACHE_TTL = 14  # snappier refresh without hammering APIs",
     "MARKET_CACHE_TTL = 20  # V80.2: let a full scan finish before TTL forces another"),
]
for a, b in replacements:
    if a in text:
        text = text.replace(a, b, 1)
layer = layer_path.read_text(encoding="utf-8")
src.write_text(text.rstrip() + "\n\n" + layer.lstrip() + "\n", encoding="utf-8")
print("applied V80.2 to", src, "size", src.stat().st_size)
