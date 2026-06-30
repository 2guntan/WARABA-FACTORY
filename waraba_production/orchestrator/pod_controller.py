import os
import time
import httpx
import asyncio
import logging
from datetime import datetime

log = logging.getLogger(__name__)

RUNPOD_API_KEY = os.environ["RUNPOD_API_KEY"]
POD_ID = os.environ["RUNPOD_POD_ID"]
POD_ENDPOINT = os.environ["POD_ENDPOINT"]  # http://<pod-ip>:<port>
POLL_INTERVAL = 30  # seconds
IDLE_GRACE = 5 * 60  # 5 min after completion before stop
MAX_JOB_TIMEOUT = 3 * 60 * 60  # 3h hard timeout

RUNPOD_BASE = "https://rest.runpod.io/v1"

HEADERS = {
    "Authorization": f"Bearer {RUNPOD_API_KEY}",
    "Content-Type": "application/json",
}


async def pod_start():
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{RUNPOD_BASE}/pods/{POD_ID}/start", headers=HEADERS, timeout=30)
        r.raise_for_status()
        log.info("Pod start requested")
        return r.json()


async def pod_stop():
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{RUNPOD_BASE}/pods/{POD_ID}/stop", headers=HEADERS, timeout=30)
        r.raise_for_status()
        log.info("Pod stop requested")
        return r.json()


async def pod_status() -> str:
    """Returns: running | stopped | unknown"""
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{RUNPOD_BASE}/pods/{POD_ID}", headers=HEADERS, timeout=30)
        if r.status_code == 200:
            data = r.json()
            desired = data.get("desiredStatus", "").lower()
            runtime = data.get("runtime")
            if desired == "running" and runtime:
                return "running"
            elif desired == "exited" or not runtime:
                return "stopped"
    return "unknown"


async def wait_for_pod_ready(timeout: int = 300):
    """Poll until Pod HTTP endpoint responds."""
    deadline = time.time() + timeout
    async with httpx.AsyncClient() as client:
        while time.time() < deadline:
            try:
                r = await client.get(f"{POD_ENDPOINT}/health", timeout=5)
                if r.status_code == 200:
                    log.info("Pod ready")
                    return True
            except Exception:
                pass
            await asyncio.sleep(10)
    raise TimeoutError("Pod did not become ready in time")


async def submit_job_to_pod(job_id: str, character: dict, shots: dict) -> bool:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{POD_ENDPOINT}/generate",
            json={"job_id": job_id, "character": character, "shots": shots},
            timeout=30,
        )
        r.raise_for_status()
        return True


async def poll_job_until_done(job_id: str) -> tuple[str, str | None]:
    """Returns (status, result_url). status: completed | failed | timeout"""
    deadline = time.time() + MAX_JOB_TIMEOUT
    async with httpx.AsyncClient() as client:
        while time.time() < deadline:
            try:
                r = await client.get(f"{POD_ENDPOINT}/status/{job_id}", timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    status = data.get("status")
                    if status == "completed":
                        return "completed", data.get("result_url")
                    elif status == "failed":
                        return "failed", None
            except Exception as e:
                log.warning(f"Poll error: {e}")
            await asyncio.sleep(POLL_INTERVAL)
    return "timeout", None


async def run_generation_job(job_id: str, character: dict, shots: dict, on_update):
    """
    Full lifecycle: start pod → submit → poll → stop.
    on_update(job_id, **kwargs) called on status changes.
    """
    try:
        status = await pod_status()
        if status != "running":
            log.info("Starting pod...")
            await pod_start()

        on_update(job_id, status="processing")
        await wait_for_pod_ready(timeout=300)
        await submit_job_to_pod(job_id, character, shots)

        final_status, result_url = await poll_job_until_done(job_id)

        if final_status == "completed":
            on_update(job_id, status="completed", result_url=result_url)
        elif final_status == "timeout":
            on_update(job_id, status="failed", error="Job exceeded 3h timeout — pod force-stopped")
        else:
            on_update(job_id, status="failed", error="Generation failed on pod")

    except Exception as e:
        log.exception(f"Job {job_id} crashed")
        on_update(job_id, status="failed", error=str(e))
    finally:
        log.info(f"Waiting {IDLE_GRACE}s before stopping pod...")
        await asyncio.sleep(IDLE_GRACE)
        await pod_stop()
        log.info("Pod stopped.")
