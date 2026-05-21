# API & Library References

## yt-dlp (Video Download)
- **Docs:** https://github.com/yt-dlp/yt-dlp#readme
- **Python API:** `yt_dlp.YoutubeDL(opts).download([url])`
- **Key Options:**
  - `format`: `bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best`
  - `writesubtitles`: `True` — download manual subtitles
  - `writeautomaticsub`: `True` — download auto-generated subtitles
  - `subtitlesformat`: `srt`
  - `subtitleslangs`: `['en', 'id']` — language priority
  - `outtmpl`: output filename template
  - `--download-sections`: `*START-END` for partial download
- **SRT Extraction:** Set `skip_download: True` to fetch subtitles only

## faster-whisper (Transcription)
- **Docs:** https://github.com/SYSTRAN/faster-whisper
- **Python API:** `WhisperModel(model_size, device="cuda", compute_type="float16")`
- **Transcribe:** `model.transcribe(audio_path, vad_filter=True, vad_parameters={...})`
- **Key Parameters:**
  - `beam_size`: 10 (accuracy vs speed)
  - `patience`: 2.0 (deeper beam search)
  - `temperature`: 0.0 (deterministic)
  - `vad_filter`: True (remove silence)
- **Output:** Generator of segments with `.start`, `.end`, `.text`

## google-genai (AI Provider - Gemini)
- **Docs:** https://ai.google.dev/gemini-api/docs
- **Python API:** `genai.Client(api_key=KEY)`
- **Generate:** `client.models.generate_content(model=MODEL, contents=[prompt, text])`
- **Models:** `gemini-2.5-flash` (default), `gemini-2.0-flash` (fallback)
- **Note:** Text-only input. Do NOT send media files.

## python-telegram-bot (Bot Framework)
- **Docs:** https://docs.python-telegram-bot.org/
- **Version:** 21.x (fully async)
- **Key Classes:** `Application`, `CommandHandler`, `MessageHandler`, `CallbackQueryHandler`
- **File Send:** `bot.send_document(chat_id, document=file, filename=name)`
- **Limits:** 50MB file upload limit for bots

## FFmpeg (Video Processing)
- **Portrait Reformat Command:**
```bash
ffmpeg -i input.mp4 -vf "
[0:v]split[original][copy];
[copy]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=20[bg];
[original]scale=1080:1920:force_original_aspect_ratio=decrease[fg];
[bg][fg]overlay=(W-w)/2:(H-h)/2,subtitles=subs.srt:force_style='FontSize=24,FontName=DejaVu Sans,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2,Alignment=2,MarginV=40'
" -filter:a "atempo=1.25" -c:v libx264 -crf 20 -preset fast -c:a aac output.mp4
```
- **Speed:** `-filter:a "atempo=1.25"` for audio, `setpts=PTS/1.25` for video
- **Probe:** `ffmpeg.probe(path)` returns format/stream metadata

## Gradio (Web UI)
- **Docs:** https://www.gradio.app/docs
- **Version:** 4.x
- **Key Components:** `gr.Textbox`, `gr.File`, `gr.Button`, `gr.Tabs`, `gr.Textbox(lines=10)` for log
- **Launch:** `demo.launch(share=True)` for Colab public URL
