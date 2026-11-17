"""Each character at their desk, as it is in the show: seated behind it and
facing you, so the laptop and the monitors show their backs.

`seat(key, pose)` is the whole picture, 62x40 art pixels: the chair, the
character (cast.py), the desk and what is on it, and for some of them one
small thing on the wall behind. The desk (for Erlich, his couch) starts one
pixel in from the picture's left edge, so every row's furniture lines up with
the space's sign above it. The laptop tells the status with the pose: shut
when idle, open and lit when there is work.
"""
from px import Canvas, dark, light, mix, text_width
import cast
from cast import BY_KEY, OUTLINE, TORSO_H, width

W, H = 62, 40
CX = 27              # the character's middle
SHOULDER_Y = 17      # the shoulders' row (higher if tall)
DESK_Y = 25          # the first row of a desk's top
BOTTOM = H - 2       # what stands on the floor ends on this row
DX, DW = 1, 52       # a desk's left edge (one pixel in, for the outline) and width

GREEN, RED, GOLD = "#4fc45f", "#e5533d", "#f4c542"


# ------------------------------------------------------------ furniture
def chair(c, s, kind, tt):
    tw = width(s) - 4
    tx = CX - tw // 2
    if kind in ("office", "exec"):
        col = "#3d4452" if kind == "office" else "#4a2e1c"
        up = 4 if kind == "office" else 8
        c.rect(tx - 4, tt - up, tw + 8, up + 10, col)
        c.hl(tx - 3, tt - up - 1, tw + 6, light(col, 0.2))
        c.vl(tx - 4, tt - up, up + 10, light(col, 0.12))
        c.vl(tx + tw + 3, tt - up, up + 10, dark(col, 0.2))
        if kind == "exec":
            for y in range(tt - up + 2, tt + 6, 3):
                c.p(tx - 3, y, light(col, 0.3)); c.p(tx + tw + 2, y, light(col, 0.3))
        c.rect(CX - 1, DESK_Y + 6, 2, 6, "#4a505a")
        c.hl(CX - 6, BOTTOM - 1, 12, "#4a505a")
        c.p(CX - 6, BOTTOM, "#15171b"); c.p(CX + 5, BOTTOM, "#15171b"); c.p(CX - 1, BOTTOM, "#15171b")
    elif kind == "couch":
        # As wide as a desk, its arms where a desk's ends are.
        col = "#7a4f2e"
        x0, x1 = DX, DX + DW - 4
        c.rect(x0 + 3, tt - 2, DW - 6, 13, col)
        c.hl(x0 + 3, tt - 2, DW - 6, light(col, 0.2))
        for x in range(x0 + 8, x1, 6):
            c.vl(x, tt - 1, 11, dark(col, 0.15))
        c.rect(x0, tt + 3, 4, BOTTOM - tt - 2, dark(col, 0.15))
        c.rect(x1, tt + 3, 4, BOTTOM - tt - 2, dark(col, 0.15))
        c.hl(x0, tt + 3, 4, light(col, 0.2)); c.hl(x1, tt + 3, 4, light(col, 0.2))
        c.rect(x0 + 4, tt + 11, DW - 8, BOTTOM - tt - 11, dark(col, 0.3))
    elif kind == "cushion":
        c.rect(CX - 10, BOTTOM - 4, 20, 5, "#6a3a7a")
        c.hl(CX - 9, BOTTOM - 5, 18, "#8a55a0")
    elif kind == "stool":
        c.rect(CX - 1, DESK_Y + 6, 2, 7, "#aab4bb")
        c.hl(CX - 4, BOTTOM, 8, "#aab4bb")
        c.hl(CX - 3, BOTTOM - 4, 6, "#aab4bb")


