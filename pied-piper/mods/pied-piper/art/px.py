"""A small pixel-art kit: a canvas of art pixels, a 3x5 font, shading.

One art pixel is saved as SCALE x SCALE image pixels with hard edges, and the
mod shows it as 2x2 logical pixels, so on a Retina screen every image pixel is
one screen pixel (GPUI smooths an image it has to enlarge).
"""
from PIL import Image

SCALE = 4


def rgb(c):
    """'#rrggbb' or '#rrggbbaa' or a tuple -> (r, g, b, a)."""
    if c is None:
        return None
    if isinstance(c, tuple):
        return c if len(c) == 4 else (*c, 255)
    c = c.lstrip("#")
    if len(c) == 6:
        c += "ff"
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4, 6))


def mix(a, b, t):
    """a moved t of the way to b."""
    a, b = rgb(a), rgb(b)
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (a[3],)


def dark(c, t=0.25):
    return mix(c, "#05070a", t)


def light(c, t=0.25):
    return mix(c, "#ffffff", t)


# 3x5 letters, one string per row.
FONT = {
    "A": ["###", "#.#", "###", "#.#", "#.#"], "B": ["##.", "#.#", "##.", "#.#", "##."],
    "C": ["###", "#..", "#..", "#..", "###"], "D": ["##.", "#.#", "#.#", "#.#", "##."],
    "E": ["###", "#..", "##.", "#..", "###"], "F": ["###", "#..", "##.", "#..", "#.."],
    "G": ["###", "#..", "#.#", "#.#", "###"], "H": ["#.#", "#.#", "###", "#.#", "#.#"],
    "I": ["###", ".#.", ".#.", ".#.", "###"], "J": ["..#", "..#", "..#", "#.#", "###"],
    "K": ["#.#", "#.#", "##.", "#.#", "#.#"], "L": ["#..", "#..", "#..", "#..", "###"],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#"], "N": ["#..#", "##.#", "#.##", "#..#", "#..#"],
    "O": ["###", "#.#", "#.#", "#.#", "###"], "P": ["###", "#.#", "###", "#..", "#.."],
    "Q": ["###", "#.#", "#.#", "###", "..#"], "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "S": ["###", "#..", "###", "..#", "###"], "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "U": ["#.#", "#.#", "#.#", "#.#", "###"], "V": ["#.#", "#.#", "#.#", "#.#", ".#."],
    "W": ["#...#", "#...#", "#.#.#", "##.##", "#...#"], "X": ["#.#", "#.#", ".#.", "#.#", "#.#"],
    "Y": ["#.#", "#.#", ".#.", ".#.", ".#."], "Z": ["###", "..#", ".#.", "#..", "###"],
    "0": ["###", "#.#", "#.#", "#.#", "###"], "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["###", "..#", "###", "#..", "###"], "3": ["###", "..#", ".##", "..#", "###"],
    "4": ["#.#", "#.#", "###", "..#", "..#"], "5": ["###", "#..", "###", "..#", "###"],
    "6": ["###", "#..", "###", "#.#", "###"], "7": ["###", "..#", "..#", ".#.", ".#."],
    "8": ["###", "#.#", "###", "#.#", "###"], "9": ["###", "#.#", "###", "..#", "###"],
    " ": ["...", "...", "...", "...", "..."], ".": ["...", "...", "...", "...", ".#."],
    ",": ["...", "...", "...", ".#.", "#.."], "!": [".#.", ".#.", ".#.", "...", ".#."],
    "?": ["###", "..#", ".#.", "...", ".#."], "-": ["...", "...", "###", "...", "..."],
    "+": ["...", ".#.", "###", ".#.", "..."], "=": ["...", "###", "...", "###", "..."],
    ":": ["...", ".#.", "...", ".#.", "..."], "/": ["..#", "..#", ".#.", "#..", "#.."],
    "'": [".#.", ".#.", "...", "...", "..."], ">": ["#..", ".#.", "..#", ".#.", "#.."],
    "<": ["..#", ".#.", "#..", ".#.", "..#"], "$": [".##", "##.", ".#.", ".##", "##."],
    "%": ["#.#", "..#", ".#.", "#..", "#.#"], "#": ["#.#", "###", "#.#", "###", "#.#"],
    "^": [".#.", "#.#", "...", "...", "..."], "_": ["...", "...", "...", "...", "###"],
    "*": ["...", "#.#", ".#.", "#.#", "..."], "&": [".#.", "#.#", ".#.", "#.#", ".##"],
    "(": [".#.", "#..", "#..", "#..", ".#."], ")": [".#.", "..#", "..#", "..#", ".#."],
    "~": ["...", ".#.", "#.#", "...", "..."], "|": [".#.", ".#.", ".#.", ".#.", ".#."],
}


