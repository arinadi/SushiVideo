# Design System: SushiVideo

## 1. Visual Theme & Atmosphere

SushiVideo has **two UI surfaces** — both non-browser, so the design system focuses on **structured text formatting** and **functional clarity** rather than web aesthetics.

| Surface | Medium | Design Philosophy |
|:---|:---|:---|
| **Telegram Bot** | Markdown messages + inline keyboards | Japanese-inspired emoji vocabulary. Concise, scannable. Status-driven (🔵 → 🟡 → 🟢 → ✅). |
| **Gradio Web UI** | Gradio components (auto-themed) | Minimal. Dark theme. Functional-first — upload, paste, go. No clutter. |

### Persona: The Sushi Chef 🍣

The bot speaks with the personality of a precise, efficient sushi chef. Not chatty. Not robotic. Professional with flair.

- **Tone:** Confident, brief, action-oriented.
- **Pattern:** Status → Detail → Action. Always in that order.
- **Emoji vocabulary:** 🍣 (brand/main), 🔪 (cutting/processing), 🐟 (raw input), 🍱 (packaged output), 📋 (CSV/data), 🎬 (video), ⏳ (waiting), ✅ (done), ❌ (error).

## 2. Color Palette & Roles

> Applies to Gradio UI theme and Telegram message formatting.

| Semantic Name | Hex | Functional Role |
|:---|:---|:---|
| `sushi-black` | `#1a1a2e` | Gradio dark background |
| `sushi-dark` | `#16213e` | Secondary background / cards |
| `sushi-salmon` | `#e94560` | Primary accent — errors, warnings, brand |
| `sushi-wasabi` | `#0f3460` | Subtle accent — borders, links |
| `sushi-rice` | `#eaeaea` | Text color on dark |
| `sushi-nori` | `#2d3436` | Muted text / secondary |
| `sushi-success` | `#00b894` | Success state |
| `sushi-warning` | `#fdcb6e` | Warning state |
| `sushi-info` | `#74b9ff` | Info / progress state |

## 3. Typography Rules

| Role | Font | Context |
|:---|:---|:---|
| **Telegram messages** | System (Telegram client default) | All bot messages |
| **Code/data blocks** | Monospace (Telegram \`code\` format) | File names, timestamps, durations, config values |
| **Gradio UI** | Gradio default (system sans-serif) | All UI elements |
| **Subtitle (hardsub)** | `DejaVu Sans` or `Noto Sans` | Burned into video — high readability |

### Subtitle Styling (FFmpeg ASS format)
```
FontName=DejaVu Sans
FontSize=24
PrimaryColour=&H00FFFFFF   (white text)
OutlineColour=&H00000000   (black outline)
BorderStyle=3              (opaque box behind text)
Outline=2                  (outline thickness)
Shadow=0                   (no shadow)
Alignment=2                (bottom-center)
MarginV=40                 (margin from bottom edge)
```

## 4. Component Stylings

### Telegram Message Templates

**Startup Message:**
```
🍣 *SushiVideo is ready*
🔪 The chef is in the kitchen.

🛠️ *GPU:* `NVIDIA T4`
🤖 *Whisper:* `large-v2`
🧠 *AI:* `gemini-2.5-flash`
⏱️ *Idle Shutdown:* `10m`

Send a YouTube URL with /clip or use the Web UI.
```

**Job Received:**
```
✅ *Order received* — `{filename_or_url}`
🐟 Downloading fresh ingredients...
```

**Phase 1 Complete (Output 1):**
```
📋 *Segments ready* — {count} cuts selected

📎 Files attached:
• segments.csv
• clip_1.srt → clip_{n}.srt

🔪 Proceeding to video editing...
```

**Phase 2 Complete (Output 2):**
```
🍱 *Order complete!* — {count} clips ready

📹 Clips delivered:
• {title_1}.mp4 ({duration})
• {title_2}.mp4 ({duration})
• ...

⏱️ Total time: {processing_time}
```

**Error:**
```
❌ *Chef's apology* — something went wrong.
`{error_message}`
```

### Inline Keyboard Layouts

**Status Panel:**
```
[ 📄 View Orders ] [ 🔄 ] [ 🔌 ]
```

**Idle Warning:**
```
[ ⏳ +5m ]
```

### Gradio UI Layout
```
┌─────────────────────────────────────┐
│  🍣 SushiVideo                      │
│  "Cut the best piece."             │
├─────────────────────────────────────┤
│                                     │
│  [ Tab: URL Input ][ Tab: Upload ]  │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ YouTube URL: [____________] │    │
│  │ SRT File:    [Choose File]  │    │
│  │                             │    │
│  │      [ 🔪 Start Cutting ]  │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ Status Log:                 │    │
│  │ > Downloading video...      │    │
│  │ > Generating transcript...  │    │
│  │ > 3 segments selected       │    │
│  │ > Editing clip 1/3...       │    │
│  └─────────────────────────────┘    │
│                                     │
└─────────────────────────────────────┘
```

## 5. Layout Principles

### Telegram Messages
- **Max width:** 60 characters per line (avoid wrapping on mobile).
- **Spacing:** One blank line between sections.
- **Hierarchy:** Bold (`*text*`) for labels, backtick (`` `text` ``) for data values.
- **No walls of text.** Every message is scannable in <3 seconds.

### Gradio UI
- **Single column layout.** No unnecessary sidebars.
- **Two tabs:** "URL Input" (default) and "File Upload".
- **Status log:** Real-time text output showing pipeline progress.
- **No results display in Gradio.** All results delivered via Telegram.

## 6. Depth & Elevation

Not applicable — both surfaces (Telegram and Gradio) are flat interfaces with no custom elevation/shadow system.

## 7. Responsive Behavior

### Telegram
- Messages are inherently responsive (Telegram client handles rendering).
- Inline keyboards auto-wrap on small screens.
- File attachments auto-render with previews.

### Gradio
- Gradio components are responsive by default.
- Single-column layout ensures usability on mobile (Colab browser on tablet).
- Share URL (`*.gradio.live`) accessible from any device.

## 8. Reference Prompt

> Use this when briefing a coding agent on the visual style:

```
SushiVideo uses a Japanese sushi chef persona. UI surfaces are Telegram 
(Markdown messages) and Gradio (dark theme, minimal). Emoji vocabulary: 
🍣 brand, 🔪 processing, 🐟 raw input, 🍱 output, 📋 data, 🎬 video.

Message pattern: Status → Detail → Action. Always concise.

Subtitle style: DejaVu Sans, 24pt, white text on black outline box, 
bottom-center, 40px margin. Use FFmpeg ASS subtitle filter.

Color tokens: sushi-black #1a1a2e, sushi-salmon #e94560, 
sushi-success #00b894, sushi-warning #fdcb6e, sushi-info #74b9ff.
```
