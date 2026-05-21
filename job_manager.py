import asyncio
from bot_classes import ClipJob, JobStatus

class JobManager:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.active_jobs = {}
        
    async def add_job(self, job: ClipJob):
        self.active_jobs[job.job_id] = job
        await self.queue.put(job)
        
    def set_processing(self, job: ClipJob):
        job.status = JobStatus.PROCESSING
        
    def complete(self, job: ClipJob, failed: bool = False):
        job.status = JobStatus.FAILED if failed else JobStatus.COMPLETED
        if job.job_id in self.active_jobs:
            del self.active_jobs[job.job_id]

    def is_active(self) -> bool:
        return len(self.active_jobs) > 0
