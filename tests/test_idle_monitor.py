import pytest
import time
from unittest.mock import patch
from idle_monitor import IdleMonitor
from job_manager import JobManager

def test_idle_monitor_reset():
    jm = JobManager()
    monitor = IdleMonitor(jm)
    old_time = monitor.last_activity
    time.sleep(0.01)
    monitor.reset()
    assert monitor.last_activity > old_time
