import pytest
import asyncio
from job_manager import JobManager
from bot_classes import ClipJob, JobStatus, generate_id

@pytest.mark.asyncio
async def test_job_manager_flow():
    jm = JobManager()
    assert not jm.is_active()
    
    job = ClipJob(job_id=generate_id(), chat_id=1)
    await jm.add_job(job)
    
    assert jm.is_active()
    assert jm.queue.qsize() == 1
    
    queued_job = await jm.queue.get()
    assert queued_job.job_id == job.job_id
    
    jm.set_processing(job)
    assert job.status == JobStatus.PROCESSING
    
    jm.complete(job, failed=False)
    assert job.status == JobStatus.COMPLETED
    assert not jm.is_active()
