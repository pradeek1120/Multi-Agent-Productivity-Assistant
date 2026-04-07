# Architecture Explanation

## Overview

The system is a multi-agent productivity workflow API built on the Google stack required by the challenge.

## Components

### 1. API Layer

The service is deployed on **Cloud Run** and exposes a clean demo endpoint:

- `POST /demo/run`

This endpoint accepts a user prompt and returns a compact JSON response with the final answer, the agents involved, the MCP tools used, and the session id.

### 2. Orchestration Layer

The core workflow is implemented with **Google ADK** in [`productivity_agent/agent.py`](/home/devin/Multi-Agent-Productivity-Assistant/productivity_agent/agent.py).

The root agent is a `SequentialAgent` that runs four sub-agents in order:

- `ContextRetriever`
- `WorkflowPlanner`
- `WorkflowExecutor`
- `WorkflowReporter`

This satisfies the challenge requirement that a primary agent coordinate one or more sub-agents.

### 3. Model Layer

The agents use **Gemini** for:

- understanding the user request
- building the workflow plan
- coordinating tool usage
- generating the final response

### 4. Tool Layer

The system uses **MCP** through ADK `McpToolset` and Google GenAI Toolbox.

Tools are defined in:

- [`toolbox/tools.yaml`](/home/devin/Multi-Agent-Productivity-Assistant/toolbox/tools.yaml)
- [`toolbox/tools.cloudrun.yaml`](/home/devin/Multi-Agent-Productivity-Assistant/toolbox/tools.cloudrun.yaml)

These tools provide the agent with structured operations instead of direct database access.

### 5. Data Layer

Structured data is stored in **AlloyDB** using the schema in:

- [`schema.sql`](/home/devin/Multi-Agent-Productivity-Assistant/db/schema.sql)

Main tables:

- `workflow_runs`
- `tasks`
- `notes`
- `calendar_events`

## End-to-End Flow

1. A user sends a prompt to `/demo/run`.
2. The API creates or reuses a session.
3. `ContextRetriever` reads prior state from AlloyDB through MCP.
4. `WorkflowPlanner` creates a structured plan.
5. `WorkflowExecutor` stores the workflow, tasks, note, and calendar event through MCP tools.
6. `WorkflowReporter` finalizes the workflow and returns the final answer.

## Why This Design Works

- It is modular, because each sub-agent has a narrow responsibility.
- It is tool-driven, because data access is standardized through MCP.
- It is persistent, because workflow state is written to AlloyDB.
- It is deployable, because the full system runs on Cloud Run behind an API.

## Judge-Facing Summary

This project demonstrates real coordination between:

- multiple agents
- external tools via MCP
- structured data in AlloyDB
- an API deployment on Cloud Run

That directly matches the challenge goal of completing real-world workflows through agent, tool, and data coordination.
