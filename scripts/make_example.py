#!/usr/bin/env python3
"""Template generator: copy to scripts/make_<song>.py and fill the tables. Everything sits on the beat grid from analyze.py
(beat k = B0 + BP*k ms). Run `python3 scripts/make_<song>.py`, then `scripts/render.sh <song>`, then check.py / blink.py.
No lyrics below on purpose: paste only what lyrics.py transcribed."""
from seqlib import *
# 1. Song: name (file stem), mp3 in xlights/music/, duration ms (get_audio.sh prints it), B0 and BP from analyze.py (BP = 60000/round(bpm))
S = Song("example", "example.mp3", 180000, 43.44, 468.75, "Song Title", "Artist")
bt, NB, DUR, B0, BP = S.bt, S.NB, S.DUR, S.B0, S.BP
# 2. Palettes: 4-6 stops, dark -> bright; accent() picks the bright non-white stops for pulses
EMBER = pal("#200010", "#8000FF", "#FF2A80", "#FF6A00", "#FFD000")
TOXIC = pal("#0A1A00", "#7FFF00", "#00FF20", "#FFB000", "#7FFF00")
VOID  = pal("#100020", "#4000A0", "#8000FF", "#C040FF", "#4000A0")
# 3. Sections in beats (bars = 4, phrases = 16) from analyze.py energy + the drum tab: intro / break / build / drop / call / outro
SECTIONS = [(0, 16, "intro"), (16, 80, "drop"), (80, 96, "break"), (96, 112, "build"), (112, 176, "drop"), (176, 192, "break"), (192, 256, "drop"), (256, NB, "outro")]
THEME = [[VOID], [EMBER, TOXIC], [VOID], [EMBER], [TOXIC, EMBER], [VOID], [EMBER, TOXIC, VOID], [VOID]]   # per section, cycled per phrase
def theme_at(ms): return next(THEME[i][0] for i, (k0, k1, _) in enumerate(SECTIONS) if ms < bt(k1) or k1 == NB)
S.theme_at = theme_at
# 4. House effect per 16-beat phrase inside drops (cycled). Gradient effects only; see reference/effects.md
S.DROP_FX = [
 ("Shockwave", "E_SLIDER_Shockwave_CenterX=50,E_SLIDER_Shockwave_CenterY=50,E_SLIDER_Shockwave_Start_Radius=1,E_SLIDER_Shockwave_End_Radius=120,E_SLIDER_Shockwave_Start_Width=25,E_SLIDER_Shockwave_End_Width=70,E_TEXTCTRL_Shockwave_Cycles=2.0,E_CHECKBOX_Shockwave_Blend_Edges=1," + fade(0, .5), None),
 ("Fire", "E_SLIDER_Fire_Height=90,E_SLIDER_Fire_HueShift=0,E_CHECKBOX_Fire_GrowWithMusic=1," + fade(0, .5), None),
 ("Spirals", "E_SLIDER_Spirals_Count=3,E_SLIDER_Spirals_Rotation=40,E_SLIDER_Spirals_Thickness=70,E_CHECKBOX_Spirals_Blend=1,E_CHECKBOX_Spirals_3D=1,E_TEXTCTRL_Spirals_Movement=2.0," + fade(0, .5), None),
 ("Meteors", "E_CHOICE_Meteors_Type=Palette,E_CHOICE_Meteors_Effect=Down,E_SLIDER_Meteors_Count=30,E_SLIDER_Meteors_Length=30,E_SLIDER_Meteors_Speed=15," + fade(0, .5), None),
]
# 5. Matrix theme per phrase in drops (callables (a_ms, b_ms, palette)); hold each for S.mxspan phrases
def hero(a, b, p):   # a sprite held over fire, coloured through the unmask
    S.pic("example_hero.png", a, b); S.fire(p, a, b)
