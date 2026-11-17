"""The sidebar's two rooms at night, after the Hacker Hostel as the show built
it: one wall each, papered edge to edge, with a few things hung along its top.

The office is the hostel's main room: terracotta plaster under a white beam.
The room is dark but for its track lights: a spot on the beam over each thing
on the wall, each throwing a pool of light down the plaster. The bedroom is
Richard's, as it is in "Founder Friendly": walls painted a pale blue-gray,
white trim, a blue shag carpet. At night it is darker still, its only light
the lamp by each bunk (beds.py).

`wall(room)` is the whole wall, 240 art pixels wide and taller than a list
gets: its surface, the trim along its top, its light, and what hangs on it.
`floor(room)` is its foot, the baseboard and the floor. The lists' rows are
drawn over both and scroll; they stay put. Each character's own piece of wall
is with their desk (desks.py).
"""
from px import Canvas, dark, light, mix, noise, text_width

W, H = 240, 480
GREEN, RED = "#4fc45f", "#e5533d"
PAPER, FRAME = "#f1ece2", "#8a6a3a"
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

# wall: its paint in this room at night, away from any lamp. dim: how far what
# hangs on it sinks into the wall, 0 to 1 (in the office, where no spot reaches).
# ui.js has the same wall colors, for the folded rail.
ROOMS = {
    "office": dict(wall="#27150c", dim=0.62),
    "bedroom": dict(wall="#0e1622", dim=0.45),
}
# The office wall from unlit to the middle of a spot's pool, in steps.
LIT = "#96592f"
TOP = 6
TONES = [mix(ROOMS["office"]["wall"], LIT, (i / TOP) ** 1.15) for i in range(TOP + 1)]
# White paint (the office's beam, the bedroom's trim) in daylight.
WHITE = "#c9c5ba"
# Where the three things hang along the top of each wall: (left edge, top).
# Spread across the wall past the room's name, not in a row: the gaps and the
# heights differ a little. The office's first hangs highest: a space's name
# runs under it. The bedroom's first starts past the machine's name beside it.
SPOTS = {"office": [(41, 6), (109, 12), (181, 9)], "bedroom": [(65, 9), (124, 12), (172, 6)]}


# ------------------------------------------------------------- the office
def middle_out():
    """The whiteboard that started it."""
    c = Canvas(45, 19)
    c.rect(0, 0, 45, 17, "#dfe3e0")
    c.box(0, 0, 45, 17, "#8d959b")
    c.hl(2, 17, 41, "#6f777d")
    c.rect(4, 16, 2, 1, "#d93a34"); c.rect(7, 16, 2, 1, "#2f6fd0")
    c.text(2, 2, "MIDDLE-OUT", "#2f4f9a")
    for i in range(4):
        c.text(4 + i * 4, 9, ">", RED)
        c.text(38 - i * 4, 9, "<", "#2e8b3d")
    c.vl(22, 9, 5, "#1b1d22")
    return c


def banner():
    """The company, on its own wall."""
    w = text_width("PIED PIPER") + 16
    c = Canvas(w, 11, "#1f6f33")
    c.box(0, 0, w, 11, "#2e8b3d")
    c.rect(2, 2, 7, 7, "#2e8b3d")
    c.text(3, 3, "P", "#f4f1ea")
    c.text(12, 3, "PIED PIPER", "#f4f1ea")
    return c


def check():
    """The novelty check from Disrupt."""
    c = Canvas(61, 14, PAPER)
    c.box(0, 0, 61, 14, FRAME)
    c.text(2, 2, "DISRUPT", "#2e8b3d")
    c.text(32, 2, "$50,000", "#d93a34")
    c.text(2, 8, "PIED PIPER", "#15171b")
    for i, dy in enumerate([1, 0, 1, 2, 1, 0, -1, 1, 2, 1]):
        c.p(46 + i, 10 + dy, "#2f4f9a")
    return c


