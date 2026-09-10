# Effect strings that work

An xsq effect is `KEY=VAL,KEY=VAL,...`. Unknown keys are silently ignored (a typo means defaults, not an error). Confirm names in the xLights source (deepwiki on `xLightsSequencer/xLights` answers "what settings keys does effect X have").

Prefixes: `E_` effect settings, `T_` timing/blend (`T_CHOICE_LayerMethod=Normal|Max|1 is Unmask`, `T_TEXTCTRL_Fadein`, `T_TEXTCTRL_Fadeout`), `C_` colour (palettes are `C_BUTTON_Palette1=#RRGGBB,C_CHECKBOX_Palette1=1,...`).

| Effect | Settings that matter | Notes |
|---|---|---|
| On | `E_TEXTCTRL_Eff_On_Start=100,E_TEXTCTRL_Eff_On_End=35` | The beat pulse. Start 100 end floor, one beat long, layer Max on the house, Normal for hits on top |
| VU Meter | `E_CHOICE_VUMeter_Type=Timing Event Timed Sweep\|Bar Bounce\|Sweep 2\|Random Bar\|Bars,E_CHOICE_VUMeter_TimingTrack=Beats,E_SLIDER_VUMeter_Bars=12` | Timing-event types follow a timing track and render headless. `Timing Event Jump` = hard blink; `Song.add` rewrites it (and any timing-event type on `SMALL` models) into decaying `On` pulses, so never add it around `Song.add`. `Level Pulse`/`Level Bar` flicker frame by frame. `Spectrogram Peak`, `Volume Bars` are good on the matrix and load audio headless |
| Pictures | `E_TEXTCTRL_Pictures_Filename=sprites/x.png,E_CHOICE_Pictures_Direction=none\|left\|right\|up\|down,E_TEXTCTRL_Pictures_Speed=1.5,E_CHOICE_Scaling=Scale To Fit,E_CHECKBOX_Pictures_TransparentBlack=1` | Path show-folder-relative. Speed = crossings over the effect's duration; the position restarts every effect, so one long effect per phrase, not one per bar. GIF frame rates are inexact; one PNG per beat is exact |
| Text | `E_TEXTCTRL_Text=WORDS,E_CHOICE_Text_Dir=left\|wavey\|none,E_SLIDER_Text_Speed=12,E_FONTPICKER_Text_Font='Family' 18` | Speed is a SLIDER key. Display fonts with only a Regular face smear when asked for bold |
| Faces | `E_CHOICE_Faces_FaceDefinition=<faceInfo name>,E_CHOICE_Faces_Eyes=Auto,E_CHECKBOX_Faces_Outline=1,E_CHOICE_Faces_Phoneme=AI\|E\|O\|U\|MBP\|FV\|L\|WQ\|etc\|rest` | One effect per phoneme. Palette order mouth, eyes, outline. Eyes=Auto blinks during rest |
| Color Wash | `E_TEXTCTRL_ColorWash_Cycles=4.0` | Stays 3-4 discrete colours; cycles = bars in the phrase for beat-locked motion |
| Fire | `E_SLIDER_Fire_Height=90,E_CHECKBOX_Fire_GrowWithMusic=1` | Grows from black over ~4 s: put a floor under it |
| Bars | `E_SLIDER_Bars_BarCount=6,E_CHOICE_Bars_Direction=Left,E_CHECKBOX_Bars_Gradient=1,E_TEXTCTRL_Bars_Cycles=4.0` | `E_CHECKBOX_Bars_Highlight=1` on the matrix is solid white; steps every 150 ms on small models |
| Shockwave | `E_SLIDER_Shockwave_Start_Radius=1,E_SLIDER_Shockwave_End_Radius=120,E_SLIDER_Shockwave_Start_Width=25,E_SLIDER_Shockwave_End_Width=70,E_TEXTCTRL_Shockwave_Cycles=2.0` | The drop-moment effect |
| Plasma / Wave / Spirals / Galaxy / Meteors / Ripple / Pinwheel | see `seqlib.py` helpers | Blend into real gradients; Plasma slow settings are the safe calm-section effect |
| Single Strand | `E_CHOICE_SingleStrand_Colors=Palette,E_CHOICE_Chase_Type1=Left-Right,E_SLIDER_Number_Chases=2,E_TEXTCTRL_Chase_Rotations=4.0,E_CHECKBOX_Chase_3dFade1=1` | Chases on lines and prop outlines |

Discrete-colour effects even with an 8-stop palette: Color Wash, Marquee, Single Strand, Butterfly (Palette), Liquid.

## Palettes

- 4-6 stops. Beat pulses use `accent(p)`: bright stops that are not near-white. White + red reads as Christmas; orange/purple/green (+ white for Halloween) is the safe set.
- A theme per section (list of palettes cycled per phrase); faces follow the theme too.

## xsq skeleton

`<xsequence ... ModelBlending="true">` with `<head>` (`<sequenceType>Media</sequenceType>`, absolute `<mediaFile>`, `<sequenceTiming>25 ms</sequenceTiming>`), `<ColorPalettes>`, `<EffectDB>`, `<DisplayElements>` (timing tracks then models), `<ElementEffects>` with `<Element type="timing">` and `<Element type="model">` each holding `<EffectLayer>` lists of `<Effect ref= name= startTime= endTime= palette=/>`. `seqlib.Song.write` emits all of it and validates with minidom. Timing tracks worth emitting: `Sections`, `Bars`, `Beats`, `Lyrics`, `Cues` (empty, for the user to draw on).
