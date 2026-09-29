"""FastAPI Web Server and Real-time WebSocket Gateway for ALHSI."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from alhsi.agents.base import BaseAgent
from alhsi.agents.cheat_agent import CheatAgent
from alhsi.agents.auto_sim import AutoSimAgent
from alhsi.agents.llm_agent import LLMAgent
from alhsi.benchmarks import list_benchmarks
from alhsi.core.loop import AgentLoop

logger = logging.getLogger(__name__)

# Global active loop instance
_loop_instance: Optional[AgentLoop] = None
_active_agent_type: str = "sim"
_active_connections: List[WebSocket] = []
_main_event_loop: Optional[asyncio.AbstractEventLoop] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _main_event_loop
    _main_event_loop = asyncio.get_running_loop()
    yield


app = FastAPI(
    title="ALHSI - Agent Loop Harness Self-Improvement",
    description="Interactive demonstration of the Software 3.0 recursive self-improvement paradigm",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_agent_instance(agent_type: str, provider_model: Optional[str] = None) -> BaseAgent:
    if agent_type == "cheat":
        return CheatAgent()
    elif agent_type in ("gemini", "openai", "ollama"):
        return LLMAgent(provider=agent_type, model=provider_model)
    else:
        return AutoSimAgent()


def broadcast_state(state: Dict[str, Any]):
    """Broadcast state to all connected WebSockets from any thread."""
    global _main_event_loop
    if _main_event_loop is None or not _main_event_loop.is_running():
        try:
            _main_event_loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

    if not _active_connections or not _main_event_loop or not _main_event_loop.is_running():
        return

    payload = json.dumps({"type": "state_update", "data": state})
    for ws in list(_active_connections):
        try:
            asyncio.run_coroutine_threadsafe(ws.send_text(payload), _main_event_loop)
        except Exception:
            if ws in _active_connections:
                _active_connections.remove(ws)


def get_or_create_loop(preset_id: str = "nanogpt", agent_type: str = "sim") -> AgentLoop:
    global _loop_instance, _active_agent_type
    if _loop_instance is None or _loop_instance.preset_id != preset_id:
        agent = get_agent_instance(agent_type)
        _active_agent_type = agent_type
        _loop_instance = AgentLoop(
            preset_id=preset_id,
            agent=agent,
            on_state_change=broadcast_state,
        )
    return _loop_instance


# -----------------------------------------------------------------------------
# REST Endpoints
# -----------------------------------------------------------------------------

class LoopConfigPayload(BaseModel):
    preset_id: str = "nanogpt"
    agent_type: str = "sim"  # "sim", "gemini", "openai", "ollama", "cheat"
    model_name: Optional[str] = None


class StartPayload(BaseModel):
    max_trials: int = 15
    delay_sec: float = 1.0


@app.get("/api/presets")
def get_presets():
    return [p.to_dict() for p in list_benchmarks()]


@app.get("/api/state")
def get_state():
    loop = get_or_create_loop()
    state = loop.get_state()
    state["agent_type"] = _active_agent_type
    return state


@app.post("/api/step")
def trigger_step():
    loop = get_or_create_loop()
    if loop.running:
        raise HTTPException(status_code=400, detail="Loop is currently running continuously.")
    trial = loop.step()
    return trial.to_dict()


@app.post("/api/start")
def start_loop(payload: StartPayload):
    loop = get_or_create_loop()
    loop.start_continuous(max_trials=payload.max_trials, delay_sec=payload.delay_sec)
    state = loop.get_state()
    state["agent_type"] = _active_agent_type
    broadcast_state(state)
    return {"status": "started", "running": loop.running}


@app.post("/api/pause")
def pause_loop():
    loop = get_or_create_loop()
    loop.pause()
    state = loop.get_state()
    state["agent_type"] = _active_agent_type
    broadcast_state(state)
    return {"status": "paused"}


@app.post("/api/resume")
def resume_loop():
    loop = get_or_create_loop()
    loop.resume()
    state = loop.get_state()
    state["agent_type"] = _active_agent_type
    broadcast_state(state)
    return {"status": "resumed"}


@app.post("/api/stop")
def stop_loop():
    loop = get_or_create_loop()
    loop.stop()
    state = loop.get_state()
    state["agent_type"] = _active_agent_type
    broadcast_state(state)
    return {"status": "stopped"}


@app.post("/api/reset")
def reset_loop(payload: Optional[LoopConfigPayload] = None):
    global _loop_instance, _active_agent_type
    preset_id = payload.preset_id if payload else "nanogpt"
    agent_type = payload.agent_type if payload else "sim"
    agent = get_agent_instance(agent_type, payload.model_name if payload else None)
    _active_agent_type = agent_type

    if _loop_instance is not None and _loop_instance.running:
        _loop_instance.stop()

    if _loop_instance is None:
        _loop_instance = AgentLoop(
            preset_id=preset_id,
            agent=agent,
            on_state_change=broadcast_state,
        )
    else:
        _loop_instance.agent = agent
        _loop_instance.reset(new_preset_id=preset_id)

    state = _loop_instance.get_state()
    state["agent_type"] = _active_agent_type
    broadcast_state(state)
    return state


class CustomTrialPayload(BaseModel):
    code: str
    title: Optional[str] = "Manual Human Optimization"
    description: Optional[str] = "Human-authored modification to test against harness"
    category: Optional[str] = "manual_human"


class AttackTestPayload(BaseModel):
    attack_type: str = "os_injection"  # "os_injection", "fake_return", "file_tamper"


class SettingsPayload(BaseModel):
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    ollama_host: Optional[str] = None


@app.post("/api/custom-trial")
def trigger_custom_trial(payload: CustomTrialPayload):
    """Allows user to test their own code against the Harness (Software 1.0 vs 3.0)."""
    loop = get_or_create_loop()
    if loop.running:
        raise HTTPException(status_code=400, detail="Loop is currently running.")
    
    # We can use a custom agent that returns this exact code
    class HumanAgent(BaseAgent):
        def propose_change(self, current_code, history, config, trial_num):
            from alhsi.core.types import Hypothesis
            hyp = Hypothesis(
                title=payload.title or f"Human Trial #{trial_num}",
                category=payload.category or "manual_human",
                description=payload.description or "User-submitted code in browser editor",
                expected_impact="Manual exploration",
            )
            return hyp, payload.code

    prev_agent = loop.agent
    try:
        loop.agent = HumanAgent()
        trial = loop.step()
        return trial.to_dict()
    finally:
        loop.agent = prev_agent


@app.post("/api/cheat-test")
def trigger_cheat_test(payload: AttackTestPayload):
    """Trigger a specific adversarial attack to showcase Harness security defenses."""
    loop = get_or_create_loop()
    if loop.running:
        raise HTTPException(status_code=400, detail="Loop is currently running.")

    cheat_agent = CheatAgent()
    prev_agent = loop.agent
    try:
        loop.agent = cheat_agent
        trial = loop.step()
        return trial.to_dict()
    finally:
        loop.agent = prev_agent


@app.post("/api/settings")
def update_settings(payload: SettingsPayload):
    import os
    if payload.gemini_api_key:
        os.environ["GEMINI_API_KEY"] = payload.gemini_api_key
    if payload.openai_api_key:
        os.environ["OPENAI_API_KEY"] = payload.openai_api_key
    if payload.ollama_host:
        os.environ["OLLAMA_HOST"] = payload.ollama_host
    return {"status": "updated"}


@app.get("/api/export")
def export_history():
    loop = get_or_create_loop()
    state = loop.get_state()
    return JSONResponse(
        content=state,
        headers={"Content-Disposition": "attachment; filename=experiments.json"},
    )


@app.get("/api/export/csv")
def export_history_csv():
    import csv
    import io
    from fastapi.responses import Response
    loop = get_or_create_loop()
    state = loop.get_state()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Trial #", "Hypothesis Title", "Category", "Expected Impact",
        "Status", "Baseline Metric", "Trial Metric", "Delta",
        "Commit SHA", "Elapsed (s)", "Timestamp"
    ])
    for t in state.get("trials", []):
        writer.writerow([
            t.get("trial_num"),
            t.get("hypothesis", {}).get("title"),
            t.get("hypothesis", {}).get("category"),
            t.get("hypothesis", {}).get("expected_impact"),
            t.get("status"),
            t.get("baseline_metric"),
            t.get("trial_metric"),
            t.get("metric_delta"),
            t.get("commit_hash") or "",
            t.get("elapsed_sec"),
            t.get("timestamp"),
        ])
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=experiments.csv"},
    )


# -----------------------------------------------------------------------------
# WebSocket Endpoint for Real-time Streaming
# -----------------------------------------------------------------------------

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    _active_connections.append(websocket)
    try:
        loop = get_or_create_loop()
        state = loop.get_state()
        state["agent_type"] = _active_agent_type
        await websocket.send_text(json.dumps({"type": "state_update", "data": state}))
        while True:
            # Keep alive and receive any incoming UI commands
            msg = await websocket.receive_text()
            data = json.loads(msg)
            action = data.get("action")
            if action == "step":
                loop.step()
            elif action == "start":
                loop.start_continuous(max_trials=data.get("max_trials", 15), delay_sec=data.get("delay_sec", 1.0))
            elif action == "pause":
                loop.pause()
            elif action == "resume":
                loop.resume()
            elif action == "stop":
                loop.stop()
    except WebSocketDisconnect:
        if websocket in _active_connections:
            _active_connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in _active_connections:
            _active_connections.remove(websocket)


# -----------------------------------------------------------------------------
# Static UI Assets
# -----------------------------------------------------------------------------

static_dir = Path(__file__).parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
def serve_index():
    index_file = static_dir / "index.html"
    if not index_file.exists():
        return JSONResponse({"message": "ALHSI API is running. UI loading..."})
    return FileResponse(str(index_file))
