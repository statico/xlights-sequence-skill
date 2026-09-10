"""usage: tmp/venv/bin/python scripts/blink.py xlights/sequences/<song>.fseq
Per model: hard-on / hard-off edges (max brightness changes >90/255 in one frame) and square waves (flat and bright, then cut),
plus the effects active in the worst 10 s window. Drops should show ~0 hard-offs on lines and floods.
Face phoneme swaps and sprite frame changes count as square waves; that is fine."""
import sys, os, re, numpy as np; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import fseq
path = sys.argv[1]; F, step, starts = fseq.load(path); x = open(path.replace(".fseq", ".xsq")).read()
db = re.findall(r"<Effect>(.*?)</Effect>", x.split("<EffectDB>")[1].split("</EffectDB>")[0])
els = {}
for m in re.finditer(r'<Element type="model" name="([^"]+)">(.*?)</Element>', x, re.S):
    els[m.group(1)] = [(int(a), int(b), n, int(r)) for r, n, a, b in re.findall(r'ref="(\d+)" name="([^"]*)" startTime="(\d+)" endTime="(\d+)"', m.group(2))]
groups = {g: ms.split(",") for g, ms in re.findall(r'<modelGroup [^\n]*?name="([^"]+)"[^\n]*?models="([^"]*)"', open(os.path.join(fseq.SHOW, "xlights_rgbeffects.xml")).read())}
def active(model, t):
    out = []
    for m in [model] + [g for g, ms in groups.items() if model in ms]:
        for a, b, n, r in els.get(m, []):
            if a <= t < b: s = db[r]; typ = re.search(r"VUMeter_Type=([^,]*)", s); out.append(m + ":" + n + ("[" + typ.group(1) + "]" if typ else ""))
    return out
for n, s in starts.items():
    if n.startswith("_"): continue
    w = fseq.size(n) or 150
    m = F[:, s:s + w].max(1).astype(int); d = np.diff(m); on = np.where(d > 90)[0]; off = np.where(d < -90)[0]
    mm = F[:, s:s + w].reshape(len(F), -1, 3).max(2).mean(1); dm = np.diff(mm)
    sq = [i for i in np.where(dm < -90)[0] if i > 4 and (abs(dm[i - 4:i]) < 3).all() and mm[i] > 120]
    print(f"{n:8s} hard-on {len(on):4d} hard-off {len(off):4d} square {len(sq):4d}" + (f" (e.g. {sq[len(sq) // 2] * step / 1000:.2f}s)" if sq else ""))
    if len(off):
        ts = off * step / 1000; hist = np.bincount((ts // 10).astype(int)); worst = hist.argmax() * 10
        print(f"          worst 10s window {worst}-{worst + 10}s ({hist.max()} hard-offs); active there:", sorted(set(sum((active(n, int(t * 1000)) for t in ts[(ts >= worst) & (ts < worst + 10)][:20]), []))))
