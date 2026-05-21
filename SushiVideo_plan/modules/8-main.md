# Module 8: Main Orchestrator

| Field | Value |
|:---|:---|
| **Complexity** | M |
| **Estimated Files** | ~1 (`main.py`) |
| **Key Risks** | Startup order dependency, graceful shutdown |

## Requirements

- Tie all modules together.
- Setup Python `logging` to stream to console.
- Initialize `Config`.
- Create `JobManager` and `IdleMonitor`.
- Build Telegram `Application`.
- Create asyncio tasks for background workers (Gradio UI, Queue Processor, Idle Monitor).
- Start polling.
- Handle fatal exceptions gracefully (trigger Colab shutdown if unrecoverable).

## UI Structure

No UI. Entry point script.

## Data & API

No specific data structures. Wires dependencies.

## Technical Implementation

### `main.py`
*(Pattern strictly follows TTB `main.py` structure)*

```python
import asyncio
import sys
import os
import nest_asyncio

from config import Config
from bot import JobManager, IdleMonitor, get_application
from gradio_ui import launch_gradio

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
        await application.bot.send_message(
            chat_id=Config.TELEGRAM_CHAT_ID,
            text="🍣 *SushiVideo is ready*\nSend a link or use the Web UI.",
            parse_mode="Markdown"
        )
        
    app.post_init = post_init
    
    # 6. Start Polling
    await app.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Stopped by user.")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        # Emergency Colab Shutdown
        if Config.IS_COLAB:
            try:
                from google.colab import runtime
                runtime.unassign()
            except:
                pass
```

## Testing

| # | Test | Command / Check | Pass/Fail |
|:---|:---|:---|:---|
| T8-1 | Startup | Script runs without exceptions | Binary |
| T8-2 | Telegram hook | Bot sends startup message | Binary |
| T8-3 | Gradio hook | Gradio URL is generated and accessible | Binary |
| T8-4 | Graceful Exit | Ctrl+C stops cleanly without hanging | Binary |
