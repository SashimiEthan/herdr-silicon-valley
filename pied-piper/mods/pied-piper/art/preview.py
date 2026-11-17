"""The layout's picture for Settings: the window in miniature, built from the
same art, with made-up spaces and agents so it shows nobody's work."""
from px import FONT, Canvas, mix, noise, text_width
import beds
import hat
import cast
import desks
import decor
import world

W, H = 827, 542          # the window at one art pixel per two screen pixels
SIDE = 240
BAR = 14                 # the two bars along the bottom
TEXT, MUTED, DIM = "#e2e8f2", "#9aa7bd", "#64718a"
CHROME, CANVAS, TERM, ACCENT, BORDER = "#0b101b", "#05080f", "#0a0e17", "#4fc45f", "#1e2a44"
MARK = {"work": "#76a8ff", "blocked": "#f2705e", "done": "#a6bd91"}
OWN = {"claude": "#d97757"}   # a tool's own color, on the tabs (OWN in ui.js)
ROOM_DIM = {"office": "#a98672", "bedroom": "#6d7b90"}      # quiet text on each wall, as ROOMS in ui.js

# The tabs' billboards, as tabs.js draws them: unlit, and lit for the shown one.
BOARD = dict(face="#141d30", top="#1b2640", rim="#2c3854", post="#2a3348", lamp="#3a4358")
LIT = dict(face="#e6dfc4", top="#f6f0d8", low="#cfc7a8", rim="#f6f0d8", lamp="#fff6c8", ink="#141b2b")

# character, pose, what they are on, their space when it starts one, its sign's color
# (None: home, Pied Piper's), their priority (the office's numbers), how long ago
OFFICE = [
    ("richard", "work", "MIDDLE-OUT V2", "~", None, 1, "2M"),
    ("gilfoyle", "idle", "REBUILD ANTON", None, None, 2, "7H"),
    ("dinesh", "blocked", "PIPERCHAT COPPA FIX", None, None, 3, "20M"),
]
BEDROOM = [
    ("jared", "idle", "SPRINT RETRO NOTES", "OPS", "#e3814f", None, "51M"),
    ("bighead", "work", "NIP ALERT", "HOOLI XYZ", "#5b8def", None, "9H"),
]
# The office's rows stand clear of its priority numbers (OFFICE_INSET in spaces.js).
INSET = {"office": 11, "bedroom": 0}
ROOM_MUTED = {"office": "#d2b6a4", "bedroom": "#9eabbd"}

# The tools' marks (ui.js toolMark, art/icons.py TOOLS) cut down to this picture's
# scale: a row taller than the 3x5 font, as they are beside text on screen.
# Tinted like the text beside them, but on the tabs Claude Code's is its own
# coral (OWN in ui.js), on a dark board and the lit one.
MINI = {
    "claude": [".#######.", ".#.###.#.", ".#######.", "#########", ".#######.", ".#.#.#.#."],
    "copilot": ["..#####..", ".##.#.##.", ".#######.", "##.....##", "##.#.#.##", "..#####.."],
}


def tool(c, x, y, key, col):
    """`key`'s mark beside text whose top is y; the x after it."""
    for j, line in enumerate(MINI[key]):
        for i, ch in enumerate(line):
            if ch == "#":
                c.p(x + i, y - 1 + j, col)
    return x + len(MINI[key][0])


def by(c, x, y, name, col, key="claude", mark=None):
    """"NAME · mark", as a row's second line and a tab read; the x after it.
    `mark`: the mark's own color, else the text's."""
    x = c.text(x, y, name, col)
    c.p(x + 1, y + 2, col)
    return tool(c, x + 4, y, key, mark or col)


def by_width(name):
    return text_width(name) + 14


