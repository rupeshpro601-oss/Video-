# Video-

Episodic video series built with the **series-writer** skill + AI image generation, assembled with Python and ffmpeg.

## Current series: ECHO RELAY

Sci-fi mystery, 8-episode season. A lone relay technician beyond Saturn receives a distress
broadcast in her own voice, timestamped fourteen days in the future.

See [`series/echo-relay/SERIES_BIBLE.md`](series/echo-relay/SERIES_BIBLE.md).

## Watch

- **EP01 — "The Voice That Called Ahead"** — [`series/echo-relay/ep01.mp4`](series/echo-relay/ep01.mp4)
  1080×1920 (9:16), 52 s, 30 fps, H.264 + AAC ambient score.

## Structure

```
series/echo-relay/
├── SERIES_BIBLE.md      # series canon: characters, season arc, timeline, open threads
├── ep01.mp4             # finished episode video
├── ep01_score.wav       # synthesized episode score
├── episodes/EP01.md     # script / shot list / narration
├── boards/src/          # AI-generated story boards (1080x896 source stills)
├── stills/              # composed 9:16 frames (blur-fill + captions + title card)
└── build/               # reproducible build scripts
    ├── compose.py       # boards -> 9:16 stills with captions
    ├── score.py         # numpy-synthesized ambient score
    └── assemble.py      # ffmpeg zoompan + drawtext -> ep01.mp4
```

## Rebuild EP01

```bash
cd series/echo-relay/build
python3 compose.py
python3 score.py
python3 assemble.py
```

Requires: `pillow`, `numpy`, `matplotlib` (fonts), `imageio-ffmpeg`.

## Next episodes

EP02 — "Header Only": the beacon's routing header passes through a relay that was
decommissioned nine years ago — and the dead relay answers back.
