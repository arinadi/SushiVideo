import json
import asyncio
from typing import List
from google import genai
from config import Config
import utils
from bot_classes import Segment
from prompts import get_viral_segment_prompt

class SegmentSelector:
    """Base interface for AI providers."""
    async def select_segments(self, transcript_text: str) -> List[Segment]:
        raise NotImplementedError

class GeminiSelector(SegmentSelector):
    def __init__(self, api_key: str, model_name: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    async def select_segments(self, transcript_text: str) -> List[Segment]:
        prompt = get_viral_segment_prompt(
            max_segments=Config.MAX_SEGMENTS,
            min_duration=Config.MIN_SEGMENT_DURATION,
            max_duration=Config.MAX_SEGMENT_DURATION
        )
        
        # Handle rate limit retries (T4-5)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.model_name,
                    contents=[prompt, transcript_text],
                    config=genai.types.GenerateContentConfig(
                        response_mime_type="application/json",
                    )
                )
                return self._parse_response(response.text)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        
    def _parse_response(self, text: str) -> List[Segment]:
        """Parse AI JSON and map to Segment dataclasses."""
        try:
            clean_text = utils.extract_json_from_markdown(text)
            data = json.loads(clean_text)
            
            segments = []
            for i, item in enumerate(data.get("segments", [])):
                segments.append(Segment(
                    index=i+1,
                    start_time=item["start"],
                    end_time=item["end"],
                    title=item["title"],
                    reason=item["reason"],
                    caption=item["caption"]
                ))
            return segments
        except Exception as e:
            raise ValueError(f"Failed to parse AI output: {e}\nRaw output: {text}")

def get_ai_selector() -> SegmentSelector:
    """Factory method based on Config."""
    provider = Config.AI_PROVIDER.lower()
    
    if provider == "gemini":
        model = Config.AI_MODEL or "gemini-2.5-flash"
        return GeminiSelector(Config.AI_API_KEY, model)
    else:
        raise ValueError(f"Unsupported AI provider: {provider}")

def save_output_1(segments: List[Segment], original_srt: str, base_dir: str = "video_clipper"):
    """Generate Output 1 (Validation files): segments.csv + per-segment SRTs."""
    import os
    import csv
    
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Save CSV
    csv_path = os.path.join(base_dir, "segments.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Index', 'Start', 'End', 'Title', 'Reason', 'Caption'])
        for s in segments:
            writer.writerow([s.index, s.start_time, s.end_time, s.title, s.reason, s.caption])
            
    # 2. Slice and save SRTs
    for s in segments:
        s.srt_content = utils.slice_srt(original_srt, s.start_time, s.end_time)
        srt_path = os.path.join(base_dir, f"segment_{s.index}.srt")
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(s.srt_content)

