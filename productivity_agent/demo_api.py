from __future__ import annotations

import os
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.events import Event
from google.genai import types

from productivity_agent.agent import root_agent


APP_NAME = os.getenv("ADK_APP_NAME", "productivity_agent")
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()
memory_service = InMemoryMemoryService()
runner = Runner(
    app_name=APP_NAME,
    agent=root_agent,
    session_service=session_service,
    artifact_service=artifact_service,
    memory_service=memory_service,
)


class DemoRunRequest(BaseModel):
    prompt: str = Field(min_length=1, description="User prompt to send to the productivity assistant.")
    user_id: str = Field(default="demo-user", description="Logical user id for the session.")
    session_id: str | None = Field(
        default=None,
        description="Optional session id. If omitted, a new demo session is created automatically.",
    )


class DemoRunResponse(BaseModel):
    app_name: str
    user_id: str
    session_id: str
    final_agent: str
    answer: str
    agents_involved: list[str]
    tool_calls: list[str]
    event_count: int


app = FastAPI(
    title="Multi-Agent Productivity Assistant Demo API",
    version="1.0.0",
    description="Clean demo-facing wrapper for the ADK multi-agent productivity assistant.",
)


def _extract_text(event: Event) -> str:
    if not event.content or not event.content.parts:
        return ""
    return "\n".join(
        part.text.strip()
        for part in event.content.parts
        if getattr(part, "text", None) and part.text.strip()
    ).strip()


def _unique_in_order(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _extract_tool_calls(events: list[Event]) -> list[str]:
    names: list[str] = []
    for event in events:
        for function_call in event.get_function_calls():
            name = getattr(function_call, "name", None)
            if name:
                names.append(name)
    return _unique_in_order(names)


def _extract_agents(events: list[Event]) -> list[str]:
    names = [event.author for event in events if event.author and event.author != "user"]
    return _unique_in_order(names)


def _extract_final_answer(events: list[Event]) -> tuple[str, str]:
    for event in reversed(events):
        text = _extract_text(event)
        if text and event.author == "WorkflowReporter":
            return text, event.author

    for event in reversed(events):
        text = _extract_text(event)
        if text and event.is_final_response():
            return text, event.author

    for event in reversed(events):
        text = _extract_text(event)
        if text:
            return text, event.author

    raise HTTPException(status_code=502, detail="Agent run finished without a final text response.")


def _translate_exception(exc: Exception) -> HTTPException:
    message = str(exc)
    upper_message = message.upper()

    if "RESOURCE_EXHAUSTED" in upper_message or "QUOTA EXCEEDED" in upper_message:
        return HTTPException(
            status_code=429,
            detail="Gemini quota exhausted. Wait briefly and retry a single request.",
        )

    if "API KEY EXPIRED" in upper_message or "API_KEY_INVALID" in upper_message:
        return HTTPException(
            status_code=401,
            detail="Gemini API key is invalid or expired. Rotate the key and redeploy.",
        )

    return HTTPException(status_code=500, detail=message or "Agent run failed.")


async def _ensure_session(user_id: str, session_id: str) -> None:
    existing = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )
    if existing is None:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
            state={},
        )


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "name": "Multi-Agent Productivity Assistant Demo API",
        "app_name": APP_NAME,
        "docs": "/docs",
        "health": "/health",
        "demo_run": "/demo/run",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/demo/run", response_model=DemoRunResponse)
async def demo_run(request: DemoRunRequest) -> DemoRunResponse:
    session_id = request.session_id or f"demo-{uuid4().hex[:10]}"
    await _ensure_session(user_id=request.user_id, session_id=session_id)

    new_message = types.Content(
        role="user",
        parts=[types.Part(text=request.prompt)],
    )

    events: list[Event] = []
    try:
        async for event in runner.run_async(
            user_id=request.user_id,
            session_id=session_id,
            new_message=new_message,
        ):
            events.append(event)
    except HTTPException:
        raise
    except Exception as exc:
        raise _translate_exception(exc) from exc

    answer, final_agent = _extract_final_answer(events)

    return DemoRunResponse(
        app_name=APP_NAME,
        user_id=request.user_id,
        session_id=session_id,
        final_agent=final_agent,
        answer=answer,
        agents_involved=_extract_agents(events),
        tool_calls=_extract_tool_calls(events),
        event_count=len(events),
    )
