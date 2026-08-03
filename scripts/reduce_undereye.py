"""
reduce_undereye.py — soften under-eye shadows on a portrait so the black-and-white
CSS filter on the MFS team page doesn't over-emphasise them.

Approach
--------
1. Detect the face using OpenCV Haar cascade
2. Detect eyes within the upper half of the face
3. Define an under-eye rectangle immediately below each eye
4. Sample skin tone from the mid-cheek (below the under-eye) to know the target
5. Lift the under-eye region toward that skin tone with a soft feathered mask
6. Also apply a light Gaussian blur inside the mask to reduce texture harshness

Usage
-----
    python scripts/reduce_undereye.py INPUT.jpg OUTPUT.jpg [--strength 0.55]

Idempotent — running twice will further soften, which is why we take a --strength arg.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def _load_cascades():
    base = Path(cv2.data.haarcascades)
    face = cv2.CascadeClassifier(str(base / "haarcascade_frontalface_default.xml"))
    eye = cv2.CascadeClassifier(str(base / "haarcascade_eye.xml"))
    if face.empty() or eye.empty():
        raise RuntimeError("Failed to load Haar cascade XML files.")
    return face, eye


def _largest(rects):
    if len(rects) == 0:
        return None
    return max(rects, key=lambda r: r[2] * r[3])


def _detect_face_and_eyes(bgr: np.ndarray):
    face_cc, eye_cc = _load_cascades()
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    faces = face_cc.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(120, 120))
    face = _largest(faces)
    if face is None:
        return None, []
    fx, fy, fw, fh = face
    # Restrict eye search to top half of face to avoid nostril/mouth false positives.
    face_upper = gray[fy : fy + fh // 2, fx : fx + fw]
    eyes = eye_cc.detectMultiScale(face_upper, scaleFactor=1.1, minNeighbors=6, minSize=(fw // 8, fw // 8))
    # Convert back to full-image coordinates.
    eyes = [(fx + ex, fy + ey, ew, eh) for (ex, ey, ew, eh) in eyes]
    # Sort by area, keep up to two biggest.
    eyes = sorted(eyes, key=lambda r: r[2] * r[3], reverse=True)[:2]
    return face, eyes


def _sample_skin(bgr: np.ndarray, face_rect, eyes) -> np.ndarray:
    """Sample average skin BGR from the cheek region below the eyes."""
    fx, fy, fw, fh = face_rect
    if len(eyes) < 1:
        # Fallback: sample from lower-middle of face (cheek area).
        cy1 = fy + int(fh * 0.55)
        cy2 = fy + int(fh * 0.70)
        cx1 = fx + int(fw * 0.30)
        cx2 = fx + int(fw * 0.70)
    else:
        # Sample immediately below-and-outside the under-eye zone (cheek proper).
        ex, ey, ew, eh = eyes[0]
        cy1 = ey + int(eh * 2.2)
        cy2 = ey + int(eh * 3.4)
        cx1 = ex - int(ew * 0.2)
        cx2 = ex + int(ew * 1.2)
    cy1 = max(0, cy1)
    cy2 = min(bgr.shape[0], cy2)
    cx1 = max(0, cx1)
    cx2 = min(bgr.shape[1], cx2)
    patch = bgr[cy1:cy2, cx1:cx2]
    if patch.size == 0:
        return np.array([180, 160, 150], dtype=np.float32)  # neutral warm skin fallback
    # Use median to be robust against stray hair/shadow pixels.
    return np.median(patch.reshape(-1, 3), axis=0).astype(np.float32)


def _build_undereye_mask(shape, eyes) -> np.ndarray:
    """Feathered soft mask over the under-eye zones."""
    mask = np.zeros(shape[:2], dtype=np.float32)
    for (ex, ey, ew, eh) in eyes:
        # Under-eye rectangle: starts just below the eye, height ~ 0.9 of eye height, width ~ 1.1 of eye width.
        ux = int(ex - 0.05 * ew)
        uy = int(ey + 0.75 * eh)
        uw = int(ew * 1.10)
        uh = int(eh * 0.90)
        # Draw an ellipse (softer than a rectangle) then feather.
        center = (ux + uw // 2, uy + uh // 2)
        axes = (uw // 2, uh // 2)
        cv2.ellipse(mask, center, axes, 0, 0, 360, 1.0, thickness=-1)
    # Feather.
    k = max(15, (shape[0] // 40) | 1)  # odd kernel scaled to image size
    mask = cv2.GaussianBlur(mask, (k, k), 0)
    # Normalise to [0,1].
    if mask.max() > 0:
        mask = mask / mask.max()
    return mask


def reduce_undereye(bgr: np.ndarray, strength: float = 0.55) -> np.ndarray:
    """Return a copy of `bgr` with under-eye shadows softened.

    strength: 0..1 -- how strongly to pull the under-eye toward the skin-tone target.
    0.55 is a natural default; 0.7+ starts to look retouched.
    """
    face, eyes = _detect_face_and_eyes(bgr)
    if face is None or len(eyes) == 0:
        print("[warn] no face/eyes detected; returning input unchanged")
        return bgr.copy()

    skin = _sample_skin(bgr, face, eyes)  # BGR float
    mask = _build_undereye_mask(bgr.shape, eyes)  # HxW float 0..1

    # Build a "target" layer: a slight blend of the original with the skin tone,
    # slightly brightened, then lightly blurred to smooth texture.
    src = bgr.astype(np.float32)
    # Lightened toward skin: mix src with skin, then add a small brightness lift.
    target = 0.55 * src + 0.45 * skin.reshape(1, 1, 3)
    target = np.clip(target * 1.06, 0, 255)  # +6% brightness in the under-eye
    # Slight blur to reduce shadow texture / bags.
    target = cv2.GaussianBlur(target, (0, 0), sigmaX=2.5, sigmaY=2.5)

    mask3 = np.dstack([mask, mask, mask]) * float(strength)
    out = src * (1.0 - mask3) + target * mask3
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--strength", type=float, default=0.55, help="0..1, default 0.55")
    args = ap.parse_args()

    bgr = cv2.imread(str(args.input))
    if bgr is None:
        raise SystemExit(f"could not read {args.input}")
    result = reduce_undereye(bgr, strength=args.strength)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.output), result, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"[ok] wrote {args.output} (strength={args.strength})")


if __name__ == "__main__":
    main()
