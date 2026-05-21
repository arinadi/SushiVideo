def srt_to_plaintext(srt_content: str) -> str:
    """Extract plain text from SRT format."""
    lines = srt_content.split('\n')
    text_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip sequence numbers
        if line.isdigit():
            continue
        # Skip timestamp lines
        if '-->' in line:
            continue
        text_lines.append(line)
        
    return ' '.join(text_lines)

def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format 00:00:00,000"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def segments_to_srt(segments: list) -> str:
    """Convert faster_whisper segments to SRT content string."""
    srt_parts = []
    for i, segment in enumerate(segments, start=1):
        start_time = format_timestamp(segment.start)
        end_time = format_timestamp(segment.end)
        text = segment.text.strip()
        srt_parts.append(f"{i}\n{start_time} --> {end_time}\n{text}\n")
    return "\n".join(srt_parts)
