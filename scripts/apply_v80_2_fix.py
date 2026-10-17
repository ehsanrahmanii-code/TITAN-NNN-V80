#!/usr/bin/env python3
"""Apply V80.2 real-fix layer to TITAN source (self-contained)."""
from pathlib import Path
import base64, gzip
root = Path(__file__).resolve().parents[1]
src = root / "TITAN_PRO_V80_NNN_UNIFIED.py"
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
_B64 = "".join(p.read_text(encoding="ascii").strip() for p in sorted((root / "patches").glob("v80_2_gz_*.b64")))
layer = gzip.decompress(base64.b64decode(_B64)).decode("utf-8")
src.write_text(text.rstrip() + "\n\n" + layer.lstrip() + "\n", encoding="utf-8")
print("applied V80.2", src.stat().st_size)
