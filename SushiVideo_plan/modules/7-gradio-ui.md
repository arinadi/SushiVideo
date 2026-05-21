# Module 7: Gradio Web UI

| Field | Value |
|:---|:---|
| **Complexity** | M |
| **Estimated Files** | ~1 (`gradio_ui.py`) |
| **Key Risks** | Upload limit constraints, state sync with Telegram bot |

## Requirements

- Provide a public web interface (via Colab `share=True`) for uploading large video files.
- Support two input modes: YouTube URL (fallback to Telegram) or Direct File Upload.
- Support optional SRT file upload for both modes.
- Insert jobs into the same `job_manager.queue` as the Telegram bot.
- Display a read-only "Status Log" that tails the active job.

## UI Structure

- **Dark Theme** by default (`theme=gr.themes.Base(neutral_hue="slate")`).
- **Tabs:** "URL Input" and "File Upload".
- **Action Button:** "🔪 Start Cutting"
- **Log Window:** Textbox with `interactive=False` updated via generator.

## Data & API

- Imports `job_manager` singleton from Module 6 (or Main Orchestrator).
- Creates `ClipJob` instances and pushes them to the queue.

## Technical Implementation

### `gradio_ui.py`

```python
import gradio as gr
import asyncio
import os
from bot_classes import ClipJob, generate_id
# job_manager is injected during startup

_log_messages = []

def log_to_ui(msg: str):
    """Append message to global UI log."""
    _log_messages.append(f"> {msg}")
    if len(_log_messages) > 20:
        _log_messages.pop(0)

async def submit_url(url: str, srt_file):
    if not url:
        return "❌ Please enter a URL."
        
    job = ClipJob(
        job_id=generate_id(),
        source_url=url,
        source_file=srt_file.name if srt_file else None,
        chat_id=TELEGRAM_CHAT_ID, # Deliver to admin chat
        message_id=None
    )
    
    await job_manager.add_job(job)
    return "✅ Job queued from URL."

async def submit_file(video_file, srt_file):
    if not video_file:
        return "❌ Please upload a video."
        
    # Copy file to persistent uploads directory to prevent Gradio from deleting it
    safe_path = os.path.join("uploads", os.path.basename(video_file.name))
    import shutil
    shutil.copy(video_file.name, safe_path)
        
    job = ClipJob(
        job_id=generate_id(),
        source_url=None,
        source_file=safe_path, 
        srt_file=srt_file.name if srt_file else None,
        chat_id=TELEGRAM_CHAT_ID,
        message_id=None
    )
    
    await job_manager.add_job(job)
    return "✅ Job queued from File."

def get_logs():
    """Generator for Gradio live updates."""
    return "\n".join(_log_messages)

def build_ui(job_mgr):
    global job_manager
    job_manager = job_mgr
    
    with gr.Blocks(theme=gr.themes.Base()) as app:
        gr.Markdown("# 🍣 SushiVideo\n*Cut the best piece.*")
        
        with gr.Tabs():
            with gr.Tab("URL Input"):
                url_input = gr.Textbox(label="YouTube URL")
                srt_input_url = gr.File(label="Optional SRT File")
                url_btn = gr.Button("🔪 Start Cutting")
                url_status = gr.Textbox(label="Status")
                
                url_btn.click(submit_url, inputs=[url_input, srt_input_url], outputs=url_status)
                
            with gr.Tab("File Upload"):
                vid_input = gr.File(label="Video File")
                srt_input_file = gr.File(label="Optional SRT File")
                file_btn = gr.Button("🔪 Start Cutting")
                file_status = gr.Textbox(label="Status")
                
                file_btn.click(submit_file, inputs=[vid_input, srt_input_file], outputs=file_status)
                
        gr.Markdown("### Live Processing Log")
        log_output = gr.Textbox(lines=10, interactive=False, label="Log")
        
        # Auto-refresh log every 2 seconds
        app.load(get_logs, outputs=log_output, every=2)
        
    return app

async def launch_gradio(job_mgr):
    app = build_ui(job_mgr)
    # Share=True creates the public Colab link
    app.launch(share=True, inline=False, prevent_thread_lock=True)
```

## Testing

| # | Test | Command / Check | Pass/Fail |
|:---|:---|:---|:---|
| T7-1 | UI Launch | Gradio launches and provides public URL | Binary |
| T7-2 | URL Submit | Submitting URL adds job to `job_manager` | Binary |
| T7-3 | File Submit | Uploading video successfully copies to `uploads/` and queues | Binary |
| T7-4 | Log Sync | Status updates from queue processing appear in Gradio log box | Binary |
