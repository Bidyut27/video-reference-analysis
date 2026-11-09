# Tools & Production Workflow

AI tools change quickly. Verify the current features, pricing and **commercial-use / licensing terms** of every tool before you publish monetised content. The categories and workflow below stay stable even when individual tools change.

## 1. Recommended toolchains

### Track A: AI-first (fastest, 1 creator, ~1–2 days per video)

| Stage | Recommended tools (pick one) | Notes |
|---|---|---|
| Story / script | ChatGPT, Claude, Gemini | Brainstorm premises and beat sheets; the twist must be yours |
| Character design & consistency | Midjourney (character/style reference), GPT-image / ChatGPT image, Flux (with a trained LoRA), Leonardo, Ideogram | Create a **character sheet** first, then always generate with it as reference. A small LoRA trained on *your own* character gives the best consistency. |
| Backgrounds | Same image model; Photoshop / Krita / Photopea for cleanup | Generate without characters; add depth blur |
| Image → video motion | Kling, Runway, Google Veo, Hailuo (MiniMax), Luma, Pika, Wan (open source) | Prompt camera and action separately; generate 3–5 takes per shot and pick the best |
| Lip-sync / face animation (if VO) | Hedra, Runway Act-One, Kling lip-sync, LivePortrait (open source) | Only needed for talking versions |
| Upscale / interpolate | Topaz Video AI, CapCut upscale | Bring AI clips to 1080×1920 |
| Edit / FX / captions | **CapCut** (desktop) for speed; Premiere Pro or DaVinci Resolve for control | Overlay packs: bokeh, sparkles, speed lines, halftone, light leaks |
| Music | Licensed libraries: Epidemic Sound, Artlist, YouTube Audio Library; AI: Suno / Udio (check plan licensing) | Avoid trending copyrighted songs in monetised uploads |
| SFX | ElevenLabs Sound Effects, Epidemic/Artlist SFX, Freesound (check licences), Zapsplat | Build a reusable comedy SFX kit |
| Voice (optional) | ElevenLabs, or record yourself | Keep a wordless master |

### Track B: Hybrid 2D (best quality and consistency, small team, ~3–5 days per video)

| Stage | Tools |
|---|---|
| Design | Procreate, Clip Studio Paint, Krita (free), Photoshop; AI only for ideation/backgrounds |
| Rigging & animation | **Cartoon Animator 5** (fast cut-out rigs), Moho Pro, Toon Boom Harmony (pro), Adobe Animate, Live2D (Ref-2-style subtle motion), Blender Grease Pencil (free) |
| Compositing & camera | After Effects (parallax, puppet pin, Saber/Optical Flares), or DaVinci Fusion |
| Motion shots | Optionally AI image-to-video for complex travel/action shots, then composite |
| Edit & sound | Premiere Pro / DaVinci Resolve + Fairlight / Audition |

### Track C: Zero-budget starter

Krita (art) → Blender Grease Pencil or Cartoon Animator trial (motion) → CapCut (edit) → YouTube Audio Library + Freesound (audio).

## 2. Step-by-step pipeline (Track A, 75 s video)

