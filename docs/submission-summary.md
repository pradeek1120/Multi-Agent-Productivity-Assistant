# Submission Summary

## Project

**Multi-Agent Productivity Assistant**

This project is a multi-agent AI system that helps users plan and organize work for deadline-driven tasks such as hackathon submissions. A primary coordinator agent delegates work to specialized sub-agents for context retrieval, workflow planning, execution, and final reporting.

## Problem Solved

Users often need to turn a vague goal into a concrete execution plan. This system takes a natural-language request and converts it into:

- a structured workflow record
- prioritized tasks
- a planning note
- a scheduled calendar block when a deadline is present

## Google Stack Used

- **Gemini**
  Used as the reasoning model for planning, execution guidance, and final response generation.
- **Google ADK**
  Used to build the multi-agent workflow with a root `SequentialAgent` and specialized sub-agents.
- **MCP**
  Used through Google GenAI Toolbox and ADK `McpToolset` so agents can call external tools in a standard way.
- **AlloyDB**
  Used as the structured persistence layer for workflow runs, tasks, notes, and calendar events.
- **Cloud Run**
  Used to deploy the API as a containerized service.

## Multi-Agent Design

The system uses one primary agent and four sub-agents:

1. **ContextRetriever**
   Reads recent workflows, tasks, notes, and events from AlloyDB through MCP tools.
2. **WorkflowPlanner**
   Converts the user request into a structured plan.
3. **WorkflowExecutor**
   Persists the plan by creating workflow rows, tasks, notes, and calendar events.
4. **WorkflowReporter**
   Returns a clean final answer for the API caller and finalizes the workflow state.

## MCP Tools

The system integrates AlloyDB-backed tools via MCP, including:

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

## API Outcome

For a prompt like:

> Prepare my final hackathon submission for tomorrow at 5 PM, create tasks, save a planning note, and schedule a review block.

the API creates:

- a workflow run in AlloyDB
- a sequence of tasks
- a note with planning context
- a calendar event for the review/submission block

and returns a clean JSON response describing what was created.

## Why This Fits The Challenge

This submission satisfies the core requirements:

- primary agent coordinating sub-agents
- structured database persistence
- MCP-based tool integration
- multi-step workflow handling
- API-based deployment

It also stays aligned to the Google stack named in the challenge.
