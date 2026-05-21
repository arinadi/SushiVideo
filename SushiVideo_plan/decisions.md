# Architectural Decision Records (ADR): SushiVideo

## ADR-1: Google Colab as Execution Environment
- **Context:** Target users are solo creators without powerful local PCs.
- **Decision:** The entire pipeline runs exclusively on Google Colab's default T4 GPU instance.
- **Consequences:** 
  - **Pros:** Zero cost for user, no local hardware requirements, high bandwidth for downloading.
  - **Cons:** Ephemeral storage (data lost on disconnect), requires 10-minute idle shutdown to preserve GPU limits, no CPU fallback support.

## ADR-2: Dual Input Channels (Telegram + Gradio)
- **Context:** Telegram bots have a hard 50MB file upload limit, which is too small for raw video uploads. However, Telegram is the ideal UI for quick URL submissions.
- **Decision:** Implement both a Telegram bot (for URLs + short SRTs) and a Gradio Web UI (for large raw video uploads). Both feed into the same `asyncio.Queue` managed by the bot.
- **Consequences:** Increases complexity slightly, but solves the file size constraint elegantly while keeping the primary UX inside Telegram.

## ADR-3: Abstracted AI Provider (Segment Selection)
- **Context:** AI models change rapidly in pricing and capabilities. Hardcoding Gemini limits future flexibility.
- **Decision:** Implemented a `SegmentSelector` interface with a factory pattern. Gemini (`gemini-2.5-flash`) is the default, but OpenAI and Anthropic are supported via config.
- **Consequences:** Future-proofs the text analysis step. Text transcripts are sent via API, but media files are never sent over the network to the LLM.

## ADR-4: Local GPU Transcription (Faster-Whisper)
- **Context:** Gemini cannot process large media files natively without high costs or size limits.
- **Decision:** All media-to-text conversion is handled locally on the Colab GPU using `faster-whisper`.
- **Consequences:** Keeps data secure, eliminates transcription API costs. Model loading takes time at startup, but processing is highly efficient.

## ADR-5: Two-Phase Output Pipeline
- **Context:** Video processing via FFmpeg is expensive and time-consuming. If the AI selects poor segments, compute is wasted.
- **Decision:** Output 1 (CSV + SRT files) is delivered to Telegram immediately after AI selection. Output 2 (rendered video clips) follows.
- **Consequences:** Gives the user a chance to review the AI's choices. If the session dies during video rendering, the user at least retains the raw segment data.

## ADR-6: FFmpeg Portrait Filter Chain
- **Context:** Videos need to be converted to 9:16 portrait format for TikTok/Reels without losing important visual information.
- **Decision:** Instead of crop-to-center (which cuts off content), the video is scaled to fit within 9:16 (fit-center), and the remaining empty space is filled with a heavily blurred, scaled-up version of the same video. Subtitles are burned in simultaneously.
- **Consequences:** Professional aesthetic. Achieved entirely within a single complex FFmpeg command (`-filter_complex`), avoiding multi-pass rendering.
