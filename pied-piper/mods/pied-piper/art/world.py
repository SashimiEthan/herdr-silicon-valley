"""The valley around the panels, after the show's opening titles but at night:
the title sky over the sidebar (brand), the company skyline that carries it on
across the top (band_back, band_front), and Pied Piper's sign. (What is behind
the terminals is in hat.py.)"""
import math
from px import Canvas, dark, light, mix, noise, rgb, text_width

SKY_TOP, SKY_LOW = "#070b16", "#1b2a4a"
SHOW_RED = "#e8372f"     # the show's logo
GREEN = "#4fc45f"
HILL = "#0c1322"

# The title's letters, drawn with 2px strokes and shown twice the size. As in
# the show's logo the two words run together as small capitals, 9 rows tall,
# each behind an initial that is a little taller: 10 rows and a half. (On the
# poster the initials stand 19% over the others, 0.6 of a stroke. Two rows more
# was 22% and a whole stroke, too tall; one row was 11% and half a stroke, too
# short; a row and a half is 17% and three quarters of a stroke.) The half is
# one row of each initial drawn three pixels deep at the final size, not two.
TITLE = {
    "I": ["##", "##", "##", "##", "##", "##", "##", "##", "##"],
    "L": ["##....", "##....", "##....", "##....", "##....", "##....", "##....", "######", "######"],
    "C": [".####.", "######", "##..##", "##....", "##....", "##....", "##..##", "######", ".####."],
    "O": [".#####.", "#######", "##...##", "##...##", "##...##", "##...##", "##...##", "#######", ".#####."],
    "N": ["##...##", "###..##", "###..##", "####.##", "##.####", "##..###", "##..###", "##...##", "##...##"],
    "A": [".####.", "######", "##..##", "##..##", "######", "######", "##..##", "##..##", "##..##"],
    "E": ["######", "######", "##....", "#####.", "#####.", "##....", "##....", "######", "######"],
    "Y": ["##..##", "##..##", "##..##", "######", ".####.", "..##..", "..##..", "..##..", "..##.."],
}
INITIALS = {
    "S": [".#####.", "#######", "##...##", "##.....", "######.", ".######", ".....##", "##...##", "#######", ".#####."],
    "V": ["##.....##", "##.....##", "##.....##", ".##...##.", ".##...##.", ".##...##.", "..##.##..", "..##.##..", "...###...",
          "...###..."],
}
DEEP = {"S": 6, "V": 6}  # that row
TITLE_H = 21             # the initials' height at the final size
KERN = {"VA": -1}        # the A tucks in under the V's arm


def title(s="SILICON VALLEY", color=SHOW_RED):
    """The show's name as a game's title: red block letters, lit from above."""
    glyphs, x, prev = [], 0, " "
    for word in s.split():
        for i, ch in enumerate(word):
            g = INITIALS[ch] if i == 0 else TITLE[ch]
            x += KERN.get(prev + ch, 0) + (1 if i == 0 and glyphs else 0)      # a little more air before a word
            glyphs.append((x, g, DEEP[ch] if i == 0 else None))
            x += len(g[0]) + 1
            prev = ch
    w = x - 1
    # Twice the size, all on one baseline, then finished at the art's own pixel size.
    big = Canvas(w * 2 + 4, TITLE_H + 5)
    for gx, g, deep in glyphs:
        y = 1 + TITLE_H - len(g) * 2 - (deep is not None)
        for j, row in enumerate(g):
            d = 3 if j == deep else 2
            for i, bit in enumerate(row):
                if bit == "#":
                    big.rect(2 + (gx + i) * 2, y, 2, d, color)
            y += d
    src = big.im.copy().load()
    hi, lo = light(color, 0.35), dark(color, 0.3)
    for y in range(big.h):
        for xx in range(big.w):
            if not src[xx, y][3]:
                continue
            if not src[xx, y - 1][3]:
                big.p(xx, y, hi)
            elif y + 1 < big.h and not src[xx, y + 1][3]:
                big.p(xx, y, lo)
    # A drop shadow, then the outline.
    out = Canvas(big.w, big.h)
    for y in range(big.h):
        for xx in range(big.w):
            if big.get(xx, y)[3] and y + 2 < big.h:
                out.p(xx + 1, y + 2, "#5a1216")
    out.blit(big, 0, 0)
    out.outline("#12060a")
    return out


STARS = 135     # one star to this many pixels of sky
TAB_STARS = 190 # and fewer still over the skyline, where the tabs are


