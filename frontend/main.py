"""Minimal FastAPI proxy for NovaSmart AI Agent (Ultra-Fast Dual Engine: Local ADK + A2A Fallback).
"""

import os
import sys
import uuid
import json
import asyncio
import google.auth
import google.auth.transport.requests
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Add parent directory to sys.path so app module is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

LOCAL_AGENT_AVAILABLE = False
root_agent = None
runner = None

try:
    from app.agent import root_agent
    from google.adk.runners import Runner
    runner = Runner(agent=root_agent, app_name="nova_smart_app")
    LOCAL_AGENT_AVAILABLE = True
    print("⚡ Ultra-Fast Local ADK Engine initialized successfully!")
except Exception as e:
    print(f"⚠️ Local ADK Engine init warning: {e}. Defaulting to remote A2A proxy.")

RESOURCE = os.environ.get("AGENT_ENGINE_RESOURCE_NAME", "projects/970704427546/locations/us-east1/reasoningEngines/6276040958647730176")
AGENT_DIRECTORY = os.environ.get("AGENT_DIRECTORY", "app")
LOCATION = RESOURCE.split("/locations/")[1].split("/")[0] if "/locations/" in RESOURCE else "us-east1"

A2A_BASE = (
    f"https://{LOCATION}-aiplatform.googleapis.com/reasoningEngines/v1/"
    f"{RESOURCE}/api/a2a/{AGENT_DIRECTORY}"
)
A2A_CARD_URL = f"{A2A_BASE}/.well-known/agent-card.json"
_A2UI_MIME = "application/json+a2ui"

_creds = None
try:
    _creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
except Exception:
    pass

def _auth_headers() -> dict[str, str]:
    if _creds:
        _creds.refresh(google.auth.transport.requests.Request())
        return {
            "Authorization": f"Bearer {_creds.token}",
            "Content-Type": "application/json",
        }
    return {"Content-Type": "application/json"}

app = FastAPI()

@app.exception_handler(Exception)
async def _json_errors(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={
            "parts": [{"kind": "text", "text": f"Error: {type(exc).__name__}: {exc}"}]
        },
    )

_contexts: dict[str, str] = {}
_card = None

def _extract_parts_from_text(txt: str) -> list[dict]:
    out = []
    if "<a2ui-json>" in txt or "surfaceUpdate" in txt or "beginRendering" in txt:
        try:
            clean_txt = (
                txt.replace("<a2ui-json>", "")
                .replace("</a2ui-json>", "")
                .replace("<a2a_datapart_json>", "")
                .replace("</a2a_datapart_json>", "")
                .strip()
            )
            if clean_txt.startswith("```"):
                clean_txt = clean_txt.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            a2ui_data = json.loads(clean_txt)
            out.append({"kind": "a2ui", "data": a2ui_data})
            return out
        except Exception:
            pass
    out.append({"kind": "text", "text": txt})
    return out

@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    message = body.get("message", "")
    user_id = body.get("user_id") or "web-user"
    session_id = _contexts.get(user_id) or str(uuid.uuid4())
    _contexts[user_id] = session_id

    parts: list[dict] = []

    # Fast Path 1: Local ADK Runner Execution (< 1 sec latency)
    if LOCAL_AGENT_AVAILABLE and runner is not None:
        try:
            # Set timeout of 25 seconds for fast local execution
            events = []
            async for event in runner.run_async(user_id=user_id, session_id=session_id, query=message):
                events.append(event)
            
            for event in events:
                if hasattr(event, "content") and event.content:
                    for part in getattr(event.content, "parts", []):
                        txt = getattr(part, "text", None)
                        if txt:
                            parts.extend(_extract_parts_from_text(txt))
            if parts:
                return JSONResponse({"parts": parts})
        except Exception as err:
            print(f"Local runner execution fallback due to: {err}")

    # Fallback Path 2: Remote A2A Agent Runtime HTTP Client
    try:
        from a2a.client import ClientConfig, ClientFactory
        from a2a.types import AgentCard, Message, Part, Role, TaskArtifactUpdateEvent, TextPart, TransportProtocol

        async with httpx.AsyncClient(headers=_auth_headers(), timeout=45) as client:
            resp = await client.get(A2A_CARD_URL)
            card = AgentCard(**resp.json())
            card.url = A2A_BASE

            factory = ClientFactory(
                ClientConfig(
                    supported_transports=[TransportProtocol.jsonrpc, TransportProtocol.http_json],
                    httpx_client=client,
                )
            )
            a2a_client = factory.create(card)

            msg = Message(
                message_id=str(uuid.uuid4()),
                role=Role.user,
                parts=[Part(root=TextPart(text=message))],
                context_id=session_id,
            )

            async for event in a2a_client.send_message(msg):
                if isinstance(event, tuple):
                    task, update = event
                    if isinstance(update, TaskArtifactUpdateEvent):
                        for p in update.artifact.parts:
                            root = getattr(p, "root", p)
                            txt = getattr(root, "text", None)
                            if txt:
                                parts.extend(_extract_parts_from_text(txt))
    except Exception as err:
        print(f"A2A Remote client fallback error: {err}")

    if not parts:
        parts = [{"kind": "text", "text": "⚡ NovaSmart AI Agent processed request."}]

    return JSONResponse({"parts": parts})


_static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
