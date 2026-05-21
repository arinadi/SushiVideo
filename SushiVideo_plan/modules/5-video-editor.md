# Module 5: Video Editor

| Field | Value |
|:---|:---|
| **Complexity** | L |
| **Estimated Files** | ~1 (`video_editor.py`) |
| **Key Risks** | RC-4 (FFmpeg failure due to bad video codec, incorrect timestamps, OOM) |

## Requirements

- Process each `Segment` independently.
- Use `ffmpeg-python` to construct complex filter graphs.
- Core pipeline per clip:
  1. Cut segment from source video (fast seek `-ss`).
  2. Adjust speed (audio `atempo`, video `setpts`).
  3. Reformat to 9:16 portrait (fit-center) IF source is landscape.
  4. Generate blurred background from source.
  5. Burn hardcoded subtitles (using segment-specific SRT).
- Handle cleanup of intermediate files.
- Monitor processing progress (optional, but good for UX).

## UI Structure

No direct UI.

**Status messages:**
```
🎬 Editing clip 1/3: "The Hidden Cost"
🎬 Editing clip 2/3: "Why Startups Fail"
✅ All clips edited successfully.
```

## Data & API

### Input
- `VideoMeta` (source video path, properties)
- `Segment` (cut timestamps, titles, specific SRT)

### Output
- List of file paths to the generated MP4 clips.

## Technical Implementation

### `video_editor.py`

```python
import os
import asyncio
import ffmpeg
from config import Config
from bot_classes import VideoMeta, Segment

async def process_segments(video_meta: VideoMeta, segments: list[Segment], output_dir: str) -> list[str]:
    """Process all segments sequentially to avoid OOM on Colab."""
    output_files = []
    
    os.makedirs(output_dir, exist_ok=True)
    
    for seg in segments:
        safe_title = "".join([c for c in seg.title if c.isalnum() or c in (' ', '-', '_')]).rstrip()
        safe_title = safe_title.replace(" ", "_").lower()
        output_filename = f"clip_{seg.index}_{safe_title}.mp4"
        output_path = os.path.join(output_dir, output_filename)
        
        # Write temporary segment SRT
        temp_srt = os.path.join(output_dir, f"temp_{seg.index}.srt")
        with open(temp_srt, "w", encoding="utf-8") as f:
            f.write(seg.srt_content)
            
        try:
            await _render_clip(
                source_path=video_meta.local_path,
                start=seg.start_time,
                end=seg.end_time,
                srt_path=temp_srt,
                output_path=output_path,
                is_landscape=video_meta.is_landscape,
                speed=Config.SPEED_FACTOR
            )
            output_files.append(output_path)
        except Exception as e:
            print(f"Error processing segment {seg.index}: {e}")
            # Continue to next segment rather than failing entire job
        finally:
            if os.path.exists(temp_srt):
                os.remove(temp_srt)
                
    return output_files

async def _render_clip(source_path: str, start: str, end: str, srt_path: str, output_path: str, is_landscape: bool, speed: float):
    """Construct and execute FFmpeg command."""
    
    # Fast seek using -ss before input
    stream = ffmpeg.input(source_path, ss=start, to=end)
    
    v = stream.video
    a = stream.audio
    
    # 1. Speed Adjustment
    if speed != 1.0:
        v = v.filter('setpts', f'PTS/{speed}')
        a = a.filter('atempo', speed)
        
    # 2. Portrait Reformat & Blur Background
    if is_landscape:
        # Split stream
        split = v.split()
        bg = split[0]
        fg = split[1]
        
        # Background: scale to fill 1080x1920, crop excess, blur
        bg = bg.filter('scale', 1080, 1920, force_original_aspect_ratio='increase')
        bg = bg.filter('crop', 1080, 1920)
        bg = bg.filter('gblur', sigma=20)
        
        # Foreground: scale to fit 1080x1920 keeping aspect ratio
        fg = fg.filter('scale', 1080, 1920, force_original_aspect_ratio='decrease')
        
        # Overlay fg on bg center
        v = ffmpeg.overlay(bg, fg, x='(W-w)/2', y='(H-h)/2')
    
    # 3. Hard Subtitles
    # Note: escape path for FFmpeg filter
    escaped_srt = srt_path.replace('\\', '/').replace(':', '\\:')
    style = f"FontSize={Config.SUBTITLE_FONT_SIZE},FontName=DejaVu Sans,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2,Alignment=2,MarginV=40"
    v = v.filter('subtitles', escaped_srt, force_style=style)
    
    # 4. Output configuration
    # Use libx264, veryfast preset for Colab efficiency
    out = ffmpeg.output(
        v, a, output_path, 
        vcodec='libx264', 
        preset='veryfast', 
        crf=22, 
        acodec='aac'
    )
    
    # Run async
    await asyncio.to_thread(out.run, overwrite_output=True, quiet=True)
```

## Testing

| # | Test | Command / Check | Pass/Fail |
|:---|:---|:---|:---|
| T5-1 | Render landscape video | Input 16:9 produces 9:16 with blur bg | Binary |
| T5-2 | Render portrait video | Input 9:16 passes through layout unchanged | Binary |
| T5-3 | Subtitle burn | Output MP4 has hardcoded text matching SRT | Binary |
| T5-4 | Error isolation | One failed segment does not stop processing of next segment | Binary |
