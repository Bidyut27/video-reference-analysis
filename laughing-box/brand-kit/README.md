# Laughing Box brand kit

Channel name: **Laughing Box** · Handle on every platform: **@Officiallaughingbox**

| File | Use | Size |
|---|---|---|
| `laughing-box-logo.png` | Main logo (transparent) | 2000×1480 |
| `profile-800x800.png` | YouTube & Facebook profile picture (shown as a circle) | 800×800 |
| `youtube-banner-2560x1440.png` | YouTube channel banner | 2560×1440 |
| `facebook-cover-1640x624.png` | Facebook page cover | 1640×624 |
| `watermark-300x300.png` | YouTube video watermark (Customization → Branding) | 300×300 |
| `_preview-youtube-banner-safe-areas.png` | Review only, do not upload: green = visible on all devices, blue = desktop | — |

The logo and "Cartoon Comedy" tagline sit inside YouTube's 1546×423 safe area. On the Facebook cover they stay in the centre, so they aren't cropped on mobile.


Regenerate (uses the same characters as the episodes; name and handle are `NAME` / `HANDLE` at the top of the script):

```bash
python make_branding.py .   # needs pycairo
```
