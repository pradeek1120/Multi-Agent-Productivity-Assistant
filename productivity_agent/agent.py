from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
    StreamableHTTPServerParams,
)
from mcp import StdioServerParameters


BASE_DIR = Path(__file__).resolve().parent.parent
TOOLS_FILE = BASE_DIR / "toolbox" / "tools.yaml"
load_dotenv(BASE_DIR / ".env")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
TOOLBOX_URL = os.getenv("TOOLBOX_URL", "").strip()


def _toolbox_args() -> list[str]:
    command = os.getenv("TOOLBOX_COMMAND", "toolbox")
    if command == "npx":
        return ["-y", "@toolbox-sdk/server", "--stdio", "--tools-file", str(TOOLS_FILE)]
    return ["--stdio", "--tools-file", str(TOOLS_FILE)]


def _toolbox_connection() -> StdioConnectionParams | StreamableHTTPServerParams:
    if TOOLBOX_URL:
        headers = {}
        toolbox_bearer = os.getenv("TOOLBOX_BEARER_TOKEN", "").strip()
        if toolbox_bearer:
            headers["Authorization"] = f"Bearer {toolbox_bearer}"
        return StreamableHTTPServerParams(
            url=TOOLBOX_URL,
            headers=headers or None,
        )

    return StdioConnectionParams(
        server_params=StdioServerParameters(
            command=os.getenv("TOOLBOX_COMMAND", "toolbox"),
            args=_toolbox_args(),
        )
    )


read_toolset = McpToolset(
    connection_params=_toolbox_connection(),
    tool_filter=[
        "workflow_list_recent_runs",
        "task_manager_list_pending_tasks",
        "notes_list_recent_notes",
        "calendar_list_upcoming_events",
    ],
)

write_toolset = McpToolset(
    connection_params=_toolbox_connection(),
    tool_filter=[
        "workflow_store_run",
        "workflow_mark_completed",
        "task_manager_create_task",
        "notes_create_note",
        "calendar_create_event",
    ],
)

report_toolset = McpToolset(
    connection_params=_toolbox_connection(),
    tool_filter=[
        "workflow_finalize_latest_run",
    ],
)


context_retriever = LlmAgent(
    name="ContextRetriever",
    model=GEMINI_MODEL,
    description="Retrieves recent task, note, calendar, and workflow context from AlloyDB via MCP.",
    instruction="""
You are the retrieval specialist for a productivity assistant.

Before any planning begins, inspect existing user context using only the available read tools.

Requirements:
- Call the read tools to inspect recent workflows, pending tasks, recent notes, and upcoming calendar events.
- Do not create or modify anything.
- Produce 4 to 6 concise bullets describing what context is relevant for the new request.
- If the database is empty, say that no prior context was found.
""",
    tools=[read_toolset],
    output_key="retrieved_context",
)

workflow_planner = LlmAgent(
    name="WorkflowPlanner",
    model=GEMINI_MODEL,
    description="Turns the user request into a structured multi-step plan.",
    instruction="""
You are the planning specialist for a multi-agent productivity assistant.

Use the user's request together with this existing context:
{retrieved_context}

Create a workflow plan for the execution agent.

Output only valid JSON with this shape:
{
  "title": "short workflow title",
  "objective": "one-sentence goal",
  "workflow_note": "brief note that captures constraints and important context",
  "tasks": [
    {"title": "task title", "priority": "high|medium|low", "status": "pending", "sequence": 1, "due_at": "ISO-8601 timestamp or null"}
  ],
  "calendar_event": {
    "title": "event title",
    "start_at": "ISO-8601 timestamp",
    "end_at": "ISO-8601 timestamp",
    "description": "why this block exists"
  }
}

Rules:
- Create 3 to 6 tasks.
- Use null for any due_at value you do not know.
- Include calendar_event only when the user clearly asked for scheduling or gave a deadline/time.
- Keep task titles practical and execution-oriented.
""",
    output_key="execution_plan",
)

workflow_executor = LlmAgent(
    name="WorkflowExecutor",
    model=GEMINI_MODEL,
    description="Persists the workflow plan into AlloyDB-backed MCP tools.",
    instruction="""
You are the execution specialist for a productivity assistant.

Read the JSON plan from state:
{execution_plan}

Persist it using the write tools. Follow this order exactly:
1. Call `workflow_store_run` first.
2. Read the returned workflow `id`.
3. Call `notes_create_note` once using that workflow_id.
4. Call `task_manager_create_task` for every task in the plan, reusing the workflow_id.
5. If a calendar_event exists, call `calendar_create_event` once with the same workflow_id.
6. Call `workflow_mark_completed` last with a short summary such as how many tasks were created.

Rules:
- Do not skip workflow_store_run.
- Reuse the exact workflow id returned by workflow_store_run.
- Do not invent database results. Use the tool outputs.
- After all tool calls, write a short plain-text receipt that names:
  - the workflow id
  - number of tasks created
  - note id
  - calendar event id if one was created
  - the final summary stored on the workflow
""",
    tools=[write_toolset],
    output_key="execution_receipt",
)

workflow_reporter = LlmAgent(
    name="WorkflowReporter",
    model=GEMINI_MODEL,
    description="Explains the completed workflow in plain language for the API caller.",
    instruction="""
You are the final response agent.

Using:
- retrieved context: {retrieved_context}
- execution plan: {execution_plan}

Before writing the final answer:
- Call `workflow_finalize_latest_run` exactly once.
- Pass a short summary of what was created for the latest workflow.
- Use the returned workflow id and status in your response.

Write a short final answer that explains:
- what the system created
- which MCP-backed tools were used
- what the user should do next

Keep it practical and concise.
""",
    tools=[report_toolset],
)

root_agent = SequentialAgent(
    name="MultiAgentProductivityAssistant",
    description="Gemini + ADK + MCP + AlloyDB productivity workflow assistant.",
    sub_agents=[
        context_retriever,
        workflow_planner,
        workflow_executor,
        workflow_reporter,
    ],
)
