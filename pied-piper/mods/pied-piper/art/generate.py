#!/usr/bin/env python3
"""Draws everything the Pied Piper mod shows that isn't text.

    python3 art/generate.py            # writes ../seats, ../beds, ../cast, ../world, ../icons
    python3 art/generate.py --legs     # only seats/legs.js and beds/legs.js
    python3 art/generate.py --sheets D # also contact sheets into folder D, to look at

It also redraws the layout's picture for Settings, layouts/pied-piper.png, when
the mod is in Herdr's home.

    heads.py   the seventeen characters' heads, one drawing each
    cast.py    their bodies and clothes: one rig (cast/<key>-head.png)
    desks.py   each one seated at their own desk, their own thing on the wall behind, in four poses (seats/<key>-<pose>.png)
    beds.py    each one cross-legged on their own bunk, in the same four (beds/<key>-<pose>.png)
    decor.py   the office's wall and the bedroom's: surface, trim, what hangs on it, the floor (world/wall-*, floor-*)
    world.py   the title sky, the company skyline in two layers, Pied Piper's sign (world/)
    hat.py     behind the terminals: Pied Piper's hat as a watermark (world/watermark.png)
    icons.py   the one-color icons (icons/*.svg)
    preview.py the layout's picture: the window in miniature, with made-up agents
    px.py      the canvas and the 3x5 font

One art pixel is saved 4x4 and shown 2x2, so it is a whole number of screen
pixels on a Retina screen and on a plain one. Needs Pillow.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cast      # noqa: E402
import desks     # noqa: E402
import beds      # noqa: E402
import decor     # noqa: E402
import world     # noqa: E402
import hat       # noqa: E402
import icons     # noqa: E402
import preview   # noqa: E402
from px import rgb  # noqa: E402

ROOT = os.path.dirname(HERE)


def out(*parts):
    path = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def draw_cast():
    for s in cast.CAST:
        for pose in cast.POSES:
            desks.seat(s["key"], pose).save(out("seats", f"{s['key']}-{pose}.png"))
            beds.bed(s["key"], pose).save(out("beds", f"{s['key']}-{pose}.png"))
        cast.bust(s).save(out("cast", f"{s['key']}-head.png"))
    print(f"{len(cast.CAST)} characters at their desks and on their bunks, {len(cast.POSES)} poses each")


def floor_left(c):
    """The first art pixel from a picture's left edge where its furniture
    stands on the floor (its outline aside): a desk's left leg, the front panel
    of Gavin's desk and of Russ's bar, the arm of Erlich's couch (the coffee
    table's leg behind it is lost in the couch), or the bunk's left post."""
    for x in range(c.w):
        p = c.get(x, desks.BOTTOM)
        if p[3] and p[:3] != rgb(cast.OUTLINE)[:3]:
            return x
    return None


def draw_legs():
    """For the sidebar (spaces.js): under each agent's row its subagents'
    tree line starts where the picture's furniture stands at the left. Modules,
    not JSON: a mod can't import JSON."""
    for folder, draw, what in (("seats", desks.seat, "desk's left leg"), ("beds", beds.bed, "bunk's left post")):
        legs = {s["key"]: floor_left(draw(s["key"])) for s in cast.CAST}
        with open(out(folder, "legs.js"), "w") as f:
            f.write(f"// Written by art/generate.py (draw_legs): where each {what} starts, in art pixels\n"
                    f"// from the picture's left edge (2 logical pixels each). Don't edit; regenerate.\n"
                    f"export default {json.dumps(legs)};\n")
    print("where the furniture stands: seats/legs.js, beds/legs.js")


def draw_world():
    world.brand().save(out("world", "brand.png"))
    world.band_back().save(out("world", "band-back.png"))
    world.band_front().save(out("world", "band-front.png"))
    hat.scene().save(out("world", "watermark.png"))
    world.son_of_anton().save(out("world", "anton.png"))
    for room in decor.ROOMS:
        decor.wall(room).save(out("world", f"wall-{room}.png"))
        decor.floor(room).save(out("world", f"floor-{room}.png"))
    for name in world.COMPANIES:
        world.company(name).save(out("world", f"co-{name}.png"))
    print("the valley, the hat, the two rooms' walls, Pied Piper's sign")


def draw_icons():
    for name, art in icons.ICONS.items():
        with open(out("icons", name + ".svg"), "w") as f:
            f.write(icons.icon_svg(name, art))
    for name, art in icons.TOOLS.items():
        with open(out("icons", f"tool-{name}.svg"), "w") as f:
            f.write(icons.icon_svg(name, art, square=None))
    print(f"{len(icons.ICONS)} icons, {len(icons.TOOLS)} tools' marks")


def main():
    if "--legs" in sys.argv:
        draw_legs()
        return
    draw_cast()
    draw_legs()
    draw_world()
    draw_icons()
    layouts = os.path.join(os.path.dirname(os.path.dirname(ROOT)), "layouts")
    if os.path.exists(os.path.join(layouts, "pied-piper.json")):
        preview.preview().save(os.path.join(layouts, "pied-piper.png"), 2)
        print("layouts/pied-piper.png")
    if "--sheets" in sys.argv:
        import sheet
        d = sys.argv[sys.argv.index("--sheets") + 1]
        os.makedirs(d, exist_ok=True)
        keys = [s["key"] for s in cast.CAST]
        lit = decor.ROOMS["office"]["wall"]
        sheet.seats_sheet(os.path.join(d, "cast-1.png"), keys[:8], bg=lit)
        sheet.seats_sheet(os.path.join(d, "cast-2.png"), keys[8:], bg=lit)
        sheet.whos_who(os.path.join(d, "whos-who.png"), bg=lit)
        dim = decor.ROOMS["bedroom"]["wall"]
        sheet.seats_sheet(os.path.join(d, "beds-1.png"), keys[:8], draw=beds.bed, bg=dim)
        sheet.seats_sheet(os.path.join(d, "beds-2.png"), keys[8:], draw=beds.bed, bg=dim)
        print("sheets in", d)


if __name__ == "__main__":
    main()
