# PRD: RunPod Orchestration + Simple Web Control Interface

**Version:** 1.0  
**Date:** June 30, 2026  
**Phase:** RunPod Setup & Cost-Controlled Generation  
**Status:** Ready for implementation

---

## 1. Overview & Goal

### Objective
Build a **cost-efficient, controllable RunPod-based video generation system** for JoyAI-Echo that:

- Allows triggering video generation from the WARABA-DIRECTOR pipeline.
- Automatically **starts and stops** the RunPod Pod to minimize costs.
- Provides a **simple web interface** to control the entire generation process.
- Integrates Character JSON + Storyboard data cleanly.

### Why This Phase Matters
JoyAI-Echo generation is expensive if the Pod stays running 24/7. The core value of this phase is **intelligent resource management** + **easy human control** through a lightweight web UI.

---

## 2. User Personas & Needs

| Persona              | Needs                                                                 | Pain Points Today                  |
|----------------------|-----------------------------------------------------------------------|------------------------------------|
| **Director / Creator** | Trigger generation, monitor progress, stop Pod easily                | Manual RunPod management is painful |
| **Technical User**   | Control jobs, see costs, debug prompts                               | No visibility into running jobs    |
| **Future Agent**     | Programmatic control via API                                         | No clean API yet                   |

---

## 3. Functional Requirements

### 3.1 Core Features (MVP)

| ID | Feature | Description | Priority |
|----|---------|-------------|----------|
| F1 | **Pod Lifecycle Management** | Automatically start Pod when a generation job is submitted, stop it after completion or timeout | P0 |
| F2 | **Job Submission** | Accept Character JSON + Shot list (from WARABA-DIRECTOR) and create a generation job | P0 |
| F3 | **Simple Web Dashboard** | Web interface to: submit jobs, see status, start/stop Pod manually, view recent generations | P0 |
| F4 | **Job Status & Results** | Real-time status (Queued / Processing / Completed / Failed) + result video URL | P0 |
| F5 | **Character Management** | Upload / select CharacterProfile JSON from the web interface | P1 |
| F6 | **Cost Visibility** | Basic display of estimated cost per generation (GPU hours) | P1 |

### 3.2 Non-Functional Requirements

- **Cost Control**: Pod must stop automatically after job completion (or after configurable idle timeout).
- **Reliability**: Jobs should not be lost if Pod is stopped.
- **Simplicity**: Web interface should be minimal and usable in < 5 minutes.
- **Security**: Basic authentication (at minimum API key or simple password for MVP).

---

## 4. Technical Architecture

### Recommended Architecture for This Phase

```
Web Interface (Simple HTML + JS or Streamlit/Gradio)
          ↓
FastAPI Backend (Running on RunPod or separate cheap instance)
          ↓
Job Queue (in-memory or Redis for MVP)
          ↓
Pod Controller (RunPod API calls)
          ↓
JoyAI-Echo Pod (H100) ← Started only when needed
```

**Two possible hosting options for the FastAPI:**

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **FastAPI on RunPod Pod** | Simple, everything in one place | Pod must stay running (small cost) | Good for MVP |
| **FastAPI on cheap VPS / Railway / Render** | True zero GPU cost when idle | Slightly more complex | Better long-term |

**Recommendation for current phase**: Start with **FastAPI running on the JoyAI-Echo Pod** itself (simpler). Later move the orchestrator to a cheap always-on instance.

---

## 5. API Design (Core Endpoints)

| Method | Endpoint                    | Description                              | Auth |
|--------|-----------------------------|------------------------------------------|------|
| POST   | `/jobs`                     | Submit new generation job                | Yes  |
| GET    | `/jobs/{job_id}`            | Get job status and result                | Yes  |
| GET    | `/jobs`                     | List recent jobs                         | Yes  |
| POST   | `/pod/start`                | Manually start the JoyAI-Echo Pod        | Yes  |
| POST   | `/pod/stop`                 | Manually stop the JoyAI-Echo Pod         | Yes  |
| GET    | `/pod/status`               | Check if Pod is running                  | Yes  |
| POST   | `/characters`               | Upload new CharacterProfile JSON         | Yes  |
| GET    | `/characters`               | List available characters                | Yes  |

