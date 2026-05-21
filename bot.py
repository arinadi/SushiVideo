import os
import asyncio
import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

from config import Config
from job_manager import JobManager
from idle_monitor import IdleMonitor
from bot_classes import ClipJob, generate_id
import downloader
import transcriber
import ai_selector
import video_editor

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Silence httpx logs to prevent getUpdates spam
logging.getLogger("httpx").setLevel(logging.WARNING)

async def auth_check(update: Update) -> bool:
    """Check if the user is authorized based on TELEGRAM_CHAT_ID."""
    if not Config.TELEGRAM_CHAT_ID:
        return True
    allowed = [x.strip() for x in str(Config.TELEGRAM_CHAT_ID).split(',')]
    return str(update.effective_chat.id) in allowed

async def notify(job: ClipJob, bot: Bot, text: str):
    logger.info(f"[{job.job_id}] {text}")
    try:
        await bot.send_message(chat_id=job.chat_id, text=text)
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

class BotHandlers:
    def __init__(self, job_manager: JobManager, idle_monitor: IdleMonitor):
        self.job_manager = job_manager
        self.idle_monitor = idle_monitor

    async def start_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.idle_monitor.reset()
        if not await auth_check(update):
            return
        await update.message.reply_text("🍣 Welcome to SushiVideo!\nSend me a YouTube URL to get started.")

    async def handle_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.idle_monitor.reset()
        if not await auth_check(update):
            return
            
        import re
        url_text = update.message.text or ""
        url_match = re.search(r'(https?://[^\s]+)', url_text)
        
        if not url_match or ("youtube.com" not in url_match.group(1) and "youtu.be" not in url_match.group(1)):
            await update.message.reply_text("❌ Please send a valid YouTube URL.")
            return
            
        url = url_match.group(1)
            
        job = ClipJob(
            job_id=generate_id(),
            source_url=url,
            chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )
        
        await self.job_manager.add_job(job)
        await update.message.reply_text(f"✅ Order queued: {url}")

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.idle_monitor.reset()
        if not await auth_check(update):
            return
            
        doc = update.message.document
        if not doc.file_name.lower().endswith('.srt'):
            await update.message.reply_text("❌ Please upload a valid .srt file.")
            return
            
        import re
        url_text = update.message.caption or ""
        url_match = re.search(r'(https?://[^\s]+)', url_text)
        
        if not url_match or ("youtube.com" not in url_match.group(1) and "youtu.be" not in url_match.group(1)):
            await update.message.reply_text("❌ Please provide a valid YouTube URL in the caption of the file.")
            return
            
        url = url_match.group(1)
            
        file = await context.bot.get_file(doc.file_id)
        os.makedirs("uploads", exist_ok=True)
        safe_path = os.path.join("uploads", f"{doc.file_id}.srt")
        await file.download_to_drive(safe_path)
        
        job = ClipJob(
            job_id=generate_id(),
            source_url=url,
            srt_file=safe_path,
            chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )
        
        await self.job_manager.add_job(job)
        await update.message.reply_text(f"✅ Order queued with custom SRT: {url}")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == "extend_idle":
            if self.idle_monitor.extend_timer(5):
                await query.edit_message_text(
                    f"✅ *Idle Extended*\nTimer added +5 minutes.\n_Action by {query.from_user.first_name}_",
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text("ℹ️ Bot is already active, no need to extend.")

async def process_queue_loop(job_manager: JobManager, idle_monitor: IdleMonitor, bot: Bot):
    while True:
        job = await job_manager.queue.get()
        job_manager.set_processing(job)
        idle_monitor.reset()
        
        try:
            # Phase 1: Download
            if job.source_url:
                await notify(job, bot, "🐟 Downloading video...")
                video_meta = await downloader.download_video(job.source_url)
            else:
                await notify(job, bot, "🐟 Analyzing uploaded video...")
                video_meta = await downloader.process_uploaded_file(job.source_file)
                
            job.video_meta = video_meta
            idle_monitor.reset()
            
            # Phase 2: Transcribe
            await notify(job, bot, "🤖 Extracting/Generating transcript...")
            transcript_data = await transcriber.get_transcript(video_meta, job.srt_file)
            job.transcript_data = transcript_data
            idle_monitor.reset()
            
            # Phase 3: AI Selection
            await notify(job, bot, "🧠 AI Chef selecting best cuts...")
            ai = ai_selector.get_ai_selector()
            segments = await ai.select_segments(transcript_data.transcript_text)
            
            # Apply 3s buffer to segments
            import utils
            for seg in segments:
                start_sec = utils.time_to_seconds(seg.start_time)
                end_sec = utils.time_to_seconds(seg.end_time)
                
                start_sec = max(0.0, start_sec - 3.0)
                end_sec = min(video_meta.duration, end_sec + 3.0)
                
                seg.start_time = utils.format_timestamp(start_sec)
                seg.end_time = utils.format_timestamp(end_sec)
                
            job.segments = segments
            idle_monitor.reset()
            
            # Output 1: Delivery
            out_dir = f"video_clipper/{job.job_id}"
            ai_selector.save_output_1(segments, transcript_data.srt_content, base_dir=out_dir)
            
            csv_path = os.path.join(out_dir, "segments.csv")
            if os.path.exists(csv_path):
                with open(csv_path, 'rb') as f:
                    await bot.send_document(chat_id=job.chat_id, document=f, caption="📊 Validation Data")
            
            # Phase 4: Editing
            await notify(job, bot, f"🔪 Editing {len(segments)} clips...")
            output_clips = await video_editor.process_segments(video_meta, segments, out_dir)
            idle_monitor.reset()
            
            # Output 2: Delivery
            for clip in output_clips:
                size_mb = os.path.getsize(clip) / (1024 * 1024)
                if size_mb > Config.BOT_FILESIZE_LIMIT:
                    await notify(job, bot, f"⚠️ Clip exceeds {Config.BOT_FILESIZE_LIMIT}MB limit ({size_mb:.1f}MB). Saved to folder: {clip}")
                else:
                    with open(clip, 'rb') as f:
                        await bot.send_video(chat_id=job.chat_id, video=f)
                
            await notify(job, bot, "🍱 Order complete!")
            
        except Exception as e:
            logger.error(f"Job {job.job_id} failed: {e}", exc_info=True)
            await notify(job, bot, f"❌ Error processing job: {e}")
            job_manager.complete(job, failed=True)
        else:
            job_manager.complete(job, failed=False)
        finally:
            idle_monitor.reset()

def get_application(job_manager: JobManager, idle_monitor: IdleMonitor) -> Application:
    # Build app with telegram token, warn if missing but do not crash immediately so tests can pass
    token = Config.TELEGRAM_TOKEN or "DUMMY_TOKEN_FOR_TESTS"
    app = Application.builder().token(token).build()
    
    idle_monitor.bot = app.bot
    
    handlers = BotHandlers(job_manager, idle_monitor)
    app.add_handler(CommandHandler("start", handlers.start_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_url))
    app.add_handler(MessageHandler(filters.Document.ALL, handlers.handle_document))
    app.add_handler(CallbackQueryHandler(handlers.handle_callback))
    
    # Store process loop method in JobManager for main.py to call
    job_manager.process_queue_loop = lambda: process_queue_loop(job_manager, idle_monitor, app.bot)
    
    return app
