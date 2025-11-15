# Requirements Specification

## Overview

MemeVid is an AI-powered system that automatically generates meme videos from short-form video clips. The system uses LangGraph to orchestrate a multi-stage workflow that analyzes videos, selects humor strategies, generates captions, and renders final meme videos with human-in-the-loop review.

## Functional Requirements

### FR1: Video Input Processing
- **FR1.1**: System MUST accept video files in common formats (MP4, MOV, MKV)
- **FR1.2**: System MUST extract video duration using FFprobe
- **FR1.3**: System MUST validate file existence and accessibility
- **FR1.4**: System MUST handle video files up to 100MB in size
- **FR1.5**: System MUST support videos with duration between 5-60 seconds

### FR2: Video Analysis
- **FR2.1**: System MUST analyze video content using Google Gemini API
- **FR2.2**: System MUST extract structured insights including:
  - Raw description (one-paragraph summary)
  - Timeline segments (6-10 segments, minimum 5 seconds each)
  - Action/activity tags with humor potential markers
- **FR2.3**: System MUST ensure timeline segments cover the entire video chronologically
- **FR2.4**: System MUST clamp timestamps to video duration bounds

### FR3: Humor Strategy Selection
- **FR3.1**: System MUST load humor levers from `humor_levers.yaml` configuration
- **FR3.2**: System MUST select one humor lever from available options based on video content
- **FR3.3**: System MUST match a timeline segment to the selected humor lever
- **FR3.4**: System MUST generate a humor framing text describing the selected strategy
- **FR3.5**: System MUST store selected lever details and matched segment in state

### FR4: Caption Generation
- **FR4.1**: System MUST generate 3-5 candidate captions using OpenAI
- **FR4.2**: System MUST ensure captions are ≤50 characters each
- **FR4.3**: System MUST align captions with selected humor lever and segment context
- **FR4.4**: System MUST tune captions for GenZ Indian audience humor
- **FR4.5**: System MUST return captions as a numbered list

### FR5: Human-in-the-Loop Review
- **FR5.1**: System MUST pause workflow execution at caption selection stage
- **FR5.2**: System MUST expose candidate captions via Streamlit UI
- **FR5.3**: System MUST allow human reviewer to select preferred caption
- **FR5.4**: System MUST allow custom caption input as alternative
- **FR5.5**: System MUST resume workflow with selected caption
- **FR5.6**: System MUST use LangGraph `interrupt` mechanism for workflow pause

### FR6: Timing Composition
- **FR6.1**: System MUST determine start/end times for caption overlay
- **FR6.2**: System MUST use LLM to extract timing from selected scene segment
- **FR6.3**: System MUST validate timing window (start < end)
- **FR6.4**: System MUST create timing plan with single beat for selected caption

### FR7: Video Rendering
- **FR7.1**: System MUST construct FFmpeg commands for caption overlay
- **FR7.2**: System MUST handle multi-line caption text wrapping
- **FR7.3**: System MUST position captions in lower third of video
- **FR7.4**: System MUST apply proper font styling (white text, black semi-transparent box)
- **FR7.5**: System MUST center-align captions horizontally
- **FR7.6**: System MUST execute FFmpeg to produce final rendered video
- **FR7.7**: System MUST save output to `renders/` directory

### FR8: API Interface
- **FR8.1**: System MUST expose FastAPI endpoints for workflow execution
- **FR8.2**: System MUST support `/jokestruc/generate` endpoint to start workflow
- **FR8.3**: System MUST support `/jokestruc/resume` endpoint to resume after review
- **FR8.4**: System MUST return thread_id for workflow tracking
- **FR8.5**: System MUST return interrupt payload when awaiting human review
- **FR8.6**: System MUST return final state when workflow completes

### FR9: Streamlit UI
- **FR9.1**: System MUST provide file upload interface for video selection
- **FR9.2**: System MUST display candidate captions for review
- **FR9.3**: System MUST provide selection mechanism (dropdown or custom input)
- **FR9.4**: System MUST display final rendered video
- **FR9.5**: System MUST display workflow logs and timing plan
- **FR9.6**: System MUST handle API timeouts gracefully (180+ seconds)

## Non-Functional Requirements

### NFR1: Performance
- **NFR1.1**: Video analysis MUST complete within 300 seconds for files up to 100MB
- **NFR1.2**: Caption generation MUST complete within 30 seconds
- **NFR1.3**: Video rendering MUST complete within 60 seconds for 60-second clips
- **NFR1.4**: API endpoints MUST respond within 5 seconds for non-processing requests

### NFR2: Reliability
- **NFR2.1**: System MUST handle API failures gracefully with error messages
- **NFR2.2**: System MUST validate all LLM responses for required JSON structure
- **NFR2.3**: System MUST handle malformed JSON responses with retry logic
- **NFR2.4**: System MUST log all workflow steps for debugging

### NFR3: Security
- **NFR3.1**: System MUST load API keys from environment variables
- **NFR3.2**: System MUST NOT commit API keys to version control
- **NFR3.3**: System MUST validate file paths to prevent directory traversal

### NFR4: Maintainability
- **NFR4.1**: Code MUST follow PEP 8 style guidelines
- **NFR4.2**: Code MUST include type hints for all functions
- **NFR4.3**: Code MUST include docstrings for all modules and functions
- **NFR4.4**: Prompts MUST be stored in separate files under `prompts/` directory

### NFR5: Usability
- **NFR5.1**: Streamlit UI MUST be intuitive and require minimal training
- **NFR5.2**: Error messages MUST be clear and actionable
- **NFR5.3**: Workflow status MUST be visible in UI at all times

## Technical Constraints

### TC1: Dependencies
- Python 3.11+
- LangGraph 1.0.2+
- FastAPI for API layer
- Streamlit for UI
- Google Generative AI SDK for Gemini
- OpenAI SDK for caption generation
- FFmpeg for video processing

### TC2: State Management
- LangGraph `MemorySaver` for checkpointing (development)
- Persistent checkpointer (e.g., `SqliteSaver`) recommended for production
- State MUST be serializable to JSON

### TC3: File System
- Input videos stored in `inputvid/` directory
- Rendered outputs stored in `renders/` directory
- Font files stored in `workflows/Jokestruc/arial/` directory

## Out of Scope

- Real-time video streaming
- Multi-language caption support
- Video editing beyond caption overlay
- Batch processing of multiple videos
- User authentication and authorization
- Video storage in cloud (local filesystem only)

## Success Criteria

1. System successfully generates meme videos from 90%+ of valid input videos
2. Human reviewers rate generated captions as "funny" or "very funny" in 70%+ of cases
3. End-to-end workflow completes within 5 minutes for typical 15-second clips
4. API uptime > 99% during business hours
5. Zero security incidents related to API key exposure
