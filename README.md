# Multi-Agent Productivity Assistant

ADK-based submission scaffold for the `Multi-Agent Productivity Assistant` hackathon challenge.

This version is aligned to the Google stack named across the academy tracks:

- `Gemini` as the model
- `Google ADK` for multi-agent orchestration
- `MCP` via `McpToolset`
- `AlloyDB` as the structured database
- `Cloud Run` as the deployment target
- `ADK API Server` as the API layer

## What Is In This Repo

- `productivity_agent/agent.py`
  An ADK `SequentialAgent` that coordinates four sub-agents.
- `productivity_agent/demo_api.py`
  A thin demo-facing FastAPI wrapper that returns clean JSON instead of raw ADK event payloads.
- `toolbox/tools.yaml`
  MCP Toolbox configuration that exposes task, notes, calendar, and workflow tools backed by AlloyDB.
- `db/schema.sql`
  Postgres-compatible schema for workflow runs, tasks, notes, and calendar events.
- `Dockerfile`
  Cloud Run container that installs ADK and the Toolbox binary.
- `.env.example`
  Environment variables you need to supply.

## Submission Assets

Ready-to-use hackathon material is included in:

- [`docs/submission-summary.md`](/home/devin/Multi-Agent-Productivity-Assistant/docs/submission-summary.md)
- [`docs/demo-script.md`](/home/devin/Multi-Agent-Productivity-Assistant/docs/demo-script.md)
- [`docs/architecture.md`](/home/devin/Multi-Agent-Productivity-Assistant/docs/architecture.md)
- [`docs/hackathon-checklist.md`](/home/devin/Multi-Agent-Productivity-Assistant/docs/hackathon-checklist.md)
- [`docs/ppt-slides.md`](/home/devin/Multi-Agent-Productivity-Assistant/docs/ppt-slides.md)
- [`docs/submission-form-template.md`](/home/devin/Multi-Agent-Productivity-Assistant/docs/submission-form-template.md)

## Agent Design

The root agent is a `SequentialAgent`, which satisfies the hackathon requirement for a primary agent coordinating sub-agents.

Sub-agents:

1. `ContextRetriever`
   Reads recent workflows, tasks, notes, and events from AlloyDB through MCP tools.
2. `WorkflowPlanner`
   Uses Gemini to turn the user request into a structured workflow plan.
3. `WorkflowExecutor`
   Uses MCP tools to store the workflow run, create tasks, write a note, and optionally add a calendar event.
4. `WorkflowReporter`
   Produces the final plain-language response for the API caller.

## Tooling Through MCP

The agent does not talk to SQLite or local mock tools anymore.

Instead, it connects to MCP Toolbox and uses these AlloyDB-backed MCP tools:

- `workflow_list_recent_runs`
- `workflow_store_run`
- `workflow_mark_completed`
- `workflow_finalize_latest_run`
- `task_manager_list_pending_tasks`
- `task_manager_create_task`
- `notes_list_recent_notes`
- `notes_create_note`
- `calendar_list_upcoming_events`
- `calendar_create_event`

## Local Setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Create your environment file

```bash
cp .env.example .env
```

Fill in the AlloyDB and Gemini values in `.env`.

For public repository safety:

- keep `.env` private
- keep `cloudrun-env.yaml` private
- keep `toolbox/tools.cloudrun.yaml` private
- use the example files committed in the repo instead:
  - [`cloudrun-env.example.yaml`](/home/devin/Multi-Agent-Productivity-Assistant/cloudrun-env.example.yaml)
  - [`toolbox/tools.cloudrun.example.yaml`](/home/devin/Multi-Agent-Productivity-Assistant/toolbox/tools.cloudrun.example.yaml)

### 3. Apply the schema to AlloyDB

Run the SQL in `db/schema.sql` against your AlloyDB database before starting the agent.

### 4. Start the demo API server

Run this from the repository root:

```bash
uvicorn productivity_agent.demo_api:app --reload
```

By default the demo API serves on `http://localhost:8000`.

Clean demo endpoint:

```bash
curl -X POST "http://localhost:8000/demo/run" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Prepare my final hackathon submission for tomorrow at 5 PM, create tasks, save a planning note, and schedule a review block."
  }'
```

This endpoint returns a small response with:

- the final plain-language answer
- the final agent name
- the agents involved
- the MCP tools called
- the session id

## How The Runtime Works

`productivity_agent/agent.py` uses `McpToolset` with a synchronous stdio connection, which is the ADK deployment-safe pattern for MCP agents.

Local development:

- install the `toolbox` binary and keep `TOOLBOX_COMMAND=toolbox`, or
- set `TOOLBOX_COMMAND=npx` and let ADK start `@toolbox-sdk/server`

The Dockerfile uses the production-style Toolbox binary so the Cloud Run container does not depend on `npx`.

## Cloud Run

The container is built to run the clean demo API in Cloud Run.

Typical deployment flow:

```bash
gcloud run deploy productivity-assistant \
  --source . \
  --region YOUR_REGION \
  --set-env-vars GOOGLE_API_KEY=...,GOOGLE_CLOUD_PROJECT=...,ALLOYDB_REGION=...,ALLOYDB_CLUSTER=...,ALLOYDB_INSTANCE=...,ALLOYDB_DATABASE=...
```

If you use password auth for AlloyDB, also provide `ALLOYDB_USER` and `ALLOYDB_PASSWORD`.

## Verification

This repository includes scaffold checks rather than live integration tests because Gemini, AlloyDB, and MCP Toolbox require real external credentials and services.

Run:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall productivity_agent tests
```

## Important Notes

- This project now targets the Google services named in the challenge instead of local substitutes.
- It is a scaffold for the real service, so you still need valid Gemini and AlloyDB credentials to run it end to end.
- The MCP tools in `toolbox/tools.yaml` are the persistence boundary for tasks, notes, workflow history, and calendar events.
