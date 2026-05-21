import pytest
import time
import asyncio
from unittest.mock import patch, MagicMock
from idle_monitor import IdleMonitor
from job_manager import JobManager

def test_idle_monitor_reset():
    jm = JobManager()
    monitor = IdleMonitor(jm)
    old_time = monitor.last_activity
    time.sleep(0.01)
    monitor.reset()
    assert monitor.last_activity > old_time

@pytest.mark.asyncio
@patch('idle_monitor.os._exit')
async def test_monitor_loop_shutdown(mock_exit):
    jm = JobManager()
    monitor = IdleMonitor(jm)
    monitor.enabled = True
    monitor.timeout_minutes = 0
    monitor.last_activity = time.time() - 100
    
    with patch('asyncio.sleep', side_effect=[None, Exception("StopLoop")]):
        try:
            await monitor._monitor_loop()
        except Exception:
            pass
            
    mock_exit.assert_called_once_with(0)

@pytest.mark.asyncio
@patch('idle_monitor.os._exit')
async def test_monitor_loop_active_job(mock_exit):
    jm = JobManager()
    jm.is_active = MagicMock(return_value=True)
    monitor = IdleMonitor(jm)
    monitor.enabled = True
    monitor.timeout_minutes = 0
    monitor.last_activity = time.time() - 100
    
    with patch('asyncio.sleep', side_effect=[None, Exception("StopLoop")]):
        try:
            await monitor._monitor_loop()
        except Exception:
            pass
            
    mock_exit.assert_not_called()
