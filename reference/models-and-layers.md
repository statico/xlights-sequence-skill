# Models, groups and layers

Read `xlights/xlights_rgbeffects.xml` before writing the generator: `<model name= DisplayAs= StartChannel="!controller:N" ...>` and `<modelGroup name= models="a,b,c">`. Classify each model:

| Class | Example | Notes |
|---|---|---|
| Lines (>150 px) | roof, porch outlines | Moving effects, VU sweeps and bars all look good |
| Small (~50 px) | bushes, trunk, branch | Any moving effect steps or strobes at 10 Hz. Only slow Plasma / Color Wash / Fire; beat sync = decaying `On` pulses |
| Matrix | 35x17 P5 or similar | Sprites, text, Plasma/Wave/Fire/Galaxy/Spirals/Meteors/Spectrogram Peak/Volume Bars. Bars, Spectrogram Line/Circle Line render black; Bars Highlight = solid white |
| Face props | pumpkin, ghost (Custom models with `faceInfo`) | Driven by `Faces` effects; colour via the Faces palette (mouth, eyes, outline) plus an `Outline` submodel effect |
| Floods | DmxFloodlight | Render black when driven only through a group (each DMX channel becomes a white node): one effect row per flood |

## Groups

- Make a `house` group (`GROUP`) of every pixel-line model, i.e. `LINES`, which includes the `SMALL` ones. Face props must NOT be in it: with ModelBlending the group effect shows through the face's black pixels and the mouth "inherits" the roof. Floods stay out too.
- Consequence: a floor, fade or palette fix on the house group never reaches the props. Props read as "fading from black" when their Outline effect (Color Wash / Bars) runs through a palette whose first stops are dark: give outlines `ramp(p)`, which is `accent(p)` with a 45% copy of each stop interleaved.
- A moving outline effect needs the ramped palette **and** a blending effect. Single Strand / Color Wash / Marquee stay 3-4 discrete colours even with an 8-stop palette, so a chase along an outline is a square wave that reads as a blink; Bars (Gradient + 3D), Meteors and Wave render 25-46 brightness levels travelling along it.
- A `Faces` effect with `E_CHECKBOX_Faces_Outline=1` draws the outline itself and paints over the `Outline` submodel layers, so the prop's outline sits at one flat colour for the whole song. `Song.faces` sets it to 0 whenever that submodel has effects, and the writer emits one `<SubModelEffectLayer>` per non-empty submodel layer so `S.top("<prop>/Outline")` works like any other model.
- The `SMALL` models strobe under fast house-group effects (Meteors, Wave, Pinwheel). Give them their own calm Color Wash at layer index 1 (Normal blend hides the group effect) and leave their beat pulses on layer 0: that took one bush from 428 brightness jumps with 20 flicker seconds to 192 with none.
- Prop outlines: a submodel named `Outline` with the node ranges from the `FaceOutline` line of `faceInfo`, stored in the xsq as `<SubModelEffectLayer name="Outline">` inside the model element. Submodel effects overwrite the model's face pixels (black included). VU timing-event types render flat on submodels: use cycle-timed effects (Single Strand chase, Bars, Color Wash with cycles = bars in the phrase).

## Layers

- `EffectLayer` 0 is the TOP. A Normal-blend layer hides everything below wherever it is non-black (black is transparent). Max lets lower layers through.
- A VU Meter timing-event layer hides everything below it even with Max (opaque black between bars). Anything that must show over it (pulses, hits, cues, floors) goes above it.
- Two effects overlapping on one layer: only the first shows. A one-beat hit hides a half-beat hit that starts inside it.
- Add on top with `S.top(model)` (inserts a new layer 0). Never rotate layers by index; that put a line VU Meter above the pulses and the lines blinked.
- House group order that works: 0 house effect, 1 floor (`On` 50 % when the effect is Fire, which grows from black over ~4 s), 2 beat VU layer.
- Empty layers are stripped at write; the EffectDB de-duplicates identical settings strings, so `ref` numbers are indices into it.

## Controllers and channels (for decoding)

- `xlights_networks.xml`: one `<network>` per universe; the universe number is in the legacy `BaudRate` attribute. `<Controller Name=...>` order is the fseq sparse-range order.
- Model `StartChannel="!ctrl:N"` is controller-relative. Chained models use `ModelChain=">prev"`; that `>` breaks `grep '<model[^>]*>'`.
