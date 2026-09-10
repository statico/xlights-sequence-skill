# Render and verify

## Render
`scripts/render.sh <song>` = `xLights -r /abs/path/<song>.xsq`, serialised with a mkdir lock (parallel agents share one xLights). Exit 0 only proves the file parsed; the `.fseq` lands next to the `.xsq`. Media is never checked headless.

## fseq v2 layout (zstd)
- Header `<4sHBBHIIBBBBBBQ`: `h[1]` data offset, `h[5]` channel count, `h[6]` frames, `h[7]` step ms. Block count is 12 bits: `((byte20 >> 4) << 8) | byte21`; sparse-range count is byte 22. Blocks (`<II` frame, size) at 32; ranges (3-byte start, 3-byte count) after them.
- Sparse output packs one range per controller, in `xlights_networks.xml` `<Controller>` order, so `!ctrl2:N` is file offset `size(ctrl1)+N-1`, not `absolute_start+N-1`.
- Channel count = sum of controller sizes, not universes x 510.
- Matrix, serpentine, StartSide=T: channel row 0 is the top row, reverse odd rows when dumping. Pictures/Text render upright, so sprites need no flipping.
- Python 3.14 has `compression.zstd`; older needs `pip install zstandard`.

`fseq.py` does all of this: `F, step, starts = load(path)`; `matrix(F, step, t)`; `ascii(F, step, t)`; `size(name)`.

## What to look at
- `check.py`: per section (from the `Sections` timing track) matrix lit % and distinct colours, flood mean/max, colour counts per prop/line. 0 % lit or 1-3 colours = flat or blank effect (bad key, black palette, hidden layer). Flicker: seconds with >=6 brightness jumps >40/255 on a model (beat pulses give ~4/s in drops, jitter 10+). White-flash frames: all floods >200 on every channel. ASCII dumps at the given times.
- `blink.py`: hard-on/hard-off edges (>90/255 in one 25 ms frame) and square waves (flat bright then cut) per model, plus which effects are active in the worst window. Drops should show ~0 hard-offs on lines and floods. Face phoneme swaps and sprite changes count as square, that is fine.
- Photosensitivity: nothing above 3 Hz on any model.

## GUI round trips
- xLights won't re-read an open sequence: File > Close Sequence (No) then File > Open. `RenderCache` is irrelevant.
- `xsq_dump.py <xsq> [model]` lists every effect with start/end and its settings string: use it to harvest the user's GUI tweaks (text speed, stretched starts/ends, a marker in `Sections`) before regenerating, and to diff the user's saved file against a fresh generator run.
