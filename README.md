# Multi-Agent Productivity Assistant

An API-first productivity assistant that converts a natural-language goal into a structured workflow with tasks, notes, and a calendar block.

This project is built around the Google stack from the hackathon prompt:

- `Gemini` for reasoning
- `Google ADK` for multi-agent orchestration
- `MCP` through `McpToolset` and Toolbox
- `AlloyDB` for persistence
- `Cloud Run` for deployment

## What It Does

For a prompt like:

> Prepare my final hackathon submission for tomorrow at 5 PM, create tasks, save a planning note, and schedule a review block.

the system:

- retrieves recent workflow context
- creates a structured execution plan
- stores a workflow record
- creates prioritized tasks
- saves a planning note
- creates a calendar event when a deadline is present
- returns a clean JSON response

## Architecture

The root agent is a `SequentialAgent` with four focused sub-agents:

1. `ContextRetriever`
   Reads recent workflows, tasks, notes, and events through MCP tools.
2. `WorkflowPlanner`
   Turns the user request into a structured plan.
3. `WorkflowExecutor`
   Persists the workflow, tasks, notes, and calendar event.
4. `WorkflowReporter`
   Finalizes the workflow and returns the final answer.

High-level flow:

`User Prompt -> Cloud Run API -> ADK Agents -> MCP Toolbox -> AlloyDB -> Final Response`

Additional architecture notes are in [architecture.md](/home/devin/Multi-Agent-Productivity-Assistant/docs/architecture.md).

## Repository Layout

- `productivity_agent/agent.py`
  ADK multi-agent workflow definition.
- `productivity_agent/demo_api.py`
  FastAPI wrapper that exposes a clean demo endpoint.
- `toolbox/tools.yaml`
  MCP tool definitions backed by AlloyDB.
- `db/schema.sql`
  Database schema for workflows, tasks, notes, and calendar events.
- `tests/test_scaffold.py`
  Lightweight validation tests for repo structure and syntax.

## MCP Tools

The agent uses these AlloyDB-backed tools:

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

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create your local environment file:

```bash
cp .env.example .env
```

3. Apply `db/schema.sql` to your AlloyDB database.

4. Start the demo API:

```bash
uvicorn productivity_agent.demo_api:app --reload
```

5. Send a request:

```bash
curl -X POST "http://localhost:8000/demo/run" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Prepare my final hackathon submission for tomorrow at 5 PM, create tasks, save a planning note, and schedule a review block."
  }'
```

## Demo API

Main endpoint:

- `POST /demo/run`

Response includes:

- final answer
- final agent name
- agents involved
- tool calls made
- session id

## Cloud Run Deployment

This repo is containerized for Cloud Run.

Typical deploy shape:

```bash
gcloud run deploy productivity-assistant \
  --source . \
  --region YOUR_REGION \
  --set-env-vars GOOGLE_API_KEY=...,GOOGLE_CLOUD_PROJECT=...,ALLOYDB_REGION=...,ALLOYDB_CLUSTER=...,ALLOYDB_INSTANCE=...,ALLOYDB_DATABASE=...
```

If your AlloyDB setup uses password auth, also set:

- `ALLOYDB_USER`
- `ALLOYDB_PASSWORD`

For public repository safety, keep real env files private and use the committed examples:

- [cloudrun-env.example.yaml](/home/devin/Multi-Agent-Productivity-Assistant/cloudrun-env.example.yaml)
- [tools.cloudrun.example.yaml](/home/devin/Multi-Agent-Productivity-Assistant/toolbox/tools.cloudrun.example.yaml)

## Verification

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall productivity_agent tests
```

## Notes

- Live Gemini, AlloyDB, and MCP integrations require real credentials and quota.
- The public repo intentionally excludes private deployment files and secrets.
- This repo is structured as a working prototype that can be extended into a richer productivity platform.
