"""Contact sheets, to look at the art while drawing it: every picture with the
character's name beside it."""
from px import Canvas, text_width
import cast
import desks

# As cast.js names them.
NAMES = {
    "richard": "RICHARD", "gilfoyle": "GILFOYLE", "dinesh": "DINESH", "jared": "JARED", "erlich": "ERLICH",
    "bighead": "BIG HEAD", "monica": "MONICA", "jianyang": "JIAN-YANG", "gavin": "GAVIN", "russ": "RUSS",
    "laurie": "LAURIE", "peter": "PETER GREGORY", "jack": "JACK BARKER", "fiona": "FIONA", "denpok": "DENPOK",
    "carla": "CARLA", "ron": "RON",
}
INK = "#f4f1ea"
LABEL = 58          # the names' column


def seats_sheet(path, keys=None, poses=("idle", "work", "blocked", "done"), bg="#0b101b", scale=5, draw=desks.seat):
    """Every pose of these characters, drawn by `draw` (desks.seat or
    beds.bed): a row each, its name at the left, the poses named along the top."""
    keys = keys or [s["key"] for s in cast.CAST]
    sheet = Canvas(LABEL + len(poses) * (desks.W + 2) + 2, 9 + len(keys) * (desks.H + 2) + 2, bg)
    for i, pose in enumerate(poses):
        sheet.ctext(LABEL + 2 + i * (desks.W + 2) + desks.W // 2, 2, pose, INK)
    for j, k in enumerate(keys):
        y = 9 + 2 + j * (desks.H + 2)
        sheet.text(3, y + desks.H // 2 - 2, NAMES[k], INK)
        for i, pose in enumerate(poses):
            sheet.blit(draw(k, pose), LABEL + 2 + i * (desks.W + 2), y)
    sheet.save(path, scale)


def whos_who(path, bg="#0b101b", scale=6, draw=desks.seat, across=4):
    """All of them once, idle, each over their name; and their face as the
    tabs and pane headers show it."""
    cw, ch = desks.W + 6, desks.H + 12
    down = (len(cast.CAST) + across - 1) // across
    sheet = Canvas(across * cw + 2, down * ch + 2, bg)
    for n, s in enumerate(cast.CAST):
        x, y = 1 + (n % across) * cw, 1 + (n // across) * ch
        sheet.blit(draw(s["key"], "idle"), x + 3, y)
        sheet.blit(cast.bust(s), x + 1, y + desks.H - 6)
        sheet.text(x + 19, y + desks.H + 3, NAMES[s["key"]], INK)
    sheet.save(path, scale)
