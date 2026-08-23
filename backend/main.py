"""
TrendPulse — FastAPI Backend Server
Provides REST API + SSE streaming for the React dashboard.
"""
import asyncio
import json
from datetime import datetime
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sse_starlette.sse import EventSourceResponse

from backend.config import settings
from backend.models import PipelineResult, SwytchcodeLogEntry
from backend.trend_fetcher import fetch_all_trends
from backend.rag_engine import run_rag_pipeline
from backend.poster import post_to_linkedin
from backend.scheduler import start_scheduler, get_scheduler_status, set_pipeline_callback, shutdown_scheduler


# ── In-memory state ──────────────────────────────────────────────────────────
pipeline_history: List[dict] = []
swytchcode_audit_log: List[dict] = []
sse_clients: List[asyncio.Queue] = []


def _broadcast_sse(event: str, data: dict):
    message = json.dumps(data, default=str)
    for queue in sse_clients:
        try:
            queue.put_nowait({"event": event, "data": message})
        except asyncio.QueueFull:
            pass


async def _run_pipeline_async():
    """Execute the full TrendPulse pipeline with SSE broadcasting."""
    result = PipelineResult(
        started_at=datetime.utcnow().isoformat(),
        status="running",
    )

    try:
        # ── Step 1: Fetch Trends ─────────────────────────────────────────
        _broadcast_sse("pipeline_step", {"step": "fetch", "status": "running"})
        await asyncio.sleep(0.1)

        trends, fetch_logs = await asyncio.to_thread(fetch_all_trends)
        result.trends = trends
        result.swytchcode_log.extend(fetch_logs)

        for log in fetch_logs:
            swytchcode_audit_log.append(log.to_dict())

        _broadcast_sse("pipeline_step", {
            "step": "fetch",
            "status": "done",
            "data": {
                "count": len(trends),
                "sources": list(set(t.source for t in trends)),
                "by_type": {
                    "news": len([t for t in trends if t.source_type == "news"]),
                    "social_chatter": len([t for t in trends if t.source_type == "social_chatter"]),
                    "emerging_topic": len([t for t in trends if t.source_type == "emerging_topic"]),
                },
            },
        })

        if not trends:
            result.status = "error"
            result.completed_at = datetime.utcnow().isoformat()
            _broadcast_sse("pipeline_step", {"step": "error", "status": "done", "data": {"message": "No trends fetched"}})
            pipeline_history.append(result.to_dict())
            return result

        # ── Step 2 + 3: Ingest & Retrieve ────────────────────────────────
        _broadcast_sse("pipeline_step", {"step": "ingest", "status": "running"})
        await asyncio.sleep(0.1)

        vectors_indexed, passages, content = await asyncio.to_thread(
            run_rag_pipeline, trends
        )
        result.vectors_indexed = vectors_indexed

        _broadcast_sse("pipeline_step", {
            "step": "ingest",
            "status": "done",
            "data": {"vectors": vectors_indexed},
        })

        # ── Step 3: Vector Retrieve ──────────────────────────────────────
        _broadcast_sse("pipeline_step", {
            "step": "retrieve",
            "status": "done",
            "data": {
                "passages": [p.to_dict() for p in passages],
                "count": len(passages),
            },
        })

        # ── Step 4: Generate Content ─────────────────────────────────────
        _broadcast_sse("pipeline_step", {
            "step": "generate",
            "status": "done",
            "data": content.to_dict(),
        })

        result.generated_content = content

        # ── Step 5: Post to LinkedIn ───────────────────────────────────────
        _broadcast_sse("pipeline_step", {"step": "post", "status": "running"})
        await asyncio.sleep(0.1)

        post_result, post_log = await asyncio.to_thread(post_to_linkedin, content)
        result.post_result = post_result
        result.swytchcode_log.append(post_log)
        swytchcode_audit_log.append(post_log.to_dict())

        _broadcast_sse("pipeline_step", {
            "step": "post",
            "status": "done",
            "data": post_result.to_dict(),
        })

        result.status = "completed"
        result.completed_at = datetime.utcnow().isoformat()

        _broadcast_sse("pipeline_complete", result.to_dict())

    except Exception as e:
        result.status = "error"
        result.completed_at = datetime.utcnow().isoformat()
        _broadcast_sse("pipeline_step", {"step": "error", "status": "done", "data": {"message": str(e)}})

    pipeline_history.append(result.to_dict())
    return result


# ── App Lifecycle ────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    set_pipeline_callback(_run_pipeline_async)
    start_scheduler()
    yield
    shutdown_scheduler()


# ── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="TrendPulse API",
    description="RAG-based trend automation tool",
    version="1.0.0",
    lifespan=lifespan,
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── API Routes ───────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "credentials": settings.validate(),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/pipeline/run")
async def trigger_pipeline():
    result = await _run_pipeline_async()
    return result.to_dict() if result else {"status": "error"}


@app.get("/api/pipeline/stream")
async def pipeline_stream(request: Request):
    queue = asyncio.Queue(maxsize=100)
    sse_clients.append(queue)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=30)
                    yield msg
                except asyncio.TimeoutError:
                    yield {"event": "heartbeat", "data": json.dumps({"time": datetime.utcnow().isoformat()})}
        finally:
            if queue in sse_clients:
                sse_clients.remove(queue)

    return EventSourceResponse(event_generator())


@app.get("/api/trends")
async def get_trends():
    if pipeline_history:
        latest = pipeline_history[-1]
        return {"trends": latest.get("trends", []), "count": latest.get("trends_count", 0)}
    return {"trends": [], "count": 0}


@app.get("/api/posts")
async def get_posts():
    posts = []
    for run in pipeline_history:
        if run.get("post_result"):
            posts.append({
                "post_result": run["post_result"],
                "generated_content": run.get("generated_content"),
                "timestamp": run.get("completed_at"),
            })
    return {"posts": posts, "count": len(posts)}


@app.get("/api/swytchcode/log")
async def get_swytchcode_log():
    return {"log": swytchcode_audit_log, "count": len(swytchcode_audit_log)}


@app.get("/api/scheduler/status")
async def scheduler_status():
    return get_scheduler_status()


@app.get("/api/pipeline/history")
async def get_pipeline_history():
    return {"runs": pipeline_history, "count": len(pipeline_history)}


# ── Serve React Frontend (production build) ─────────────────────────────────
import os
frontend_build = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_build):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_build, "assets")), name="static")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_build, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_build, "index.html"))
