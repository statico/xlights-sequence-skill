"""fseq v2 (zstd, sparse) decoder for xLights renders. Import-able:
    F, step, starts = load("xlights/sequences/x.fseq")   # F[frame, channel] uint8; starts[model] = channel offset in F
    matrix(F, step, t) -> (rows, cols, 3) array at t seconds, top row first;  ascii(F, step, t) -> printable dump
Model offsets come from xlights_rgbeffects.xml (controller-relative StartChannel) mapped through the fseq sparse ranges,
which xLights writes one per controller in xlights_networks.xml <Controller> order.
Set XLIGHTS_SHOW if the show folder is not ./xlights. Matrix model name: XLIGHTS_MATRIX (default "matrix")."""
import struct, re, os, numpy as np
try:
    from compression import zstd            # Python 3.14+
    _dec = lambda b: zstd.ZstdDecompressor().decompress(b)
except ImportError:
    import zstandard                        # pip install zstandard
    _dec = lambda b: zstandard.ZstdDecompressor().decompress(b)
SHOW = os.environ.get("XLIGHTS_SHOW", "xlights")
MATRIX_NAME = os.environ.get("XLIGHTS_MATRIX", "matrix")
_models = {}

def load(path):
    d = open(path, "rb").read(); h = struct.unpack_from("<4sHBBHIIBBBBBBQ", d, 0); off, nch, nfr, step = h[1], h[5], h[6], h[7]
    nb = ((d[20] >> 4) << 8) | d[21]; nr = d[22]
    blocks = [struct.unpack_from("<II", d, 32 + 8 * i) for i in range(nb)]
    o = 32 + 8 * nb
    ranges = [(int.from_bytes(d[o + 6 * i:o + 6 * i + 3], "little"), int.from_bytes(d[o + 6 * i + 3:o + 6 * i + 6], "little")) for i in range(nr)]
    raw = b""; p = off
    for fr, sz in blocks:
        if sz: raw += _dec(d[p:p + sz]); p += sz
    F = np.frombuffer(raw, np.uint8)[:nfr * nch].reshape(nfr, nch)
    net = open(os.path.join(SHOW, "xlights_networks.xml")).read()
    ctrls = re.findall(r'<Controller [^>]*?Name="([^"]+)"', net)
    base = {}; acc = 0                       # file offset of each controller's range (ranges are concatenated in controller order)
    for i, c in enumerate(ctrls):
        base[c] = acc; acc += ranges[i][1] if i < len(ranges) else 0
    x = open(os.path.join(SHOW, "xlights_rgbeffects.xml")).read()
    starts = {}
    for m in re.finditer(r'<model [^\n]*?name="([^"]+)"[^\n]*?StartChannel="!(\w+):(\d+)"[^\n]*', x):   # one line per model; [^>] would stop at ModelChain=">prev"
        n, c, s = m.groups(); starts[n] = base.get(c, 0) + int(s) - 1
        _models[n] = dict(re.findall(r'(\w+)="([^"]*)"', m.group(0)))
    starts["_ranges"] = ranges
    return F, step, starts

def size(name):
    """Channel count of a model, from its own attributes where possible, else the gap to the next model start."""
    a = _models.get(name, {})
    if a.get("DisplayAs") == "Matrix": return int(a["NodesPerString"]) * int(a["NumStrings"]) * 3
    if "PixelCount" in a: return int(a["PixelCount"]) * 3
    if a.get("DisplayAs") == "DmxFloodlight": return 3
    return None

def matrix_dims():
    a = _models.get(MATRIX_NAME, {}); rows = int(a.get("StrandsPerString", 17)); n = int(a.get("NodesPerString", 595)) * int(a.get("NumStrings", 1))
    return rows, n // rows

def matrix(F, step, t, starts=None):
    s = (starts or {}).get(MATRIX_NAME) or _matrix_start; rows, cols = matrix_dims()
    M = F[int(t * 1000 / step), s:s + rows * cols * 3].reshape(rows, cols, 3)
    return np.array([M[r][::-1] if r % 2 else M[r] for r in range(rows)])   # serpentine, StartSide=T: channel row 0 is the top row

def ascii(F, step, t, starts=None):
    M = matrix(F, step, t, starts).max(2)
    return "\n".join("".join("#" if v > 128 else ("+" if v > 0 else ".") for v in row) for row in M)

_matrix_start = 0
_load = load
def load(path):   # remember the matrix start so matrix()/ascii() work without passing starts
    global _matrix_start
    F, step, starts = _load(path); _matrix_start = starts.get(MATRIX_NAME, 0); return F, step, starts
