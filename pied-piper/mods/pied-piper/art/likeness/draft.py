"""A first tracing of each conversion in the sprite's own letters (s d skin,
h H k hair, b facial hair, x a dark spot in the face, n neck, . nothing), and
the colors measured: skin, hair, and the clothes' main colors. A draft to draw
over, not the drawing."""
import site, sys, os
site.addsitedir(site.getusersitepackages())
import numpy as np
from PIL import Image

EYE, LEFT, TOP, ROWS = 11, 7, 1, 24


def lab(rgb):
    c = np.asarray(rgb, dtype=np.float64) / 255
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], axis=-1)


def hexc(c):
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in c)


def med(pix):
    return np.median(np.array(pix, dtype=np.float64), axis=0)


def draft(path):
    a = np.asarray(Image.open(path).convert("RGBA"), dtype=np.float64)
    rgb, on = a[..., :3], a[..., 3] > 0
    L = lab(rgb)
    cheeks = [rgb[r, c] for r in (12, 13, 14) for c in (12, 13, 14, 15) if on[r, c]]
    skin = med(cheeks)
    sl = lab(skin)
    top = [(r, c) for r in range(0, 9) for c in range(LEFT, LEFT + 14) if on[r, c]]
    far = [rgb[r, c] for r, c in top if np.linalg.norm(L[r, c] - sl) > 18]
    bald = len(far) < 8
    hair = med(far) if not bald else skin * 0.5
    hl = lab(hair)
    rows = []
    for r in range(TOP, TOP + ROWS):
        line = ""
        for c in range(LEFT, LEFT + 14):
            if not on[r, c]:
                line += "."; continue
            ds, dh = np.linalg.norm(L[r, c] - sl), np.linalg.norm(L[r, c] - hl)
            inface = EYE - 1 <= r <= EYE + 6 and LEFT + 3 <= c <= LEFT + 10
            if ds <= dh:
                ch = "s" if L[r, c][0] >= sl[0] - 7 else "d"
            elif inface and r <= EYE + 1:
                ch = "x"
            elif inface and not bald and r >= EYE + 2:
                ch = "b"
            else:
                ch = "H" if L[r, c][0] > hl[0] + 9 else "k" if L[r, c][0] < hl[0] - 9 else "h"
            if r > EYE + 6 and ch in "sd":
                ch = "n" if LEFT + 4 <= c <= LEFT + 9 and r <= EYE + 8 else ","
            if r > EYE + 7 and ch not in "n,":
                # under the chin only hair counts; clothes are not the head
                ch = ch if (dh < 16 and not bald) else ","
            line += ch
        rows.append(line)
    body = [tuple(rgb[r, c]) for r in range(21, 40) for c in range(28) if on[r, c]]
    cols = {}
    for p in body:
        cols[p] = cols.get(p, 0) + 1
    clothes = [f"{hexc(p)}x{n}" for p, n in sorted(cols.items(), key=lambda kv: -kv[1])[:6]]
    hairs = [rgb[r, c] for r in range(TOP, TOP + ROWS) for c in range(LEFT, LEFT + 14) if on[r, c] and np.linalg.norm(L[r, c] - hl) < 16]
    lum = sorted(hairs, key=lambda p: p.sum())
    spread = (hexc(med(lum[:max(1, len(lum) // 4)])), hexc(med(lum[-max(1, len(lum) // 4):]))) if lum else ("-", "-")
    return rows, dict(skin=hexc(skin), skin_shade=hexc(med([p for p in cheeks if p.sum() <= skin.sum()])), hair=hexc(hair), hair_dark_light=spread, bald=bald, clothes=clothes)


if __name__ == "__main__":
    conv = sys.argv[1]
    keys = sys.argv[2:]
    out = [draft(os.path.join(conv, k + ".png")) for k in keys]
    for k, (rows, info) in zip(keys, out):
        print(k, info)
    for i in range(0, len(keys), 5):
        part = keys[i:i + 5]
        print()
        print("    " + "  ".join(f"{k:14s}" for k in part))
        for r in range(ROWS):
            mark = ">" if r + TOP == EYE else " "
            print(f"{r:2d}{mark} " + "  ".join(out[i + j][0][r] for j in range(len(part))))
