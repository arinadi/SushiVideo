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
        if not safe_title:
            safe_title = "clip"
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
    # FFmpeg expects dot instead of comma for fractional seconds
    start_ff = start.replace(',', '.')
    end_ff = end.replace(',', '.')
    stream = ffmpeg.input(source_path, ss=start_ff, to=end_ff)
    
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
    if os.path.getsize(srt_path) > 0:
        # Note: escape path for FFmpeg filter. Absolute path is safer for ffmpeg.
        escaped_srt = os.path.abspath(srt_path).replace('\\', '/').replace(':', '\\:')
        style = f"FontSize={Config.SUBTITLE_FONT_SIZE},FontName=Arial,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2,Alignment=2,MarginV=60,Bold=1"
        v = v.filter('subtitles', escaped_srt, force_style=style)
    else:
        print(f"⚠️ Warning: SRT file {srt_path} is empty. Rendering clip without subtitles.")
    
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
    def _run():
        try:
            out.run(overwrite_output=True, quiet=True)
        except ffmpeg.Error as e:
            err_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            raise RuntimeError(f"FFmpeg failed: {err_msg}")

    await asyncio.to_thread(_run)
