"""Build the team portrait set.

For each subject we:
  1. Download / load the source portrait.
  2. Remove the background with rembg (u2net) to get a person-only RGBA cutout.
  3. Center + scale the cutout inside a 1000x1000 canvas that already contains
     a shared brand background.
  4. Save the flattened result to assets/images/team/<name>.jpg (JPEG, no alpha).

The shared background is a deep-navy gradient with a soft electric-blue radial
spotlight and a subtle dot grid — matches the site palette and reads well in
both B&W (rest state) and full color (hover state).
"""
from __future__ import annotations

import io
import math
import os
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
from rembg import remove, new_session

ROOT = Path("/home/user/workspace/mfs")
OUT_DIR = ROOT / "assets/images/team"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CANVAS = 1000  # final square size
NAVY_950 = (5, 11, 31)
NAVY_900 = (11, 27, 58)
NAVY_800 = (18, 36, 74)
ELECTRIC = (30, 99, 255)
ELECTRIC_SOFT = (59, 123, 255)

# ---------------------------------------------------------------------------
# Shared brand background
# ---------------------------------------------------------------------------


def _radial_gradient(size, inner, outer, center=(0.5, 0.4), radius=0.9):
    """Return an RGB image with a smooth radial gradient."""
    w, h = size
    cx, cy = int(w * center[0]), int(h * center[1])
    max_r = int(max(w, h) * radius)
    img = Image.new("RGB", size, outer)
    px = img.load()
    for y in range(h):
        for x in range(w):
            dx, dy = x - cx, y - cy
            d = math.sqrt(dx * dx + dy * dy)
            t = min(1.0, d / max_r)
            # ease-out cubic for a soft falloff
            t = 1 - (1 - t) ** 3
            px[x, y] = (
                int(inner[0] * (1 - t) + outer[0] * t),
                int(inner[1] * (1 - t) + outer[1] * t),
                int(inner[2] * (1 - t) + outer[2] * t),
            )
    return img


