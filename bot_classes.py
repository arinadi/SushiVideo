from dataclasses import dataclass, field
from enum import Enum
import time
import uuid

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobPhase(Enum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    TRANSCRIBING = "transcribing"
    AI_SELECTING = "ai_selecting"
    EDITING = "editing"

class TranscriptSource(Enum):
    YOUTUBE_AUTO = "youtube_auto"
    WHISPER = "whisper"
    USER_UPLOAD = "user_upload"

@dataclass
class VideoMeta:
    local_path: str
    duration: float        # seconds
    width: int
    height: int
    is_landscape: bool     # width > height
    original_filename: str
    has_youtube_subs: bool  # True if yt-dlp found subtitles
    subtitle_path: str | None = None # Path to downloaded .srt

@dataclass
class TranscriptData:
    source: TranscriptSource
    srt_content: str
    transcript_text: str
    language: str

@dataclass
class Segment:
    index: int
    start: float | str
    end_time: float | str
    title: str
    reason: str
    caption: str

@dataclass
class ClipJob:
    job_id: str
    chat_id: int
    source_url: str | None = None
    source_file: str | None = None
    srt_file: str | None = None
    message_id: int | None = None
    status: JobStatus = JobStatus.PENDING
    phase: JobPhase = JobPhase.QUEUED
    created_at: float = field(default_factory=time.time)
    
    video_meta: VideoMeta | None = None
    transcript_data: TranscriptData | None = None
    segments: list[Segment] = field(default_factory=list)

def generate_id() -> str:
    return uuid.uuid4().hex[:8]
