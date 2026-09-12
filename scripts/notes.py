"""usage: python3 scripts/notes.py [<song> ...]
Prints the marks on the `Notes` timing track of each sequence: the time, the beat index on that song's grid, and the
note text. Leave notes in the xLights GUI by hitting `t` on the Notes track and double-clicking the mark to type.
The generator keeps the track verbatim, so notes survive regeneration until you delete them."""
import sys, re, glob, os
SEQ = "xlights/sequences"
songs = sys.argv[1:] or [os.path.basename(f)[:-4] for f in sorted(glob.glob(f"{SEQ}/*.xsq"))]
for song in songs:
    x = open(f"{SEQ}/{song}.xsq").read()
    m = re.search(r'<Element type="timing" name="Notes">(.*?)</Element>', x, re.S)
    marks = re.findall(r'<Effect label="([^"]*)" startTime="(\d+)" endTime="(\d+)"', m.group(1)) if m else []
    marks = [(int(a), int(b), l) for l, a, b in marks if l.strip()]
    if not marks: continue
    bts = re.search(r'name="Beats"><EffectLayer>(.*?)</EffectLayer>', x, re.S)   # the grid, read off the Beats track itself
    bts = [int(t) for t in re.findall(r'startTime="(\d+)"', bts.group(1))[:200]] if bts else []
    b0, bp = (bts[0], (bts[-1] - bts[0]) / (len(bts) - 1)) if len(bts) > 1 else (None, None)
    print(f"== {song} ({len(marks)} notes)")
    for a, b, l in marks:
        k = f"beat {(a - b0) / bp:7.2f}" if bp else ""
        un = l.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&amp;", "&")
        print(f"  {a/1000:8.2f}s - {b/1000:8.2f}s  {k}  {un}")
