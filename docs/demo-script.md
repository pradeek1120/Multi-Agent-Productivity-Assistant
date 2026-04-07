# Demo Script

## 1-Minute Demo

Hello, this is our **Multi-Agent Productivity Assistant** built for the Gen AI Academy hackathon.

Our system uses **Gemini**, **Google ADK**, **MCP**, **AlloyDB**, and **Cloud Run**.

Here is the flow.

First, I send a natural-language request to the API:

> Prepare my final hackathon submission for tomorrow at 5 PM, create tasks, save a planning note, and schedule a review block.

The request goes to our **primary coordinator agent**. That agent does not do everything itself. It delegates to four specialized sub-agents:

1. a context retriever that checks previous workflows and pending work
2. a planner that turns the request into a structured workflow
3. an executor that uses MCP tools to write data into AlloyDB
4. a reporter that returns the final result

The executor creates:

- a workflow record
- task entries
- a planning note
- a calendar event

All of these are stored in **AlloyDB**, and the tools are exposed through **MCP Toolbox**.

The service is deployed on **Cloud Run**, so the whole workflow is available as an API.

Finally, I can show the generated rows in AlloyDB and the clean API response, which proves that the agents, tools, and database are working together end to end.

That is our multi-agent productivity assistant.

## Demo Order

1. Show the Cloud Run endpoint.
2. Send one clean `POST /demo/run` request.
3. Show the response JSON.
4. Open AlloyDB Studio and show the new workflow, tasks, notes, and calendar event rows.
5. End on the architecture slide or repo overview.

## Backup Talking Points

- The root agent is a `SequentialAgent`.
- Tool calls are standardized through MCP.
- AlloyDB stores all structured workflow data.
- The API is demo-friendly because `/demo/run` returns a clean response instead of raw event traces.
