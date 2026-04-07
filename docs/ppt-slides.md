# PPT Slide Text

## Slide 1: Title

**Multi-Agent Productivity Assistant**  
Gen AI Academy APAC Edition Hackathon Submission

- Built with Gemini, Google ADK, MCP, AlloyDB, and Cloud Run
- Focus: turning a natural-language goal into an executable productivity workflow

## Slide 2: Problem

Users often know what they want to achieve, but not how to structure the work.

Typical pain points:

- vague goals with unclear next steps
- missed deadlines
- disconnected task, note, and calendar management
- no persistent workflow history

## Slide 3: Solution

Our system takes a natural-language request and automatically creates:

- a workflow record
- prioritized tasks
- a planning note
- a calendar block when a deadline is present

The result is a multi-step, persistent workflow managed by cooperating agents.

## Slide 4: Google Stack

- **Gemini** for planning and reasoning
- **Google ADK** for multi-agent orchestration
- **MCP** for standardized tool access
- **AlloyDB** for structured persistence
- **Cloud Run** for API deployment

## Slide 5: Multi-Agent Architecture

Primary agent: `SequentialAgent`

Sub-agents:

1. `ContextRetriever`
2. `WorkflowPlanner`
3. `WorkflowExecutor`
4. `WorkflowReporter`

Each agent has a focused role, which makes the workflow modular and easier to reason about.

## Slide 6: MCP Tools

MCP tools used in the project:

- workflow tools
- task manager tools
- notes tools
- calendar tools

These tools are backed by AlloyDB and accessed through Google GenAI Toolbox.

## Slide 7: End-to-End Flow

1. User sends a prompt to the API
2. Context agent checks prior workflows and pending tasks
3. Planner agent creates a structured plan
4. Executor agent stores workflow, tasks, note, and calendar event
5. Reporter agent returns a clean response

## Slide 8: Database Persistence

All structured outputs are stored in AlloyDB:

- `workflow_runs`
- `tasks`
- `notes`
- `calendar_events`

This gives the system persistent memory for future requests.

## Slide 9: Deployment

The project is deployed on Cloud Run and exposed as an API.

Demo endpoint:

- `POST /demo/run`

This endpoint returns a clean JSON response suitable for demos and evaluation.

## Slide 10: Demo Example

Prompt:

> Prepare my final hackathon submission for tomorrow at 5 PM, create tasks, save a planning note, and schedule a review block.

System output:

- workflow created
- tasks created
- note saved
- calendar event created
- clean response returned through the API

## Slide 11: Outcomes

- satisfied the multi-agent requirement
- used the required Google stack
- persisted structured data in AlloyDB
- exposed the system as a deployable API
- demonstrated coordination across agents, tools, and data

## Slide 12: Next Steps

- richer external tool integrations
- stronger session memory across users
- better scheduling logic
- UI dashboard for real-time workflow tracking
