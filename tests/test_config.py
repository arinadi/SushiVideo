import os
from config import Config, IS_COLAB

def test_config_defaults():
    # If not overridden by env vars, SPEED_FACTOR should be 1.25
    assert Config.SPEED_FACTOR == 1.25
    assert Config.MAX_SEGMENTS == 5
    assert Config.AI_PROVIDER == 'gemini'

def test_is_colab():
    assert isinstance(IS_COLAB, bool)
