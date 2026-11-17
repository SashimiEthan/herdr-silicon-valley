"""The cast, drawn to look like themselves.

Each head is its own drawing (heads.py): a photo of the character measured and
redrawn as a small sprite, then touched up by hand. The bodies are one rig
with each person's build, height and clothes, so a new pose or an animation
frame is drawn once here and all seventeen get it. The clothes are the ones
worn in the photo the head came from (for the five at the hostel, the group
still: Richard's maroon hoodie, Dinesh's striped rugby shirt), or in another
picture of the same outfit where that photo stops at the collar. desks.py
seats one behind a desk, facing you; beds.py sits one cross-legged on a bunk.
"""
from px import Canvas, dark, light, mix
from heads import HEADS

OUTLINE = "#06080d"
POSES = ["idle", "work", "blocked", "done"]
TORSO_H = 10        # shoulders to lap
ARM = 3             # an arm's width
SLOPE = 0.34        # how far a shoulder falls for each pixel out from the collar (about 19 degrees)
COLLAR = 3          # the shoulders are level this far out from the middle: the neck and a collar

# top: how the clothes are cut.
#   open     a hoodie, flannel or jacket worn open over a shirt (`inner`);
#            `strings` are a hoodie's, `lapel` makes it a blazer, `buttons`
#            run down the shirt, `inner_print` is a picture on a tee
#   sweater  a pullover; `collar` is the shirt under it, `vee` a V-neck showing
#            it, `placket` a henley's buttons, `open_neck` the top ones undone
#   polo     a rugby shirt: a collar and a placket in `collar`
#   zip      a jacket zipped up to a standing collar
#   blazer   lapels closed over a shirt (`inner`)
#   shirt    a printed blouse, open at the neck
#   tunic    a long plain shirt; `scarf` lies around its neck
# pattern: "plaid" or "stripes" in `alt`, on the outer layer; inner_alt checks
# the shirt, inner_band stripes it. `hood` bunches one behind the neck.
# `short` sleeves end above the elbow. `chain` is a necklace, `beads` long
# strands of them, `cable` a robot's lead at the neck.
# The skin's two colors come from the head's drawing (heads.py).
CAST = [
    # A maroon zip hoodie with white strings, open over a pale pink shirt buttoned to the collar; dark brown trousers.
    dict(key="richard", build="slim",
         top="open", top_color="#7a2f3a", hood=True, strings="#f0ece4", inner="#e3d2d1", collar="#f1e4e2", buttons=True,
         pants="#3b2c26", shoes="#d9d6cb"),
    # A dark plaid flannel open over a maroon tee; black jeans.
    dict(key="gilfoyle",
         top="open", top_color="#2f3340", pattern="plaid", alt="#59607a", inner="#5c1f2b", pants="#24262d", shoes="#15161a"),
    # A rugby shirt in wide purple and olive stripes, white at the collar and the placket; maroon cords.
    dict(key="dinesh", tall=-1,
         top="polo", top_color="#5d3a8c", pattern="stripes", alt="#6b6a3f", collar="#e8e1d6", pants="#6b2430", shoes="#2a1a1e"),
    # A tan V-neck over a pale blue shirt; the tallest of them.
    dict(key="jared", build="slim", tall=1,
         top="sweater", top_color="#a08a72", collar="#b9c6d6", vee=True, pants="#2f3340", shoes="#5a3d28"),
    # A tan plaid shirt open over a mustard henley; the biggest of them.
    dict(key="erlich", build="heavy",
         top="open", top_color="#b59a6a", pattern="plaid", alt="#7a5f3c", inner="#e2b04e", buttons=True,
         pants="#3f4652", shoes="#6b4a2f"),
    # A blue knit hoodie striped orange, open over a red tee with a dark print; jeans.
    dict(key="bighead", tall=-1,
         top="open", top_color="#3f5fa0", pattern="stripes", alt="#c9794a", hood=True, strings="#ece6da",
         inner="#b03a3c", inner_print="#5a1f24", pants="#5a7088", shoes="#e2dfd6"),
    # A dark teal blouse with small pale flowers.
    dict(key="monica", build="slim",
         top="shirt", top_color="#2b4447", alt="#c9a6ae", pants="#22252e", shoes="#111216"),
    # A plum long-sleeved tee in thin paler stripes.
    dict(key="jianyang", tall=-1,
         top="sweater", top_color="#6c3d4c", pattern="stripes", alt="#94687a", pants="#3b4150", shoes="#d7d4c9"),
    # A navy jacket over a bright blue shirt, open at the collar.
    dict(key="gavin",
         top="blazer", top_color="#1c2a4e", inner="#2f5db0", pants="#2a2c33", shoes="#101114"),
    # A dark navy long-sleeved tee with a faint rib.
    dict(key="russ",
         top="sweater", top_color="#23263a", pattern="stripes", alt="#2c3048", pants="#7f97bd", shoes="#3a2418"),
    # A black sweater vest over a white shirt.
    dict(key="laurie", build="slim",
         top="sweater", top_color="#17181d", collar="#e6e8f0", vee=True, sleeve="#e6e8f0", pants="#8f979f", shoes="#24262b"),
    # A cream knit sweater over a periwinkle collar.
    dict(key="peter", build="slim",
         top="sweater", top_color="#e9e0d4", collar="#7f8ac0", pants="#565a63", shoes="#1c1c20"),
    # A navy zip cardigan over a pale lavender shirt.
    dict(key="jack", build="heavy",
         top="sweater", top_color="#1e2338", collar="#cfc3dc", vee=True, pants="#b7a47c", shoes="#4a3323"),
    # The robot: a dark plum wrap over a black top, the lead from her neck in teal.
    dict(key="fiona", build="slim",
         top="sweater", top_color="#3a1c28", collar="#141417", vee=True, cable="#3f9aa0", pants="#1b1c21", shoes="#3a4048"),
    # A white kurta, a knitted cream scarf around the neck, long strands of dark beads.
    dict(key="denpok",
         top="tunic", top_color="#ece7dc", scarf="#d6c48c", beads="#2e1c1c", pants="#8a6d4a", shoes="#6b4a2f"),
    # A gray pullover hoodie, a black cord at the neck.
    dict(key="carla", build="slim",
         top="sweater", top_color="#6f737b", hood=True, chain="#1a1b20", pants="#1c1d22", shoes="#0f1013"),
    # A dark brown henley with the top buttons undone, a long silver chain.
    dict(key="ron",
         top="sweater", top_color="#3f302a", pattern="stripes", alt="#473832", open_neck=True, chain="#b9bec6", long_chain=True,
         pants="#2d3140", shoes="#3a2418"),
]
for _s in CAST:
    _h = HEADS[_s["key"]]
    _s["skin"] = tuple(_h["pal"][ch] for ch in _h["skin"])
