import os
import json
import pytest
from unittest.mock import patch, MagicMock
from ai_selector import GeminiSelector, save_output_1, get_ai_selector
from bot_classes import Segment

def test_parse_response_valid_json():
    selector = GeminiSelector("dummy_key", "dummy_model")
    mock_json = """```json
    {
        "segments": [
            {
                "start": "00:00:00.000",
                "end": "00:00:10.000",
                "title": "Test Title",
                "reason": "Test Reason",
                "caption": "Test Caption"
            }
        ]
    }
    ```"""
    segments = selector._parse_response(mock_json)
    assert len(segments) == 1
    assert segments[0].title == "Test Title"
    assert segments[0].start_time == "00:00:00.000"
    assert segments[0].index == 1

def test_parse_response_invalid_json():
    selector = GeminiSelector("dummy_key", "dummy_model")
    with pytest.raises(ValueError, match="Failed to parse AI output"):
        selector._parse_response("this is not json")

def test_save_output_1(tmp_path):
    segments = [
        Segment(index=1, start_time="00:00:01.000", end_time="00:00:05.000", title="A", reason="B", caption="C")
    ]
    original_srt = "1\n00:00:01,000 --> 00:00:05,000\nHello\n"
    
    # tmp_path is a pytest fixture providing a temporary directory
    output_dir = tmp_path / "video_clipper"
    save_output_1(segments, original_srt, base_dir=str(output_dir))
    
    # Check CSV
    assert (output_dir / "segments.csv").exists()
    
    # Check SRT
    srt_file = output_dir / "segment_1.srt"
    assert srt_file.exists()
    assert "Hello" in srt_file.read_text(encoding="utf-8")

@patch('ai_selector.Config')
def test_get_ai_selector(mock_config):
    mock_config.AI_PROVIDER = "gemini"
    mock_config.AI_MODEL = "gemini-test"
    mock_config.AI_API_KEY = "test_key"
    
    selector = get_ai_selector()
    assert isinstance(selector, GeminiSelector)
    assert selector.model_name == "gemini-test"