def desk(c, style, ty=DESK_Y):
    x, w = DX, DW
    b = BOTTOM

    def top(col, hi, edge, depth=5):
        c.rect(x, ty, w, depth, col)
        c.hl(x, ty, w, hi)
        c.hl(x, ty + depth, w, edge)
        return ty + depth + 1

    def posts(y0, col, wide=2):
        for lx in (x + 1, x + w - 1 - wide):
            c.rect(lx, y0, wide, b - y0 + 1, col)
            c.vl(lx + wide - 1, y0, b - y0 + 1, dark(col, 0.25))

    if style == "white":
        posts(top("#e6e2d8", "#f7f4ee", "#a8a49a"), "#bdb9ae")
    elif style == "wood":
        y0 = top("#b98248", "#cf9a5e", "#86592f")
        posts(y0, "#6f4a2b")
        c.rect(x + w - 15, y0, 12, b - y0 + 1, "#7a5230")
        c.vl(x + w - 15, y0, b - y0 + 1, "#5d3d22")
        c.hl(x + w - 14, y0 + 4, 10, "#5d3d22")
        c.rect(x + w - 10, y0 + 1, 2, 1, "#d9b36a"); c.rect(x + w - 10, y0 + 6, 2, 1, "#d9b36a")
    elif style == "black":
        posts(top("#343741", "#4d515d", "#17181d"), "#23252c")
    elif style == "glass":
        y0 = top("#8fb9c6", "#d6eef4", "#4f6b75", 4)
        for i in range(x + 4, x + w - 4, 9):
            c.hl(i, ty + 2, 3, "#b9dbe4")
        posts(y0, "#aab4bb", 1)
    elif style == "exec":
        y0 = top("#7a4a2a", "#9a6238", "#4a2a16")
        c.rect(x + 1, y0, w - 2, b - y0 + 1, "#56321c")
        c.box(x + 4, y0 + 1, w - 8, b - y0 - 1, "#3f2414")
        c.hl(x + 7, y0 + 3, w - 14, "#c79a4a")
    elif style == "steel":
        y0 = top("#aab2b8", "#cdd4d9", "#6b7379")
        posts(y0, "#59616a")
        c.hl(x + 3, y0 + 4, w - 6, "#7c858b")
    elif style == "bar":
        y0 = top("#3a2a22", "#6b4a3a", "#1c1210")
        c.rect(x + 1, y0, w - 2, b - y0 + 1, "#4a2233")
        for i in range(x + 5, x + w - 3, 7):
            c.p(i, y0 + 2, "#d9b36a"); c.p(i, y0 + 5, "#d9b36a")
        c.hl(x + 1, b - 1, w - 2, "#d9b36a")
    elif style in ("low", "floor"):
        # A coffee table in front of the couch; a floor table is a desk's width.
        if style == "low":
            x, w = DX + 5, DW - 10
        c.rect(x, ty, w, 4, "#9a6a3c")
        c.hl(x, ty, w, "#b9834c")
        c.hl(x, ty + 4, w, "#6b4526")
        for lx in (x + 1, x + w - 3):
            c.rect(lx, ty + 5, 2, b - ty - 4, "#5a3a20")