def _dot_grid(size, color=(255, 255, 255), alpha=14, spacing=28, radius=1):
    """Return an RGBA overlay with a subtle dot grid."""
    w, h = size
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(spacing // 2, h, spacing):
        for x in range(spacing // 2, w, spacing):
            draw.ellipse(
                [x - radius, y - radius, x + radius, y + radius],
                fill=(color[0], color[1], color[2], alpha),
            )
    return overlay


def build_background() -> Image.Image:
    """Build one canonical background used behind every subject."""
    size = (CANVAS, CANVAS)

    # Base: vertical gradient navy_800 -> navy_950
    base = Image.new("RGB", size, NAVY_950)
    px = base.load()
    for y in range(size[1]):
        t = y / (size[1] - 1)
        # ease-in curve so top stays warmer navy longer
        t = t * t
        px_row = (
            int(NAVY_800[0] * (1 - t) + NAVY_950[0] * t),
            int(NAVY_800[1] * (1 - t) + NAVY_950[1] * t),
            int(NAVY_800[2] * (1 - t) + NAVY_950[2] * t),
        )
        for x in range(size[0]):
            px[x, y] = px_row

    # Electric radial spotlight, offset top-right
    spotlight = _radial_gradient(
        size,
        inner=ELECTRIC_SOFT,
        outer=NAVY_900,
        center=(0.72, 0.28),
        radius=0.85,
    )
    # Blend at low opacity so it stays subtle
    base = Image.blend(base, spotlight, alpha=0.22)

    # Second, warmer spotlight bottom-left for depth
    warm = _radial_gradient(
        size,
        inner=NAVY_800,
        outer=NAVY_950,
        center=(0.15, 0.85),
        radius=0.8,
    )
    base = Image.blend(base, warm, alpha=0.35)

    # Dot grid overlay
    dots = _dot_grid(size, color=(120, 160, 255), alpha=14, spacing=26, radius=1)
    base_rgba = base.convert("RGBA")
    base_rgba = Image.alpha_composite(base_rgba, dots)

    # Soft top vignette to focus attention on head area
    vignette = Image.new("RGBA", size, (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    for i in range(0, 120):
        alpha = int(60 * (1 - i / 120))
        v_draw.rectangle([0, i, size[0], i + 1], fill=(0, 0, 0, alpha))
    base_rgba = Image.alpha_composite(base_rgba, vignette)

    return base_rgba.convert("RGB")


# ---------------------------------------------------------------------------
# Subject cutout + composite
# ---------------------------------------------------------------------------


@dataclass
class Subject:
    name: str            # output filename stem
    src: str             # path or URL
    y_bias: float = 0.0  # positive shifts subject down; keeps top of head off canvas edge
    scale: float = 1.0   # 1.0 = subject fills 92% of canvas height
    pre_crop: tuple | None = None  # (left_pct, top_pct, right_pct, bottom_pct) applied before cutout


def _load(src: str) -> Image.Image:
    if src.startswith("http"):
        req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
        return Image.open(io.BytesIO(urllib.request.urlopen(req).read()))
    return Image.open(src)


def _apply_pre_crop(img: Image.Image, pct: tuple) -> Image.Image:
    """Crop by percent from each edge, then mask everything outside a soft ellipse
    so adjacent people/objects don't get fed into rembg."""
    w, h = img.size
    l, t, r, b = pct
    box = (int(w * l), int(h * t), int(w * (1 - r)), int(h * (1 - b)))
    return img.crop(box)


def cutout(img: Image.Image, session) -> Image.Image:
    """Return an RGBA image of the subject only."""
    return remove(img.convert("RGBA"), session=session)


def _tight_crop(rgba: Image.Image) -> Image.Image:
    """Crop the transparent margins around the subject."""
    bbox = rgba.getbbox()
    if not bbox:
        return rgba
    return rgba.crop(bbox)


def composite(subject_rgba: Image.Image, bg: Image.Image, y_bias=0.0, scale=1.0) -> Image.Image:
    """Fit the subject onto the background canvas."""
    canvas = bg.copy().convert("RGBA")
    subj = _tight_crop(subject_rgba)

    # Target height: 92% of canvas by default (people fill the frame like editorial portraits)
    target_h = int(CANVAS * 0.92 * scale)
    ratio = target_h / subj.height
    new_w = int(subj.width * ratio)
    subj = subj.resize((new_w, target_h), Image.LANCZOS)

    # Feather the alpha edges very slightly so the cutout doesn't look "stickered"
    r, g, b, a = subj.split()
    a = a.filter(ImageFilter.GaussianBlur(radius=0.6))
    subj.putalpha(a)

    # Horizontal center; vertical anchored so head/shoulders sit visually right
    x = (CANVAS - new_w) // 2
    # Anchor top of subject near y=4% of canvas, plus optional bias
    y = int(CANVAS * (0.04 + y_bias))
    canvas.alpha_composite(subj, (x, y))
    return canvas.convert("RGB")


def main() -> None:
    bg = build_background()
    bg.save("/tmp/team_bg.jpg", "JPEG", quality=92)  # sanity export

    session = new_session("u2net")

    subjects = [
        Subject(
            name="drew",
            src=str(ROOT / "assets/images/drew-original.jpg"),
            y_bias=0.06,
            scale=0.95,
        ),
        Subject(
            name="joe",
            src=str(ROOT / "assets/images/joe-original.jpg"),
            y_bias=0.03,
            scale=1.0,
        ),
        Subject(
            name="dakarai",
            src=str(ROOT / "assets/images/dakarai.jpg"),
            y_bias=0.04,
            scale=1.02,
        ),
        Subject(
            name="rodrigo",
            src=str(ROOT / "assets/images/rodrigo-original.jpg"),
            y_bias=0.05,
            scale=1.0,
        ),
    ]

    for s in subjects:
        print(f"[+] {s.name} <- {s.src}")
        img = _load(s.src)
        if s.pre_crop:
            img = _apply_pre_crop(img, s.pre_crop)
        cut = cutout(img, session)
        # Debug: save the raw cutout
        cut.save(f"/tmp/team_cut_{s.name}.png")
        result = composite(cut, bg, y_bias=s.y_bias, scale=s.scale)
        out = OUT_DIR / f"{s.name}.jpg"
        result.save(out, "JPEG", quality=90, optimize=True)
        print(f"    -> {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
