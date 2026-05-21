import os
import asyncio
from faster_whisper import WhisperModel
import utils
from bot_classes import VideoMeta, TranscriptData, TranscriptSource

_whisper_model = None

async def init_whisper(model_size: str = "large-v2"):
    """Initialize Whisper model in background."""
    global _whisper_model
    if not _whisper_model:
        # Using float16 for CUDA execution in Colab
        _whisper_model = await asyncio.to_thread(
            WhisperModel, model_size, device="cuda", compute_type="float16"
        )

async def get_transcript(video_meta: VideoMeta, user_srt_path: str | None = None) -> TranscriptData:
    """Resolve transcript based on priority."""
    
    # Priority 1: User SRT
    if user_srt_path and os.path.exists(user_srt_path):
        return await _process_existing_srt(user_srt_path, TranscriptSource.USER_UPLOAD)
        
    # Priority 2: YouTube Auto-Sub
    if video_meta.has_youtube_subs and video_meta.subtitle_path:
        return await _process_existing_srt(video_meta.subtitle_path, TranscriptSource.YOUTUBE_AUTO)
        
    # Priority 3: Whisper Generation
    return await _generate_whisper_transcript(video_meta.local_path)

async def _process_existing_srt(srt_path: str, source: TranscriptSource) -> TranscriptData:
    """Read SRT and extract plain text."""
    with open(srt_path, 'r', encoding='utf-8') as f:
        srt_content = f.read()
    
    # Extract plain text from SRT format using simple regex/parsing
    plain_text = utils.srt_to_plaintext(srt_content)
    
    return TranscriptData(
        source=source,
        srt_content=srt_content,
        transcript_text=plain_text,
        language="unknown" # Could parse from yt-dlp filename if needed
    )

async def _generate_whisper_transcript(video_path: str) -> TranscriptData:
    """Run faster-whisper on local video file."""
    global _whisper_model
    if not _whisper_model:
        await init_whisper()
        
    segments_generator, info = await asyncio.to_thread(
        _whisper_model.transcribe, 
        video_path,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500)
    )
    
    # Convert generator to list to force execution
    segments = list(segments_generator)
    
    # Format to SRT and plain text
    srt_content = utils.segments_to_srt(segments)
    plain_text = "\n".join([s.text.strip() for s in segments])
    
    return TranscriptData(
        source=TranscriptSource.WHISPER,
        srt_content=srt_content,
        transcript_text=plain_text,
        language=info.language
    )
