# Module 4: AI Selector

| Field | Value |
|:---|:---|
| **Complexity** | M |
| **Estimated Files** | ~2 (`ai_selector.py`, `prompts.py`) |
| **Key Risks** | RC-3 (AI API failures, rate limits, or bad JSON parsing) |

## Requirements

- Abstract interface (`SegmentSelector`) for AI providers.
- Default implementation using Google Gemini (`gemini-2.5-flash`).
- Formulate prompt to identify viral moments (hooks, emotion, insights).
- Enforce strict JSON output schema from AI provider.
- Parse JSON to list of `Segment` dataclasses.
- Generate standalone SRT file for each segment (slicing original SRT).
- Generate Output 1 (Validation files): `segments.csv` + per-segment SRTs.

## UI Structure

No direct UI. Output files are sent to Telegram via Module 6.

**Status messages:**
```
🧠 AI Chef analyzing transcript ({word_count} words)...
✅ AI selected {n} segments. Generating validation files...
```

## Data & API

### Output: `Segment` Dataclass
```python
from dataclasses import dataclass

@dataclass
class Segment:
    index: int
    start_time: str  # Format: "HH:MM:SS.mmm"
    end_time: str    # Format: "HH:MM:SS.mmm"
    title: str
    reason: str
    caption: str
    srt_content: str = "" # Subset of original SRT just for this segment
```

### JSON Schema (Expected AI Output)
```json
{
  "segments": [
    {
      "start": "00:01:15.000",
      "end": "00:02:10.500",
      "title": "The Hidden Cost of AI",
      "reason": "Strong hook, controversial statement about pricing, high retention potential.",
      "caption": "Is AI actually saving you money? 🤯 #AI #TechTrends"
    }
  ]
}
```

## Technical Implementation

### `ai_selector.py`

```python
import json
import asyncio
from typing import List, Dict, Any
from google import genai
from config import Config
import utils

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
        
        # Use Structured Outputs (JSON Schema) feature of Gemini API if available,
        # or enforce via prompt and parse carefully.
        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.model_name,
            contents=[prompt, transcript_text],
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        return self._parse_response(response.text)
        
    def _parse_response(self, text: str) -> List[Segment]:
        """Parse AI JSON and map to Segment dataclasses."""
        try:
            # Handle potential markdown code blocks returned by LLM
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
```

### Prompt Engineering (`prompts.py`)
- Emphasize finding self-contained thoughts.
- Emphasize respecting `min_duration` and `max_duration`.
- Mandate strict JSON output.

### SRT Slicing Logic
- Need utility function in `utils.py` to parse original SRT, find subtitles overlapping `start_time` and `end_time`, and generate a new SRT with adjusted timestamps (starting from 00:00:00).

## Testing

| # | Test | Command / Check | Pass/Fail |
|:---|:---|:---|:---|
| T4-1 | Factory instantiation | `get_ai_selector()` returns correct class based on config | Binary |
| T4-2 | API Call execution | `selector.select_segments(text)` returns `List[Segment]` | Binary |
| T4-3 | JSON Parsing | Handles markdown-wrapped JSON ```json ... ``` | Binary |
| T4-4 | SRT Slicing | Output segment SRT has timestamps shifted to 00:00:00 base | Binary |
| T4-5 | Fallback behavior | Retries on rate limit (HTTP 429) | Binary |
