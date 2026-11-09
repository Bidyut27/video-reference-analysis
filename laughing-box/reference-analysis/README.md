# Reference Video Analysis — Index & Method

This folder breaks down three short-form animated reference videos (Uzbek-language social posts) to learn the *production techniques* behind them. Nothing here reproduces their characters, artwork or scenes; the goal is to create **original** 60–90 s animated stories with similar production quality.

| # | File (original title) | Short name | Length | Genre |
|---|---|---|---|---|
| 1 | *Velikni shunaqa uchganlar bormi (remake)* — "Did anyone else ride their bike like this as a kid?" | **Bike Ride** | 29.7 s | Nostalgic slice-of-life comedy |
| 2 | *Kimda shunaqa FARA'ga o'xshagan xolatga tushgan* — "Who has ended up in a situation like this?" | **Bus Seat** | 19.7 s | Romance-misread twist gag |
| 3 | *Yo'llarda tezlikni oshirmang* — "Don't speed on the roads" | **Speeding Rider** | 36.7 s | Cartoon comedy + safety message |

Detailed breakdowns:

- [Video 1 — Bike Ride](video-1-bike-ride.md)
- [Video 2 — Bus Seat](video-2-bus-seat.md)
- [Video 3 — Speeding Rider](video-3-speeding-rider.md)
- [Comparison & strongest techniques](comparison.md)

Production deliverables live in [`../production/`](../production/README.md).

## How the analysis was done

Every figure below was measured from the files themselves, not estimated from memory.

| Check | Tool | Purpose |
|---|---|---|
| Container / codec / resolution / fps | `ffprobe` | Technical delivery specs |
| Contact sheets at 1 fps and 2 fps | `ffmpeg` (`fps`, `tile`) | Shot-by-shot story mapping |
| Cut detection | `ffmpeg` `select='gt(scene,0.3)'`, then manual check against 2 fps sheets | Shot count and average shot length |
| Held / duplicate frames | `ffmpeg` `mpdecimate` | Full vs. limited animation |
| Loudness | `ffmpeg` `ebur128` | Mix level |
| Silence gaps | `ffmpeg` `silencedetect` (−35 dB, 0.3 s) | Comedic audio drop-outs |
| Spectrograms | `ffmpeg` `showspectrumpic` | Music vs. SFX vs. voice structure |
| Tempo | `librosa.beat.beat_track` | Music BPM |
| Speech | `faster-whisper` (small) | Check for narration / dialogue |

## Measured technical facts

| Metric | Bike Ride | Bus Seat | Speeding Rider |
|---|---|---|---|
| Resolution / aspect | 720×1280 (9:16) | 720×1280 (9:16) | 720×1280 (9:16) |
| Frame rate | 24 fps | 24 fps | 24 fps |
| Video codec / bitrate | H.264, ~0.89 Mbps | H.264, ~1.13 Mbps | H.264, ~1.18 Mbps |
| Audio | AAC 44.1 kHz stereo | AAC 44.1 kHz stereo | AAC 44.1 kHz stereo |
| Integrated loudness | −14.1 LUFS | −14.1 LUFS | −14.1 LUFS |
| Shots (manual count) | 4 | ~15 | ~38 |
| Average shot length | ~7.4 s | ~1.3 s | ~1.0 s |
| Unique frames (mpdecimate) | 710 / 710 (100 %) | 371 / 470 (79 %) | 607 / 877 (69 %) |
| Estimated music tempo | ~134 BPM | ~78 BPM (≈156 half-time) | ~144 BPM |
| Intelligible speech | None (scat-like vocal melody only) | None | None ("RRRR" engine sound only) |

Notes:

- The 720p / ~1 Mbps figures are what the platform delivered after download. Production masters should be **1080×1920**, then the platform re-encodes them.
- All three are mixed to exactly **−14 LUFS**, the common loudness-normalisation target for streaming and social platforms.
- **None of the three uses narration or dialogue.** The stories are carried by visuals, music, SFX and a few on-screen words. That keeps them language-independent and easy to share across regions, which is the biggest strategic takeaway.
