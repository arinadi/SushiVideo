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

def extract_json_from_markdown(text: str) -> str:
    """Extract JSON string from markdown code block if present."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("\n", 1)[0]
    return text.strip()

def time_to_seconds(time_str: str) -> float:
    """Convert HH:MM:SS,mmm or HH:MM:SS.mmm to seconds."""
    time_str = time_str.replace(',', '.')
    parts = time_str.split(':')
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    return float(time_str)

def slice_srt(srt_content: str, start_time_str: str, end_time_str: str) -> str:
    """Extract and re-time SRT subtitles between start and end times."""
    start_sec = time_to_seconds(start_time_str)
    end_sec = time_to_seconds(end_time_str)
    
    lines = srt_content.strip().split('\n')
    new_srt_parts = []
    
    i = 0
    seq_out = 1
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        if line.isdigit():
            i += 1
            if i >= len(lines): break
            time_line = lines[i].strip()
            if '-->' not in time_line:
                continue
                
            times = time_line.split('-->')
            sub_start = time_to_seconds(times[0].strip())
            sub_end = time_to_seconds(times[1].strip())
            
            i += 1
            text_lines = []
            while i < len(lines) and lines[i].strip():
                text_lines.append(lines[i].strip())
                i += 1
                
            # Check overlap
            if sub_start < end_sec and sub_end > start_sec:
                # Adjust timestamps relative to segment start
                adj_start = max(0.0, sub_start - start_sec)
                adj_end = min(end_sec - start_sec, sub_end - start_sec)
                
                new_start_str = format_timestamp(adj_start)
                new_end_str = format_timestamp(adj_end)
                
                new_srt_parts.append(f"{seq_out}\n{new_start_str} --> {new_end_str}\n" + "\n".join(text_lines) + "\n")
                seq_out += 1
        else:
            i += 1
            
    return "\n".join(new_srt_parts)
