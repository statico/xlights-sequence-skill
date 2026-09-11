---
name: xlights-sequence
description: Use when asked to make, generate, fix or tune an xLights light-show sequence (.xsq/.fseq) for a song: beat-synced house lights, matrix sprites and text, singing faces, cymbal/drop accents, or when a rendered sequence flickers, flashes white, teleports sprites or shows an unrecognisable shape.
---

# xLights sequence from any song

Generate the `.xsq` from a Python script on a fitted beat grid, render it headless, decode the `.fseq` and look at what actually rendered. Never hand-edit in the GUI: regeneration overwrites it. Skill root = the directory holding this file; `scripts/` here are copied into the show project on first use.

## 0. Setup (once per show folder)

1. Show folder layout: `xlights/` (opened in xLights, holds `xlights_rgbeffects.xml`, `xlights_networks.xml`), `xlights/sequences/`, `xlights/music/`, `xlights/sprites/`, `scripts/`, `tmp/` (disposable).
2. `python3 -m venv tmp/venv && tmp/venv/bin/pip install librosa numpy pillow mlx-whisper` (mlx-whisper is Apple Silicon; elsewhere use `faster-whisper` and edit `lyrics.py`). Needs `ffmpeg`, `yt-dlp`, xLights installed (`render.sh` has the macOS path).
3. `cp <skill>/scripts/*.py <skill>/scripts/*.sh scripts/` then adapt the constants at the top of `scripts/seqlib.py` (`LINES`, `ROOFS`, `SMALL`, `FLOODS`, `FACE`, `GROUP`, `FONT`) to the models in `xlights_rgbeffects.xml`; trim `FACE` to the props you have (`{}` if none). Sprite sizes come from the matrix model, not a constant. Read [reference/models-and-layers.md](reference/models-and-layers.md) first: which models may share a group decides half the bugs.

## 1. Audio

```
scripts/get_audio.sh "<artist> <title>" <song>     # yt-dlp ytsearch1 -> mp3, then a clean ffmpeg re-encode to xlights/music/<song>.mp3
```
Or tell the user: `yt-dlp -x --audio-format mp3 "ytsearch1:ARTIST TITLE official audio"` and drop the file in `music/`; then run only the re-encode line. Only use audio the user is entitled to. The sequence must point at the re-encoded copy inside the show folder (absolute `<mediaFile>`); the original download made the GUI report "Media File Missing or Corrupted" and the headless render never checks.

## 2. Analyse

```
tmp/venv/bin/python scripts/analyze.py xlights/music/<song>.mp3      # bpm, fitted grid B0/BP (ms), per-second rms/bass/treble/onset, segment bounds
```
Round the bpm, `BP = 60000/bpm`, keep `B0` from the fit, then check beat 0 is a downbeat (onset column) and shift by whole beats if bars land wrong. Sections are beat indices, bars = 4 beats, phrases = 16. Drops = bass jumps, breaks = bass gone, builds = rising onset density before a drop.

**Drum tabs for inflection points.** Web-search `"<title>" "<artist>" drum tab` (Songsterr, Ultimate Guitar, drumtabs sites) and read the structure: which bars have crashes, fills before a chorus, stops, half-time or double-time sections, the 'and-of-4' anticipations. Turn bar numbers into beat indices (`(bar-1)*4`) and confirm each with `crashes.py` / the onset column. Never paste tab content into the repo, use it as a map only. Then read [reference/beats-and-hits.md](reference/beats-and-hits.md).

## 3. Lyrics (optional, for singing props / matrix text)

```
tmp/venv/bin/python scripts/lyrics.py xlights/music/<song>.mp3 10 32 45 70 "Title by Artist"
```
Whole-file whisper hallucinates on chopped vocals: 10-30 s clips only, prompt = title and artist only. Keep only words really sung, drop what whisper heard in instrumental parts. **Never write song lyrics from memory anywhere** (script, prompt, report): reproducing lyrics trips the API content filter and kills the agent. Paste only whisper's own output. See [reference/lyrics-faces-sprites.md](reference/lyrics-faces-sprites.md).

## 4. Generate

