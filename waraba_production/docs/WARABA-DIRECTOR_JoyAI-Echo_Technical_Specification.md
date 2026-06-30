# WARABA-DIRECTOR + JoyAI-Echo Technical Specification

**Version:** 1.0  
**Date:** June 28, 2026  
**Author:** Grok (based on user requirements)  
**Status:** Draft for implementation with Grok Build tools

---

## 1. Executive Summary & Goal

### Project Goal
Build a **professional, controllable AI video production pipeline** for generating high-quality, long-form animated episodes (fable-style stories) with strong narrative coherence, character consistency, and cinematic directing.

The system combines:
- Human creative direction and pre-production structure (**WARABA-DIRECTOR**)
- AI video generation engine (**JoyAI-Echo**)
- Explicit character control layer

### Core Objective
Enable the user to maintain **high-level creative and character control** while leveraging JoyAI-Echo for efficient video generation, without being limited by its text-only input constraints.

---

## 2. Project Context

### 2.1 WARABA-DIRECTOR (Existing Work)
A structured pre-production and directing pipeline located in Google Drive under `WARABA-DIRECTOR/04_EPISODE_01_MVP`.

Key artifacts include:
- Story adaptation
- Visual development
- Audio direction
- **Storyboard Package** (detailed shot list with timing, camera, actions, objectives)
- Validation pipeline
- Character consistency rules

### 2.2 JoyAI-Echo (Generation Engine)
- Open-source long-form text-to-audio-video model (JD Open Source)
- Strengths: Multi-shot coherence, native audio, cross-modal memory for consistency, structured prompt support
- Limitations: Text-only input (no native image references or IP-Adapter)
- Runs best on high-VRAM GPUs (H100 / A100 / L40S recommended)

### 2.3 Key Constraint
JoyAI-Echo does **not** accept image inputs. Character consistency must be achieved through:
- Rich text descriptions
- Internal memory bank
- Strong prompt engineering

---

## 3. High-Level Architecture

```
Character Image Generation (Google Flow / Imagen)
          ↓
Character Definition Tool → Structured Character JSON
          ↓
WARABA-DIRECTOR Documents (Storyboard + Character Log)
          ↓
Prompt Assembly Layer (Character JSON + Shot List)
          ↓
RunPod Orchestration Layer (FastAPI)
          ↓
JoyAI-Echo Inference (H100 Pod)
          ↓
Generated Video + Audio
```

**Core Principle**: Separate **creative control** (human + structured tools) from **generation** (JoyAI-Echo).

---

## 4. Core Components

### 4.1 Character Definition System (New)
- **Purpose**: Create reusable, versioned, rich character profiles.
- **Input**: Character reference images from Google Flow.
- **Output**: Structured `CharacterProfile.json`.
- **Key Features**:
  - Versioning (`leuk_v1.json`, `leuk_v2.json`)
  - Rich appearance + voice description optimized for JoyAI-Echo
  - Personality and behavioral notes

### 4.2 Directing System (WARABA-DIRECTOR)
- Existing pre-production pipeline.
- Primary artifact: **Episode 01 Storyboard Package** (shot list).
- Provides camera language, timing, dramatic objectives, and continuity rules.

### 4.3 Generation Engine (JoyAI-Echo)
- Deployed on **RunPod** (H100 recommended).
- Uses structured JSON prompts.
- Leverages internal memory bank for cross-shot consistency.

### 4.4 Orchestration Layer (RunPod)
- Custom FastAPI application running on RunPod Pod.
- Responsibilities:
  - Accept Character JSON + Storyboard/Shot data
  - Assemble final JoyAI-Echo prompts
  - Manage Pod lifecycle (start/stop for cost control)
  - Handle job queuing and result delivery
  - Expose API for local stack / agents

---

## 5. Data Models

### 5.1 CharacterProfile JSON Schema (Recommended)

```json
{
  "character_id": "leuk_young_hare_v1",
  "name": "Leuk",
  "species": "Young hare",
  "age_appearance": "Young adult",
  "physical_description": "Slender and agile build, light brown fur with white underbelly, sharp intelligent eyes, long expressive ears, quick and precise movements",
  "clothing": "Simple light-colored tunic, no footwear",
  "distinctive_features": "Expressive eyebrows, alert posture, slight mischievous smile",
  "voice": {
    "timbre": "Clear, young male voice with slight mischievous quality",
    "tone": "Confident and articulate"
  },
  "personality_traits": ["clever", "observant", "slightly vain"],
  "reference_version": "v1",
  "locked_date": "2026-06-28"
}
```

