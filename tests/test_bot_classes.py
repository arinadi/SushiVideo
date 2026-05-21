from bot_classes import Segment, TranscriptData, TranscriptSource, VideoMeta, ClipJob

def test_segment_dataclass():
    seg = Segment(index=1, start_time="00:00", end_time="00:01", title="T", reason="R", caption="C")
    assert seg.index == 1
    assert seg.srt_content == ""

def test_video_meta():
    meta = VideoMeta(local_path="test.mp4", duration=10.0, width=1920, height=1080, is_landscape=True, original_filename="test", has_youtube_subs=False)
    assert meta.is_landscape is True
    assert meta.subtitle_path is None
