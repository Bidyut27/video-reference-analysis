# Laughing Box series bible

Keep every episode on-model. Character dicts live in `laughing-box/episodes/01-grandpa-vs-self-checkout/make_video.py` (Leo in `laughing-box/episodes/02-grandpa-vs-video-call/make_video.py`). Reuse them; don't redraw.

## Brand

| Item | Value |
|---|---|
| Channel name | **Laughing Box** (shown as "LAUGHING BOX" in the logo) |
| Handle | **@Officiallaughingbox** (YouTube, Facebook, Instagram, TikTok) |
| Tagline | CARTOON COMEDY |
| Mascot | A laughing orange cardboard box with "HA HA HA" above it |
| Palette | Sunburst yellow `#fff1a8` → orange `#ff9d2e`; letters `#ffd23f #ff7a3d #ff4d8d #9b6bff #2fb7ff #25c486`; outline ink `#17121a` |
| Type | DejaVu Sans Bold, thick dark outline, bouncy multicolour letters |
| Brand files | `laughing-box/brand-kit/` (logo, profile, YouTube banner, Facebook cover, watermark) |

## Art style

Flat 2D vector cartoon: big round heads, thick dark outlines, rosy cheeks, simple bright colours, oversized expressions. Cartoon slapstick only. Expressions available: `neutral, happy, smug, furious, shock, cry, suspicious, nervous, victory, wink, yawn`.

## Main cast

| Character | Look | Personality | Voice (Kokoro: voice, speed, semitones) |
|---|---|---|---|
| **Grandpa (Harold)** | Mustard cardigan `#e3a72f`, cream shirt, brown trousers, white side-hair, big white moustache, round glasses, big nose | Proud, stubborn, "I don't need help!"; loses to technology but never gives up | `bm_george`, 0.95, −1.5 |
| **Grandma (Margaret)** | Lilac dress `#b78ad8` with pearl necklace, grey bun, small nose, reading glasses she slides on | Calm, smug, secretly better at tech, but has her own quirks (adopts a robot vacuum) | `bf_emma`, 0.95, 0 |
| **Leo** (grandson) | Blue hoodie `#3a6fd8`, brown spiky hair, freckles | Cheerful, patient-ish, facepalms a lot | `am_puck`, 1.1, +2.5 |

## Supporting cast

| Character | Look | Voice |
|---|---|---|
| Teen staffer | Cream shirt, teal apron `#1fa59a`, spiky dark hair, freckles | `am_puck`, 1.1, +1 |
| Big shopper | Green hoodie, red cap, beard, extra-wide | `am_fenrir`, 1.05, 0 |
| Queue woman | Pink top, long dark hair | `af_bella`, 1.05, 0 |
| Queue kid | Yellow top, blue trousers, balloon | `af_sky`, 1.15, +3 |
| Machines (kiosk etc.) | n/a | `af_nicole`, 1.0, 0, plus a robot ring-mod filter |
| **Biscuit** | Robot vacuum with a **pink** bow and a heart LED | (silent; motor, bonks, hiccups) |
| **Cookie** | Robot vacuum with a **blue** bow | (silent) |
| **Mittens** | Leo's orange tabby cat with green eyes and a smug half-lidded look; sits on homework | (silent; meow, purr) |
| **The Smart Speaker** | Small dark-grey fabric cylinder with a glowing top ring (blue = talking, rainbow = party, pink = love, red = alarm) and two LED eyes; mishears everything | Machine voice (`af_nicole` + robot filter) |
| **Rosa** (flight attendant) | Navy uniform, red scarf with a gold wing pin, dark hair in a bun; endlessly polite, slowly losing patience | `af_sarah`, 1.05, 0 |
| Pilot (voice only) | Heard over the cabin speaker | `am_michael`, 0.95, −1, plus a cabin-PA band filter |

Caption colours: Grandpa `#ffd25a`, Grandma `#e3c4ff`, Leo `#8fd3ff`, teen `#7ff0e3`, machines `#ffffff`.

## Sets

| Set | Where it's drawn |
|---|---|
| Pickle Mart supermarket (shelves, self-checkout kiosk) | `store_bg`, `kiosk` in episode 1 |
| Grandparents' living room (curtained window, fish photo, floor lamp, rug, red armchair) | `living_bg`, `armchair` in episode 2 |
| Leo's room (blue walls, GAME ON poster, night-sky picture) | `leo_bg` in episode 2 |
| Phone and video-call UI, cat filter | `phone`, `call_ui`, `cat_filter` in episode 2 |
| Robot vacuum, yarn ball, knitting basket | `vacuum`, `yarn_ball`, `basket` in episode 3 |
| Leo's desk with lamp, day-to-night window, wall clock, books, pencil, sharpener, crayon, Mittens | `room_bg`, `desk`, `clock`, `book`, `pencil`, `cat` in episode 4 |
| Smart speaker, side table, delivery box, feathers, disco lights and mirror ball, rubber ducks | `speaker`, `side_table`, `box`, `feathers`, `disco_lights`, `duck` in episode 5 |
| Airplane cabin (overhead bins, seats, aisle), call-button panel, life vest (flat/inflated), window views (runway, clouds, sunset), plane exterior with a Laughing Box tail | `cabin_bg`, `cabin_row`, `seat_back`, `call_panel`, `vest`, `window`, `plane` in episode 6 |

## Sound

All synthesised: theme music at 130 BPM in C–F–G–C (marimba melody, plucked bass, light drums), a pad for calm scenes, and SFX like buzz, boing, bonk, meow, motor, sad trombone, record scratch, fanfare and claps. Dialogue ducks the music.

## Episode log

| # | Title | Folder | Premise | Format |
|---|---|---|---|---|
| 1 | Grandpa vs. the Self-Checkout | `laughing-box/episodes/01-grandpa-vs-self-checkout/` | The kiosk rejects his melon; Grandma's karate chop fixes it; he paid for a stranger's giant cart | 1080p, wordless + voice versions |
| 2 | Grandpa vs. the Video Call | `laughing-box/episodes/02-grandpa-vs-video-call/` | Nose, forehead and cat-filter calls with Leo; Grandma fixes it, then turns herself into a cat | 1080p, voice |
| 3 | Grandma vs. the Robot Vacuum | `laughing-box/episodes/03-grandma-vs-robot-vacuum/` | She adopts it as "Biscuit"; Grandpa rides it and crashes; she brings home "Cookie" | **4K**, voice |
| 4 | Leo vs. Homework | `laughing-box/episodes/04-leo-vs-homework/` | Phone, cat and pencil distractions; Grandpa "helps" with wild math; it was the history homework | **4K**, voice |
| 5 | Grandpa vs. the Smart Speaker | `laughing-box/episodes/05-grandpa-vs-smart-speaker/` | It mishears everything ("Baby Duck Disco", 40 feathers, party mode, a 3 a.m. alarm); Grandma's whisper works; the alarm wakes Grandma | **4K**, voice |
| 6 | Grandpa's First Flight | `laughing-box/episodes/06-grandpas-first-flight/` | Seat belt mix-up, the life-vest tab ("POOF!"), takeoff, 40 call-button presses; he loves it just as they land and gets stuck in the seat | **4K**, voice |

Unused ideas: Beach Day: The Seagull Heist · The Family Photo · Grandpa Learns to Dance · The Night Snack Mission · Picnic vs. the Ants · Grandma vs. the Air Fryer · Mittens vs. the Laser Dot · Grandpa vs. the Automatic Door · First Day at the Gym (new character) · The Delivery Driver (new character).
