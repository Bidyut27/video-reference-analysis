# Production Blueprint — Original 60–90 s Animated Storytelling Shorts

Target platforms: **YouTube Shorts, Facebook Reels, Instagram Reels**.
Derived from the techniques measured in [`../reference-analysis/`](../reference-analysis/comparison.md).

---

## 1. Format spec

| Item | Spec |
|---|---|
| Aspect ratio | 9:16 vertical |
| Master resolution | 1080×1920 (generate art at ≥1080 px wide; upscale AI clips if needed) |
| Frame rate | 24 fps (animate key motion "on 2s" = 12 drawings/s where hand-animated) |
| Length | 60–90 s (sweet spot 65–75 s) |
| Codec | H.264 High, 15–20 Mbps VBR (or HEVC); AAC 48 kHz stereo, 320 kbps |
| Loudness | −14 LUFS integrated, true peak ≤ −1 dBTP |
| Safe zone | Keep faces and text inside the centre ~1080×1420. Avoid the top ~220 px (status/title) and the bottom ~380 px (caption, buttons). Keep ~120 px clear on the right edge (action icons). |
| Language | **Wordless by default.** Optional short on-screen labels; optional VO version as a separate export |
| Captions | Burned-in only for labels/punchline words; use platform captions for any VO |

## 2. Story structure for 60–90 s: "Hook → 3 Escalations → Double Twist"

The references run 20–37 s with one or two beats. To fill 60–90 s **without slowing down**, add beats, not duration.

| Beat | Time (75 s version) | Purpose | Technique source |
|---|---|---|---|
| **0. Hook** | 0–3 s | Absurd image, action, or an unexplained label. No establishing shots. | Ref 2 labels, Ref 3 wheelie |
| **1. Setup** | 3–12 s | Who is the hero, what do they want, what is their flaw? Show it, don't tell it. | Ref 1, 3 |
| **2. Escalation A** | 12–25 s | First obstacle; hero tries their way. Music/SFX shift. | Ref 3 checkpoint |
| **3. Breather / world shot** | 25–32 s | One longer moving shot (parallax, drone-style wide) to reset the eye | Ref 1 side-scroll |
| **4. Escalation B** | 32–48 s | Bigger obstacle or second character enters (the ~30 s retention dip happens here, so the new character must arrive *now*) | Ref 1 cart entrance |
| **5. Twist 1** | 48–60 s | Clever reversal: the hero seems to win | Ref 3 helmet delivery |
| **6. Twist 2 / punchline** | 60–70 s | Bigger reversal or reveal that recontextualises the hook | Ref 2 reveal, Ref 3 radar |
| **7. Button + loop** | 70–75 s | Hold the reaction 2–3 s; the last frame should visually rhyme with the first so the loop feels seamless | Ref 3 held shock |

**Rules**

- Something must change on screen at least every **2 s**: a cut, camera move, expression swap or FX hit.
- Every 10–15 s there must be a **new question** in the viewer's mind.
- The punchline must work **with the sound off** (visual reveal, thought bubble, prop) and get **better with the sound on** (stinger, music drop).
- Write the caption as a relatable question ("Who else got caught like this? 😅") to farm comments.

## 3. Visual direction

Pick **one** style per channel and keep it forever. Consistency builds recognition.

| Style option | Inspired technique | Best for | Effort |
|---|---|---|---|
| A. Soft cel + painterly BG | Ref 1 | Nostalgia, family, kids | Medium (AI i2v friendly) |
| B. Webtoon glow | Ref 2 | Romance, relationships, school | Low (near-still + overlays) |
| C. Thick-outline TV cartoon | Ref 3 | Slapstick, workplace, traffic, family comedy | Medium (expression sheets) |

**Design rules (all styles)**

1. **Colour-owned characters:** each lead gets one dominant hue (e.g. hero = orange, rival = teal). No two leads share a family.
2. **Silhouette test:** the character must be identifiable as a black silhouette at thumbnail size.
3. **Expression sheet** per lead, at least 10 expressions: neutral, smug, shock, cry, rage, idea, nervous grin, love, deadpan, defeated.
4. **Sharp characters, soft backgrounds:** blur the BG slightly, or generate with depth of field, so the character pops.
5. **Colour script per beat:** neutral setup → saturated escalation → warm gold "win" → cool navy "loss" → neutral daylight reveal.
6. **Lighting:** one strong motivated source (window, sun) with bloom; rim-light the hero in emotional beats.

## 4. Animation direction

| Shot type | Approach | Share of runtime |
|---|---|---|
| Action/travel shots | AI image-to-video or 2D rig + parallax loop, continuous motion | ~25 % |
| Acting/dialogue-free reaction shots | Near-still pose + blink/head turn + slow push-in | ~45 % |
| Punch shots | Pose-to-pose snap, crash zoom, 2–4 frame shake | ~15 % |
| Graphic cards | Split-screen, halftone burst, thought bubble, phone UI | ~15 % |

- Use holds deliberately. 20–30 % held frames is normal (Refs 2–3) and saves budget.
- Camera vocabulary: push-in (tension), low angle (power), POV over-the-shoulder (threat), dutch sway (fun/chaos), crash zoom (realisation), whip pan (time skip).
- FX library: speed lines, dust puffs, sweat drops, sparkles/bokeh, gloom lines, impact stars, halftone flashes, light leaks.

## 5. Audio direction

| Layer | Rule |
|---|---|
| Music | 1–2 licensed or self-generated tracks. **Switch or enter on the conflict beat** (Ref 3). 120–150 BPM for comedy, 70–90 BPM for romance/emotional. Cut on the beat. |
| Silence | Drop the music for 0.3–0.5 s right before or on a physical gag or reveal (Ref 1). |
| SFX | Every on-screen action gets a sound: whooshes on cuts and camera moves, pops on expression swaps, stingers on twists (record scratch, slide whistle, "ding" for idea, "dun-dun" for doom). |
| Voice | Optional "mouth sounds" and efforts (grunts, gasps, laughs) keep it wordless yet human. A VO version can be a separate export. |
| Mix | Music −18 to −20 LUFS under SFX peaks; master at −14 LUFS, −1 dBTP. Check on phone speakers. |

## 6. Editing direction

- **Average shot length 1.2–2.0 s** (between Ref 2 and Ref 3), with 1–2 longer "breather" shots of 4–7 s.
- **Accelerate cuts before each twist** (Ref 2: four cuts in under 1 s before the reveal).
- Hard cuts only; let graphic cards and split-screens be the "transitions".
- No intro, no logo sting, no end card. Brand with a consistent character, palette and a small corner watermark.
- First frame = most intriguing frame. Last frame = held reaction (2–3 s).
- Export one master plus platform variants (see the [workflow](tools-and-workflow.md)).

## 7. Retention targets to review after publishing

| Metric | Target |
|---|---|
| Viewed vs. swiped away (Shorts) / 3-s hold | ≥ 70 % |
| Average % viewed | ≥ 80 % for a 60–75 s video |
| Rewatch / loop rate | > 100 % average view duration means loops are working |
| Comments per 1k views | Driven by the caption question; track per format |

Iterate on the **hook** first, then the **twist**, then visual polish.