### 5.2 Shot Prompt Structure
Each shot in the Storyboard Package should be converted into a structured string containing:
1. Roles & Subjects (inject CharacterProfile)
2. Action & Dialogue
3. Style
4. Camera Movement
5. Background
6. Sound Effects & Audio

---

## 6. Prompt Strategy

### 6.1 Character Injection
- The Character JSON is converted into a rich paragraph.
- This paragraph is **injected** into every relevant shot prompt under "Roles & Subjects".
- The memory bank in JoyAI-Echo reinforces consistency.

### 6.2 Shot Grouping Strategy
- Not every shot needs to be generated individually.
- Group 3–6 shots into logical sequences when possible for better coherence.
- Keep critical dramatic moments (e.g., Leuk’s fall) as separate generations when needed.

---

## 7. RunPod Deployment Architecture

### 7.1 Pod Configuration
- **GPU**: H100 80GB (preferred) or L40S 48GB
- **Storage**: Network Volume (150–200 GB) for model weights + outputs
- **Environment**: Custom Docker image with:
  - JoyAI-Echo inference code
  - PyTorch 2.8 + CUDA 12.8
  - FastAPI server
  - Character prompt assembler

### 7.2 Cost Control
- Pod is **stopped** when not in use.
- Only Network Volume storage incurs minimal ongoing cost.
- Generation jobs trigger Pod start → process → stop.

### 7.3 API Endpoints (Proposed)
- `POST /generate` — Submit Character JSON + Shot data
- `GET /status/{job_id}`
- `GET /result/{job_id}`
- `POST /characters` — Register new CharacterProfile

---

## 8. Integration Flow (End-to-End)

1. Create/Lock character images in Google Flow.
2. Run Character Definition Tool → Generate `CharacterProfile.json`.
3. Use WARABA-DIRECTOR Storyboard Package to define shots.
4. Call RunPod API with:
   - `character_profile` (JSON)
   - `shot_list` (from Storyboard)
5. Orchestration layer assembles prompts and sends to JoyAI-Echo.
6. JoyAI-Echo generates video sequence.
7. Results returned to user (URL or file).

---

## 9. Phased Implementation Plan

### Phase 1: Foundation (Week 1)
- Define Character JSON schema
- Create Character Definition Tool (basic version)
- Set up RunPod Pod + Network Volume with JoyAI-Echo
- Build basic FastAPI wrapper

### Phase 2: Core Integration (Week 2)
- Implement prompt assembly logic (Character + Shot)
- Test single-shot and multi-shot generation
- Integrate with existing Storyboard Package

### Phase 3: Orchestration & Polish (Week 3)
- Add job management and status tracking
- Implement Pod start/stop automation
- Add result delivery (storage + URLs)
- Create local client / agent tool interface

### Phase 4: Production Readiness
- Versioning system for characters and episodes
- Validation pipeline integration
- Cost monitoring and optimization
- Documentation and agent tool wrapping

---

## 10. Success Criteria

- Character consistency maintained across 5+ minute episodes
- Director retains creative control through structured documents
- Generation cost remains manageable (< $30–40 per episode at current volume)
- System is usable from local stack and AI agents
- Clear separation between creative direction and technical generation

---

## 11. Risks & Mitigations

| Risk                              | Impact | Mitigation |
|-----------------------------------|--------|----------|
| JoyAI-Echo character drift        | High   | Strong text descriptions + memory bank tuning + versioned Character JSONs |
| High generation cost              | Medium | Pod stop/start strategy + shot grouping |
| Prompt engineering complexity     | Medium | Create reusable prompt templates and assembler |
| Model version changes             | Low    | Pin JoyAI-Echo version and document inference config |

---

## 12. Next Steps & Recommendations

1. Finalize **Character JSON schema** (based on proposed structure above).
2. Build the **Character Definition Tool** as a separate Google Flow workflow.
3. Set up the **RunPod environment** (Docker + FastAPI skeleton).
4. Create prompt assembly logic that merges Character JSON + Storyboard shots.
5. Test with Episode 01 shots from the existing Storyboard Package.

---

**Document Status**: Ready for use with Grok Build CLI / agent development tools.

This specification provides a clear, actionable blueprint for building the full system while respecting JoyAI-Echo’s current capabilities and maximizing creative control through structured inputs.