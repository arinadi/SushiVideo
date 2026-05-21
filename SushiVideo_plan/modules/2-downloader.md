# Module 2: Downloader

| Field | Value |
|:---|:---|
| **Complexity** | M |
| **Estimated Files** | ~1 (`downloader.py`) |
| **Key Risks** | RC-1 (YouTube download failure: geo-block, age-gate, rate limit) |

## Requirements

- Download YouTube videos via yt-dlp with best available quality.
- Extract YouTube auto-subtitles (SRT format) if available.
- Support direct video file input (from Gradio upload — just validate + probe).
- Return `VideoMeta` dataclass with file path, duration, resolution, landscape flag.
- All operations async-friendly (run in thread to avoid blocking event loop).

## UI Structure

No direct UI. Called by Telegram Bot and Gradio modules.

**Status messages sent during download:**
```
🐟 Downloading fresh ingredients...
🐟 Download complete — {duration} ({resolution})
```

## Data & API

### Input
| Parameter | Type | Source |
|:---|:---|:---|
| `url` | `str` | YouTube URL from user |
| `file_path` | `str` | Local path from Gradio upload |

### Output: `VideoMeta` Dataclass
```python
@dataclass
class VideoMeta:
    local_path: str
    duration: float        # seconds
    width: int
    height: int
    is_landscape: bool     # width > height
    original_filename: str
    has_youtube_subs: bool  # True if yt-dlp found subtitles
    subtitle_path: str | None  # Path to downloaded .srt
```

### yt-dlp Options
```python
YDL_OPTS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': 'uploads/%(id)s.%(ext)s',
    'writesubtitles': True,
    'writeautomaticsub': True,
    'subtitlesformat': 'srt',
    'subtitleslangs': ['id', 'en'],  # Indonesian first, English fallback
    'merge_output_format': 'mp4',
    'quiet': True,
    'no_warnings': True,
}
```

## Technical Implementation

### `downloader.py`

```python
async def download_video(url: str) -> VideoMeta:
    """Download YouTube video + subtitles via yt-dlp."""
    # Run in thread to avoid blocking
    meta = await asyncio.to_thread(_download_sync, url)
    return meta

def _download_sync(url: str) -> VideoMeta:
    """Synchronous download logic."""
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
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
```

## Testing

| # | Test | Command / Check | Pass/Fail |
|:---|:---|:---|:---|
| T2-1 | Download short YouTube video | `download_video("https://youtu.be/test")` returns valid `VideoMeta` | Binary |
| T2-2 | VideoMeta fields populated | `meta.duration > 0` and `meta.width > 0` | Binary |
| T2-3 | Subtitle extraction | `meta.has_youtube_subs` is `True` for video with captions | Binary |
| T2-4 | File upload processing | `process_uploaded_file("test.mp4")` returns valid `VideoMeta` | Binary |
| T2-5 | Invalid URL handling | `download_video("invalid")` raises handled exception | Binary |
