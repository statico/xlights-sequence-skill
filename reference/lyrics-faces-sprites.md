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