Copy `scripts/make_example.py` to `scripts/make_<song>.py` and fill the tables (effect strings, palettes and the xsq skeleton: [reference/effects.md](reference/effects.md)): `Song(...)`, palettes, `SECTIONS`, `THEME`, `DROP_FX`, `MATRIX_DROP`, hits, lyrics, sprites. Rules that came from a real house, in priority order:

- **No white flashes, no hard on/off blinks.** Beat pulses are palette colours decaying 100 -> `S.floor` (35 %), layer Max, so they melt into the house effect. `accent()` strips near-white stops. A big musical moment (drop after a build) is the one place for white -> colour: `On` Max WHITE over 2 beats plus a Shockwave. `S.eff` rewrites every `On` 100->0 to end at `S.floor`, so write 100->0 and let the floor apply (set `S.floor=0` only if you truly want black).
- **Hold things.** One matrix theme per 1-2 phrases (`S.mxspan`), one sprite per bar, moving Pictures = one effect per phrase with `speed = laps`. Per-beat sprite flips, per-crash sprite pops, and 4 short effects instead of one long one all read as flicker or teleporting.
- **Hits follow the drummer**, not the grid: crash onsets from `crashes.py` in ms, `(ms-B0)/BP` fractional beats, often 50 ms early or on the 'and'.
- Text scrolls (`dir=left`; a 17 px matrix shows about 6 letters at a time). Size it with `S.txtfit(text, a, b)` rather than guessing a speed, and remember it is a stencil over the layer below: lyric lines must tile their window with no gaps or the background flashes through. Font: a Regular face only, never bold.
- Every section has something moving on the house, the matrix and the floods; vary effects phrase to phrase, pulsing gets old.

```
python3 scripts/make_<song>.py && scripts/render.sh <song>
```

## 5. Verify from the fseq, not the GUI

```
tmp/venv/bin/python scripts/check.py xlights/sequences/<song>.fseq 12 43.5 61     # per-section lit%/colours, flicker seconds, white-flash frames, ASCII matrix at those times
tmp/venv/bin/python scripts/blink.py xlights/sequences/<song>.fseq              # hard on/off and square-wave edges per model, with the effects active there
python3 scripts/textfit.py                                                      # every scrolling Text: does the line cross its window, or clear early and let the background flash?
tmp/venv/bin/python scripts/textcheck.py                                        # the same question answered from the rendered frames
```
Fix what they show: a section with 0 % lit or 1-3 colours is a flat/blank effect (typo in a key = silent default); text must be legible in the ASCII dump; drops should have ~0 hard-offs on lines and floods. [reference/verify.md](reference/verify.md) has the fseq layout and what each number means.

## 6. Iterate by ear with the user

They name timestamps ("the drop at 0:55", "the props fade from 0 % at 1:52", "the dragster teleports"). Map each to the table in [reference/beats-and-hits.md](reference/beats-and-hits.md) (symptom -> cause). Marks they draw on a `Cues` timing track are kept across regeneration (`S.apply_cues`); a split in their `Sections` track is a marker: onset-check the mp3 there and put the hit at the marker. If they edited text speed/start/end in the GUI, `scripts/xsq_dump.py` lists their values so you can fold them into the generator before the next run. xLights won't reload an open sequence: File > Close Sequence (No) then Open.

## Common mistakes

| Symptom | Cause |
|---|---|
| Whole model blinks on the beat | VU Meter `Timing Event Jump` (225 ms full-on then black) or any timing-event sweep on a ~50 px model. `Song.add` silently turns both into decaying `On` pulses, so the seqlib tables may still name `Timing Event Jump`; only effects added around `Song.add` can blink |
| Props fade from black | Outline palette starts with dark stops; pass `accent()` colours. The floor only helps models in the house group |
| Layer effect invisible | Something above it on a Normal blend, or a VU timing-event layer (opaque black between bars). New effects go on `S.top()` |
| Matrix solid white | `Bars` with `Highlight=1`; Spectrogram Line / Circle Line render near-black instead |
| Effect renders flat | Wrong settings key (silently ignored). Confirm key names against xLights source |
| Sequence unchanged in GUI | It is open; close without saving and reopen |