S.MATRIX_DROP = [hero, lambda a, b, p: S.vu("Spectrogram Peak", p, a, b), lambda a, b, p: S.swirl(p, a, b), lambda a, b, p: S.galaxy(p, a, b)]
S.mxspan = 2
CALM = {"intro": ("Twinkle", "E_SLIDER_Twinkle_Count=8,E_SLIDER_Twinkle_Steps=60,E_CHECKBOX_Twinkle_ReRandom=1," + FADE),
        "break": ("Plasma", "E_CHOICE_Plasma_Color=Normal,E_SLIDER_Plasma_Style=1,E_SLIDER_Plasma_Line_Density=2,E_SLIDER_Plasma_Speed=6," + FADE),
        "build": ("Curtain", "E_CHOICE_Curtain_Edge=center,E_CHOICE_Curtain_Effect=close,E_SLIDER_Curtain_Swag=6,E_CHECKBOX_Curtain_Repeat=0,E_TEXTCTRL_Curtain_Speed=1.0," + fade(0, 0)),
        "outro": ("Plasma", "E_CHOICE_Plasma_Color=Normal,E_SLIDER_Plasma_Style=2,E_SLIDER_Plasma_Line_Density=2,E_SLIDER_Plasma_Speed=4," + fade(0, 3))}
for si, (k0, k1, kind) in enumerate(SECTIONS):
    theme = THEME[si]; a, b = bt(k0), min(bt(k1), DUR)
    if kind == "drop": p = S.drop(k0, k1, theme)
    else:
        n, s = CALM[kind]; p = theme[0]; S.house(n, s, p, a, b); S.floods_wash(p, a, b, (k1 - k0) / 8)
        if kind == "build":   # riser: triplets then double time then 4x on the matrix + floods, floods ramp up
            S.sub_pics(["example_hero.png", "example_hero2.png"], k0, k1, [2] * 8 + [3] * 4 + [4] * 4); S.fire(p, a, b)
        elif kind == "outro": S.txt("GOOD NIGHT", a, b, dir="wavey", speed=8, fo=2); S.plasma(p, a, b, 2, 2, 4, fo=3)
        else: S.plasma(p, a, b); S.beat_pics(["example_hero.png"], a, b)   # held sprite, one per bar would use S.sprite
S.calm_beats(SECTIONS, THEME)
# 6. Hits: crash onsets from crashes.py in ms (drummers anticipate; never snap to the grid), plus the user's markers
CRASH_MS = []                                             # paste the MS list printed by crashes.py
HITS = [((ms - B0) / BP, 1) for ms in CRASH_MS]
S.hits(HITS, lambda a, d: pal(accent(theme_at(a))[0]))
BIG = [bt(112)]                                           # ms of the big drop(s): white -> colour over 2 beats
for W in BIG:
    for r in LINES + FLOODS + [GROUP]:
        S.top(r).append(S.eff("On", "E_TEXTCTRL_Eff_On_Start=100,E_TEXTCTRL_Eff_On_End=0,T_CHOICE_LayerMethod=Max", WHITE, W, W + 2 * int(BP)))
    S.top(GROUP).append(S.eff("Shockwave", S.DROP_FX[0][1], pal(*accent(theme_at(W))), W, W + 2 * int(BP)))
# 7. Lyrics: paste lyrics.py output here in parse_lyrics format (who t word t word ...); leave empty for an instrumental
LYRICS = ""
WORDS, PHON = parse_lyrics(LYRICS) if LYRICS.strip() else ([], {f: [] for f in FACE})
def facepal(who, ms):
    ac = accent(theme_at(ms)); return pal(ac[0], "#FFFFFF", ac[-1]) if who == list(FACE)[0] else pal(ac[-1], "#FFFFFF", ac[0])
if FACE: S.faces(PHON, facepal)
S.apply_cues(S.load_cues(), ["example_hero.png", "example_hero2.png"])   # marks the user drew on the Cues track survive regeneration
S.write(S.timings(SECTIONS, WORDS), os.path.basename(__file__))
