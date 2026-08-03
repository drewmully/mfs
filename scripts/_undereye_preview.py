"""Assemble a 2x2 preview: original vs. corrected, in color and grayscale."""
import cv2
import numpy as np
from pathlib import Path

pre = cv2.imread("assets/images/team/drew-precorrection.jpg")
post = cv2.imread("assets/images/team/drew.jpg")

def gray3(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # match the CSS: grayscale(1) contrast(1.02)
    g = np.clip((g.astype(np.float32) - 128) * 1.02 + 128, 0, 255).astype(np.uint8)
    return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)

def crop_face(img):
    h, w = img.shape[:2]
    # centered face crop (approx)
    x1, y1 = int(w * 0.20), int(h * 0.10)
    x2, y2 = int(w * 0.80), int(h * 0.60)
    return img[y1:y2, x1:x2]

pre_c = crop_face(pre); post_c = crop_face(post)
pre_g = gray3(pre_c);  post_g = gray3(post_c)

# 2x2 layout
def label(img, text):
    img = img.copy()
    cv2.rectangle(img, (0, 0), (img.shape[1], 32), (30, 30, 30), -1)
    cv2.putText(img, text, (10, 22), cv2.FONT_HERSHEY_DUPLEX, 0.6, (240, 240, 240), 1, cv2.LINE_AA)
    return img

row1 = np.hstack([label(pre_c, "BEFORE - color"), label(post_c, "AFTER - color")])
row2 = np.hstack([label(pre_g, "BEFORE - B&W (site render)"), label(post_g, "AFTER - B&W (site render)")])
grid = np.vstack([row1, row2])
cv2.imwrite("/home/user/workspace/mfs_undereye_preview.jpg", grid, [cv2.IMWRITE_JPEG_QUALITY, 92])
print("wrote /home/user/workspace/mfs_undereye_preview.jpg", grid.shape)