BY_KEY = {c["key"]: c for c in CAST}


def chest(s):
    """The chest's width, between the arms."""
    return {"slim": 10, "normal": 12, "heavy": 14}[s.get("build", "normal")]


def width(s):
    """Shoulder to shoulder."""
    return chest(s) + 2 * ARM


def neck(s):
    """How many rows the head takes, down to and with the neck."""
    return HEADS[s["key"]]["neck"] + 1


# -------------------------------------------------------------------- head
def head(c, s, cx, hy):
    """Their head, its face centered on cx, its drawing's top row at hy."""
    h = HEADS[s["key"]]
    c.grid(cx - h["axis"], hy, h["rows"], h["pal"])


# ------------------------------------------------------------------- torso
def cloth(s, x, y, tt):
    """Their outer layer's color at a pixel: plain, plaid or striped."""
    col, kind = s["top_color"], s.get("pattern")
    if kind == "plaid":
        return s["alt"] if (x % 3 == 0 or (y - tt) % 3 == 1) else col
    if kind == "stripes":
        return s["alt"] if ((y - tt) // 2) % 2 else col
    return col


def collar(c, s, cx, tt, col):
    """A shirt collar's two points, either side of the throat."""
    for dx in (-3, -2, 1, 2):
        c.p(cx + dx, tt, col)
    c.p(cx - 2, tt + 1, col); c.p(cx + 1, tt + 1, col)


def torso(c, s, cx, tt):
    """The chest, its top row at tt, centered on cx (between cx-1 and cx)."""
    cw = chest(s)
    x0 = cx - cw // 2
    top, col = s["top"], s["top_color"]
    inner = s.get("inner", col)
    skin, skin2 = s["skin"]
    rows = range(tt, tt + TORSO_H)
    for y in rows:
        for x in range(x0, x0 + cw):
            c.p(x, y, cloth(s, x, y, tt))
        c.p(x0 + cw - 1, y, dark(cloth(s, x0 + cw - 1, y, tt), 0.22))
    c.rect(cx - 1, tt, 2, 1, skin2)                      # the throat
    if top == "open":
        gap = 4
        for y in rows:
            for x in range(cx - gap // 2, cx + gap // 2):
                shade = inner
                if s.get("inner_alt") and (x + y) % 2:
                    shade = s["inner_alt"]
                if s.get("inner_band") and (y - tt) % 4 == 2:
                    shade = s["inner_band"]
                c.p(x, y, shade)
            if s.get("buttons") and (y - tt) % 2 == 0 and y > tt:
                c.p(cx, y, dark(inner, 0.28))
            edge = light(col, 0.25) if s.get("lapel") and y < tt + 5 else dark(col, 0.3)
            c.p(cx - gap // 2 - 1, y, edge)
            c.p(cx + gap // 2, y, edge)
        c.rect(cx - 1, tt, 2, 1, skin2)
        if s.get("inner_print"):
            c.rect(cx - 1, tt + 3, 2, 2, s["inner_print"])
            c.p(cx - 2, tt + 4, s["inner_print"]); c.p(cx + 1, tt + 3, s["inner_print"])
        if s.get("collar"):
            collar(c, s, cx, tt, s["collar"])
        if s.get("hood"):
            hood(c, s, cx, tt)
        if s.get("strings"):
            for y in (tt + 1, tt + 2, tt + 3):
                c.p(cx - gap // 2 - 1, y, s["strings"]); c.p(cx + gap // 2, y, s["strings"])
    elif top == "sweater":
        if s.get("high"):
            c.rect(cx - 3, tt - 1, 6, 2, light(col, 0.12))   # up the neck
        elif s.get("vee"):
            for i in range(3):                           # the shirt, in the V
                c.rect(cx - 2 + i, tt + i, 4 - 2 * i, 1, s["collar"])
            c.rect(cx - 1, tt, 2, 1, skin2)
            c.p(cx - 3, tt, s["collar"]); c.p(cx + 2, tt, s["collar"])
        elif s.get("collar"):
            collar(c, s, cx, tt, s["collar"])
        if s.get("hood"):
            hood(c, s, cx, tt)
        if s.get("open_neck"):                           # the top buttons undone
            c.rect(cx - 1, tt, 2, 2, skin2)
            c.p(cx - 2, tt, dark(col, 0.25)); c.p(cx + 1, tt, dark(col, 0.25))
        if s.get("placket"):                             # a henley's buttons
            c.rect(cx - 1, tt + 1, 2, 3, dark(col, 0.25))
        if s.get("print"):                               # lettering across a tee
            for x in range(cx - 4, cx + 4):
                if x % 3 != 2:
                    c.p(x, tt + 4, s["print"])
            for x in range(cx - 3, cx + 3):
                if x % 2:
                    c.p(x, tt + 6, s["print"])
    elif top == "polo":
        collar(c, s, cx, tt, s["collar"])
        c.rect(cx - 1, tt + 1, 2, 3, s["collar"])        # the placket
    elif top == "zip":
        c.rect(cx - 3, tt - 1, 6, 1, col)                # the collar, standing
        c.rect(cx - 3, tt, 6, 1, light(col, 0.15))
        c.vl(cx - 1, tt + 1, TORSO_H - 1, s["alt"])
    elif top == "blazer":
        for i in range(5):                               # the shirt, in a V
            half = 3 - (i + 1) // 2
            c.rect(cx - half, tt + i, half * 2, 1, inner)
        c.rect(cx - 1, tt, 2, 1, skin2)
        for i in range(5):                               # the lapels
            c.p(cx - 4 + (i + 1) // 2, tt + i, light(col, 0.25)); c.p(cx + 3 - (i + 1) // 2, tt + i, light(col, 0.25))
        c.vl(cx - 1, tt + 5, TORSO_H - 5, dark(col, 0.3))
        c.p(cx, tt + 7, light(col, 0.35))
    elif top == "shirt":
        c.rect(cx - 1, tt, 2, 3, skin)
        c.p(cx - 1, tt + 2, skin2)
        for y in rows:
            for x in range(x0, x0 + cw):
                if (x * 3 + y * 5) % 7 == 0 and not (cx - 1 <= x <= cx and y < tt + 3):
                    c.p(x, y, s["alt"])
    elif top == "tunic":
        c.rect(cx - 1, tt, 2, 2, skin2)
        c.vl(cx - 1, tt + 2, TORSO_H - 2, dark(col, 0.12))     # where it closes
        if s.get("scarf"):
            # Around the neck and out over the shoulders, its knit showing.
            c.rect(x0 + 1, tt - 1, cw - 2, 1, s["scarf"])
            c.rect(cx - 2, tt - 1, 4, 1, skin2)
            c.rect(x0, tt, cw, 2, s["scarf"])
            for x in range(x0, x0 + cw):
                if (x + tt) % 2:
                    c.p(x, tt + 1, dark(s["scarf"], 0.18))
            c.rect(cx - 1, tt, 2, 1, skin2)
    if s.get("beads"):
        # Two long strands, the inner one shorter.
        for dx, dy in [(-3, 2), (-3, 3), (-2, 4), (-2, 5), (-1, 6), (0, 6), (1, 5), (1, 4), (2, 3), (2, 2)]:
            c.p(cx + dx, tt + dy, s["beads"])
        for dx, dy in [(-2, 2), (-1, 3), (0, 3), (1, 2)]:
            c.p(cx + dx, tt + dy, s["beads"])
    if s.get("chain"):
        long = [(-2, 1), (-2, 2), (-1, 3), (-1, 4), (0, 4), (0, 3), (1, 2), (1, 1)]
        for dx, dy in long if s.get("long_chain") else [(-2, 1), (-1, 2), (0, 2), (1, 1)]:
            c.p(cx + dx, tt + dy, s["chain"])
    if s.get("cable"):
        # A robot's lead, from behind the jaw down to the shoulder.
        c.p(cx - 3, tt - 2, s["cable"]); c.p(cx - 3, tt - 1, s["cable"]); c.p(cx - 4, tt, light(s["cable"], 0.2))


def hood(c, s, cx, tt):
    """A hood, bunched behind the neck."""
    cw = chest(s)
    c.rect(cx - cw // 2 + 1, tt - 1, cw - 2, 1, light(s["top_color"], 0.15))
    c.rect(cx - 2, tt - 1, 4, 1, s["skin"][1])


def sleeve(s, x, y, tt):
    """An arm's color at a pixel: the outer layer's, or a vest's shirt."""
    return s["sleeve"] if s.get("sleeve") else cloth(s, x, y, tt)


def bare(s):
    """How many rows of sleeve before the arm is bare; skin, or a robot's joint."""
    return (3 if s.get("short") else 99), s["skin"][0]


def upper_arms(c, s, cx, tt, pose):
    """The arms above the desk: at the sides, or raised."""
    cw = chest(s)
    lx, rx = cx - cw // 2 - ARM, cx + cw // 2      # each arm's left edge
    cut, skin = bare(s)

    def side(x, shade_x):
        for i in range(TORSO_H - 1):
            for dx in range(ARM):
                if i == 0 and x + dx in (lx, rx + ARM - 1):
                    continue                        # the shoulder, rounded
                col = sleeve(s, x + dx, tt + i, tt) if i < cut else skin
                c.p(x + dx, tt + i, dark(col, 0.22) if x + dx == shade_x else col)

    def up(x):
        # Straight up beside the head, the hand open at the top.
        top = tt - 11
        for y in range(top, tt + 2):
            col = skin if (y < top + 3 or (cut < 99 and y < tt - 3)) else sleeve(s, x, y, tt)
            c.rect(x, y, 2, 1, col)
        c.rect(x - 1, tt, ARM, 2, sleeve(s, x, tt, tt))

    def cheer(x, out):
        pts = [(0, 1), (1, 0), (2, -1), (2, -2), (3, -3), (3, -4), (4, -5), (4, -6)]
        for i, (dx, dy) in enumerate(pts):
            col = skin if (i >= len(pts) - 3 or (cut < 99 and i >= 3)) else sleeve(s, x, tt + dy, tt)
            c.rect(x + out * dx, tt + dy, 2, 1, col)

    if pose == "blocked":
        side(lx, -1)
        up(rx + 2)
        slope(c, s, cx, tt, -1)
    elif pose == "done":
        cheer(lx + 1, -1)
        cheer(rx, 1)
    else:
        side(lx, -1)
        side(rx, rx + ARM - 1)
        slope(c, s, cx, tt, -1)
        slope(c, s, cx, tt, 1)


def slope(c, s, cx, tt, side):
    """Slopes one shoulder, the left (-1) or the right (1): takes the top off
    the chest and the arm, more with each pixel out from the collar. Only for
    an arm that hangs: a raised one lifts its shoulder level."""
    for d in range(COLLAR, width(s) // 2):
        drop = int((d - COLLAR + 1) * SLOPE + 0.5)
        x = cx - 1 - d if side < 0 else cx + d
        for y in range(tt - 1, tt + drop):
            if 0 <= x < c.w and 0 <= y < c.h:
                c.px[x, y] = (0, 0, 0, 0)


def forearms(c, s, cx, y, pose):
    """The forearms on the desk, whose surface starts at row y: resting at the
    sides when idle, reaching in for the keys when working."""
    cw = chest(s)
    cut, skin = bare(s)
    left = pose != "done"
    right = pose in ("idle", "work")
    for on, x, d in ((left, cx - cw // 2 - ARM, 1), (right, cx + cw // 2 + ARM - 2, -1)):
        if not on:
            continue
        arm = skin if cut < 99 else sleeve(s, x, y, y)
        if pose == "work":
            c.rect(x, y, 2, 1, arm)
            c.rect(x + d, y + 1, 2, 1, arm)
            c.rect(x + 2 * d, y + 2, 2, 1, skin)
        else:
            c.rect(x, y, 2, 2, arm)
            c.rect(x, y + 2, 2, 1, skin)


def legs(c, s, cx, top, bottom):
    """Legs sitting down, seen from the front under a desk: rows top..bottom.
    The lap shows under the desk's edge, the thighs run out from it to knees
    set wide, and the shins drop from the knees to the shoes. (They were two
    straight columns, which read as short legs standing.)"""
    pants, shoes = s["pants"], s["shoes"]
    c.rect(cx - 5, top, 10, 1, pants)                             # the lap, as wide as the knees are apart
    for out in (-1, 1):
        def span(a, n):
            """n pixels going outward, starting a pixels from the middle."""
            return (cx - a - n, n) if out < 0 else (cx + a, n)
        x, n = span(2, 3)
        c.rect(x, top + 1, n, 1, pants)                           # the thigh, going out
        x, n = span(3, 3)
        c.rect(x, top + 2, n, 1, light(pants, 0.2))               # the knee
        c.rect(x, top + 3, n, bottom - top - 4, pants)            # the shin
        c.hl(x, top + 3, n, dark(pants, 0.3))                     # in the knee's shadow
        c.vl(cx + 5 if out > 0 else cx - 4, top + 4, bottom - top - 5, dark(pants, 0.25))
        x, n = span(3, 4)
        c.rect(x, bottom - 1, n, 2, shoes)
        c.hl(x, bottom, n, dark(shoes, 0.25))                     # the sole


def crossed(c, s, cx, top):
    """Legs crossed, seen from the front: five rows from `top`, the knees out
    past the shoulders, each foot in its sock under the other knee."""
    pants = s["pants"]
    sock = s["skin"][0] if s["key"] == "denpok" else "#e8e4da"
    half = width(s) // 2 + 3
    for row, inset in enumerate((3, 1, 0, 0, 2)):
        c.rect(cx - half + inset, top + row, (half - inset) * 2, 1, pants)
    c.hl(cx - half + 3, top, half * 2 - 6, light(pants, 0.12))
    # Where the shins cross, and the shade under them.
    for i in range(3):
        c.p(cx - 2 + i, top + 2 + i, dark(pants, 0.3))
        c.p(cx + 1 - i, top + 2 + i, dark(pants, 0.3))
    c.hl(cx - half + 5, top + 4, half * 2 - 10, dark(pants, 0.22))
    for x in (cx - half + 1, cx + half - 4):
        c.rect(x, top + 3, 3, 1, sock)
        c.rect(x + (1 if x < cx else 0), top + 4, 2, 1, sock)


def bust(s):
    """Head and shoulders, 16x16, for a tab, a pane header or a toast."""
    c = Canvas(16, 16)
    # The shoulders' row: lower for a tall head, so less of its hair is cut off.
    tt = 15 if neck(s) > 14 else 14
    torso(c, s, 8, tt)
    upper_arms(c, s, 8, tt, "idle")
    head(c, s, 8, tt - neck(s))
    c.outline(OUTLINE)
    return c
