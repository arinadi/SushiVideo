# Module 6: Telegram Bot

| Field | Value |
|:---|:---|
| **Complexity** | XL |
| **Estimated Files** | ~3 (`bot.py`, `handlers.py`, `idle_monitor.py`) |
| **Key Risks** | RC-5 (Telegram 50MB file size limit), RC-6 (Colab session timeout) |

## Requirements

- Initialize `python-telegram-bot` Application.
- Enforce `TELEGRAM_CHAT_ID` authorization filter.
- Handle `/start`, `/status`, `/queue`, `/extend` commands.
- Process incoming text messages (URLs) and document uploads (SRT files).
- Manage job queue (sequential processing to protect Colab memory).
- Deliver Output 1 (Validation CSV/SRT).
- Deliver Output 2 (Final MP4 videos) with error handling for large files.
- Implement IdleMonitor to auto-shutdown Colab when inactive.

## UI Structure

- **Inline Keyboards:** 
  - Status Menu: `[ View Queue ] [ Refresh ] [ Shutdown ]`
  - Validation Output: `[ 🔪 Approve & Cut ] [ ❌ Cancel ]` (Optional enhancement for explicit validation gate, or auto-proceed). Let's implement auto-proceed but send the files immediately as they are ready.

## Data & API

### Core Components
- `JobManager`: AsyncQueue for `ClipJob`.
- `IdleMonitor`: Timer that tracks inactivity. Pattern directly from TTB.
- `TelegramNotifier`: Utility class to send formatted markdown messages.

## Technical Implementation

### `bot.py`
- Setup PTB Application.
- Register handlers.
- Start polling loop (no webhooks needed for Colab).

### `handlers.py`
```python
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process incoming YouTube URL."""
    url = update.message.text
    # Validate URL loosely
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ Please send a valid YouTube URL.")
        return
        
    job = ClipJob(
        job_id=generate_id(),
        source_url=url,
        chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )
    
    await job_manager.add_job(job)
    await update.message.reply_text(f"✅ Order queued: {url}")
```

### Job Processing Loop (The Orchestrator within Bot)
*This is the core loop that ties M2, M3, M4, M5 together.*

```python
async def process_queue():
    while True:
        job = await job_manager.queue.get()
        job_manager.set_processing(job)
        
        try:
            # Phase 1: Download
            await notify(job, "🐟 Downloading video...")
            video_meta = await downloader.download_video(job.source_url)
            
            # Phase 2: Transcribe
            await notify(job, "🤖 Extracting/Generating transcript...")
            transcript_data = await transcriber.get_transcript(video_meta, job.source_file)
            
            # Phase 3: AI Selection
            await notify(job, "🧠 AI Chef selecting best cuts...")
            ai = ai_selector.get_ai_selector()
            segments = await ai.select_segments(transcript_data.transcript_text)
            
            # Output 1: Delivery
            csv_path = generate_csv(segments)
            await send_files(job, [csv_path])
            
            # Phase 4: Editing
            await notify(job, f"🔪 Editing {len(segments)} clips...")
            output_clips = await video_editor.process_segments(video_meta, segments, Config.OUTPUT_FOLDER)
            
            # Output 2: Delivery
            await send_video_files(job, output_clips)
            
            await notify(job, "🍱 Order complete!")
            
        except Exception as e:
            await notify(job, f"❌ Error processing job: {e}")
        finally:
            job_manager.complete(job)
            cleanup_temp_files(job)
```

### File Size Limit Handling
- Telegram bot API limits file uploads to 50MB.
- `send_video_files` must check `os.path.getsize()`.
- If > 50MB, send a message: `⚠️ Clip "{title}" exceeds Telegram 50MB limit. Saved to Colab folder: {path}`.

## Testing

| # | Test | Command / Check | Pass/Fail |
|:---|:---|:---|:---|
| T6-1 | Authorization | Ignore messages from unauthorized chat IDs | Binary |
| T6-2 | Queue management | Jobs process sequentially, not concurrently | Binary |
| T6-3 | Delivery success | Documents and Video clips successfully sent to chat | Binary |
| T6-4 | Large file fallback | Clip > 50MB results in warning message, not crash | Binary |
| T6-5 | Idle Monitor | Shut down triggers after `IDLE_SHUTDOWN_MINUTES` | Binary |
