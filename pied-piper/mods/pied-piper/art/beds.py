"""Each character on their own bunk, for the bedroom: the hostel's bedrooms
have bunk beds. They sit on the lower one cross-legged, facing you, with the
laptop on their lap, as they do most nights.

`bed(key, pose)` is the whole picture, the size of a desk's (desks.W x
desks.H): the bunk seen from its long side, the character (cast.py), their
blanket, what they keep by the pillow, and the lamp on its little shelf at
the pillow's end, which is the room's only light. The pose says the status as
at a desk: the laptop is shut when idle, lying on the lap with its mark on the
lid, and open when there is work, its screen lit while they work; a hand goes
up when blocked, both when done.
"""
from px import Canvas, dark, light, mix
import cast
import desks
from cast import BY_KEY, OUTLINE, TORSO_H
from desks import W, H, BOTTOM, GREEN, GOLD

LEFT, RIGHT = 1, 58      # the bunk's posts: their outer edges (the left one where a desk's left edge is)
CX = 30                  # the character's middle, the middle of the bunk
MATTRESS = 31            # the lower mattress's first row; they sit on it
RAIL = 34                # the lower bunk's side rail, under the mattress
SHOULDER_Y = 18          # the shoulders' row, sitting on the mattress

SHEET, PILLOW = "#a4adc0", "#dde2ea"
FRAMES = {"wood": "#7a5230", "black": "#2a2d34", "white": "#cfcabd", "steel": "#8a9298", "dark": "#4a2e1c"}


# ---------------------------------------------------------------- the bunk
def frame(c, style):
    """The posts, the upper bunk's rail across the top, the ladder, the lower
    bunk's rail."""
    col = FRAMES[style]
    hi, lo = light(col, 0.25), dark(col, 0.25)
    for x in (LEFT, RIGHT - 1):
        c.rect(x, 0, 2, BOTTOM + 1, col)
        c.vl(x, 0, BOTTOM + 1, hi)
    # The upper bunk: its rail, a strip of its mattress over it.
    c.rect(LEFT + 2, 1, RIGHT - LEFT - 3, 2, col)
    c.hl(LEFT + 2, 1, RIGHT - LEFT - 3, hi)
    c.hl(LEFT + 2, 0, RIGHT - LEFT - 3, dark(SHEET, 0.2))
    # The ladder, at the foot.
    c.vl(RIGHT - 7, 3, MATTRESS - 3, col)
    for y in range(7, MATTRESS, 5):
        c.hl(RIGHT - 6, y, 5, lo)
    # The lower bunk.
    c.rect(LEFT + 2, MATTRESS, RIGHT - LEFT - 3, 3, SHEET)
    c.hl(LEFT + 2, MATTRESS, RIGHT - LEFT - 3, light(SHEET, 0.3))
    c.rect(LEFT + 2, RAIL, RIGHT - LEFT - 3, 2, col)
    c.hl(LEFT + 2, RAIL, RIGHT - LEFT - 3, hi)


def pillow(c):
    x, y = LEFT + 3, MATTRESS - 5
    c.rect(x + 1, y, 10, 5, PILLOW)
    c.rect(x, y + 1, 12, 3, PILLOW)
    c.hl(x + 1, y + 4, 10, dark(PILLOW, 0.18))


