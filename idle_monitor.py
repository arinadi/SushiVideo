import asyncio
import time
import os
from config import Config
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class IdleMonitor:
    def __init__(self, job_manager):
        self.job_manager = job_manager
        self.bot = None
        self.timeout_minutes = Config.IDLE_SHUTDOWN_MINUTES
        self.enabled = Config.ENABLE_IDLE_MONITOR
        self.task = None
        
        self.shutdown_on = None
        self.shutdown_imminent = False
        self.alerts_sent = {'first': False, 'warn': False}

    def reset(self):
        if self.shutdown_on is not None:
            self.shutdown_on = None
            self.alerts_sent = {'first': False, 'warn': False}

    def extend_timer(self, minutes: int):
        if self.shutdown_on is not None:
            self.shutdown_on += (minutes * 60)
            self.alerts_sent = {'first': False, 'warn': False}
            return True
        return False

    async def _notify(self, text: str, reply_markup=None):
        if not self.bot or not Config.TELEGRAM_CHAT_ID:
            return
        chat_id = int(str(Config.TELEGRAM_CHAT_ID).split(',')[0])
        try:
            await self.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=reply_markup)
        except Exception as e:
            print(f"Failed to send idle alert: {e}")

    async def _monitor_loop(self):
        if not self.enabled:
            return
            
        while True:
            await asyncio.sleep(60)
            
            if self.shutdown_imminent:
                continue
                
            if self.job_manager.is_active():
                self.reset()
                continue
                
            if self.shutdown_on is None:
                self.shutdown_on = time.time() + (self.timeout_minutes * 60)
                
            remaining = (self.shutdown_on - time.time()) / 60
            elapsed = self.timeout_minutes - remaining
            
            if remaining > 0 and elapsed >= self.timeout_minutes / 2:
                print(f"💤 System idle. Shutdown in {remaining:.1f} minutes...")
                
            # First Alert (Halfway)
            if elapsed >= (self.timeout_minutes / 2) and not self.alerts_sent['first']:
                self.alerts_sent['first'] = True
                kb = InlineKeyboardMarkup([[InlineKeyboardButton("⏳ +5m", callback_data="extend_idle")]])
                await self._notify(f"⏸️ *Idle Alert*\nSushiVideo will shut down in `{int(remaining)}m`.", reply_markup=kb)
                
            # Final Warning (1 min left)
            if remaining <= 1.0 and remaining > 0 and not self.alerts_sent['warn']:
                self.alerts_sent['warn'] = True
                await self._notify(f"⚠️ *Final Warning*\nShutdown in `< 1m`!")
                
            if remaining <= 0:
                self.shutdown_imminent = True
                await self._notify(f"🔴 *Shutting down* (idle for {self.timeout_minutes}m)")
                print(f"🛑 Idle limit reached. Shutting down runtime...")
                self._shutdown()
                
    def start(self):
        self.task = asyncio.create_task(self._monitor_loop())
        
    def _shutdown(self):
        if Config.IS_COLAB:
            try:
                from google.colab import runtime
                runtime.unassign()
            except Exception:
                os._exit(0)
        else:
            print("Not in Colab. Would have shut down.")
            os._exit(0)
