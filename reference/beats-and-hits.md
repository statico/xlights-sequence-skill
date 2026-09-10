# Beat grid, hits, drums

## Grid

`analyze.py` fits `beat_k = B0 + BP*k` (ms) through librosa's beats. Beat tracking quantises to the hop: trust the round bpm over the raw median, keep B0 from the fit. Before blaming the tempo for "off" hits, run a drift check: per 16 beats, find the phase shift that best aligns onset peaks with the grid. A steady song holds within ~50 ms all the way; then bad hits are bad picks, not drift.

## Crashes and anticipations

Drummers crash on the 'and of 4' before a downbeat and run off-beat crashes through choruses. On-beat pulses feel late there. `crashes.py <mp3> B0 BP` finds them grid-free: treble (4-11 kHz) onsets that still ring 250-400 ms later (crash yes, hi-hat no). Output: `(ms, fractional beat, sustain ratio, attack)` and an `MS = [...]` list. Paste the ms list, convert `(ms-B0)/BP`, feed `S.hits([(beat,len)], colour)`. Never snap to the grid.

Use the drum tab as the map: where the tab shows crashes, fills, stops, half-time, count the bar and look for the onset there. A user's marker (a split in the `Sections` timing track) beats both: once it sat an eighth after the grid beat and the onset check agreed with the marker.

## Builds and subdivisions

Risers before a drop: `S.sub_pics(frames, k0, k1, [3,3,3,3,2,2,4,4])` puts that many sprite frames inside each beat (triplets, then double time, then 4x), floods pulse at the same subdivision. Mirror what the user hears: "triplet build", "eighth-note accents", "four big quarters".

## Emphasis

- Ordinary hit: `On` Normal 100->floor, one beat, on a fresh top layer of every line and flood, in a contrast colour (a theme colour the section is not using) so it reads as a colour change.
- Big moment (drop after a build, the marker): `On` Max WHITE 100->0 (rewritten to the floor by `S.eff`) over 2 beats on lines, floods and house, plus a Shockwave on the house, so everything fades white -> colours.

## Symptom -> cause table (from user feedback)

| User says | Fix |
|---|---|
| "too blinky / jarring" | pulses to a floor (35 %), Max blend, or 2x the decay |
| "cymbal hits are off" | crashes.py, not the grid; check drift first |
| "flashes of X on the matrix" | a sprite pop on every crash; hold one sprite per bar/phrase |
| "sprite teleports" | one Pictures effect per bar; make it one per phrase with speed = laps |
| "moving way too fast" | halve Pictures speed (it is laps per effect) |
| "text just says SKELETON S" | speed too low for the length; ~1 letter per 100 ms at speed 15 on 35 px |
| "props fade from 0 %" | outline palette starts dark, use accent stops |
| "solid white on the matrix" | Bars Highlight, or a near-white palette stop on a gradient effect |
| "not sure what that shape is" | 17 px sprite too detailed; redraw as chunky silhouette |
| "emphasise the drop at m:ss" | white -> colour hit at their marker, remove the grid hit next to it |
