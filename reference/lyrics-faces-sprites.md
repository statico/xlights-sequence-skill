# Lyrics, singing faces, sprites, text

## Lyrics
- `lyrics.py mp3 START END [START END ...] "Title by Artist"`: mlx-whisper large-v3-turbo, word timestamps, per clip (10-30 s). Whole-file runs hallucinate on chopped or stuttered vocals; instrumental hooks get transcribed as words (a xylophone melody came back as the chorus). Keep only words really sung.
- Format for `parse_lyrics`: one line per phrase, `who t word t word ... [t]` with who = pumpkin | ghost | both; a bare trailing timestamp closes the last word, a bare timestamp inside a line is a rest.
- Content filter: never write lyrics from memory, not even as the whisper prompt. Whisper output pasted from a tool result is fine.
- Split voices between props for call and response; alternate lines otherwise; `both` on choruses. Mouths must not move outside lyrics (check with the fseq decoder).

## Faces
Crude grapheme -> phoneme map in `seqlib.phonemes` (a/i/y -> AI, e -> E, o -> O, u -> U, m/b/p -> MBP, f/v -> FV, l -> L, w/q -> WQ, else etc), spread evenly over the word. `S.faces(phon, facepal)` fills rests with `rest`. Palette: mouth, eyes, outline, following the section theme.

## Sprites
- 35x17 (or your matrix size), white on black, 1-bit style, one PNG per frame, drawn with PIL in `scripts/sprite_<song>.py` (start from `scripts/sprite_example.py`). At 17 px only chunky silhouettes read; downscaled art is mush; diagonal lines come out ragged, so build letters and shapes from rectangles; a letter needs 5 px of width to read as M, 3 px reads as H.
- Colour: sprite on layer 0 with `T_CHOICE_LayerMethod=1 is Unmask`, a gradient effect (Plasma, Fire, Galaxy) on layer 1 shows through it.
- Beat animation: `S.beat_pics([f0,f1], a, b)` one frame per beat (exact); GIF frame rates are not.
- Movement: `S.sprite(f, a, b, [("right",1.5),("left",1.5)])` (PNG or GIF) re-issues the Pictures effect every bar with a new direction, so the position restarts each bar: fine for a wiggle, wrong for a drive. For continuous motion use one `S.pic(f,a,b,dir="right",speed=laps)` per phrase.
- Hold: one theme per 1-2 phrases (`S.mxspan`), one sprite per bar in calm sections, no sprite pops on hits.

## Text
- `S.txt("WORDS", a, b, dir="left", speed=12)`; short hook phrases of at most 4 words; scroll everything (static text on a 35 px matrix shows 6 letters); 2x speed for one-second cues. When the user tunes speeds in the GUI, read them back with `xsq_dump.py` and keep a `{start_ms: speed}` table in the generator.
- Font string `'Family' 18`, Regular face only; wx fake-bold smears at 17 px.
- Dump the ASCII matrix at every text moment; it must be legible.

## Matrix text that has to fit its window

A `left` scroll crosses the matrix once and stops, in `0.341*(11*chars+35)/speed` seconds (measured with a text-only
probe sequence: 16 chars clear in 7.2 s at speed 10, 3.6 s at 20, 1.8 s at 40). `S.txtfit(text, a, b)` inverts that to
pick the speed for the window you give it. Its `margin` defaults to `.85`, not 1.0: the formula counts characters, not
glyph widths, so it overestimates on short strings — a 10-char line at the "exact" speed cleared a full second early.
Running slightly slow and letting the effect's fade-out cover the tail is the safe side of that error.

**Text over a background effect is a stencil.** With `1 is Unmask` (the default in `S.txt`) the layer below shows only
through the glyphs, so wherever *no* Text effect is active the background shows at full brightness. Short gaps between
lyric lines therefore read as random full-screen flashes, not as text. Rules:

- Lyric lines must tile the whole window with no holes: each line holds until the next one starts, the last until the
  section ends. Don't cap a line's length and leave the remainder bare.
- Watch the seams. A matrix theme held for `S.mxspan` phrases is called once per span, so a 48-beat chorus is two
  calls; the first line of each call has to start at that call's own `a`, not at its sung time, or the seam is bare.
- A text window that straddles a phrase boundary gets clipped into two effects, and each one restarts the scroll from
  the right, so neither half crosses. Emit a straddling hook whole from the phrase that owns its start and skip it in
  the next phrase (keep a `set()` of the ones already emitted); don't clip it.
- `S.txt(..., mask=False)` blends solid glyphs over the background instead (layer method Max), for when the background
  should stay visible the whole time.

Audit both with the two scripts: `textfit.py` reads the .xsq and compares predicted traversal to each window (target
ratio ~1.18; CUT never crosses, EARLY leaves the background bare), and `textcheck.py` decodes the .fseq and checks the
text is still lit 85% of the way through its window and that the matrix is never almost fully lit.
