import utils

def test_time_to_seconds():
    assert utils.time_to_seconds("00:00:05,000") == 5.0
    assert utils.time_to_seconds("00:01:15.500") == 75.5
    assert utils.time_to_seconds("01:00:00.000") == 3600.0

def test_format_timestamp():
    assert utils.format_timestamp(5.0) == "00:00:05,000"
    assert utils.format_timestamp(75.5) == "00:01:15,500"

def test_extract_json_from_markdown():
    markdown = "```json\n{\"test\": 123}\n```"
    assert utils.extract_json_from_markdown(markdown) == "{\"test\": 123}"
    
    raw = "{\"test\": 123}"
    assert utils.extract_json_from_markdown(raw) == "{\"test\": 123}"

def test_slice_srt():
    original_srt = "1\n00:00:01,000 --> 00:00:05,000\nHello World\n\n2\n00:00:10,000 --> 00:00:15,000\nSkip this"
    
    # Slice from 0s to 6s
    sliced = utils.slice_srt(original_srt, "00:00:00,000", "00:00:06,000")
    assert "Hello World" in sliced
    assert "Skip this" not in sliced
    
    # Check that timestamps were adjusted (base relative)
    assert "00:00:01,000 --> 00:00:05,000" in sliced