def blanket(c, spec):
    """Their blanket, over the mattress and down its side."""
    col = spec["color"]
    alt = spec.get("alt", light(col, 0.25))
    kind = spec.get("pattern", "plain")
    x, w = LEFT + 17, RIGHT - LEFT - 18
    top, h = MATTRESS, RAIL + 2 - MATTRESS
    c.rect(x, top, w, h, col)
    c.hl(x, top, w, light(col, 0.2))
    if kind == "stripe":
        c.hl(x, top + 2, w, alt)
    elif kind == "plaid":
        c.hl(x, top + 2, w, alt)
        for xx in range(x + 2, x + w, 5):
            c.vl(xx, top + 1, h - 1, alt)
    elif kind == "cross":
        c.vl(x + 5, top, 5, alt); c.hl(x + 4, top + 3, 3, alt)
    elif kind == "trim":
        c.hl(x, top + h - 1, w, alt)
        for xx in range(x + 2, x + w - 1, 5):
            c.p(xx, top + 2, spec["dot"])
    elif kind == "flames":
        for i, xx in enumerate(range(x + 1, x + w - 2, 3)):
            hgt = 1 + (i * 5) % 3
            c.rect(xx, top + h - hgt, 2, hgt, alt)
            c.p(xx, top + h - hgt - 1, GOLD)
    elif kind == "tri":
        # The conjoined triangles of success.
        for i in range(4):
            c.hl(x + 4, top + 1 + i, i + 1, alt)
            c.hl(x + 6 + i, top + 1 + i, 4 - i, light(alt, 0.35))
    elif kind == "patches":
        for dx, dy, pc in [(2, 1, "#ff5fa2"), (8, 3, "#f2c94c"), (15, 1, "#6fe0ff"), (22, 3, "#a6e08a"), (29, 1, "#ff5fa2")]:
            c.rect(x + dx, top + dy, 3, 1, pc)
    elif kind == "dots":
        for yy in (top + 1, top + 3):
            for xx in range(x + 1 + (yy % 2) * 2, x + w - 1, 4):
                c.p(xx, yy, alt)
    elif kind == "panel":
        for xx in range(x + 3, x + w - 2, 6):
            c.vl(xx, top + 1, h - 1, alt)
        c.rect(x + 8, top + 2, 3, 1, spec["dot"])
    # Turned back at the pillow's end.
    c.vl(x, top, h, SHEET)
    c.vl(x + 1, top, h, dark(col, 0.3))
    c.vl(x + w - 1, top + 1, h - 1, dark(col, 0.25))


LAMP = (LEFT + 4, 15)    # the middle of the lamp's shade


def lamp(c):
    """A lamp on a little shelf at the pillow's end, on: the bedroom's light."""
    x, y = LAMP
    c.hl(x - 2, y + 6, 7, "#8a6238"); c.hl(x - 2, y + 7, 7, "#5a3d22"); c.p(x - 1, y + 8, "#5a3d22")
    c.hl(x - 1, y + 5, 3, "#8d959b"); c.vl(x, y + 3, 2, "#8d959b")
    c.rect(x - 1, y - 1, 3, 1, "#f6dc8a")
    c.rect(x - 2, y, 5, 3, "#f6dc8a")
    c.hl(x - 2, y + 2, 5, "#fff3c4")


def glow():
    """The lamp's light on the wall around it, to lie under the bunk: a warm
    circle in four steps, the paint showing through."""
    c = Canvas(W, H)
    cx, cy = LAMP
    # Only inside the bunk: its posts and the bunk above stop the light.
    for y in range(3, MATTRESS):
        for x in range(LEFT + 2, RIGHT - 1):
            d = ((x - cx) ** 2 + ((y - cy) * 1.15) ** 2) ** 0.5
            for reach, alpha in ((6, 96), (11, 66), (16, 40), (21, 20)):
                if d < reach:
                    c.px[x, y] = (255, 205, 120, alpha)
                    break
    return c