# ------------------------------------------------------------ the bedroom
def window():
    """The bedroom's window: white painted trim like the door's, the blinds
    half up, and past them the night and the moon that is over the title."""
    c = Canvas(34, 27, WHITE)
    c.rect(2, 2, 30, 22, "#16223f")
    for (x, y) in [(6, 15), (12, 19), (9, 21), (17, 16), (27, 20), (22, 22)]:
        c.p(x, y, "#c9d6f2")
    for (x, y, w) in [(22, 14, 3), (21, 15, 5), (21, 16, 5), (22, 17, 3)]:
        c.hl(x, y, w, "#f3edc8")
    for y in range(2, 13):
        c.hl(2, y, 30, "#d9d5ca" if y % 2 == 0 else "#aaa69a")
    c.vl(16, 2, 22, WHITE)
    c.box(1, 1, 32, 24, dark(WHITE, 0.3))
    c.hl(0, 25, 34, light(WHITE, 0.3)); c.hl(0, 26, 34, dark(WHITE, 0.45))
    return c


def bachmanity():
    """Bachmanity Insanity, the night on the Rock."""
    c = Canvas(45, 15, "#f48fb8")
    c.box(0, 0, 45, 15, "#1f6f8f")
    c.ctext(22, 2, "BACHMANITY", "#f4f1ea")
    c.ctext(22, 8, "INSANITY", "#16324a")
    for px in (4, 40):
        c.vl(px, 8, 5, "#16324a")
        for dx, dy in [(-1, 0), (-2, 1), (1, 0), (2, 1), (0, -1)]:
            c.p(px + dx, 8 + dy, "#16324a")
    return c


def shelf():
    """A shelf of what the house runs on: Tres Comas, Homicide, a cup from Disrupt."""
    c = Canvas(36, 15)
    c.rect(0, 12, 36, 2, "#7a5230"); c.hl(0, 12, 36, "#9a6a40")
    c.p(3, 14, "#5a3a20"); c.p(32, 14, "#5a3a20")
    c.rect(4, 4, 4, 8, "#cfe3ea"); c.rect(5, 1, 2, 3, "#cfe3ea"); c.hl(5, 0, 2, "#d9b36a")     # Tres Comas
    c.rect(4, 7, 4, 3, "#15171b"); c.p(5, 8, "#f4c542"); c.p(6, 8, "#f4c542")
    for x in (12, 16):                                                                          # Homicide
        c.rect(x, 7, 3, 5, "#15171b"); c.hl(x, 7, 3, "#c9cfd3"); c.hl(x, 9, 3, RED)
    c.rect(25, 3, 6, 4, "#f4c542"); c.p(24, 4, "#f4c542"); c.p(31, 4, "#f4c542")               # the cup
    c.rect(27, 7, 2, 3, "#d9b36a"); c.hl(25, 10, 6, "#3a2a1e"); c.hl(25, 11, 6, "#3a2a1e")
    return c


# -------------------------------------------------------------- the walls
LENS_Y = 5                      # a spot's lens, under the beam
POOL = (20, 52, 34, 54)         # its pool on the wall: the widest row, half its width, how far up and down it goes
PEAK = 4.1                      # how lit the middle of one pool is, of TOP


def light_at(x, y, lamps):
    """How lit the office wall is at a pixel, 0 to TOP. Each spot throws a wide,
    soft pool down the plaster; three in a row run together into one wash
    along the top of the wall, a little brighter under each lamp, fading out
    behind the first row. Nothing else lights the room."""
    cy, rx, up, down = POOL
    level = 0.0
    for fx in lamps:
        r2 = ((x - fx) / rx) ** 2 + ((y - cy) / (down if y > cy else up)) ** 2
        if r2 < 1:
            level += PEAK * (1 - r2) ** 1.4
    # A little hotter right at each lens.
    for fx in lamps:
        near = ((x - fx) ** 2 + ((y - LENS_Y) * 1.3) ** 2) ** 0.5
        level = max(level, PEAK + 1.4 - 1.5 * near)
    # Out before the picture's own edge, so a wider sidebar shows no step.
    return min(float(TOP), level) * min(1.0, x / 12.0, (W - 1 - x) / 12.0)


def steps(t, x, y):
    """A light level as a whole step, dithered into the next: no rings."""
    step = int(t)
    if (t - step) * 16 > BAYER[y % 4][x % 4]:
        step += 1
    return min(step, TOP)