def sky(c, y0=0, rows=None, seed=1, stars=True, every=STARS):
    """Night sky into c: canvas row 0 is world row y0 of a 56-row sky."""
    rows = rows or c.h
    bayer = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
    bands = [SKY_TOP, "#0a1020", "#0e162b", "#131d38", SKY_LOW, "#263257"]
    for y in range(rows):
        t = (y + y0) / 56 * (len(bands) - 1)
        i = min(len(bands) - 2, int(t))
        f = t - i
        for x in range(c.w):
            c.p(x, y, bands[i + 1] if f * 16 > bayer[(y + y0) % 4][x % 4] else bands[i])
    if stars:
        for i in range(c.w * rows // every):
            x = int(noise(i, seed) * c.w)
            y = int(noise(i, seed + 3) ** 1.5 * rows)
            c.p(x, y, ["#5f7199", "#9fb4d8", "#e8eefc"][int(noise(i, seed + 7) * 3)])


def palm(c, x, base, h=12):
    for i in range(h):
        c.p(x + (1 if i > h * 2 // 3 else 0), base - i, "#3a2c20")
    top = base - h
    fr = "#1f4a2c"
    for dx, dy in [(-1, 0), (-2, 0), (-3, 1), (-4, 2), (1, 0), (2, 0), (3, 1), (4, 2), (-1, -1), (-2, -2), (1, -1), (2, -2), (0, -1),
                   (-3, -1), (3, -1), (-4, 0), (4, 0)]:
        c.p(x + dx, top + dy, fr)
    c.p(x, top, "#2f6b3a")


def building(c, x, base, w, h, body="#0d1524", lit="#f2c94c", seed=0, density=0.5):
    c.rect(x, base - h + 1, w, h, body)
    c.hl(x, base - h + 1, w, light(body, 0.12))
    for wy in range(base - h + 3, base, 2):
        for wx in range(x + 1, x + w - 1, 2):
            if noise(wx, wy, seed) < density:
                c.p(wx, wy, lit if noise(wx, wy, seed + 2) > 0.25 else "#8fb7ff")


def rooftop_sign(c, x, base, s, color, pole=True, bg="#0a0f1a"):
    w = text_width(s) + 4
    c.rect(x, base - 8, w, 9, bg)
    c.box(x, base - 8, w, 9, dark(color, 0.45))
    c.text(x + 2, base - 6, s, color)
    if pole:
        c.vl(x + 2, base + 1, 2, "#2a3348")
        c.vl(x + w - 3, base + 1, 2, "#2a3348")
    return w


def hostel(c, x, base):
    """The Hacker Hostel from the street: 5230 Newell Road."""
    wall, roof, trim = "#3a3026", "#241c18", "#5a4a38"
    c.rect(x, base - 9, 44, 10, wall)
    for i in range(6):
        c.hl(x - 2 + i, base - 10 - i, 48 - i * 2, roof)
    c.hl(x - 2, base - 10, 48, light(roof, 0.15))
    c.rect(x + 34, base - 17, 3, 5, "#4a3a30")
    # Lit windows: somebody is always up.
    for wx in (x + 4, x + 13):
        c.rect(wx, base - 7, 6, 5, "#f2c94c")
        c.vl(wx + 3, base - 7, 5, trim)
        c.hl(wx, base - 5, 6, trim)
    c.rect(x + 22, base - 7, 4, 8, "#5a3a20")
    c.p(x + 25, base - 3, "#d9b36a")
    c.rect(x + 29, base - 7, 13, 8, "#4a4e55")
    for yy in (base - 5, base - 3, base - 1):
        c.hl(x + 29, yy, 13, "#3a3e45")
    c.rect(x + 16, base - 14, 5, 4, GREEN)
    c.p(x + 18, base - 12, "#f4f1ea")
    # A dish, for PiperNet.
    c.p(x + 6, base - 14, "#aab4bb"); c.hl(x + 5, base - 13, 3, "#aab4bb"); c.p(x + 6, base - 12, "#59606a")


def suv(c, x, base):
    car = "#2c3440"
    c.rect(x, base - 4, 18, 4, car)
    c.rect(x + 3, base - 7, 11, 3, car)
    c.rect(x + 4, base - 6, 4, 2, "#16202c"); c.rect(x + 9, base - 6, 4, 2, "#16202c")
    c.hl(x + 4, base - 3, 9, "#e5533d")
    c.rect(x + 2, base - 1, 4, 2, "#0b0c0e"); c.rect(x + 12, base - 1, 4, 2, "#0b0c0e")
    c.p(x + 17, base - 3, "#f2c94c")


def brand(w=240, h=56):
    """The sidebar's top: the title over the valley at night."""
    c = Canvas(w, h)
    sky(c, seed=5)
    # The moon.
    for a in range(0, 360, 4):
        for r in range(5):
            c.p(228 + round(r * math.cos(math.radians(a))), 26 + round(r * math.sin(math.radians(a))), "#f3edc8")
    for (x, y) in [(226, 24), (229, 27), (227, 28), (230, 24)]:
        c.p(x, y, "#d9d2a8")
    # Hills.
    for x in range(w):
        y = 40 + round(3 * math.sin(x / 23) + 2 * math.sin(x / 9 + 1))
        c.vl(x, y, h - y, "#0c1322")
    # The PiperNet tower on the ridge.
    c.vl(214, 34, 9, "#2a3348")
    c.line(212, 42, 214, 36, "#2a3348"); c.line(216, 42, 214, 36, "#2a3348")
    c.p(214, 33, "#e5533d")
    # Hooli, across the valley.
    building(c, 6, h - 5, 16, 13, "#101b30", "#8fb7ff", 3, 0.6)
    building(c, 23, h - 5, 22, 9, "#101b30", "#8fb7ff", 4, 0.6)
    c.text(8, h - 24, "HOOLI", "#8fb7ff")
    building(c, 150, h - 5, 12, 10, "#131a2a", "#f2c94c", 8, 0.4)
    building(c, 164, h - 5, 9, 14, "#131a2a", "#f2c94c", 9, 0.4)
    # The street.
    c.rect(0, h - 5, w, 5, "#16241b")
    c.hl(0, h - 5, w, "#2f5a38")
    for x in range(0, w, 3):
        if noise(x, 5) > 0.5:
            c.p(x, h - 6, "#2f5a38")
    c.rect(0, h - 2, w, 2, "#1d2126")
    for x in range(4, w, 12):
        c.hl(x, h - 2, 5, "#4a4e55")
    palm(c, 58, h - 5, 15)
    palm(c, 136, h - 5, 12)
    hostel(c, 72, h - 5)
    suv(c, 118, h - 3)
    t = title()
    c.blit(t, (w - t.w) // 2, 5)
    # The condor's nest, and the egg.
    c.vl(190, h - 19, 14, "#3a2c20")
    c.hl(187, h - 20, 7, "#5a4632")
    c.p(189, h - 21, "#f1ece2"); c.p(190, h - 21, "#f1ece2")
    c.grid(192, h - 26, ["..##", ".###", "####", ".##.", ".#.."], {"#": "#17161c"})
    c.p(193, h - 26, "#e8e4da")
    return c


# Pied Piper's sign, for the home folder's space; every other space shows its initial.
COMPANIES = {
    "piedpiper": (["gggggggggggg", "gggggggggggg", "gggwwwwggggg", "gggwggwggggg", "gggwwwwggggg", "gggwgggwwwwg", "gggwgggwggwg",
                   "gggwgggwwwwg", "gggggggwgggg", "gggggggwgggg", "gggggggggggg", "gggggggggggg"], {"g": "#2e8b3d", "w": "#f4f1ea"}),
}


def company(name):
    rows, pal = COMPANIES[name]
    c = Canvas(12, 12)
    c.grid(0, 0, rows, pal)
    return c


def son_of_anton():
    """A sub-agent: a small server somebody's agent started."""
    c = Canvas(9, 7)
    c.rect(0, 0, 9, 7, "#23262c")
    c.box(0, 0, 9, 7, "#4a505a")
    c.hl(2, 2, 5, "#15171b")
    c.hl(2, 4, 5, "#15171b")
    c.p(2, 2, GREEN); c.p(2, 4, "#f2c94c")
    return c


# ------------------------------------------------------------------ the band
# Past the title, the valley as the opening titles map it: one company after
# another, each under its name. Names are plain pixel letters, not logos.
def letters(c, x, y, s, colors, glow=True):
    """Sign letters in one color or one per letter, softly lit. Returns the end."""
    if isinstance(colors, str):
        colors = [colors] * len(s)
    if glow:
        halo = (*mix(colors[0], "#000000", 0.25)[:3], 44)
        for xx in range(x - 1, x + text_width(s) + 1):
            for yy in range(y - 1, y + 6):
                c.p(xx, yy, halo)
    for ch, col in zip(s, colors):
        x = c.text(x, y, ch, col)
    return x


def block(c, x, base, w, h, body, lit="#f2c94c", seed=0, density=0.45, step=(3, 3)):
    """A building at night: its body, a roof line, some windows still lit."""
    top = base - h + 1
    c.rect(x, top, w, h, body)
    c.hl(x, top, w, light(body, 0.22))
    c.vl(x + w - 1, top + 1, h - 1, dark(body, 0.25))
    for wy in range(top + 2, base - 1, step[1]):
        for wx in range(x + 2, x + w - 2, step[0]):
            if noise(wx, wy, seed) < density:
                c.p(wx, wy, lit)
    return top


def sign_on(c, x, w, top, s, colors, lift=7):
    """A name standing on a roof, centered over a building x..x+w."""
    sx = x + (w - text_width(s)) // 2
    letters(c, sx, top - lift, s, colors)
    c.p(sx + 1, top - 1, "#2a3348")
    c.p(sx + text_width(s) - 2, top - 1, "#2a3348")


def lot_google(c, x, b):
    top = block(c, x, b, 46, 12, "#1f2937", "#9fd0ff", 3, 0.55)
    c.rect(x + 19, b - 6, 9, 6, "#27506b"); c.vl(x + 23, b - 6, 6, "#1f2937")
    sign_on(c, x, 46, top, "GOOGLE", ["#4f8cf7", "#ea5a4f", "#f7c443", "#4f8cf7", GREEN, "#ea5a4f"])
    # The lawn statue, and the bikes.
    c.grid(x + 3, b - 6, [".g.g.", "ggggg", "gkgkg", "ggggg", "ggggg", ".g.g."], {"g": "#78c257", "k": "#15171b"})
    for i, col in enumerate(("#f7c443", "#4f8cf7", "#ea5a4f")):
        c.p(x + 33 + i * 4, b - 1, col); c.p(x + 34 + i * 4, b - 2, col); c.p(x + 35 + i * 4, b - 1, col)
    return 46


def lot_facebook(c, x, b):
    top = block(c, x + 10, b, 34, 13, "#1a2c52", "#bcd0ff", 5, 0.5)
    letters(c, x + 12, top + 2, "FACEBOOK", "#f4f1ea")
    # The sign at the gate.
    c.vl(x + 4, b - 4, 4, "#59606a")
    c.rect(x, b - 13, 9, 9, "#2f6fd0"); c.box(x, b - 13, 9, 9, "#bcd0ff")
    c.grid(x + 2, b - 11, ["..#..", "..#..", ".####", "#####", ".####"], {"#": "#f4f1ea"})
    return 44


# Its logo, big enough to read: the leaf, the dip between the two lobes at the
# top, the bite out of the right side, the two bumps at the bottom.
APPLE_LOGO = [
    ".....##..",
    "....##...",
    ".###.###.",
    "#########",
    "########.",
    "#######..",
    "#######..",
    "########.",
    "#########",
    ".#######.",
    "..##.##..",
]


def lot_apple(c, x, b):
    """One of its stores: a glass box with the logo lit on its front, as the
    real ones have, and the name on the roof like everybody else's."""
    w, h = 32, 15
    top = b - h + 1
    c.rect(x, top, w, h, "#2f343c")
    c.hl(x - 1, top - 1, w + 2, "#c9ced3")
    c.rect(x + 1, top + 1, w - 2, h - 1, "#2c4a5c")              # the glass
    c.hl(x + 1, top + 1, w - 2, "#8fb4c6")
    for i in (x + 7, x + w - 8):
        c.vl(i, top + 1, h - 1, "#2f343c")
    lx, ly = x + (w - 9) // 2, top + 2
    halo = (*rgb("#bfe3f2")[:3], 40)
    for xx in range(lx - 2, lx + 11):
        for yy in range(ly - 1, ly + len(APPLE_LOGO) + 1):
            c.p(xx, yy, halo)
    c.grid(lx, ly, APPLE_LOGO, {"#": "#f4f1ea"})
    sign_on(c, x, w, top - 1, "APPLE", "#f4f1ea")
    return w


def lot_raviga(c, x, b):
    top = block(c, x, b, 28, 15, "#262a33", "#f2c94c", 7, 0.3)
    sign_on(c, x, 28, top, "RAVIGA", "#c9ced3")
    return 28


def lot_oracle(c, x, b):
    for i, (dx, h) in enumerate(((0, 17), (11, 21), (22, 15))):
        top = b - h + 1
        c.rect(x + dx, top + 1, 10, h - 1, "#14505c")
        c.hl(x + dx + 1, top, 8, "#2a8a9a")
        for yy in range(top + 3, b, 3):
            c.hl(x + dx, yy, 10, "#1f7080")
        c.vl(x + dx + 9, top + 1, h - 1, "#0e3a44")
        c.vl(x + dx + 2, top + 1, h - 1, "#2a8a9a")
    c.rect(x + 3, b - 7, 27, 7, "#0f1319"); c.box(x + 3, b - 7, 27, 7, "#3a1418")
    c.text(x + 5, b - 6, "ORACLE", "#f2463a")
    return 33


def lot_hp(c, x, b):
    # The garage it started in.
    c.rect(x, b - 7, 16, 8, "#33423a")
    for i in range(5):
        c.hl(x - 1 + i * 2, b - 8 - i, 18 - i * 4, "#22302a")
    c.rect(x + 3, b - 5, 10, 6, "#4a5a50")
    for yy in (b - 4, b - 2):
        c.hl(x + 3, yy, 10, "#33423a")
    c.rect(x + 18, b - 9, 9, 7, "#0f1319"); c.vl(x + 22, b - 2, 3, "#59606a")
    c.text(x + 19, b - 8, "HP", "#8fb7ff")
    return 28


def lot_intel(c, x, b):
    """The Robert Noyce Building: blue glass in bands, a lower wing beside it."""
    mw, mh, ww, wh = 24, 15, 12, 9
    top, wing = b - mh + 1, b - wh + 1
    for bx, by, bw, bh, body in ((x, top, mw, mh, "#16345c"), (x + mw, wing, ww, wh, "#12294a")):
        c.rect(bx, by, bw, bh, body)
        for yy in range(by + 2, b - 1, 3):                       # ribbon windows
            c.rect(bx + 1, yy, bw - 2, 2, "#2a5f9a")
            for wx in range(bx + 1, bx + bw - 2, 3):
                if noise(wx, yy, 9) < 0.35:
                    c.rect(wx, yy, 2, 2, "#9fd0ff")
        c.hl(bx, by, bw, "#5fb0ff")
        c.vl(bx + bw - 1, by + 1, bh - 1, dark(body, 0.3))
    c.rect(x + 3, top - 2, 6, 2, "#1f4576")
    sign_on(c, x, mw, top, "INTEL", "#5fb0ff")
    return mw + ww


def lot_yahoo(c, x, b):
    top = block(c, x, b, 28, 14, "#2e1c44", "#d9b8ff", 11, 0.4)
    sign_on(c, x, 28, top, "YAHOO!", "#b48cff")
    return 28


def lot_endframe(c, x, b):
    top = block(c, x, b, 36, 13, "#101319", "#6fe0ff", 13, 0.25)
    sign_on(c, x, 36, top, "ENDFRAME", "#6fe0ff")
    return 36


def lot_netscape(c, x, b):
    # Still standing, mostly.
    top = block(c, x, b, 38, 12, "#1b1e24", "#59606a", 15, 0.12)
    sx = x + 3
    for i, ch in enumerate("NETSC PE"):
        col = "#59606a" if i % 3 else "#3a3e47"
        sx = c.text(sx, top - 7 + (1 if i == 2 else 0), ch, col)
    c.text(x + 21, top - 4, "A", "#3a3e47")
    c.rect(x + 8, b - 7, 22, 6, "#d9d4c8")
    c.text(x + 9, b - 6, "LEASE", "#b3262c")
    return 38


def lot_ebay(c, x, b):
    top = block(c, x, b, 22, 11, "#262a30", "#f2c94c", 17, 0.4)
    sign_on(c, x, 22, top, "EBAY", ["#ea5a4f", "#4f8cf7", "#f7c443", GREEN])
    return 22


def lot_twitter(c, x, b):
    """The old furniture mart on Market Street: stone piers, stepping up in the
    middle to a tower, the name over the doors."""
    w, h = 34, 14
    top = b - h + 1
    stone, pier, dim = "#5e5142", "#84745f", "#231f1b"
    c.rect(x, top, w, h, stone)
    c.rect(x + 9, top - 3, 16, 3, stone)
    c.rect(x + 12, top - 6, 10, 3, stone)
    for (lx, ly, lw) in ((x, top, w), (x + 9, top - 3, 16), (x + 12, top - 6, 10)):
        c.hl(lx, ly, lw, pier)
    c.vl(x + 16, top - 8, 2, pier); c.vl(x + 17, top - 8, 2, pier)       # the flagpole's base
    for wx in range(x + 2, x + w - 1, 3):
        y0 = top - 5 if x + 12 < wx < x + 21 else top - 2 if x + 9 < wx < x + 24 else top + 2
        for wy in range(y0, b - 7, 2):
            c.p(wx, wy, "#f2d9a0" if noise(wx, wy, 19) < 0.4 else dim)
    c.vl(x + w - 1, top + 1, h - 1, dark(stone, 0.3))
    c.rect(x + 2, b - 6, w - 4, 7, "#0e1d27")                    # the marquee
    c.box(x + 2, b - 6, w - 4, 7, "#1f4a63")
    c.text(x + (w - text_width("TWITTER")) // 2, b - 5, "TWITTER", "#5fc0f7")
    return w


def lot_aviato(c, x, b):
    # A billboard he paid for himself.
    c.vl(x + 5, b - 6, 7, "#59606a"); c.vl(x + 24, b - 6, 7, "#59606a")
    c.rect(x, b - 16, 30, 10, "#f4f1ea"); c.box(x, b - 16, 30, 10, "#8d959b")
    c.text(x + 4, b - 13, "AVIATO", "#e5533d")
    c.p(x + 3, b - 17, "#f2c94c"); c.p(x + 15, b - 17, "#f2c94c"); c.p(x + 26, b - 17, "#f2c94c")
    return 30


def lot_netflix(c, x, b):
    """Los Gatos: stucco and red tile, arches along the front, a bell tower."""
    w = 38
    top = b - 8 + 1                                             # the hall's eave
    stucco, tile, ridge = "#75624b", "#8a3626", "#b5503a"
    c.rect(x + 7, top, w - 7, 8, stucco)
    for i, (dx, cut) in enumerate(((6, 0), (8, 4), (10, 8))):    # the hall's tile roof
        c.hl(x + dx, top - 1 - i, w - dx - cut // 2, ridge if i == 2 else tile)
    for wx in range(x + 10, x + w - 3, 5):                       # the arcade
        c.rect(wx, b - 4, 3, 5, "#f2c98a")
        c.p(wx, b - 4, stucco); c.p(wx + 2, b - 4, stucco)
    c.vl(x + w - 1, top, 8, dark(stucco, 0.3))
    c.rect(x, b - 13, 7, 14, stucco)                             # the tower
    c.vl(x + 6, b - 13, 14, dark(stucco, 0.25))
    c.hl(x - 1, b - 14, 9, tile); c.hl(x + 1, b - 15, 5, tile); c.hl(x + 2, b - 16, 3, ridge)
    c.rect(x + 2, b - 11, 3, 3, "#17120f"); c.p(x + 2, b - 11, stucco); c.p(x + 4, b - 11, stucco)
    sign_on(c, x + 8, w - 9, top - 3, "NETFLIX", "#f2463a")
    return w


def lot_tesla(c, x, b):
    c.rect(x, b - 9, 30, 10, "#2f343c"); c.hl(x - 1, b - 10, 32, "#c9ced3")
    c.rect(x + 2, b - 7, 26, 7, "#27506b"); c.hl(x + 2, b - 7, 26, "#bfe3f2")
    c.grid(x + 8, b - 3, ["..#####...", ".#######..", "##########", ".o.....o.."], {"#": "#d93a34", "o": "#0b0c0e"})
    letters(c, x + 5, b - 18, "TESLA", "#f2463a")
    for i in (33, 37):
        c.rect(x + i, b - 6, 2, 7, "#f4f1ea"); c.hl(x + i, b - 6, 2, "#d93a34")
    return 40


def lot_amazon(c, x, b):
    top = block(c, x, b, 36, 11, "#2b241a", "#f2c94c", 23, 0.2)
    for i in range(x + 3, x + 33, 8):
        c.rect(i, b - 5, 5, 5, "#3d3324"); c.hl(i, b - 5, 5, "#59606a")
    sign_on(c, x, 36, top, "AMAZON", "#ff9d2e")
    # One of its drones, with somebody's order.
    dx, dy = x + 14, top - 17
    c.hl(dx, dy, 9, "#aab4bb"); c.rect(dx + 3, dy + 1, 3, 2, "#59606a")
    c.p(dx, dy - 1, "#e8eefc"); c.p(dx + 8, dy - 1, "#e8eefc"); c.p(dx + 4, dy + 3, "#59606a")
    c.rect(dx + 3, dy + 4, 3, 3, "#a9814f"); c.p(dx + 1, dy + 1, "#e5533d")
    return 36


def sign_mark(c, x, w, top, mark, pal, s, colors, lift=7):
    """A name standing on a roof with the company's mark before it, both lit
    as one sign, centered over a building x..x+w."""
    mw = len(mark[0])
    total = mw + 2 + text_width(s)
    sx = x + (w - total) // 2
    first = colors if isinstance(colors, str) else colors[0]
    halo = (*mix(first, "#000000", 0.25)[:3], 44)
    for xx in range(sx - 1, sx + total + 1):
        for yy in range(top - lift - 1, top - lift + 6):
            c.p(xx, yy, halo)
    c.grid(sx, top - lift + (5 - len(mark)) // 2, mark, pal)
    letters(c, sx + mw + 2, top - lift, s, colors, glow=False)
    for yy in range(top - lift + 6, top):      # its posts, from under the name down to the roof
        c.p(sx + 1, yy, "#2a3348")
        c.p(sx + total - 2, yy, "#2a3348")


def lot_microsoft(c, x, b):
    # Its valley campus: low and wide under a planted roof, and the four squares.
    top = block(c, x, b, 46, 12, "#1f2a3a", "#9fd0ff", 71, 0.5)
    c.hl(x, top, 46, "#4f8a4a")
    for i in range(x + 2, x + 45, 5):
        c.p(i, top - 1, "#3f7a40")
    sign_mark(c, x, 46, top, ["rr.gg", "rr.gg", ".....", "bb.yy", "bb.yy"],
              {"r": "#f25022", "g": "#7fba00", "b": "#00a4ef", "y": "#ffb900"}, "MICROSOFT", "#e8eefc")
    return 46


def lot_nvidia(c, x, b):
    """Its headquarters in Santa Clara: low and wide under one white roof that
    slopes away, the walls and the roof all triangles."""
    w = 42
    body = "#121712"

    def roof(i):
        return b - (13 - (i * 6) // w) + 1          # the roof's row over column i: high on the left

    for i in range(w):
        top = roof(i)
        c.vl(x + i, top + 1, b - top, body)
        c.p(x + i, top, "#d9dde2")
        # The triangles: a zigzag under the eave, another through the glass.
        z = (0, 1, 2, 1)[i % 4]
        c.p(x + i, top + 2 + z, "#76b900")
        if top + 6 + z < b - 1:
            c.p(x + i, top + 6 + z, "#2c3a2c")
    c.vl(x, roof(0), b - roof(0) + 1, "#2a322a")
    c.vl(x + w - 1, roof(w - 1), b - roof(w - 1) + 1, "#0a0d0a")
    c.rect(x + 17, b - 3, 7, 4, "#cfe89a")                       # the doors, lit
    c.vl(x + 20, b - 3, 4, "#76b900")
    sign_mark(c, x, w, roof(0), [".ggg.", "gwwwg", "gwgwg", "gwwwg", ".ggg."], {"g": "#76b900", "w": "#f4f1ea"}, "NVIDIA", "#f4f1ea")
    return w


# OpenAI's knot, as small as it still looks like one: the hexagon in the
# middle, and round it two strands that each start at the rim and curl in to
# it, so the rim is not a plain ring (a ring with a dot read as a life saver).
# The real one has six strands and lines a seventeenth of its width; drawn
# truly it needs ten cells, twice the name's height, which was far too big.
OPENAI_LOGO = [
    "..##...",
    ".#..##.",
    "#.##..#",
    "#.#.#.#",
    "#..##.#",
    ".##..#.",
    "...##..",
]


def lot_openai(c, x, b):
    """The Pioneer Building in the Mission: old brick, rows of tall windows, a
    low parapet in the middle, wide doors at the street."""
    w, h = 34, 14
    top = b - h + 1
    brick, course, stone = "#4a2a22", "#3c211b", "#8a6a58"
    c.rect(x, top, w, h, brick)
    for yy in range(top + 1, b, 2):
        c.hl(x, yy, w, course)
    c.hl(x, top, w, stone)
    c.rect(x + w // 2 - 5, top - 1, 10, 1, stone)
    c.vl(x + w - 1, top + 1, h - 1, dark(brick, 0.3))
    for wy in (top + 2, top + 6):
        for wx in range(x + 2, x + w - 3, 4):
            c.rect(wx, wy, 2, 3, "#f2e2c0" if noise(wx, wy, 75) < 0.45 else "#17110f")
            c.hl(wx, wy + 3, 2, stone)
    for wx in range(x + 2, x + w - 5, 8):
        c.rect(wx, b - 3, 5, 4, "#120d0b")
        c.hl(wx, b - 3, 5, stone)
    sign_mark(c, x, w, top - 1, OPENAI_LOGO, {"#": "#f4f1ea"}, "OPENAI", "#f4f1ea")
    return w


def lot_anthropic(c, x, b):
    """Its building south of Market: ten floors of glass in a concrete grid,
    the name across the top on ivory, the spark before it."""
    w, h = 46, 18
    top = b - h + 1
    body, pier = "#2b2420", "#463b32"
    c.rect(x, top, w, h, body)
    c.rect(x + 17, top - 2, 13, 2, "#3a3028")                    # the plant on the roof
    c.rect(x, top, w, 7, "#dcd2c0")
    c.hl(x, top, w, "#f0e6d6"); c.hl(x, top + 6, w, "#a89c88")
    c.grid(x + 2, top + 1, ["#.#.#", ".###.", "#####", ".###.", "#.#.#"], {"#": "#d97757"})
    c.text(x + 9, top + 1, "ANTHROPIC", "#191817")
    for wy in range(top + 8, b - 2, 3):
        for wx in range(x + 1, x + w - 3, 4):
            c.rect(wx, wy, 3, 2, "#f0b98a" if noise(wx, wy, 77) < 0.5 else "#17120f")
    for wx in range(x, x + w, 4):
        c.vl(wx, top + 7, h - 7, pier)
    c.vl(x + w - 1, top + 7, h - 7, dark(body, 0.3))
    c.rect(x + w // 2 - 3, b - 2, 6, 3, "#f0b98a")               # the lobby
    return w


def simple_lot(name, colors, w, h, body, lit="#f2c94c", seed=0, density=0.4):
    def lot(c, x, b):
        top = block(c, x, b, w, h, body, lit, seed, density)
        sign_on(c, x, w, top, name, colors)
        return w
    return lot


def gap(c, x, b):
    """A stretch of road with nothing on it but a palm: where the drive starts over."""
    palm(c, x + 8, b, 11)
    return 16


# Left to right is the drive down the Peninsula, San Francisco to Los Gatos:
# neighbors here are neighbors there. It is driven twice. First the companies
# in the show's titles and the ones the valley turns on now, which is what a
# window of ordinary width shows; then, past a gap, the rest, north to south
# again. Last, for a very wide window, the companies that only exist in the
# show, which are nowhere.
LOTS = [
    # San Francisco: SoMa, Market Street, the Mission.
    lot_anthropic, lot_twitter, lot_openai,
    # Redwood Shores, Menlo Park.
    lot_oracle, lot_facebook,
    # Palo Alto: the garage on Addison Avenue, then Deer Creek Road.
    lot_hp, lot_tesla,
    # Mountain View.
    lot_google, lot_microsoft,
    # Santa Clara, Cupertino, Los Gatos.
    lot_intel, lot_nvidia, lot_apple, lot_netflix,
    gap,
    # San Francisco again.
    simple_lot("UBER", "#f4f1ea", 22, 16, "#101216", "#c9ced3", 43, 0.3),
    simple_lot("ZYNGA", "#f2463a", 26, 12, "#2a1518", "#ffb0a8", 55),
    simple_lot("AIRBNB", "#ff7a85", 30, 12, "#2c1a1f", "#ffc0c6", 45),
    simple_lot("DROPBOX", "#5fa0ff", 34, 14, "#12264a", "#bcd0ff", 47),
    # San Bruno, San Mateo.
    simple_lot("YOUTUBE", "#f2463a", 34, 14, "#2a1518", "#ffb0a8", 37),
    simple_lot("ALIBABA", "#ff9d2e", 34, 15, "#2b2014", "#f2c94c", 51),
    # Palo Alto, Mountain View: AOL beside the company it bought.
    simple_lot("AOL", "#59606a", 18, 9, "#1b1e24", "#59606a", 53, 0.1),
    lot_netscape,
    # Sunnyvale.
    simple_lot("LINKEDIN", "#5fa0e8", 36, 15, "#12284a", "#bcd0ff", 31),
    lot_yahoo, lot_amazon,
    # San Jose: North First Street, downtown, Hamilton Avenue.
    simple_lot("PAYPAL", "#5fb0ff", 30, 12, "#14264a", "#bcd0ff", 35),
    simple_lot("ADOBE", "#f2463a", 26, 18, "#2a1215", "#ffb0a8", 41),
    lot_ebay,
    gap,
    lot_raviga, lot_endframe, lot_aviato,
    simple_lot("BREAM-HALL", "#c9ced3", 44, 13, "#24222c", "#f2c94c", 33, 0.3),
    simple_lot("SLICELINE", "#f08f3c", 40, 10, "#2b1c14", "#f2c94c", 39, 0.3),
    simple_lot("HOMICIDE", "#e5533d", 38, 11, "#15171b", "#e5533d", 49, 0.2),
    simple_lot("NUCLEUS", "#8fb7ff", 34, 16, "#1c2533", "#8fb7ff", 57),
    simple_lot("SEEFOOD", "#f2c94c", 34, 11, "#2b2414", "#f2c94c", 59, 0.3),
    simple_lot("EKLOW LABS", "#6fe0ff", 44, 13, "#1d2629", "#6fe0ff", 61, 0.3),
]


def car(c, x, road, body, kind="car"):
    """A car headed right, its wheels on row `road`."""
    if kind == "bus":
        c.rect(x, road - 8, 30, 8, body); c.hl(x, road - 8, 30, light(body, 0.3))
        for i in range(x + 2, x + 27, 4):
            c.rect(i, road - 6, 3, 2, "#16202c")
        c.hl(x, road - 3, 30, "#3f7bd9")
        c.text(x + 6, road - 3, "", body)
        c.rect(x + 3, road - 1, 4, 2, "#0b0c0e"); c.rect(x + 22, road - 1, 4, 2, "#0b0c0e")
        c.p(x + 29, road - 2, "#f2c94c"); c.p(x, road - 2, "#d93a34")
        return
    if kind == "narrow":
        c.rect(x, road - 7, 5, 7, body); c.rect(x + 1, road - 6, 3, 3, "#16202c")
        c.p(x, road, "#0b0c0e"); c.p(x + 4, road, "#0b0c0e"); c.p(x + 4, road - 2, "#f2c94c")
        return
    low = kind == "low"
    c.rect(x, road - 3, 13, 3, body)
    c.rect(x + 3, road - (4 if low else 5), 6, 2 if not low else 1, body)
    if not low:
        c.rect(x + 4, road - 5, 4, 1, "#16202c")
    c.hl(x, road - 3, 13, light(body, 0.2))
    c.rect(x + 1, road - 1, 3, 2, "#0b0c0e"); c.rect(x + 9, road - 1, 3, 2, "#0b0c0e")
    c.p(x + 12, road - 2, "#f2c94c"); c.p(x, road - 2, "#d93a34")
    if kind == "pod":
        c.p(x + 6, road - 6, "#6fe0ff"); c.p(x + 6, road - 7, "#59606a")
    elif kind == "lyft":
        c.rect(x + 11, road - 2, 3, 1, "#f04aa0"); c.p(x + 13, road - 3, "#f04aa0")


def balloon(c, x, y, s, body, fg="#f4f1ea", pad=2):
    w = text_width(s) + 2 * pad
    rim = light(body, 0.35)
    c.rect(x + 2, y, w - 4, 1, rim)
    c.rect(x + 1, y + 1, w - 2, 1, body)
    c.rect(x, y + 2, w, 6, body)
    c.rect(x + 1, y + 8, w - 2, 1, body)
    c.rect(x + 3, y + 9, w - 6, 1, body)
    c.p(x + 1, y + 1, rim); c.p(x + w - 2, y + 1, rim)
    c.vl(x, y + 2, 6, rim); c.vl(x + w - 1, y + 2, 6, dark(body, 0.2))
    c.text(x + pad, y + 3, s, fg)
    c.p(x + 4, y + 10, "#8d959b"); c.p(x + w - 5, y + 10, "#8d959b")
    c.p(x + 5, y + 11, "#8d959b"); c.p(x + w - 6, y + 11, "#8d959b")
    c.rect(x + w // 2 - 2, y + 12, 4, 2, "#8a6a3a")


FRONT_Y = 23        # the first row of the band that band_front() keeps


def squashed_pair(c, seam, y):
    """Uber's and Lyft's balloons from the titles, the same size, driven into
    each other and held there: each squeezed narrow and tall, flat where it
    meets the other, round everywhere else."""
    w, h = 19, 12                       # at rest one is 23 x 10
    far = (8, 4, 2, 1, 0, 0, 0, 0, 1, 2, 4, 8)       # how far in each row starts, on the round side:
    near = (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)      # the balloon bulges toward the side they meet
    for side, name, body in ((-1, "UBER", "#101216"), (1, "LYFT", "#f04aa0")):
        rim, shade = light(body, 0.35), dark(body, 0.2)
        x0 = seam - w if side < 0 else seam
        for r in range(h):
            xa, xb = (x0 + far[r], seam - near[r]) if side < 0 else (seam + near[r], x0 + w - far[r])
            c.rect(xa, y + r, xb - xa, 1, body)
        for r in range(4):                                       # lit along the top of the bulge
            xa = x0 + far[r] if side < 0 else seam + near[r]
            xb = (x0 + far[r - 1] if r else seam - near[0]) if side < 0 else (x0 + w - far[r] if not r else seam + near[r] + 0)
            if side < 0:
                c.hl(xa, y + r, max(1, xb - xa), rim)
            else:
                c.hl(x0 + w - (far[r - 1] if r else far[0] + (w - far[0] - near[0])), y + r, max(1, (far[r - 1] if r else w - near[0]) - far[r]), rim)
        c.vl(x0 if side < 0 else x0 + w - 1, y + 4, 4, rim if side < 0 else shade)   # and down the round side
        # Pressed: a crease just inside the flat side.
        c.vl(seam - 2 if side < 0 else seam + 1, y + 3, 6, light(body, 0.18) if side < 0 else dark(body, 0.14))
        c.text(x0 + 2, y + 4, name, "#f4f1ea")
        # The basket, swung away from the other balloon.
        mid = x0 + w // 2 + side
        c.p(mid - 4, y + h, "#8d959b"); c.p(mid + 3, y + h, "#8d959b")
        c.p(mid - 3, y + h + 1, "#8d959b"); c.p(mid + 2, y + h + 1, "#8d959b")
        c.rect(mid - 2, y + h + 2, 4, 2, "#8a6a3a")
    # The knock.
    for (dx, dy) in ((-3, -2), (-1, -3), (0, -3), (2, -2), (-2, h + 1), (1, h + 1)):
        c.p(seam + dx, y + dy, "#f2e9c4")


def band_back(w=1400, h=56):
    """The top of the main side, behind the tabs: the title's sky and hills
    carried on to the right, and what floats over the valley."""
    c = Canvas(w, h)
    sky(c, seed=23, every=TAB_STARS)
    off = 240                      # where the title's picture ends
    for x in range(w):
        g = x + off
        y = 40 + round(3 * math.sin(g / 23) + 2 * math.sin(g / 9 + 1))
        c.vl(x, y, h - y, HILL)
    # Overhead: the ride-share balloons from the titles, colliding, and one
    # company's last.
    squashed_pair(c, 423, 3)
    nx = 322
    c.rect(nx + 2, 6, 30, 1, "#3d424b"); c.rect(nx, 7, 34, 5, "#3d424b"); c.rect(nx + 3, 12, 26, 1, "#3d424b")
    c.rect(nx + 20, 12, 10, 2, "#3d424b"); c.rect(nx + 24, 14, 5, 1, "#3d424b")
    c.text(nx + 3, 7, "NAPSTER", "#6f777d")
    c.line(nx + 26, 15, nx + 30, 30, "#3a3e47")
    return c


def band_front(w=1400, h=56):
    """In front of the tabs' posts: the roofs, the companies one after another
    and the street, on nothing. Only rows FRONT_Y and down, where they are."""
    c = Canvas(w, h)
    off = 240
    # Far roofs, between the hills and the street.
    x, k = 0, 0
    while x < w:
        bw = 6 + int(noise(k, 141) * 12)
        bh = 4 + int(noise(k, 143) * 9)
        building(c, x, h - 5, bw, bh, "#0e1626", "#5f7199", k + 70, 0.18)
        x += bw + int(noise(k, 147) * 6)
        k += 1
    # The street, as under the title.
    c.rect(0, h - 5, w, 5, "#16241b")
    c.hl(0, h - 5, w, "#2f5a38")
    for x in range(w):
        if (x + off) % 3 == 0 and noise(x + off, 5) > 0.5:
            c.p(x, h - 6, "#2f5a38")
    c.rect(0, h - 2, w, 2, "#1d2126")
    for x in range(w):
        if (x + off - 4) % 12 < 5:
            c.p(x, h - 2, "#4a4e55")
    # The companies.
    x = 5
    edges = []
    for lot in LOTS:
        if x > w - 50:
            break
        wide = lot(c, x, h - 5)
        edges.append(x + wide)
        x += wide + 5 + int(noise(x, 151) * 4)
    for i, e in enumerate(edges):
        if i % 4 == 1:
            palm(c, e + 2, h - 5, 9 + i % 3)
    # Traffic: a car with nobody driving, a shuttle, the rest of the cast's rides.
    road = h - 2
    for cx, body, kind in ((36, "#e8e4da", "pod"), (96, "#d93a34", "car"), (240, "#2c3440", "lyft"), (372, "#e8e4da", "bus"),
                           (352, "#9fb4c4", "narrow"), (322, "#ff7a1a", "low"), (441, "#2c3440", "car"), (640, "#e8e4da", "pod"),
                           (760, "#d93a34", "car"), (880, "#e8e4da", "bus"), (1010, "#2c3440", "lyft"), (1160, "#ff7a1a", "low")):
        car(c, cx, road, body, kind)
    assert c.im.crop((0, 0, w, FRONT_Y)).getbbox() is None, "something stands above FRONT_Y"
    return c.crop(0, FRONT_Y, w, h - FRONT_Y)


def band(w=1400, h=56):
    """Both layers as one picture, for the layout's preview."""
    c = band_back(w, h)
    c.blit(band_front(w, h), 0, FRONT_Y)
    return c