def keeps(c, item, on):
    """What they keep on the bed, between themselves and the ladder."""
    ix, by = CX + 12, MATTRESS - 1
    if item == "cans":
        desks.cans(c, ix, by, n=2)
    elif item == "blackcans":
        desks.cans(c, ix, by, "#15171b", 2, "#a6e08a")
    elif item == "mug":
        desks.mug(c, ix, by)
    elif item == "candle":
        c.rect(ix + 1, by - 3, 2, 4, "#101114")
        c.p(ix + 1, by - 4, "#f2c94c"); c.p(ix + 1, by - 5, "#ff8a1f")
    elif item == "books":
        for i, bc in enumerate(["#2f6fd0", "#f2c94c", "#d93a34"]):
            c.rect(ix, by - 1 - i * 2, 5, 2, bc)
            c.p(ix + 4, by - 1 - i * 2, dark(bc, 0.25))
    elif item == "cup":
        c.rect(ix, by - 5, 4, 6, "#d93a34"); c.hl(ix, by - 3, 4, "#f1ece2"); c.hl(ix - 1, by - 6, 6, "#f1ece2")
        c.vl(ix + 3, by - 9, 3, "#f1ece2")
    elif item == "phone":
        c.rect(ix + 1, by - 4, 3, 5, "#15171b"); c.rect(ix + 2, by - 3, 1, 3, "#8fb7ff" if on else "#2a3348")
    elif item == "bottle":
        c.rect(ix + 1, by - 4, 3, 5, "#cfe3ea"); c.rect(ix + 2, by - 7, 1, 3, "#cfe3ea"); c.p(ix + 2, by - 8, "#d9b36a")
        c.hl(ix + 1, by - 2, 3, "#15171b"); c.p(ix + 2, by - 2, GOLD)
    elif item == "trophy":
        c.rect(ix + 1, by - 5, 3, 3, GOLD); c.p(ix, by - 4, GOLD); c.p(ix + 4, by - 4, GOLD)
        c.vl(ix + 2, by - 2, 2, "#d9b36a"); c.hl(ix + 1, by, 3, "#3a2a1e")
    elif item == "orchid":
        c.rect(ix + 1, by - 1, 3, 2, "#f4f1ea"); c.vl(ix + 2, by - 7, 6, "#3f8f4e")
        c.p(ix + 1, by - 7, "#f4f1ea"); c.p(ix + 3, by - 6, "#f7b7d2"); c.p(ix + 1, by - 4, "#f4f1ea")
    elif item == "incense":
        c.hl(ix, by, 5, "#6b4a2f"); c.line(ix + 2, by - 1, ix + 4, by - 6, "#8a6a3a"); c.p(ix + 4, by - 7, "#ff8a1f")
    elif item == "hotdog":
        c.hl(ix - 1, by, 6, "#e8e4da"); c.hl(ix, by - 1, 4, "#d99a4a"); c.hl(ix, by - 2, 4, "#c0452f"); c.hl(ix, by - 3, 4, "#d99a4a")
    elif item == "bun":
        c.hl(ix + 1, by - 3, 3, "#d99a4a"); c.hl(ix, by - 2, 5, "#e8b060"); c.hl(ix, by - 1, 5, "#5a2f1c"); c.hl(ix, by, 5, "#d99a4a")
    elif item == "battery":
        c.rect(ix, by - 5, 4, 6, "#20252b"); c.p(ix + 1, by - 6, "#8d959b"); c.p(ix + 2, by - 6, "#8d959b")
        for i in range(3 if on else 1):
            c.hl(ix + 1, by - 1 - i * 2, 2, GREEN)
    elif item == "plant":
        c.rect(ix, by - 1, 4, 2, "#b5653a"); c.rect(ix + 1, by - 6, 2, 5, "#3f8f4e")
        c.p(ix, by - 4, "#3f8f4e"); c.p(ix + 3, by - 5, "#3f8f4e")


