#!/usr/bin/env python3
"""Create a simple launcher icon PNG for Titan NNN."""
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    PNG = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D,
        0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53, 0xDE, 0x00, 0x00, 0x00,
        0x0C, 0x49, 0x44, 0x41, 0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
        0x00, 0x00, 0x03, 0x00, 0x01, 0x00, 0x05, 0xFE, 0xD4, 0xEF, 0x00, 0x00,
        0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82,
    ])
    root = Path(__file__).resolve().parents[1]
    for dens in ("mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"):
        d = root / "app" / "src" / "main" / "res" / f"mipmap-{dens}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "ic_launcher.png").write_bytes(PNG)
    print("wrote fallback icons")
    raise SystemExit(0)

root = Path(__file__).resolve().parents[1]
sizes = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
for dens, size in sizes.items():
    d = root / "app" / "src" / "main" / "res" / f"mipmap-{dens}"
    d.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGBA", (size, size), (11, 15, 26, 255))
    draw = ImageDraw.Draw(img)
    margin = size // 8
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=size // 5,
        fill=(91, 140, 255, 255),
    )
    cx, cy = size // 2, size // 2
    tw = size // 3
    th = max(2, size // 12)
    draw.rectangle([cx - tw // 2, cy - tw // 2, cx + tw // 2, cy - tw // 2 + th], fill=(255, 255, 255, 255))
    draw.rectangle([cx - th // 2, cy - tw // 2, cx + th // 2, cy + tw // 2], fill=(255, 255, 255, 255))
    img.save(d / "ic_launcher.png")
    print("icon", dens, size)
print("icons ok")