---

## 6. Simple Web Interface – Proposed Screens (MVP)

### Screen 1: Dashboard (Main Page)
- Big button: **"Generate New Episode"**
- Current Pod Status: `Running` / `Stopped` + button to toggle
- List of recent jobs with status and "View Result" links
- Estimated cost of last generation

### Screen 2: New Generation Form
- Dropdown to select **Character** (from uploaded JSONs)
- Upload or select **Storyboard / Shots** file (or paste JSON)
- Optional: Episode name
- Button: **Submit Generation Job**

### Screen 3: Job Detail
- Job ID + Status (with live refresh)
- Input Character + Shots summary
- Progress / logs (if available)
- Result video player + download link (when completed)

**Tech suggestion for Web UI (MVP):**
- Use **Gradio** or **Streamlit** → fastest to build
- Or simple **FastAPI + Jinja2** HTML templates

---

## 7. Pod Auto-Stop Logic (Critical)

The system must implement the following behavior:

1. When a job is submitted:
   - If Pod is stopped → automatically start it via RunPod API
   - Queue the job

2. After generation finishes:
   - Wait X minutes (configurable, e.g. 5–10 min)
   - If no new job arrived → automatically stop the Pod

3. Manual override buttons in the web UI (`Start Pod` / `Stop Pod now`)

This is the most important cost-saving mechanism.

---

## 8. Ideas & Recommendations

### Idea 1: Minimal but Powerful Web UI (Recommended for now)
Use **Gradio** for the web interface. It’s extremely fast to build and integrates well with FastAPI.

### Idea 2: Job Queue + Worker Pattern
Even in MVP, separate job submission from actual generation. This makes auto start/stop much cleaner.

### Idea 3: Cost Dashboard (Nice to have)
Show simple metrics:
- GPU hours used this month
- Estimated cost of last 10 generations
- Current running cost per hour

### Idea 4: Future-Proofing
Design the FastAPI so it can later be moved to a cheap always-on server (Railway, Render, or a small VPS) while the heavy JoyAI-Echo Pod starts/stops on demand.

### Idea 5: Authentication (MVP)
Start with a simple **API Key** in the header + basic password protection on the web UI. Add proper auth later.

---

## 9. Success Metrics (This Phase)

- User can submit a generation job from the web interface in under 2 minutes.
- Pod automatically stops after generation (no manual intervention needed 90% of the time).
- Clear visibility of job status and results.
- Generation cost per episode stays predictable and low.

---

## 10. Risks & Mitigations

| Risk                              | Mitigation |
|-----------------------------------|----------|
| Pod fails to start automatically  | Add manual "Start Pod" button + clear error messages |
| Job is lost when Pod stops        | Store jobs in persistent storage (even simple JSON file for MVP) |
| User forgets to stop Pod          | Implement automatic idle timeout |
| Complex debugging                 | Add basic logging + job history in the web UI |

---

## 11. Recommended Next Steps

1. **Implement the FastAPI backend** with Pod start/stop logic (use the skeleton I provided).
2. **Add auto-stop mechanism** (most important feature).
3. **Build a simple Gradio or Streamlit web interface** on top of the API.
4. **Test end-to-end** with one of your Episode 01 shots + a Character JSON.
5. **Iterate** based on real usage.

---

**This PRD is focused and actionable** for the current RunPod setup phase while keeping the door open for future improvements (agents, more advanced UI, multi-Pod support, etc.).

Would you like me to also generate:
- A more detailed **API specification** (OpenAPI style)?
- A **Gradio UI code skeleton**?
- A **step-by-step implementation checklist** for setting this up on RunPod today?