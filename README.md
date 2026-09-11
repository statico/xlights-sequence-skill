# xlights-sequence-skill

An agent skill (Claude Code, Codex, Cursor, anything that reads `SKILL.md`) that turns any song into a beat-synced [xLights](https://xlights.org) light-show sequence: house lines, small models, floods, a pixel matrix with sprites and text, singing face props.

It packages a workflow and tools that came out of building a seven-song Halloween show and tuning it by ear:

- audio via `yt-dlp` + a clean ffmpeg re-encode
- beat grid, energy and section analysis with librosa, cymbal-crash detection that follows the drummer instead of the grid
- drum tabs as the map of fills, crashes and drops
- lyrics with local whisper (word timestamps) for lip-synced faces and matrix text
- a Python library that writes the `.xsq` directly, a headless render, and an `.fseq` decoder that checks what actually rendered (flicker, white flashes, blank effects, legible text)
- the xLights file-format and effect gotchas that cost the most time

## Install

```
git clone https://github.com/statico/xlights-sequence-skill ~/.agents/skills/xlights-sequence
ln -s ~/.agents/skills/xlights-sequence ~/.claude/skills/xlights-sequence      # Claude Code
ln -s ~/.agents/skills/xlights-sequence ~/.codex/skills/xlights-sequence       # Codex (also reads ~/.agents/skills)
ln -s ~/.agents/skills/xlights-sequence .cursor/skills/xlights-sequence        # Cursor, per project (also reads .agents/skills)
```

Requirements: xLights, ffmpeg, yt-dlp, Python 3.11+ with a venv holding `librosa numpy pillow` and `mlx-whisper` (Apple Silicon) or `faster-whisper`.

## Use

Ask the agent: "make an xLights sequence for Enter Sandman". It reads `SKILL.md`, copies `scripts/` into your show project, adapts `seqlib.py` to your models, and works through audio, analysis, generation, render and verification, then iterates on your feedback ("the drop at 0:55 needs more", "the props fade from black").

## Layout

```
SKILL.md                 the workflow (what the agent reads)
reference/               models and layers, effect strings, beats and hits, lyrics/faces/sprites, verify
scripts/                 get_audio.sh analyze.py crashes.py lyrics.py seqlib.py make_example.py sprite_example.py
                         render.sh fseq.py check.py blink.py textfit.py textcheck.py xsq_dump.py
```

Only use audio you are entitled to. Generated sequences are yours; this repo contains no song content.

MIT.
