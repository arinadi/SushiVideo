import os
import asyncio
import yt_dlp
import ffmpeg
from bot_classes import VideoMeta

YDL_OPTS = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': 'uploads/%(id)s.%(ext)s',
    'writesubtitles': False,
    'writeautomaticsub': False,
    'merge_output_format': 'mp4',
    'quiet': True,
    'no_warnings': True,
}

async def download_video(url: str) -> VideoMeta:
    """Download YouTube video + subtitles via yt-dlp."""
    # Run in thread to avoid blocking
    meta = await asyncio.to_thread(_download_sync, url)
    return meta

def _download_sync(url: str) -> VideoMeta:
    """Synchronous download logic."""
    os.makedirs('uploads', exist_ok=True)
    
    opts = YDL_OPTS.copy()
    if os.path.exists("cookies.txt"):
        opts['cookiefile'] = "cookies.txt"
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info)
        
        # Check for downloaded subtitles
        subtitle_path = _find_subtitle_file(video_path)
        
        # Probe video metadata
        probe = ffmpeg.probe(video_path)
        video_stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        
        return VideoMeta(
            local_path=video_path,
            duration=float(probe['format']['duration']),
            width=int(video_stream['width']),
            height=int(video_stream['height']),
            is_landscape=int(video_stream['width']) > int(video_stream['height']),
            original_filename=info.get('title', 'video'),
            has_youtube_subs=subtitle_path is not None,
            subtitle_path=subtitle_path,
        )

async def process_uploaded_file(file_path: str) -> VideoMeta:
    """Process a directly uploaded video file (from Gradio)."""
    probe = await asyncio.to_thread(ffmpeg.probe, file_path)
    video_stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    
    return VideoMeta(
        local_path=file_path,
        duration=float(probe['format']['duration']),
        width=int(video_stream['width']),
        height=int(video_stream['height']),
        is_landscape=int(video_stream['width']) > int(video_stream['height']),
        original_filename=os.path.basename(file_path),
        has_youtube_subs=False,
        subtitle_path=None,
    )

def _find_subtitle_file(video_path: str) -> str | None:
    """Find SRT file downloaded alongside video."""
    base = os.path.splitext(video_path)[0]
    for lang in ['id', 'en']:
        srt_path = f"{base}.{lang}.srt"
        if os.path.exists(srt_path):
            return srt_path
    return None
