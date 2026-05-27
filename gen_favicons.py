# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "cairosvg>=2.7",
#     "pillow>=10.0",
# ]
# ///
"""
Rasterize logo.svg into the favicon PNGs and a multi-resolution favicon.ico.

Run with uv (installs deps in an isolated env automatically):

    uv run gen_favicons.py

logo.svg uses stroke="currentColor"; since a standalone raster has no CSS
context to resolve that, COLOR below is substituted in before rendering.
"""

from __future__ import annotations

import io
from pathlib import Path

import cairosvg
from PIL import Image

# --- config -------------------------------------------------------------
HERE = Path(__file__).parent
SRC = HERE / "logo.svg"

# Color baked into the favicons (the inline SVG in index.html stays themeable
# via currentColor; only the raster output needs a concrete value).
COLOR = "#2f7e39"  # --green

PNG_SIZES = (16, 32, 48)
ICO_SIZES = (16, 32, 48)
ICO_RENDER = 256  # render once at high res, downscale for crisp .ico entries
# -----------------------------------------------------------------------


def load_svg() -> str:
    if not SRC.exists():
        raise SystemExit(f"missing source SVG: {SRC}")
    svg = SRC.read_text(encoding="utf-8")
    if "currentColor" not in svg:
        print("warning: 'currentColor' not found in logo.svg; rendering as-is")
    return svg.replace("currentColor", COLOR)


def render_png(svg: str, size: int) -> bytes:
    return cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        output_width=size,
        output_height=size,
    )


def main() -> None:
    svg = load_svg()

    # individual PNGs
    for size in PNG_SIZES:
        out = HERE / f"favicon-{size}x{size}.png"
        out.write_bytes(render_png(svg, size))
        print(f"wrote {out.name} ({size}x{size})")

    # multi-resolution .ico from a single high-res render
    master = Image.open(io.BytesIO(render_png(svg, ICO_RENDER))).convert("RGBA")
    ico = HERE / "favicon.ico"
    master.save(ico, format="ICO", sizes=[(s, s) for s in ICO_SIZES])
    print(f"wrote {ico.name} (sizes: {', '.join(str(s) for s in ICO_SIZES)})")


if __name__ == "__main__":
    main()