| # | Step | Output | Time |
|---|---|---|---|
| 1 | **Premise**: one relatable situation + flaw + twist. Test: can you pitch it in one sentence that ends with "...but then"? | Logline | 30 min |
| 2 | **Beat sheet** using the 8-beat structure in the [blueprint](blueprint.md) | Beat sheet | 30 min |
| 3 | **Shot list**: 35–50 shots, each with duration, camera, action, SFX, music cue ([template](templates.md#2-shot-list-template)) | Shot list | 1 h |
| 4 | **Character sheets**: front, ¾, side, plus 10 expressions per lead, fixed palette | Sheets + LoRA/reference set | 2–3 h (once per character) |
| 5 | **Animatic**: rough still per shot (even stick figures) timed to a temp music track in the editor. **Fix story problems here.** | Timed animatic | 1–2 h |
| 6 | **Key frames**: generate final illustration per shot at 9:16 with character references; inpaint fixes (hands, faces, props) | 30–50 stills | 3–5 h |
| 7 | **Motion**: image-to-video for ~25 % of shots; subtle motion (blink, sway, push-in) for reaction shots; keep stills for snap/punch shots | Clips | 3–6 h |
| 8 | **Assembly**: replace animatic frames; trim to the beat; add camera keyframes, shakes, crash zooms | Picture lock | 2 h |
| 9 | **Graphics & grade**: colour script per beat, overlays, split-screens, thought bubbles, labels | Graded cut | 1–2 h |
| 10 | **Sound**: music bed(s), silence drops, SFX on every action, stingers on twists, mix to −14 LUFS | Final mix | 2 h |
| 11 | **QC** with the [checklist](templates.md#5-qc-checklist) on a real phone, sound on and off | Approved master | 30 min |
| 12 | **Export & publish** per platform (below); A/B test the first 2 s on later uploads | Live video | 30 min |

## 3. Prompting patterns

**Character sheet (image model):**

```
Original cartoon character design sheet, [age/role], [one dominant colour] outfit,
[2–3 distinctive features], thick clean black outlines, flat cel shading,
front view, three-quarter view, side view, neutral pose, plain white background,
consistent proportions, 2D TV animation style
```

**Expression sheet:**

```
Same character, expression sheet, 10 head close-ups in a grid: neutral, smug,
shocked, crying, furious, idea (lightbulb), nervous grin, lovestruck, deadpan,
defeated; identical design and colours, white background
```

**Shot key frame (9:16):**

```
Vertical 9:16 frame, [shot size] of [character] [action], [location],
low/eye/high angle, [lighting: backlit window glow / harsh noon sun],
background softly blurred, character crisp, [style keywords], no text
```

**Image → video:**

```
Camera: slow push-in. Subject: the character pedals steadily, body bobbing,
hair blowing in wind. Background: scrolls left with parallax. Keep character
design unchanged. No new characters. No text.
```

Tips: describe **one** action per clip, lock the camera move in words, keep clips at 3–5 s, and regenerate rather than accept morphing faces.

## 4. Export settings per platform

| Platform | Resolution | Length | Notes |
|---|---|---|---|
| YouTube Shorts | 1080×1920, 24/30 fps | Up to 3 min supported; target 60–90 s | Title ≤ 60 chars with a hook; the first frame works as the thumbnail |
| Instagram Reels | 1080×1920 | Target 60–90 s | Pick a cover frame; keep text out of the bottom ~20 % |
| Facebook Reels | 1080×1920 | Target 60–90 s | Cross-post from Instagram or upload natively; add caption question |

One master export (H.264, 15–20 Mbps, AAC 48 kHz, −14 LUFS) works for all three. Platforms re-encode anyway; the references were delivered at 720p ~1 Mbps after re-encoding.

## 5. Budget & capacity guide

| Setup | Monthly tool cost (approx.) | Output |
|---|---|---|
| Starter (free tiers + CapCut) | $0–30 | 1 video/week, watermark/limit risk |
| Solo pro (image model + i2v model + music library + CapCut Pro) | $80–200 | 2–3 videos/week |
| Small team (adds Adobe CC, Cartoon Animator/Moho, Topaz) | $250–500 | 4–7 videos/week |

## 6. Legal & originality checklist

- [ ] Characters designed from scratch; no prompts naming existing IP, studios or living artists
- [ ] No reference-video frames used as image inputs
- [ ] Music and SFX licensed for commercial social use (keep receipts/licence IDs)
- [ ] No real brand logos or app UIs unless sponsored or permitted; use invented brands
- [ ] AI-disclosure toggles set where the platform requires them for realistic synthetic content
- [ ] Safety messages (traffic, health) are accurate and not dangerous to imitate
