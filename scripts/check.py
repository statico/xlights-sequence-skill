"""usage: tmp/venv/bin/python scripts/check.py xlights/sequences/<song>.fseq [t t ...]
Per section (from the xsq `Sections` timing track): matrix lit % and distinct colour count, then colour count per other model;
flicker seconds per model; white-flash frames on the floods; ASCII matrix dumps at the given times.
A section with 0 % lit or 1-3 colours is a flat/blank effect. Beat pulses give ~4 jumps/s in drops, jitter gives 10+."""
import sys, os, re, numpy as np; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import fseq
path = sys.argv[1]; F, step, starts = fseq.load(path)
x = open(path.replace(".fseq", ".xsq")).read()
sec = [(int(a) / 1000, int(b) / 1000, l) for l, a, b in re.findall(r'<Effect label="([^"]*)" startTime="(\d+)" endTime="(\d+)"/>', x.split('name="Sections">')[1].split("</Element>")[0])]
fr = lambda t: int(t * 1000 / step)
cc = lambda A: len(set(map(tuple, A.reshape(-1, 3)[::7])))
models = {n: (s, fseq.size(n) or 150) for n, s in starts.items() if not n.startswith("_")}
floods = [n for n in models if fseq._models[n].get("DisplayAs") == "DmxFloodlight"]
rows, cols = fseq.matrix_dims(); mx = models.get(fseq.MATRIX_NAME)
others = [n for n in models if n != fseq.MATRIX_NAME and n not in floods]
print(f"{len(F)} frames, {step} ms; matrix {cols}x{rows}; sections: start  matrix%lit colours | floods mean/max | " + " ".join(f"{n}" for n in others))
for a, b, n in sec:
    M = F[fr(a):fr(b), mx[0]:mx[0] + mx[1]]; lit = (M.reshape(len(M), -1, 3).max(2) > 0).mean()
    fl = np.concatenate([F[fr(a):fr(b), models[f][0]:models[f][0] + 3] for f in floods], 1) if floods else np.zeros((1, 3))
    print(f"{n:8s} {a:6.1f}  {lit:5.2f} {cc(M):5d} | {fl.mean():5.1f}/{fl.max():3d} | " + " ".join(f"{cc(F[fr(a):fr(b), models[o][0]:models[o][0] + models[o][1]]):{len(o)}d}" for o in others))
print("flicker check (seconds with >=6 brightness jumps >40/255):")
for n, (s, w) in models.items():
    m = F[:, s:s + w].mean(1); d = np.abs(np.diff(m)); ts = (np.where(d > 40)[0] * step // 1000); bad = sorted({t for t in ts if (ts == t).sum() >= 6})
    print(f"  {n:8s} jumps {len(ts):4d}  seconds with >=6: {bad[:20]}")
if floods:
    w = np.stack([F[:, models[f][0]:models[f][0] + 3] for f in floods], 1)
    print("white-flash check: frames where all floods >200 on every channel:", int((w.min(axis=(1, 2)) > 200).sum()))
for t in map(float, sys.argv[2:]): print(f"-- matrix t={t}"); print(fseq.ascii(F, step, t))