# ------------------------------------------------------------- devices
def sticker(c, kind, x, y, lit):
    """What is on a laptop's lid, around (x, y), its middle."""
    up = (lambda col: light(col, 0.3)) if lit else (lambda col: col)
    if kind == "pp":
        c.rect(x - 2, y - 1, 4, 3, up("#2e8b3d"))
        c.p(x - 1, y - 1, "#f4f1ea"); c.p(x - 1, y, "#f4f1ea"); c.p(x, y - 1, "#f4f1ea")
    elif kind == "cross":
        c.vl(x, y - 2, 5, up("#b3262c")); c.hl(x - 1, y + 1, 3, up("#b3262c"))
    elif kind == "chat":
        c.rect(x - 2, y - 1, 4, 2, up("#2f6fd0")); c.p(x - 1, y + 1, up("#2f6fd0"))
    elif kind == "hooli":
        c.vl(x - 1, y - 2, 4, up("#3f7bd9")); c.p(x, y, up("#3f7bd9")); c.p(x + 1, y + 1, up("#f08f3c"))
    elif kind == "aviato":
        c.hl(x - 2, y, 4, up(RED)); c.p(x, y - 1, up(RED)); c.p(x, y + 1, up(RED)); c.p(x + 1, y, "#f4f1ea")
    elif kind == "raviga":
        c.vl(x - 1, y - 2, 4, up("#8d959b")); c.p(x, y - 2, up("#8d959b")); c.p(x + 1, y - 1, up("#8d959b"))
        c.p(x, y, up("#8d959b")); c.p(x + 1, y + 1, up("#8d959b"))
    elif kind == "hotdog":
        c.hl(x - 2, y - 1, 4, up("#d99a4a")); c.hl(x - 2, y, 4, up("#c0452f")); c.hl(x - 2, y + 1, 4, up("#d99a4a"))
    elif kind == "commas":
        for dx in (-2, 0, 2):
            c.p(x + dx, y, up(GOLD)); c.p(x + dx, y + 1, up("#c79a4a"))
    elif kind == "tri":
        for i in range(3):
            c.hl(x - 2, y - 1 + i, 3 - i, up("#2f6fd0"))
            c.hl(x + 1 - i, y - 1 + i, i + 1, up("#f08f3c"))
    elif kind == "dot":
        c.rect(x - 1, y - 1, 2, 2, up("#6fe0ff"))
    elif kind == "many":
        for dx, dy, col in [(-4, -2, "#ff5fa2"), (-1, -2, "#f2c94c"), (2, -1, "#6fe0ff"), (-3, 1, "#a6e08a"), (0, 1, "#ff5fa2"),
                            (3, 2, "#f2c94c"), (-1, 0, "#f4f1ea")]:
            c.rect(x + dx, y + dy, 2, 1, up(col))
    elif kind == "apple":
        c.rect(x - 1, y - 1, 2, 2, "#f4f1ea" if lit else "#d5dade")


def laptop(c, body, mark, ty, is_open, lit, cx=CX):
    x = cx - 6
    if not is_open:
        c.rect(x, ty + 2, 12, 2, light(body, 0.1))
        c.hl(x, ty + 4, 12, dark(body, 0.35))
        return
    c.rect(x, ty - 4, 12, 8, body)
    c.hl(x, ty - 4, 12, "#eaf2ff" if lit else light(body, 0.2))
    c.vl(x + 11, ty - 3, 7, dark(body, 0.18))
    c.hl(x, ty + 4, 12, dark(body, 0.4))
    sticker(c, mark, cx, ty, lit)


