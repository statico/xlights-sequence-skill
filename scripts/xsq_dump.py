"""usage: python3 scripts/xsq_dump.py xlights/sequences/<song>.xsq [model|timing-track ...]
Lists every effect (start ms, end ms, name, settings) per model, and every mark per timing track, so GUI edits
(text speed, stretched starts/ends, a split in `Sections`, marks on `Cues`) can be read back into the generator.
Diff two dumps (the user's saved file vs a fresh generator run) to see exactly what they changed."""
import sys, re
x = open(sys.argv[1]).read(); want = set(sys.argv[2:])
db = re.findall(r"<Effect>(.*?)</Effect>", x.split("<EffectDB>")[1].split("</EffectDB>")[0])
for m in re.finditer(r'<Element type="(timing|model)" name="([^"]+)">(.*?)</Element>', x, re.S):
    typ, name, body = m.groups()
    if want and name not in want: continue
    print(f"== {typ} {name}")
    if typ == "timing":
        for l, a, b in re.findall(r'<Effect label="([^"]*)" startTime="(\d+)" endTime="(\d+)"', body): print(f"  {a:>7} {b:>7} {l}")
        continue
    for li, layer in enumerate(re.findall(r"<EffectLayer>(.*?)</EffectLayer>", body, re.S)):
        for r, n, a, b in re.findall(r'ref="(\d+)" name="([^"]*)" startTime="(\d+)" endTime="(\d+)"', layer):
            s = db[int(r)]; keep = [kv for kv in s.split(",") if not kv.startswith("T_TEXTCTRL_Fade") and "=" in kv][:6]
            print(f"  L{li} {a:>7} {b:>7} {n:12s} " + ",".join(keep))
