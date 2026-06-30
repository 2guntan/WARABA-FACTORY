import os
import json
import httpx
import gradio as gr

API_BASE = os.environ.get("ORCHESTRATOR_URL", "http://localhost:8000")
API_KEY = os.environ["ORCHESTRATOR_API_KEY"]
UI_USER = os.environ.get("UI_USERNAME", "waraba")
UI_PASS = os.environ["UI_PASSWORD"]

HEADERS = {"X-API-Key": API_KEY}


def api(method: str, path: str, **kwargs):
    r = httpx.request(method, f"{API_BASE}{path}", headers=HEADERS, timeout=15, **kwargs)
    r.raise_for_status()
    return r.json()


def get_pod_status():
    try:
        data = api("GET", "/pod/status")
        status = data["status"]
        color = "🟢" if status == "running" else "🔴"
        return f"{color} Pod: **{status}**"
    except Exception as e:
        return f"❓ Pod status error: {e}"


def start_pod():
    try:
        api("POST", "/pod/start")
        return "✅ Pod start requested"
    except Exception as e:
        return f"❌ Error: {e}"


def stop_pod():
    try:
        api("POST", "/pod/stop")
        return "✅ Pod stop requested"
    except Exception as e:
        return f"❌ Error: {e}"


def list_jobs():
    try:
        jobs = api("GET", "/jobs")
        if not jobs:
            return "No jobs yet."
        lines = []
        for j in jobs:
            icon = {"queued": "⏳", "processing": "⚙️", "completed": "✅", "failed": "❌"}.get(j["status"], "❓")
            url = f" → [{j['result_url']}]({j['result_url']})" if j.get("result_url") else ""
            lines.append(f"{icon} `{j['id']}` | {j['episode_name'] or 'unnamed'} | {j['status']} | {j['created_at'][:16]}{url}")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Error: {e}"


def submit_job(character_json_str: str, shots_json_str: str, episode_name: str):
    try:
        character = json.loads(character_json_str)
        shots = json.loads(shots_json_str)
        result = api("POST", "/jobs", json={"character": character, "shots": shots, "episode_name": episode_name})
        return f"✅ Job submitted: `{result['job_id']}`"
    except json.JSONDecodeError as e:
        return f"❌ JSON invalid: {e}"
    except Exception as e:
        return f"❌ Error: {e}"


def check_job(job_id: str):
    try:
        job = api("GET", f"/jobs/{job_id.strip()}")
        icon = {"queued": "⏳", "processing": "⚙️", "completed": "✅", "failed": "❌"}.get(job["status"], "❓")
        result = f"\n**Result:** {job['result_url']}" if job.get("result_url") else ""
        error = f"\n**Error:** {job['error']}" if job.get("error") else ""
        return f"{icon} **{job['status']}**{result}{error}"
    except Exception as e:
        return f"❌ Error: {e}"


with gr.Blocks(title="WARABA Director", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎬 WARABA Director — Generation Control")

    with gr.Row():
        with gr.Column(scale=2):
            pod_status_box = gr.Markdown()
        with gr.Column(scale=1):
            btn_refresh_status = gr.Button("Refresh Status")
        with gr.Column(scale=1):
            btn_start = gr.Button("▶ Start Pod", variant="primary")
        with gr.Column(scale=1):
            btn_stop = gr.Button("⏹ Stop Pod", variant="stop")

    pod_action_msg = gr.Markdown()

    gr.Markdown("---")
    gr.Markdown("## Submit Generation Job")

    with gr.Row():
        with gr.Column():
            character_input = gr.Textbox(label="Character JSON", lines=8, placeholder='{"name": "Waraba", ...}')
            shots_input = gr.Textbox(label="Shots JSON (array)", lines=6, placeholder='[{"shot_id": 1, ...}]')
            episode_name_input = gr.Textbox(label="Episode Name (optional)")
            btn_submit = gr.Button("🚀 Submit Job", variant="primary")
            submit_result = gr.Markdown()

    gr.Markdown("---")
    gr.Markdown("## Job History")
    jobs_output = gr.Markdown()
    btn_refresh_jobs = gr.Button("Refresh Jobs")

    gr.Markdown("---")
    gr.Markdown("## Check Specific Job")
    job_id_input = gr.Textbox(label="Job ID")
    btn_check_job = gr.Button("Check")
    job_detail = gr.Markdown()

    # Events
    btn_refresh_status.click(get_pod_status, outputs=pod_status_box)
    btn_start.click(start_pod, outputs=pod_action_msg)
    btn_stop.click(stop_pod, outputs=pod_action_msg)
    btn_submit.click(submit_job, inputs=[character_input, shots_input, episode_name_input], outputs=submit_result)
    btn_refresh_jobs.click(list_jobs, outputs=jobs_output)
    btn_check_job.click(check_job, inputs=job_id_input, outputs=job_detail)

    demo.load(get_pod_status, outputs=pod_status_box)
    demo.load(list_jobs, outputs=jobs_output)


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("UI_PORT", 7860)),
        auth=(UI_USER, UI_PASS),
        share=False,
    )
