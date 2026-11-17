"""Behind the terminals: Pied Piper's hat, as a watermark.

The company's last logo is a piper's hat with a long feather, in green. Here
it is alone in the middle of an empty picture the color of the terminal's own
background, so all that shows behind the text is the hat, faintly: with the
layout's terminal_opacity at 0.7 about a tenth of a picture comes through
(measured in the window), and the hat gets only STRENGTH of its green.

It is centered by eye, not by its box: the feather reaches far up and to the
right of the hat, so a centered box leaves the hat itself low and looking as
if it were sinking. What sits in the middle is the center of its green, pixel
for pixel; and the middle is that of the terminal under the pane's header,
which covers the top of the picture.

HAT is the logo's outline at this size, one row to a string, each run of
green as start+length. It was traced from the logo with trace() below (shrink
it to WIDE across, keep each pixel that is at least half covered); the logo
file itself is not kept here.
"""
from px import Canvas, mix

W, H = 640, 480
PAPER = "#0a0e17"       # the theme's background, so the picture's edges never show
GREEN = "#4fc45f"       # the green of the theme's Pied Piper sign
STRENGTH = 0.4          # how much of that green the hat gets; the rest is the background
HEADER = 18             # the pane's 33px header, in this picture's pixels at the size it is shown
WIDE = 220

HAT = [
    "219+1",
    "216+2",
    "214+2",
    "212+3",
    "210+4",
    "208+4",
    "206+6",
    "205+5",
    "203+6",
    "202+6",
    "201+6",
    "200+5",
    "198+6",
    "197+6",
    "196+6",
    "194+7",
    "194+6",
    "193+6",
    "191+7",
    "191+7",
    "190+7",
    "188+8",
    "187+8",
    "186+8",
    "186+8",
    "185+8",
    "184+9",
    "183+9",
    "182+9",
    "181+10",
    "181+10",
    "180+10",
    "179+11",
    "178+11",
    "177+11",
    "177+11",
    "176+11",
    "175+12",
    "175+12",
    "174+13",
    "173+13",
    "172+14",
    "172+14",
    "171+15",
    "170+16",
    "170+15",
    "169+16",
    "168+17",
    "168+16",
    "167+17",
    "166+18",
    "166+18",
    "165+19",
    "164+19",
    "164+19",
    "163+20",
    "162+21",
    "162+20",
    "161+21",
    "161+21",
    "160+21",
    "160+21",
    "159+22",
    "159+21",
    "158+22",
    "158+21",
    "157+21",
    "156+22",
    "156+21",
    "155+21",
    "155+20",
    "155+19",
    "154+18",
    "153+18",
    "153+16",
    "108+3 152+16",
    "100+17 152+14",
    "95+26 152+12",
    "92+32 151+11",
    "90+35 150+11",
    "88+39 150+9",
    "86+42 149+9",
    "84+46 149+7",
    "83+48 148+7",
    "81+51 148+6",
    "79+54 147+6",
    "78+56 147+6",
    "77+58 146+6",
    "75+61 145+6",
    "74+62 145+6",
    "73+64 144+6",
    "71+67 143+6",
    "70+68 143+6",
    "69+70 142+6",
    "68+71 142+6",
    "67+73 141+6",
    "66+81",
    "65+81",
    "64+82",
    "64+81",
    "63+81",
    "62+82",
    "61+82",
    "60+83",
    "59+66",
    "59+61",
    "58+56",
    "57+52",
    "56+50",
    "55+48",
    "55+44",
    "54+44",
    "53+42 121+37",
    "52+40 115+51",
    "52+39 111+56",
    "51+38 108+60",
    "51+36 103+65",
    "50+35 99+68",
    "49+34 96+71",
    "49+32 93+73",
    "48+32 90+75",
    "48+30 88+77",
    "47+30 85+79",
    "46+28 83+81",
    "46+27 81+82",
    "45+26 78+84",
    "44+25 76+86",
    "44+24 74+88",
    "43+23 72+89",
    "42+22 70+90",
    "42+21 68+92",
    "42+19 65+94",
    "41+18 63+96",
    "40+18 61+97",
    "40+16 59+99",
    "39+118",
    "39+117",
    "38+118",
    "38+117",
    "37+118",
    "37+117",
    "34+120",
    "29+124",
    "26+127",
    "19+133",
    "11+141",
    "2+149",
    "0+150",
    "1+149",
    "2+147",
    "3+146",
    "4+91 132+16",
    "6+80 142+5",
    "7+73",
    "9+65",
    "11+56",
    "14+48",
    "17+38",
    "23+22",
]


def trace(path, wide=WIDE):
    """The rows for HAT, from a picture of the logo on a clear background."""
    from PIL import Image
    a = Image.open(path).convert("RGBA").split()[3]
    a = a.crop(a.point(lambda v: 255 if v > 128 else 0).getbbox())
    a = a.resize((wide, round(a.height * wide / a.width)), Image.BOX)
    rows = []
    for y in range(a.height):
        on = [x for x in range(wide) if a.getpixel((x, y)) >= 128]
        starts = [x for x in on if x - 1 not in on]
        rows.append(" ".join(f"{x}+{next(e for e in range(x, wide + 1) if e not in on) - x}" for x in starts))
    return rows


def hat(color=GREEN):
    c = Canvas(WIDE, len(HAT))
    for y, row in enumerate(HAT):
        for run in row.split():
            x, n = run.split("+")
            c.rect(int(x), y, int(n), 1, color)
    return c


def middle():
    """The center of the hat's green: (x, y) within its box."""
    runs = [(y, int(x), int(n)) for y, row in enumerate(HAT) for x, n in (run.split("+") for run in row.split())]
    ink = sum(n for _, _, n in runs)
    return sum((x + n / 2) * n for _, x, n in runs) / ink, sum((y + 0.5) * n for y, _, n in runs) / ink


def scene():
    c = Canvas(W, H, PAPER)
    cx, cy = middle()
    c.blit(hat(mix(PAPER, GREEN, STRENGTH)), round(W / 2 - cx), round((H + HEADER) / 2 - cy))
    return c