# blanket: color, pattern, its second color; the bunk's frame; what they keep on it
BEDS = {
    "richard": dict(blanket=dict(color="#4f5f7a", pattern="stripe", alt="#6f819c"), frame="wood", item="cans"),
    "gilfoyle": dict(blanket=dict(color="#1d1f25", pattern="cross", alt="#a02b2b"), frame="black", item="candle"),
    "dinesh": dict(blanket=dict(color="#7a2a34", pattern="plain"), frame="wood", item="incense"),
    "jared": dict(blanket=dict(color="#7f9cc0", pattern="plaid", alt="#a9c1dc"), frame="white", item="books"),
    "erlich": dict(blanket=dict(color="#27506b", pattern="trim", alt="#d9662b", dot="#e2b43a"), frame="wood", item="mug"),
    "bighead": dict(blanket=dict(color="#4a5f86", pattern="dots", alt="#8fb7ff"), frame="wood", item="cup"),
    "monica": dict(blanket=dict(color="#8a8f9c", pattern="plain"), frame="white", item="plant"),
    "jianyang": dict(blanket=dict(color="#3f7a4e", pattern="stripe", alt="#5a9a68"), frame="wood", item="hotdog"),
    "gavin": dict(blanket=dict(color="#3d2a5e", pattern="trim", alt="#c79a4a", dot="#c79a4a"), frame="dark", item="trophy"),
    "russ": dict(blanket=dict(color="#2a2228", pattern="flames", alt="#ff7a1a"), frame="black", item="bottle"),
    "laurie": dict(blanket=dict(color="#b9bec6", pattern="plain"), frame="steel", item="orchid"),
    "peter": dict(blanket=dict(color="#8a7a5a", pattern="plaid", alt="#a3936f"), frame="wood", item="bun"),
    "jack": dict(blanket=dict(color="#9a8a62", pattern="tri", alt="#2c3a57"), frame="wood", item="trophy"),
    "fiona": dict(blanket=dict(color="#aab4bb", pattern="panel", alt="#8d959b", dot="#6fe0ff"), frame="steel", item="battery"),
    "denpok": dict(blanket=dict(color="#c9772e", pattern="trim", alt="#e2b43a", dot="#8a5a34"), frame="wood", item="phone"),
    "carla": dict(blanket=dict(color="#22242b", pattern="patches"), frame="black", item="blackcans"),
    "ron": dict(blanket=dict(color="#2c3a57", pattern="stripe", alt="#46587a"), frame="wood", item="books"),
}


def flat(mark):
    """A lid's mark (desks.sticker) on a shut laptop lying on a lap, seen
    nearly edge on: each of its columns becomes one pixel, of the color most
    of that column is. {dx: color}, dx out from the lid's middle."""
    t = Canvas(16, 16)
    desks.sticker(t, mark, 8, 8, False)
    row = {}
    for x in range(t.w):
        col = [t.get(x, y) for y in range(t.h) if t.get(x, y)[3]]
        if col:
            row[x - 8] = max(col, key=col.count)
    return row


def bed(key, pose="idle"):
    s = BY_KEY[key]
    b = BEDS[key]
    work = pose != "idle"
    # Sitting, the tall ones are only a little taller.
    tt = SHOULDER_Y - max(-1, min(1, s.get("tall", 0)))
    hy = tt - cast.neck(s)
    c = Canvas(W, H)
    frame(c, b["frame"])
    blanket(c, b["blanket"])
    pillow(c)
    lamp(c)
    keeps(c, b["item"], work)
    # The character, outlined on its own so it stands off the bunk.
    f = Canvas(W, H)
    cast.crossed(f, s, CX, MATTRESS - 4)
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
    rest = MATTRESS - 7       # where the forearms rest, as on a desk's top
    body, mark = desks.DESKS[key]["laptop"]
    if pose == "idle":
        # Shut, lying on the lap as a shut one lies on a desk, the mark across
        # the lid's near row; outlined on its own, so it stands off the shirt
        # and the legs, the hands beside it.
        l = Canvas(W, H)
        desks.laptop(l, body, mark, rest, False, False, CX)
        for dx, col in flat(mark).items():
            l.p(CX + dx, rest + 3, col)
        l.outline(OUTLINE)
        c.blit(l, 0, 0)
    a = Canvas(W, H)
    cast.forearms(a, s, CX, rest, pose)
    a.outline(OUTLINE)
    c.blit(a, 0, 0)
    if pose != "idle":
        # Open on the lap, its back to you, lit with work.
        desks.laptop(c, body, mark, MATTRESS - 6, True, pose == "work", CX)
    c.outline(OUTLINE)
    if pose in ("blocked", "done"):
        desks.bubble(c, pose, desks.bubble_x(CX), max(0, hy - 2))
    lit = glow()
    lit.blit(c, 0, 0)
    return lit
