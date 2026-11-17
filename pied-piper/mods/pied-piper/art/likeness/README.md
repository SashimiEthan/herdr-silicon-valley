# Likeness: a photo turned into the sprite's pixels

The heads are no longer drawn this way. Since 2026-11-16 each one is in
`../heads.py`: a photo redrawn as a small sprite by
pixelface (a separate tool, not published), which measures the
face and draws eyes, glasses and a mouth as well, then touched up by hand.
These tools are kept for comparing a drawing with its photo.

How the first heads in `../cast.py` were drawn: each over a conversion of a photo of
the character, not from memory. The photos and the conversions are not kept
here (they are the show's pictures); only the tools are.

1. One photo per character in a folder, named by its key: `photos/richard.png`.
2. Find the faces and the silhouettes (macOS, Xcode's command line tools):
   `swiftc -O vision.swift -o /tmp/vision && /tmp/vision masks photos/*.png > faces.jsonl`
3. Convert (needs Pillow and numpy): `python3 convert.py faces.jsonl photos masks conv`.
   Each face is leveled on its eyes and scaled so the eye line sits 6 art
   pixels above the chin, the same for everyone, so the faces can be compared.
4. A first tracing in `cast.py`'s letters, and the colors measured:
   `python3 draft.py conv richard gilfoyle`.
5. Draw the head over it in `../cast.py`, then look at photo, conversion and
   drawing side by side: `python3 compare.py conv .. sheet.png richard gilfoyle`.

What the conversion is good for: the hair's outline and length, the hairline,
how long or broad the face is, skin, hair and clothes colors. What it cannot
give at 14 pixels: eyes, glasses, a mouth. Those are drawn by hand.
