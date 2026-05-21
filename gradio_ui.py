import gradio as gr
import asyncio
import os
import shutil
from bot_classes import ClipJob, generate_id
from config import Config

_log_messages = []
job_manager = None

def log_to_ui(msg: str):
    """Append message to global UI log."""
    _log_messages.append(f"> {msg}")
    if len(_log_messages) > 20:
        _log_messages.pop(0)

async def submit_url(url: str, srt_file):
    if not url:
        return "❌ Please enter a URL."
        
    # Send to first admin chat id, default to 0 if not set for testing
    chat_id = int(str(Config.TELEGRAM_CHAT_ID).split(',')[0]) if Config.TELEGRAM_CHAT_ID else 0
    
    job = ClipJob(
        job_id=generate_id(),
        source_url=url,
        source_file=srt_file.name if srt_file else None,
        chat_id=chat_id,
        message_id=None
    )
    
    if job_manager:
        await job_manager.add_job(job)
        log_to_ui(f"✅ Job queued from URL: {url}")
        return "✅ Job queued from URL."
    else:
        log_to_ui("⚠️ Mockup Mode: Job ignored.")
        return "⚠️ UI is in Mockup Mode (Orchestrator not running)."

async def submit_file(video_file, srt_file):
    if not video_file:
        return "❌ Please upload a video."
        
    os.makedirs("uploads", exist_ok=True)
    safe_path = os.path.join("uploads", os.path.basename(video_file.name))
    shutil.copy(video_file.name, safe_path)
        
    chat_id = int(str(Config.TELEGRAM_CHAT_ID).split(',')[0]) if Config.TELEGRAM_CHAT_ID else 0
        
    job = ClipJob(
        job_id=generate_id(),
        source_url=None,
        source_file=safe_path, 
        srt_file=srt_file.name if srt_file else None,
        chat_id=chat_id,
        message_id=None
    )
    
    if job_manager:
        await job_manager.add_job(job)
        log_to_ui(f"✅ Job queued from File: {safe_path}")
        return "✅ Job queued from File."
    else:
        log_to_ui("⚠️ Mockup Mode: Job ignored.")
        return "⚠️ UI is in Mockup Mode (Orchestrator not running)."

def get_logs():
    """Generator for Gradio live updates."""
    if not _log_messages:
        return "Waiting for activity..."
    return "\n".join(_log_messages)

def build_ui(job_mgr=None):
    global job_manager
    job_manager = job_mgr
    
    with gr.Blocks(theme=gr.themes.Base(neutral_hue="slate")) as app:
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
        refresh_btn = gr.Button("🔄 Refresh Logs")
        refresh_btn.click(get_logs, outputs=log_output)
        
        # Load logs once on startup
        app.load(get_logs, outputs=log_output)
        
    return app

async def launch_gradio(job_mgr):
    app = build_ui(job_mgr)
    # Share=True creates the public Colab link
    app.launch(share=True, inline=False, prevent_thread_lock=True)

if __name__ == "__main__":
    # Mockup execution logic for standalone testing in Colab
    print("🚀 Running Gradio in Standalone Mockup Mode...")
    log_to_ui("🚀 Standalone UI test initialized. Jobs will not be processed.")
    app = build_ui(None)
    app.launch(share=True, debug=True)