def monitor(c, x, w, h, ty, lit):
    """A monitor from behind."""
    y = ty - h
    c.rect(x, y, w, h, "#22252c")
    c.hl(x, y, w, "#9fc4ff" if lit else "#3a3e48")
    c.vl(x + w - 1, y + 1, h - 1, "#191b20")
    c.rect(x + w // 2 - 2, y + h // 2 - 1, 4, 3, "#2d3139")
    c.rect(x + w // 2 - 1, ty, 2, 2, "#3a3e48")
    c.hl(x + w // 2 - 3, ty + 2, 6, "#4a4f5a")
    c.p(x + 1, y + h - 2, GREEN if lit else "#3a3e48")


# --------------------------------------------------------------- props
def cans(c, x, by, col="#3bb54a", n=2, band="#f1ece2"):
    for i in range(n):
        c.rect(x + i * 3, by - 3, 2, 4, col)
        c.hl(x + i * 3, by - 3, 2, "#c9cfd3")
        c.hl(x + i * 3, by - 1, 2, band)


def mug(c, x, by, col="#e8e4da"):
    c.rect(x, by - 2, 3, 3, col)
    c.p(x + 3, by - 1, col)
    c.hl(x, by - 2, 3, light(col, 0.35))


def props(c, key, ty):
    """What makes it their desk. L and R are the free ends of the top."""
    by = ty + 3
    L, R = DX + 3, CX + 10
    if key == "richard":
        cans(c, L + 1, by)
        cans(c, L + 9, by - 1, n=1)
        monitor(c, R + 1, 13, 9, ty, False)
        mug(c, R - 2, by + 1)
        # The bin he keeps close.
        bx = W - 7
        c.rect(bx, BOTTOM - 5, 6, 6, "#5f666c"); c.hl(bx - 1, BOTTOM - 6, 8, "#8a9298")
        c.vl(bx + 2, BOTTOM - 5, 6, "#454b50"); c.vl(bx + 4, BOTTOM - 5, 6, "#454b50")
    elif key == "gilfoyle":
        monitor(c, L - 1, 13, 10, ty, False)
        monitor(c, R + 1, 13, 10, ty, False)
        c.rect(R - 2, by - 3, 2, 5, "#101114")
        c.p(R - 2, by - 4, "#f2c94c"); c.p(R - 2, by - 5, "#ff8a1f")
        # Anton's little brother, under the desk.
        ax = DX + DW - 12
        c.rect(ax, BOTTOM - 6, 8, 7, "#111317"); c.box(ax, BOTTOM - 6, 8, 7, "#2a2d34")
        c.vl(ax + 2, BOTTOM - 5, 5, "#b3262c"); c.p(ax + 5, BOTTOM - 4, GREEN)
    elif key == "dinesh":
        monitor(c, L - 1, 13, 9, ty, False)
        c.grid(R - 1, by - 3, ["..#####...", ".#######..", "##########", ".o.....o.."], {"#": "#d93a34", "o": "#111317"})
        c.rect(R + 2, by - 2, 3, 1, "#9fd0e8")
        for (x, y) in [(R + 10, by), (R + 11, by - 1), (R + 12, by), (R + 13, by + 1), (R + 14, by)]:
            c.p(x, y, GOLD)
    elif key == "jared":
        for i, col in enumerate(["#d93a34", "#f2c94c", "#2e8b3d", "#2f6fd0", "#8e5bd0"]):
            c.rect(L + i * 2, by - 7 + (i % 2), 2, 8 - (i % 2), col)
            c.vl(L + i * 2 + 1, by - 7 + (i % 2), 8 - (i % 2), dark(col, 0.25))
        mug(c, R, by + 1, "#f4f1ea")
        c.hl(R + 8, by, 4, "#3a3e47"); c.vl(R + 9, by - 7, 7, "#6f777d"); c.p(R + 10, by - 8, "#6f777d")
        c.rect(R + 10, by - 10, 5, 2, "#2f3a36"); c.hl(R + 10, by - 8, 5, "#f4d27a")
    elif key == "erlich":
        glass, edge, water = "#a9e0d6", "#4f9088", "#3f8f6a"
        c.rect(L + 9, by - 11, 2, 9, glass); c.vl(L + 10, by - 11, 9, edge); c.hl(L + 8, by - 12, 4, glass)
        c.rect(L + 8, by - 3, 4, 4, glass); c.rect(L + 8, by - 1, 4, 2, water)
        c.p(L + 12, by - 5, edge); c.p(L + 13, by - 6, "#6b4a2f")
        c.rect(R, by - 1, 6, 2, "#d9c9a3"); c.hl(R + 1, by - 1, 4, "#b08a5a")
        c.rect(R + 9, by, 3, 1, "#3a3e47")
    elif key == "bighead":
        c.rect(R + 3, by - 9, 6, 10, "#d93a34"); c.rect(R + 3, by - 5, 6, 2, "#f1ece2"); c.hl(R + 2, by - 10, 8, "#f1ece2")
        c.vl(R + 7, by - 14, 4, "#f1ece2"); c.p(R + 8, by - 15, "#f1ece2")
        c.rect(L + 6, by - 2, 3, 3, "#2f6fd0"); c.p(L + 6, by - 2, "#8fb7ff")
    elif key == "monica":
        c.rect(L + 6, by - 4, 3, 5, "#f4f1ea"); c.hl(L + 6, by - 2, 3, "#8a6a3a"); c.hl(L + 6, by - 4, 3, "#3a2a1e")
        c.rect(R + 2, by, 4, 1, "#15171b")
        c.rect(R + 9, by - 1, 4, 2, "#f4f1ea"); c.hl(R + 9, by - 1, 4, "#d93a34")
    elif key == "jianyang":
        c.hl(L + 2, by, 11, "#e8e4da"); c.hl(L + 4, by - 1, 7, "#d99a4a"); c.hl(L + 3, by - 2, 9, "#c0452f")
        c.p(L + 5, by - 3, "#f2c94c"); c.p(L + 7, by - 3, "#f2c94c"); c.p(L + 9, by - 3, "#f2c94c")
        c.rect(R, by - 6, 4, 7, "#15171b"); c.rect(R + 1, by - 5, 2, 4, "#d93a34"); c.p(R + 1, by - 1, "#f4f1ea")
        c.hl(R + 7, by, 9, "#e8e4da")
        c.grid(R + 8, by - 3, ["..###...", ".#####.#", "..###..."], {"#": "#8fa9b8"})
    elif key == "gavin":
        c.rect(L + 1, by - 8, 12, 9, "#0d0e11"); c.box(L + 1, by - 8, 12, 9, "#2a2d34")
        for i, dy in enumerate([0, -1, -2, -1, 0, -1, -2, -1]):
            c.p(L + 3 + i, by - 3 + dy, "#f4f1ea")
        c.p(L + 3, by - 6, "#3f7bd9")
        c.rect(R + 5, by - 1, 5, 2, "#3a2a1e"); c.vl(R + 7, by - 4, 3, "#d9b36a")
        c.rect(R + 5, by - 7, 5, 3, GOLD); c.p(R + 4, by - 6, GOLD); c.p(R + 10, by - 6, GOLD)
    elif key == "russ":
        for i, x in enumerate((L + 1, L + 7)):
            c.rect(x, by - 6, 4, 7, "#cfe3ea"); c.rect(x + 1, by - 9, 2, 3, "#cfe3ea"); c.hl(x + 1, by - 10, 2, "#d9b36a")
            c.rect(x, by - 4, 4, 3, "#15171b"); c.p(x + 1, by - 3, GOLD); c.p(x + 2, by - 3, GOLD)
            c.hl(x, by - 1 - i, 4, "#e8c98a")
        for x in (R + 1, R + 5, R + 9):
            c.rect(x, by - 1, 2, 2, "#cfe3ea"); c.p(x, by, "#e8c98a")
        c.rect(R + 13, by, 3, 1, "#3f8f4e")
    elif key == "laurie":
        c.rect(L + 6, by - 2, 4, 3, "#f4f1ea"); c.vl(L + 8, by - 9, 7, "#3f8f4e")
        c.p(L + 7, by - 9, "#f4f1ea"); c.p(L + 9, by - 8, "#f4f1ea"); c.p(L + 7, by - 6, "#f4f1ea"); c.p(L + 9, by - 10, "#f7b7d2")
        c.hl(R + 3, by - 6, 9, "#aab4bb"); c.vl(R + 3, by - 6, 7, "#aab4bb"); c.vl(R + 11, by - 6, 7, "#aab4bb")
        for x in (R + 5, R + 7, R + 9):
            c.vl(x, by - 5, 3, "#6f777d"); c.p(x, by - 2, "#d5dade")
    elif key == "peter":
        for i in range(2):
            x = L + 1 + i * 7
            c.hl(x + 1, by - 3, 3, "#d99a4a"); c.hl(x, by - 2, 5, "#e8b060"); c.p(x + 2, by - 3, "#f4e3b0")
            c.hl(x, by - 1, 5, "#5a2f1c" if i % 2 == 0 else "#3f8f4e"); c.hl(x, by, 5, "#d99a4a")
        c.rect(R + 1, by - 7, 7, 8, "#f1ece2"); c.hl(R + 1, by - 7, 7, "#d9d4c8"); c.text(R + 2, by - 5, "B", "#d93a34")
        c.rect(R + 11, by - 3, 3, 4, "#cfe3ea"); c.hl(R + 11, by - 3, 3, "#8d959b"); c.rect(R + 11, by - 1, 3, 2, "#f4e3b0")
    elif key == "jack":
        c.grid(L + 3, by - 7, ["......##.", ".....###.", "#...###..", ".#######.", "..#####..", "..#...#..", "..#...#..", ".########"],
               {"#": "#c79a4a"})
        c.rect(R + 1, by - 5, 13, 6, "#15171b"); c.box(R + 1, by - 5, 13, 6, "#2a2d34")
        c.rect(R + 3, by - 3, 2, 2, GREEN); c.hl(R + 7, by - 3, 5, "#3d424b"); c.hl(R + 7, by - 1, 5, "#3d424b")
    elif key == "fiona":
        c.rect(L - 1, by - 9, 14, 10, "#c9c2ad"); c.box(L - 1, by - 9, 14, 10, "#8a8472"); c.rect(L + 1, by - 7, 7, 6, "#0c1a12")
        for i, dy in enumerate([0, -1, -2, -1, 0, 1, 2]):
            c.p(L + 1 + i, by - 4 + dy, GREEN)
        c.p(L + 10, by - 7, "#d93a34"); c.p(L + 10, by - 4, "#15171b")
        c.grid(R + 2, by - 4, ["#.#.#.", "#.#.#.", "######", ".#####", "..###."], {"#": "#dfe6ea"})
        c.line(R + 10, by, R + 13, by - 5, "#2f6fd0"); c.p(R + 14, by - 6, "#aab4bb")
    elif key == "denpok":
        c.hl(L + 8, by, 5, "#6b4a2f"); c.line(L + 10, by - 1, L + 12, by - 8, "#8a6a3a"); c.p(L + 12, by - 9, "#ff8a1f")
        for (x, y) in [(L + 13, by - 11), (L + 12, by - 13), (L + 13, by - 15)]:
            c.p(x, y, (200, 200, 200, 120))
        c.rect(R + 1, by - 3, 9, 4, "#c79a4a"); c.hl(R, by - 3, 11, GOLD); c.hl(R + 2, by, 7, "#8a6a3a")
    elif key == "carla":
        monitor(c, L - 1, 13, 9, ty, False)
        cans(c, R + 1, by, "#15171b", 2, "#a6e08a")
        c.rect(R + 10, by - 1, 4, 2, "#b5653a"); c.rect(R + 11, by - 6, 2, 5, "#3f8f4e")
        c.p(R + 10, by - 4, "#3f8f4e"); c.p(R + 13, by - 5, "#3f8f4e")
    elif key == "ron":
        # A lawyer's desk: the scales in brass, a term sheet to sign, his coffee.
        c.grid(L + 3, by - 7, ["...#...", "#######", "#..#..#", "##.#.##", "...#...", "...#...", "..###.."], {"#": "#c79a4a"})
        c.rect(R + 1, by - 1, 7, 2, "#f1ece2"); c.hl(R + 2, by - 1, 4, "#aab4bb"); c.hl(R + 2, by, 5, "#aab4bb")
        c.line(R + 9, by, R + 11, by - 2, "#2c3a57")
        mug(c, R + 13, by + 1, "#2c3a57")


# ------------------------------------------------------ on the wall behind
def sign(text, fg, bg, edge=None):
    """A small sign with a word on it. A long word gets no frame, to fit."""
    tight = text_width(text) > 19
    c = Canvas(text_width(text) + (2 if tight else 4), 9, bg)
    if edge and not tight:
        c.box(0, 0, c.w, 9, edge)
    c.text(1 if tight else 2, 2, text, fg)
    return c


def poster(w, h, bg, edge="#8a6a3a"):
    c = Canvas(w, h, bg)
    c.box(0, 0, w, h, edge)
    return c


def hanging(key):
    """What hangs on the wall behind them, for those who have something: a
    thing that hangs by them in the show, or a joke of theirs from it. The
    rest have a bare wall. It hangs to their left, where the wall is about
    18 wide before their hair: a wider one runs on behind them."""
    if key == "richard":
        # Tabs, not spaces: a plain printed sign. (It was green with a check
        # mark, which read as an agent's status.)
        return sign("TABS", "#2c3a57", "#f1ece2", "#8a6a3a")
    if key == "gilfoyle":
        # The cross he wears, the way he wears it.
        c = poster(11, 11, "#0d0e11", "#3a1418")
        c.vl(5, 2, 7, "#b3262c"); c.hl(3, 6, 5, "#b3262c")
        return c
    if key == "jared":
        # His scrum board.
        c = poster(21, 12, "#dfe3e0", "#8d959b")
        c.vl(7, 1, 10, "#8d959b"); c.vl(14, 1, 10, "#8d959b")
        for x, y, col in [(2, 2, "#f2d24c"), (2, 5, "#f08fb0"), (2, 8, "#8fd0f0"), (9, 2, "#a6e08a"), (9, 5, "#f2d24c"), (16, 2, "#f08fb0")]:
            c.rect(x, y, 4, 2, col)
        return c
    if key == "erlich":
        return sign("AVIATO", "#e5533d", "#f4f1ea", "#b3262c")
    if key == "jianyang":
        # Not hotdog.
        c = poster(17, 11, "#f2c94c")
        c.hl(4, 4, 9, "#d99a4a"); c.hl(3, 5, 11, "#c0452f"); c.hl(4, 6, 9, "#d99a4a")
        c.line(4, 8, 12, 2, "#15171b")
        return c
    if key == "gavin":
        c = sign("HOOLI", "#2f6fd0", "#f4f1ea", "#8d959b")
        c.p(c.w - 3, 6, "#f08f3c")
        return c
    if key == "russ":
        # Tres comas.
        c = poster(15, 9, "#15171b", "#c79a4a")
        for x in (3, 7, 11):
            c.rect(x, 3, 2, 2, GOLD); c.p(x, 5, GOLD)
        return c
    if key == "jack":
        # The conjoined triangles of success, framed in his office.
        c = poster(13, 11, "#f1ece2")
        for i in range(7):
            c.hl(2, 2 + i, i + 1, "#2c3a57")
            c.hl(4 + i, 2 + i, 7 - i, "#f08f3c")
        return c
    if key == "fiona":
        return sign("EKLOW", "#6fe0ff", "#1d2629", "#3a4048")
    return None


# Where it hangs: its left edge and its top row. Always to their left, over
# the desk's end, so the word they say when blocked or done (`bubble`) is
# always to their right; how far in and how high differ a little from one to
# the next. A piece wider than the wall there is not made smaller: it starts at
# the desk's end and its far end is behind their head or the chair's back, as
# a raised hand may be in front of any of them.
HANGS = {
    "richard": (1, 2), "gilfoyle": (4, 1), "jared": (1, 1), "erlich": (1, 2), "jianyang": (1, 2),
    "gavin": (1, 1), "russ": (3, 3), "jack": (2, 1), "fiona": (1, 3),
}


# device: laptop color and what is on its lid
DESKS = {
    "richard": dict(desk="white", laptop=("#c3cad0", "pp")),
    "gilfoyle": dict(desk="black", laptop=("#2a2d34", "cross")),
    "dinesh": dict(desk="white", laptop=("#c3cad0", "chat")),
    "jared": dict(desk="white", laptop=("#c3cad0", "apple")),
    "erlich": dict(desk="low", seat="couch", laptop=("#c3cad0", "aviato")),
    "bighead": dict(desk="white", laptop=("#c3cad0", "hooli")),
    "monica": dict(desk="glass", laptop=("#d5dade", "raviga")),
    "jianyang": dict(desk="wood", laptop=("#c3cad0", "hotdog")),
    "gavin": dict(desk="exec", seat="exec", laptop=("#3a3e48", "hooli")),
    "russ": dict(desk="bar", seat="stool", laptop=("#ff7a1a", "commas")),
    "laurie": dict(desk="glass", laptop=("#d5dade", "apple")),
    "peter": dict(desk="wood", laptop=("#c3cad0", "apple")),
    "jack": dict(desk="wood", laptop=("#c3cad0", "tri")),
    "fiona": dict(desk="steel", laptop=("#3a4048", "dot")),
    "denpok": dict(desk="floor", seat="cushion", laptop=("#c3cad0", "apple")),
    "carla": dict(desk="white", laptop=("#3a3e48", "many")),
    "ron": dict(desk="wood", laptop=("#c3cad0", "apple")),
}


# A bubble's left edge when it is to the right of a head in the middle at `cx`.
def bubble_x(cx):
    return cx + 10


def bubble(c, kind, x, y):
    """A small word from the character: ! when it needs you, a tick when done.
    It is always to the right of their head, so its tail comes out of its
    lower left corner, toward them."""
    b = Canvas(13, 13)
    b.rect(2, 1, 9, 8, "#f4f1ea")
    b.rect(1, 2, 11, 6, "#f4f1ea")
    b.p(4, 9, "#f4f1ea"); b.p(3, 9, "#f4f1ea"); b.p(3, 10, "#f4f1ea")
    if kind == "blocked":
        b.rect(6, 2, 2, 4, "#d93a34")
        b.rect(6, 7, 2, 1, "#d93a34")
    else:
        for (xx, yy) in [(3, 5), (4, 6), (5, 7), (6, 6), (7, 5), (8, 4), (9, 3)]:
            b.p(xx, yy, "#2e8b3d")
            b.p(xx, yy - 1, "#2e8b3d")
    b.outline(OUTLINE)
    c.blit(b, x, y)


def seat(key, pose="idle"):
    s = BY_KEY[key]
    d = DESKS[key]
    low = d["desk"] in ("low", "floor")
    ty = DESK_Y + (4 if low else 0)
    tt = SHOULDER_Y - s.get("tall", 0)
    hy = tt - cast.neck(s)
    lit = pose != "idle"
    c = Canvas(W, H)
    # Their piece of the wall, if they have one, up beside their head, to the left.
    piece = hanging(key)
    if piece:
        c.blit(piece, *HANGS[key])
    chair(c, s, d.get("seat", "office"), tt)
    # The character, outlined on its own so it stands off the chair.
    f = Canvas(W, H)
    if low:
        tw = width(s)
        f.rect(CX - tw // 2 - 1, tt + TORSO_H, tw + 2, ty - tt - TORSO_H + 1, s["pants"])
    else:
        cast.legs(f, s, CX, DESK_Y + 6, BOTTOM)
    cast.torso(f, s, CX, tt)
    cast.upper_arms(f, s, CX, tt, pose)
    cast.head(f, s, CX, hy)
    if pose == "work":
        # The screen lights them from below.
        for y in range(hy + 5, tt + TORSO_H):
            for x in range(CX - 9, CX + 9):
                p = f.get(x, y)
                if p[3]:
                    f.px[x, y] = mix(p, "#a9ccff", 0.12)
    f.outline(OUTLINE)
    c.blit(f, 0, 0)
    desk(c, d["desk"], ty)
    props(c, key, ty)
    a = Canvas(W, H)
    cast.forearms(a, s, CX, ty, pose)
    a.outline(OUTLINE)
    c.blit(a, 0, 0)
    body, mark = d["laptop"]
    laptop(c, body, mark, ty, lit, pose == "work")
    c.outline(OUTLINE)
    if pose in ("blocked", "done"):
        bubble(c, pose, bubble_x(CX), max(0, hy - 2))
    return c