def row(c, room, y, pic, name, title, pose, on=False, rank=None, when=""):
    if on:
        for yy in range(y, y + desks.H + 1):
            for xx in range(4, SIDE - 4):
                c.p(xx, yy, mix(c.get(xx, yy), "#ffffff", 0.14))
    left = 7 + INSET[room]
    if rank:
        c.text(8, y + desks.H // 2 - 2, str(rank), ROOM_MUTED[room])
    c.blit(pic, left, y)      # the desk's edge under the sign's
    c.text(left + 69, y + 13, title[:34 - INSET[room] // 4], TEXT)
    by(c, left + 69, y + 21, name.upper(), ROOM_DIM[room])
    if when:
        c.text(SIDE - 19 - text_width(when), y + 16, when, ROOM_DIM[room])
    if pose in MARK:
        c.rect(SIDE - 14, y + 16, 4, 4, MARK[pose])
    else:
        c.box(SIDE - 14, y + 16, 4, 4, ROOM_DIM[room])


def room(c, name, y0, y1, agents, picture, focused=None):
    """A list as its room: one papered wall, the rows over it."""
    c.blit(decor.wall(name).crop(0, 0, SIDE, y1 - y0), 0, y0)
    c.blit(decor.floor(name), 0, y1 - 8)
    c.rect(4, y0 + 3, text_width(name) + 5, 9, "#21130e")
    c.text(7, y0 + 5, name.upper(), MUTED)
    if name == "bedroom":
        c.text(text_width(name) + 13, y0 + 5, "+", MUTED)
    inset = INSET[name]
    y = y0 + 15
    for key, pose, title, space, co, rank, when in agents:
        if y + desks.H > y1:
            break
        if space:
            if co:
                # The space's initial on its color, the letter twice the font's size.
                c.rect(8 + inset, y + 2, 12, 12, co)
                for j, bits in enumerate(FONT[space[0]]):
                    for i, bit in enumerate(bits):
                        if bit == "#":
                            c.rect(11 + inset + i * 2, y + 3 + j * 2, 2, 2, "#ffffff")
            else:
                c.blit(world.company("piedpiper"), 8 + inset, y + 2)
            c.text(24 + inset, y + 6, space, TEXT)
            y += 17
        row(c, name, y, picture(key, pose), key, title, pose, on=(key == focused), rank=rank, when=when)
        y += desks.H + 1


def board(c, x, y, w, lit):
    """A billboard: its lamps, its face, the posts it stands on."""
    b = LIT if lit else BOARD
    for px in (x + 5, x + w - 7):
        c.rect(px, y + 11, 1, 30, BOARD["post"])
    if lit:
        for yy in range(y - 1, y + 12):
            for xx in range(x - 1, x + w + 1):
                c.p(xx, yy, mix(c.get(xx, yy), "#ffd27a", 0.14))
    c.rect(x, y, w, 11, b["face"])
    c.hl(x, y + 1, w, b["top"]); c.hl(x, y + 2, w, b["top"])
    if lit:
        c.hl(x, y + 9, w, b["low"]); c.hl(x, y + 10, w, b["low"])
    c.box(x, y, w, 11, b["rim"] if not lit else "#8d8a78")
    for lx in (x + 5, x + w // 2 - 1, x + w - 7):
        c.rect(lx, y - 2, 2, 1, b["lamp"])
        c.p(lx, y - 1, "#59606a")


def preview():
    c = Canvas(W, H, CANVAS)
    # Sidebar: the title, the office, the bedroom.
    c.rect(0, 0, SIDE, H, CHROME)
    c.blit(world.brand(), 0, 0)
    split = 56 + 15 + 17 + 3 * (desks.H + 1) + 6
    room(c, "office", 56, split, OFFICE, desks.seat, focused="richard")
    c.hl(0, split, SIDE, BORDER)
    room(c, "bedroom", split + 1, H - BAR, BEDROOM, beds.bed)
    c.rect(0, H - BAR, SIDE, BAR, CHROME)
    c.hl(0, H - BAR, SIDE, BORDER)
    c.text(8, H - 9, "SETTINGS", MUTED)
    c.text(52, H - 9, "+ ADD MACHINE", DIM)
    c.vl(SIDE, 0, H, BORDER)
    # The band: the sky, the tabs as billboards on their posts, then the
    # skyline in front of the posts.
    x0 = SIDE + 1
    c.blit(world.band_back().crop(0, 0, W - x0, 56), x0, 0)
    tx = x0 + 6
    for i, key in enumerate(("richard", "gilfoyle", "dinesh")):
        label = key.upper()
        tw = 14 + by_width(label) + 6
        board(c, tx, 9, tw, i == 0)
        face = cast.bust(cast.BY_KEY[key]).im.resize((8, 8), 0)
        small = Canvas(8, 8); small.im = face; small.px = face.load()
        c.blit(small, tx + 2, 10)
        by(c, tx + 13, 12, label, LIT["ink"] if i == 0 else MUTED, mark=OWN["claude"])
        tx += tw + 4
    # The buttons: green freeway signs under a gantry.
    labels = ("+", "copilot", "FILES", "CHANGES")
    size = lambda s: len(MINI[s][0]) if s in MINI else text_width(s)
    wide = sum(size(s) + 8 for s in labels) + 2 * (len(labels) - 1)
    gx = W - 8 - wide
    c.rect(gx - 3, 6, 1, 45, "#3d4656"); c.rect(W - 6, 6, 1, 45, "#3d4656")
    c.hl(gx - 3, 6, wide + 6, "#59606a"); c.hl(gx - 3, 7, wide + 6, "#59606a")
    for label in labels:
        tw = size(label) + 8
        c.rect(gx, 9, tw, 11, "#0f4d35")
        c.box(gx, 9, tw, 11, "#b9d6c4")
        if label in MINI:
            tool(c, gx + 4, 12, label, "#e8f3ea")
        else:
            c.text(gx + 4, 12, label, "#e8f3ea")
        gx += tw + 2
    c.blit(world.band_front().crop(0, 0, W - x0, 56 - world.FRONT_Y), x0, world.FRONT_Y)
    # The pane: a slim header, then the terminal over Pied Piper's hat.
    px0, py0, pw, ph = x0 + 4, 60, W - x0 - 8, H - 60 - BAR - 4
    c.rect(px0, py0, pw, ph, TERM)
    night = hat.scene()
    for yy in range(ph - 17):
        for xx in range(pw):
            n = night.get(int(xx * 640 / pw), int(yy * 480 / (ph - 17)))
            if n[0] + n[1] + n[2] > 0:
                c.p(px0 + xx, py0 + 17 + yy, mix(TERM, n, 0.13))
    c.rect(px0, py0, pw, 17, CHROME)
    c.hl(px0, py0 + 16, pw, BORDER)
    c.blit(cast.bust(cast.BY_KEY["richard"]), px0 + 1, py0)
    hx = c.text(px0 + 22, py0 + 6, "RICHARD", TEXT)
    hx = tool(c, hx + 3, py0 + 6, "claude", MUTED)
    c.text(hx + 5, py0 + 6, "~/PIED-PIPER", DIM)
    c.rect(px0 + pw - 9, py0 + 6, 4, 4, MARK["work"])
    lines = [(TEXT, 46), (MUTED, 30), (None, 0), (TEXT, 62), (TEXT, 38), (MUTED, 24), (None, 0), (ACCENT, 12), (TEXT, 54), (MUTED, 34),
             (None, 0), (TEXT, 66), (TEXT, 20), (MUTED, 28), (None, 0), ("#76a8ff", 16), (TEXT, 48), (None, 0), (TEXT, 58), (MUTED, 22)]
    ly = py0 + 28
    for col, n in lines:
        if col:
            k, lx = 0, px0 + 12
            while k < n:
                word = 2 + int(noise(k, ly) * 6)
                c.rect(lx, ly, word * 4 - 1, 2, col)
                lx += word * 4 + 3
                k += word
        ly += 7
    c.rect(px0 + 12, ly + 6, 3, 6, ACCENT)
    c.box(px0, py0, pw, ph, BORDER)
    # The status bar: one light per agent.
    c.rect(x0, H - BAR, W - x0, BAR, CHROME)
    c.hl(x0, H - BAR, W - x0, BORDER)
    c.text(x0 + 6, H - 9, "THIS COMPUTER", MUTED)
    lx = x0 + 66
    for col in (MARK["work"], None, MARK["blocked"], None, MARK["work"]):
        if col:
            c.rect(lx, H - 9, 3, 3, col)
        else:
            c.box(lx, H - 9, 3, 3, DIM)
        lx += 5
    c.text(lx + 2, H - 9, "5 AGENTS", MUTED)
    tag = "MAKING THE WORLD A BETTER PLACE"
    c.text(W - 8 - text_width(tag), H - 9, tag, DIM)
    return c
