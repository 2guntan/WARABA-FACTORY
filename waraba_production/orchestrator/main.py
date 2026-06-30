import asyncio
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import os

from job_manager import init_db, create_job, update_job, get_job, list_jobs
from pod_controller import pod_status, pod_start, pod_stop, run_generation_job

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

API_KEY = os.environ["ORCHESTRATOR_API_KEY"]
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


def require_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="WARABA Orchestrator", lifespan=lifespan)


class JobRequest(BaseModel):
    character: dict
    shots: list
    episode_name: str = ""


def _on_update(job_id: str, **kwargs):
    update_job(job_id, **kwargs)


@app.post("/jobs", dependencies=[Depends(require_api_key)])
async def submit_job(req: JobRequest):
    job_id = create_job(req.character, {"shots": req.shots}, req.episode_name)
    asyncio.create_task(
        run_generation_job(job_id, req.character, {"shots": req.shots}, _on_update)
    )
    return {"job_id": job_id, "status": "queued"}


@app.get("/jobs", dependencies=[Depends(require_api_key)])
async def get_jobs(limit: int = 20):
    return list_jobs(limit)


@app.get("/jobs/{job_id}", dependencies=[Depends(require_api_key)])
async def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/pod/status", dependencies=[Depends(require_api_key)])
async def get_pod_status():
    return {"status": await pod_status()}


@app.post("/pod/start", dependencies=[Depends(require_api_key)])
async def start_pod():
    result = await pod_start()
    return {"result": result}


@app.post("/pod/stop", dependencies=[Depends(require_api_key)])
async def stop_pod():
    result = await pod_stop()
    return {"result": result}


@app.get("/health")
async def health():
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
