"""Photo to pixel art, by measurement: levels each face on its eyes, scales
everyone to the same head size (eye line to chin = E2C art pixels), cuts the
person out with the silhouette, shrinks to the sprite's grid by averaging and
reduces the colors. Writes conv/<key>.png (the grid itself), conv/<key>-2x.png
(twice as fine) and conv/<key>-photo.png (the leveled photo in the same frame)."""
import site, sys, os, json, math
site.addsitedir(site.getusersitepackages())
import numpy as np
from PIL import Image, ImageEnhance

AW, AH = 28, 40                 # the frame, in art pixels
CX, EYE = 14.0, 11.5            # where the midpoint between the eyes goes
E2C = 6.0                       # eye line to chin
K = 12                          # working pixels per art pixel


def kmeans(pix, n, seed=1):
    rng = np.random.default_rng(seed)
    cent = [pix[rng.integers(len(pix))]]
    for _ in range(n - 1):                                    # spread the starting colors out
        d = np.min([((pix - c) ** 2).sum(axis=1) for c in cent], axis=0)
        cent.append(pix[int(np.argmax(d))])
    cent = np.array(cent, dtype=np.float64)
    for _ in range(25):
        lab = np.argmin(((pix[:, None, :] - cent[None]) ** 2).sum(axis=2), axis=1)
        for i in range(n):
            if (lab == i).any():
                cent[i] = pix[lab == i].mean(axis=0)
    return cent, lab


def pixelate(rgb, alpha, colors):
    """The averaged picture with its colors cut down; outside the person, clear."""
    im = ImageEnhance.Contrast(ImageEnhance.Color(rgb).enhance(1.2)).enhance(1.1)
    a = np.asarray(im, dtype=np.float64)
    keep = alpha > 0.5
    cent, lab = kmeans(a[keep], colors)
    out = np.zeros(a.shape[:2] + (4,), dtype=np.uint8)
    out[keep, :3] = np.clip(cent[lab], 0, 255).astype(np.uint8)
    out[keep, 3] = 255
    return Image.fromarray(out, "RGBA")


def convert(d, src_dir, mask_dir, out_dir):
    key = d["name"]
    img = Image.open(os.path.join(src_dir, key + ".png")).convert("RGB")
    mask = Image.open(os.path.join(mask_dir, key + ".png")).convert("L").resize(img.size, Image.BILINEAR)
    eyes = sorted((np.mean(d["left_eye"], axis=0), np.mean(d["right_eye"], axis=0)), key=lambda p: p[0])
    mid = (eyes[0] + eyes[1]) / 2
    th = math.atan2(eyes[1][1] - eyes[0][1], eyes[1][0] - eyes[0][0])
    down = np.array([-math.sin(th), math.cos(th)])
    e2c = max(float(np.dot(np.array(p) - mid, down)) for p in d["contour"])
    u = e2c / E2C                                             # photo pixels per art pixel
    cs, sn = math.cos(th), math.sin(th)
    coef = (u * cs / K, -u * sn / K, mid[0] - CX * u * cs + EYE * u * sn,
            u * sn / K, u * cs / K, mid[1] - CX * u * sn - EYE * u * cs)
    size = (AW * K, AH * K)
    hi = img.transform(size, Image.AFFINE, coef, resample=Image.BICUBIC)
    m = mask.transform(size, Image.AFFINE, coef, resample=Image.BILINEAR)
    valid = Image.new("L", img.size, 255).transform(size, Image.AFFINE, coef, resample=Image.BILINEAR)
    cut = Image.fromarray((np.asarray(m, dtype=np.float64) * np.asarray(valid, dtype=np.float64) / 255).astype(np.uint8))
    hi.save(os.path.join(out_dir, key + "-photo.png"))
    for scale, colors, tag in ((1, 12, ""), (2, 16, "-2x")):
        small = hi.resize((AW * scale, AH * scale), Image.BOX)
        alpha = np.asarray(cut.resize((AW * scale, AH * scale), Image.BOX), dtype=np.float64) / 255
        pixelate(small, alpha, colors).save(os.path.join(out_dir, key + tag + ".png"))
    ipd = float(np.linalg.norm(eyes[1] - eyes[0])) / u
    return dict(key=key, art_px=round(u, 2), tilt=round(math.degrees(th), 1), eyes_apart=round(ipd, 2))


if __name__ == "__main__":
    faces, src_dir, mask_dir, out_dir = sys.argv[1:5]
    for line in open(faces):
        d = json.loads(line)
        if "contour" in d:
            print(convert(d, src_dir, mask_dir, out_dir))
