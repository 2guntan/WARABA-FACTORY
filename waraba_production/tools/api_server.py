#!/usr/bin/env python3
"""
RunPod FastAPI server for WARABA JoyAI-Echo Pod.
Exposes /health, /generate, /status/{job_id} for the VPS orchestrator.
"""

import os
import asyncio
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi import FastAPI
from pydantic import BaseModel
import json

app = FastAPI(title="WARABA JoyAI-Echo Pod API")

jobs: Dict[str, Dict[str, Any]] = {}

JOYAI_DIR = Path(os.environ.get("JOYAI_DIR", "/workspace/JoyAI-Echo"))
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "/workspace/outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ── Models ──────────────────────────────────────────────────────────────────

class GenerationRequest(BaseModel):
    job_id: Optional[str] = None  # provided by orchestrator
    character: Dict[str, Any]
    shots: Any  # list or dict with shots key
    episode_name: Optional[str] = ""


# ── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/generate")
async def generate(request: GenerationRequest):
    job_id = request.job_id or str(uuid.uuid4())[:8]
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
        "result_url": None,
        "error": None,
    }
    asyncio.create_task(_run_inference(job_id, request))
    return {"job_id": job_id, "status": "queued"}


@app.get("/status/{job_id}")
async def status(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}
    return jobs[job_id]


# ── Inference ────────────────────────────────────────────────────────────────

async def _run_inference(job_id: str, request: GenerationRequest):
    jobs[job_id]["status"] = "processing"
    try:
        # Build prompt from character + shots
        prompt = _build_prompt(request.character, request.shots)
        prompt_file = OUTPUT_DIR / f"{job_id}_prompt.txt"
        prompt_file.write_text(prompt)

        output_path = OUTPUT_DIR / f"{job_id}.mp4"

        # Call JoyAI-Echo inference
        cmd = [
            "python", str(JOYAI_DIR / "inference.py"),
            "--prompt", str(prompt_file),
            "--output", str(output_path),
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(JOYAI_DIR),
        )
        stdout, _ = await proc.communicate()

        if proc.returncode == 0 and output_path.exists():
            jobs[job_id]["status"] = "completed"
            jobs[job_id]["result_url"] = str(output_path)
        else:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = stdout.decode()[-1000:] if stdout else "Unknown error"

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
    finally:
        jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()


def _build_prompt(character: dict, shots: Any) -> str:
    name = character.get("name", "character")
    description = character.get("physical_description", "")
    personality = character.get("personality", "")

    shots_list = shots if isinstance(shots, list) else shots.get("shots", [])
    shots_text = "\n".join(
        f"Shot {s.get('shot_id', i+1)}: {s.get('description', '')}"
        for i, s in enumerate(shots_list)
    )

    return f"""Character: {name}
Description: {description}
Personality: {personality}

Shots:
{shots_text}"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
