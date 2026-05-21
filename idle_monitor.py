import asyncio
import time
import os
from config import Config

class IdleMonitor:
    def __init__(self, job_manager):
        self.job_manager = job_manager
        self.last_activity = time.time()
        self.timeout_minutes = Config.IDLE_SHUTDOWN_MINUTES
        self.enabled = Config.ENABLE_IDLE_MONITOR
        self.task = None

    def reset(self):
        self.last_activity = time.time()

    async def _monitor_loop(self):
        if not self.enabled:
            return
            
        while True:
            await asyncio.sleep(60)
            
            # Don't shutdown if jobs are processing
            if self.job_manager.is_active():
                self.reset()
                continue
                
            elapsed = (time.time() - self.last_activity) / 60
            if elapsed >= self.timeout_minutes:
                print(f"💤 Idle for {elapsed:.1f} minutes. Shutting down runtime...")
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
