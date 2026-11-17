"""For showing: each character's photo, its conversion on the sprite's grid,
and the head drawn over it, side by side."""
import site, sys, os, tempfile
site.addsitedir(site.getusersitepackages())
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw

conv, art, out = sys.argv[1], sys.argv[2], sys.argv[3]
keys = sys.argv[4:]
sys.path.insert(0, art)
import cast
from px import Canvas

Z, FW, FH, X0, Y0, EYE, K = 9, 16, 22, 6, 1, 11, 12
cw, ch = FW * Z, FH * Z
per = 4
gap = 14
sheet = Image.new("RGB", (per * (3 * cw + gap) + gap, ((len(keys) + per - 1) // per) * (ch + 26) + 8), (12, 14, 19))
d = ImageDraw.Draw(sheet)
for i, k in enumerate(keys):
    x0 = gap + (i % per) * (3 * cw + gap)
    y0 = 22 + (i // per) * (ch + 26)
    d.text((x0, y0 - 15), k.upper() + "   photo  >  converted  >  drawn", fill=(225, 225, 225))
    photo = Image.open(os.path.join(conv, k + "-photo.png")).crop((X0 * K, Y0 * K, (X0 + FW) * K, (Y0 + FH) * K)).resize((cw, ch), Image.LANCZOS)
    im = Image.open(os.path.join(conv, k + ".png")).convert("RGBA").crop((X0, Y0, X0 + FW, Y0 + FH)).resize((cw, ch), Image.NEAREST)
    mid = Image.new("RGB", (cw, ch), (22, 26, 34)); mid.paste(im, (0, 0), im)
    rows = cast.HEADS[k]["rows"]
    eye = next(j for j, r in enumerate(rows) if "e" in r)
    c = Canvas(FW, FH, "#161a22")
    cast.head(c, cast.BY_KEY[k], 8, (EYE - Y0) - eye)
    tmp = os.path.join(tempfile.gettempdir(), "likeness-head.png")
    c.save(tmp, 1)
    drawn = Image.open(tmp).convert("RGB").resize((cw, ch), Image.NEAREST)
    for j, cell in enumerate((photo, mid, drawn)):
        sheet.paste(cell, (x0 + j * cw, y0))
sheet.save(out)
print(out, sheet.size)
