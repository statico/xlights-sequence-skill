"""Draw 1-bit matrix sprites with PIL: white on black, one PNG per frame, exactly the matrix size (35x17 here).
At 17 px only chunky silhouettes read: rectangles and filled ellipses, no thin diagonals (they come out ragged),
block letters from rectangles (a letter needs 5 px of width to read as M; 3 px reads as H). Preview at 10x before rendering.
usage: tmp/venv/bin/python scripts/sprite_example.py  -> xlights/sprites/example_hero.png, example_hero2.png, tmp/preview_*.png"""
from PIL import Image, ImageDraw
W, H = 35, 17
def frame(name, draw_fn):
    im = Image.new("1", (W, H), 0); d = ImageDraw.Draw(im); draw_fn(d); im.save(f"xlights/sprites/{name}.png")
    im.resize((W * 10, H * 10), Image.NEAREST).save(f"tmp/preview_{name}.png")
def moon(d, stars):
    d.ellipse((8, 1, 24, 15), fill=1); d.ellipse((12, 0, 27, 12), fill=0)   # crescent = disc minus offset disc
    for x, y in stars: d.rectangle((x, y, x + 1, y + 1), fill=1)
frame("example_hero", lambda d: moon(d, [(3, 3), (30, 5), (28, 13)]))
frame("example_hero2", lambda d: moon(d, [(5, 12), (31, 2), (2, 8)]))   # second frame: stars move, so beat_pics twinkles