def paper(c, room, lamps=()):
    """The wall's own surface in its light, and the trim along its top."""
    r = ROOMS[room]
    wall = r["wall"]
    if room == "office":
        for y in range(c.h):
            for x in range(c.w):
                tone = TONES[steps(light_at(x, y, lamps), x, y)]
                # Painted plaster: two close shades, checkered, a darker fleck here and there.
                c.p(x, y, light(tone, 0.05) if (x + y) % 2 else tone)
                if noise(x, y, 71) > 0.985:
                    c.p(x, y, dark(tone, 0.14))
        # The white beam along the top of the hostel's walls, lit only where a
        # spot hangs from it, and its shadow.
        for x in range(c.w):
            near = max([0.0] + [1 - abs(x - fx) / 34.0 for fx in lamps])
            beam = mix(mix(WHITE, wall, 0.62), mix(WHITE, LIT, 0.3), 0.7 * near ** 1.5)
            c.vl(x, 0, 2, beam)
            c.p(x, 2, dark(beam, 0.22))
        c.hl(0, 3, c.w, dark(wall, 0.45))
        # A spot on the beam over each thing on the wall: its can, its lit lens.
        for fx in lamps:
            c.rect(fx - 2, 2, 5, 3, "#17191e")
            c.hl(fx - 2, 2, 5, "#2c3038")
            c.rect(fx - 1, 5, 3, 1, "#fff3c4")
            c.p(fx - 2, 5, "#e9b96a"); c.p(fx + 2, 5, "#e9b96a")
    else:
        # Painted drywall, the brush just showing: short strokes a touch lighter
        # or darker, a fleck here and there.
        for y in range(c.h):
            for x in range(c.w):
                n = noise((x + 2 * (y % 2)) // 4, y, 73)
                col = light(wall, 0.03) if n > 0.7 else dark(wall, 0.12) if n < 0.22 else wall
                if noise(x, y, 79) > 0.988:
                    col = light(wall, 0.07)
                c.p(x, y, col)
        # White trim along the top, as around the room's door and closet.
        trim = mix(WHITE, wall, 0.74)
        c.rect(0, 0, c.w, 3, trim)
        c.hl(0, 0, c.w, light(trim, 0.1))
        c.hl(0, 2, c.w, dark(trim, 0.25))
        c.hl(0, 3, c.w, dark(wall, 0.5))


def floor(room):
    """The foot of the wall, to lie along the bottom of a list, in this room's
    light: the baseboard, then the office's hardwood or the bedroom's carpet."""
    r = ROOMS[room]
    c = Canvas(W, 8)
    c.hl(0, 0, W, dark(r["wall"], 0.35))
    if room == "office":
        base, board, gap = "#5d574c", "#4a3019", "#321f10"
        c.rect(0, 1, W, 2, base)
        c.hl(0, 2, W, dark(base, 0.2))
        c.rect(0, 3, W, 5, board)
        c.hl(0, 3, W, dark(gap, 0.25))
        for y in (5, 7):
            c.hl(0, y, W, gap)
        for row, y in enumerate((4, 6)):
            for x in range(row * 13, W, 29):
                c.p(x, y, gap)
    else:
        base = mix(WHITE, r["wall"], 0.7)
        c.rect(0, 1, W, 2, base)
        c.hl(0, 2, W, dark(base, 0.25))
        # Blue shag: three close blues, tufted.
        pile = "#17293c"
        for y in range(3, 8):
            for x in range(W):
                n = noise(x, y, 83)
                c.p(x, y, light(pile, 0.1) if n > 0.72 else dark(pile, 0.3) if n < 0.3 else pile)
        c.hl(0, 3, W, dark(pile, 0.45))
    return c


def hang(c, room, piece, x, y, lamps=()):
    """A piece on the wall, in this room's light, a shadow under it."""
    r = ROOMS[room]
    c.rect(x + 1, y + piece.h, piece.w, 1, dark(r["wall"], 0.3))
    for j in range(piece.h):
        for i in range(piece.w):
            p = piece.px[i, j]
            if p[3]:
                # Under a spot it shows as it is; out of the light it sinks into the wall.
                lit = min(1.0, light_at(x + i, y + j, lamps) / 1.8) if lamps else 0.0
                c.p(x + i, y + j, mix(p, r["wall"], r["dim"] * (1 - lit)))


def wall(room):
    """The whole wall. What hangs on it is spread along its top, past the
    room's name."""
    pieces = [banner(), check(), middle_out()] if room == "office" else [bachmanity(), shelf(), window()]
    c = Canvas(W, H)
    lamps = [x + p.w // 2 for (x, _), p in zip(SPOTS[room], pieces)] if room == "office" else []
    paper(c, room, lamps)
    for (x, y), piece in zip(SPOTS[room], pieces):
        hang(c, room, piece, x, y, lamps)
    return c
