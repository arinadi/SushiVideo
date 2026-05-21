import asyncio
import sys
import os
import nest_asyncio

from config import Config
from bot import get_application
from job_manager import JobManager
from idle_monitor import IdleMonitor
from gradio_ui import launch_gradio

# Apply nest_asyncio to allow asyncio.run() within Colab's existing event loop
nest_asyncio.apply()

async def main():
    print("🍣 Starting SushiVideo Orchestrator...")
    
    # 1. Init Core Services
    job_manager = JobManager()
    idle_monitor = IdleMonitor(job_manager)
    
    # 2. Build Telegram App
    app = get_application(job_manager, idle_monitor)
    
    async def post_init(application):
        # 3. Start Background Tasks after bot connects
        application.create_task(job_manager.process_queue_loop())
        
        if Config.ENABLE_IDLE_MONITOR:
            idle_monitor.start()
            
        # 4. Launch Gradio (non-blocking)
        application.create_task(launch_gradio(job_manager))
        
        # 5. Send Startup Message
        if Config.TELEGRAM_CHAT_ID:
            chat_id = int(str(Config.TELEGRAM_CHAT_ID).split(',')[0])
            try:
                await application.bot.send_message(
                    chat_id=chat_id,
                    text="🍣 *SushiVideo is ready*\nSend a link or use the Web UI.",
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"Warning: Failed to send startup message to {chat_id}: {e}")
        
    app.post_init = post_init
    
    # 6. Start Polling
    print("🤖 Telegram Bot Polling Started...")
    await app.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Stopped by user.")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        # Emergency Colab Shutdown if configured
        if Config.IS_COLAB:
            try:
                from google.colab import runtime
                print("⚠️ Unassigning Colab runtime...")
                runtime.unassign()
            except Exception:
                pass
