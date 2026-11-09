# Templates & Checklists

## 1. One-page story template

```
Title (working):
Caption question (for comments):
Logline: [Hero] wants [goal], but [flaw/obstacle]... but then [twist].
Emotional engine: nostalgia / cringe / comeuppance / wholesome / suspense
Style: A soft cel | B webtoon glow | C thick-outline cartoon
Length target: __ s

Beats
0. Hook (0–3 s):
1. Setup (3–12 s):
2. Escalation A (12–25 s):
3. Breather shot (25–32 s):
4. Escalation B / new character (32–48 s):
5. Twist 1 (48–60 s):
6. Twist 2 / punchline (60–70 s):
7. Button + loop (70–75 s):

Colour script: setup __ | escalation __ | win __ | loss __ | reveal __
Music: track 1 (__ BPM, enters at __ s), track 2 / switch at __ s
Silence drops at: __ s
```

## 2. Shot list template

| # | Beat | Dur (s) | Shot size / angle | Camera move | Action / expression | FX / overlay | SFX | Music cue | Motion method (i2v / rig / still) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Hook | 2.0 | Wide, low | Push-in | | | | | |
| 2 | Setup | 1.5 | MCU, eye | Static | | | | | |
| … | | | | | | | | | |

Rule of thumb for 75 s: 40–50 rows, average 1.5–1.9 s, with 1–2 rows of 4–7 s.

## 3. Character bible template

```
Name:
Role / flaw / want:
Dominant colour (hex): | Secondary:
Silhouette features (3):
Proportions (heads tall):
Outfit (locked):
Expression sheet file:
Reference/LoRA ID:
Signature sound (e.g. sneaker squeak, humming):
Never: (things this character never does/wears)
```

## 4. Sample ORIGINAL story (75 s, Style C)

**Title:** *"Grandpa vs. the Self-Checkout"*
**Caption:** "Who else has a relative who fights with machines? 😂"
**Logline:** A proud grandpa refuses help at a supermarket self-checkout and battles the machine, but his "victory" ends with an unexpected revelation.

| Beat | Time | Content |
|---|---|---|
| Hook | 0–3 s | Extreme close-up: grandpa's squinting eye reflected in a glowing screen that flashes a big red "✖". Error buzz SFX. |
| Setup | 3–12 s | Grandpa (mustard cardigan, colour-owned) waves away a helpful teen staff member (teal apron). Proud low-angle pose. |
| Escalation A | 12–25 s | He scans a melon. Rejected. Scans it again, harder. Rejected. Snap expression cuts: confident → suspicious → furious. Music: quirky 130 BPM track enters on the first rejection. |
| Breather | 25–32 s | Slow side-tracking shot along the queue growing behind him: each shopper's face has a different reaction (parallax). |
| Escalation B | 32–48 s | Grandma (lilac, a new character) arrives, sees the chaos, and pulls out her reading glasses. Split-screen face-off: grandpa vs. the machine. Halftone burst as he "karate chops" the scan button. |
| Twist 1 | 48–60 s | Machine chimes ✔ "Payment approved". Gold sparkle grade, triumphant sting, grandpa victory pose. Music drop to silence for 0.4 s, then fanfare. |
| Twist 2 | 60–70 s | Crash zoom on the receipt: he has paid for the **next shopper's** entire cart. Record-scratch. Cool navy "gloom" grade on grandpa. |
| Button | 70–75 s | Grandma calmly hands the teen staffer her *own* coupons and walks off; grandpa frozen in shock (held 3 s). The last frame mirrors the first: a red "✖" glow on his face. |

All characters, brands ("FreshMart"), and situations are invented for this sample.

## 5. QC checklist

**Story**
- [ ] The first frame is intriguing without context
- [ ] Something changes on screen at least every 2 s
- [ ] A new question every 10–15 s; second-act character arrives before ~35 s
- [ ] The punchline reads with the sound **off**

**Picture**
- [ ] Characters on-model in every shot (face, colours, outfit)
- [ ] No AI artefacts: hands, extra limbs, melting faces, garbled text
- [ ] Faces and text inside the safe zone on a real phone with the platform UI visible
- [ ] Colour script matches the beats

**Sound**
- [ ] Every action has SFX; every twist has a stinger or music change
- [ ] Silence drop placed on the main gag
- [ ] −14 LUFS integrated, ≤ −1 dBTP; checked on phone speaker and headphones

**Delivery**
- [ ] 1080×1920, 24/30 fps, 60–90 s
- [ ] Caption question + 3–5 relevant hashtags
- [ ] Licences logged; originality checklist passed

**Thumbnail (required for every Laughing Box episode)**
- [ ] `cover-1080x1920.png` (9:16 only) for Shorts and Reels; title and faces inside the centre 3:4 area (y 240–1680) that Instagram's profile grid shows
- [ ] Main character's face large, with a strong expression; the conflict readable without the text
- [ ] Headline of 2–4 words in the "X VS Y" or similar series style, readable at phone size
- [ ] Built with a `make_thumbnail.py` in the episode folder, following `videos/grandpa-vs-self-checkout/make_thumbnail.py`
- [ ] Titles, descriptions and hashtags written for YouTube, Facebook and Instagram