def text_width(s):
    return max(0, sum(len(FONT.get(ch, FONT["?"])[0]) + 1 for ch in s.upper()) - 1)


class Canvas:
    def __init__(self, w, h, bg=None):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w, h), rgb(bg) if bg else (0, 0, 0, 0))
        self.px = self.im.load()

    # --- pixels ---
    def p(self, x, y, c):
        if c is None or not (0 <= x < self.w and 0 <= y < self.h):
            return
        c = rgb(c)
        if c[3] == 255:
            self.px[x, y] = c
        elif c[3] > 0:
            # Blend a translucent color over what is there.
            o = self.px[x, y]
            a = c[3] / 255
            if o[3] == 0:
                self.px[x, y] = c
            else:
                self.px[x, y] = tuple(round(o[i] + (c[i] - o[i]) * a) for i in range(3)) + (max(o[3], c[3]),)

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.px[x, y]
        return (0, 0, 0, 0)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.p(xx, yy, c)

    def box(self, x, y, w, h, c, fill=None):
        """An outline rectangle, optionally filled."""
        if fill is not None:
            self.rect(x + 1, y + 1, w - 2, h - 2, fill)
        self.rect(x, y, w, 1, c)
        self.rect(x, y + h - 1, w, 1, c)
        self.rect(x, y, 1, h, c)
        self.rect(x + w - 1, y, 1, h, c)

    def hl(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vl(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.p(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def grid(self, x, y, rows, pal):
        """An ASCII sprite: one letter per pixel, '.' and ' ' are empty."""
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in ". ":
                    continue
                self.p(x + i, y + j, pal[ch])

    def text(self, x, y, s, c):
        for ch in s.upper():
            g = FONT.get(ch, FONT["?"])
            for j, row in enumerate(g):
                for i, bit in enumerate(row):
                    if bit == "#":
                        self.p(x + i, y + j, c)
            x += len(g[0]) + 1
        return x

    def ctext(self, cx, y, s, c):
        """Text centered on cx."""
        self.text(cx - text_width(s) // 2, y, s, c)

    def blit(self, other, x, y):
        self.im.alpha_composite(other.im, (x, y)) if x >= 0 and y >= 0 else self._blit_clip(other, x, y)
        self.px = self.im.load()

    def _blit_clip(self, other, x, y):
        for j in range(other.h):
            for i in range(other.w):
                c = other.px[i, j]
                if c[3]:
                    self.p(x + i, y + j, c)

    # --- effects ---
    def outline(self, c, corners=False):
        """Rings every opaque shape with a 1px line where there is room."""
        c = rgb(c)
        src = self.im.copy().load()
        for y in range(self.h):
            for x in range(self.w):
                if src[x, y][3]:
                    continue
                near = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                if corners:
                    near += [(x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1)]
                for nx, ny in near:
                    if 0 <= nx < self.w and 0 <= ny < self.h and src[nx, ny][3]:
                        self.px[x, y] = c
                        break

    def dither_fade(self, x0, x1, c):
        """Fades to color c from x0 (untouched) to x1 (solid), in an ordered dither."""
        bayer = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
        span = max(1, x1 - x0)
        for y in range(self.h):
            for x in range(x0, self.w):
                t = min(1.0, (x - x0) / span)
                if t * 17 > bayer[y % 4][x % 4] + 0.5:
                    self.p(x, y, c)

    def dither_clear(self, x0, x1):
        """Fades to nothing from x0 (untouched) to x1 (gone), in an ordered dither."""
        bayer = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
        span = max(1, x1 - x0)
        for y in range(self.h):
            for x in range(x0, self.w):
                t = min(1.0, (x - x0 + 1) / span)
                if t * 16 > bayer[y % 4][x % 4]:
                    self.px[x, y] = (0, 0, 0, 0)

    def crop(self, x, y, w, h):
        out = Canvas(w, h)
        out.im = self.im.crop((x, y, x + w, y + h))
        out.px = out.im.load()
        return out

    def flip(self):
        out = Canvas(self.w, self.h)
        out.im = self.im.transpose(Image.FLIP_LEFT_RIGHT)
        out.px = out.im.load()
        return out

    def save(self, path, scale=SCALE):
        self.im.resize((self.w * scale, self.h * scale), Image.NEAREST).save(path, optimize=True)


def noise(x, y, seed=0):
    """A repeatable 0..1 value per pixel, for speckle."""
    n = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 0xFFFF
