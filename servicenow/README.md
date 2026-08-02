# ServiceNow MCP Local Agent

This project combines a local ServiceNow MCP server with a LangChain agent so you can interact with ServiceNow incidents from the terminal. It uses a local Gemma 4 model running with Ollama.

## What it does

The local agent can help you:
- create incidents in ServiceNow
- retrieve incident details
- add work notes or comments
- update incident fields
- resolve or close incidents

The MCP server implementation lives in [servicenow/servicenow_mcp-local.py](servicenow/servicenow_mcp-local.py), and the chat agent lives in [servicenow/myagent-local.py](servicenow/myagent-local.py).

## Prerequisites

Before you start, make sure you have:
- Python 3.12 or newer
- UV installed
- Ollama installed and running locally
- A ServiceNow instance with valid API credentials. Specifically you might want to add the "itil" role.

If you do not already have the Ollama model installed, pull one first:

```bash
ollama pull gemma4
```

If you prefer a different model, update the model name in [servicenow/myagent-local.py](servicenow/myagent-local.py).

## Install dependencies

From the repository root, run:

```bash
uv sync
```

## Configure the environment

Create a file named `.env` in the repository root (the same directory as this README) with your ServiceNow credentials:

```env
SN_INSTANCE=your-instance-name
SN_USERNAME=your-service-now-username
SN_PASSWORD=your-service-now-password
```

### Notes about the variables
- `SN_INSTANCE` should be only the instance name, not the full URL. For example, if your ServiceNow URL is `https://dev12345.service-now.com`, use `dev12345`.
- `SN_USERNAME` and `SN_PASSWORD` should be your ServiceNow login credentials.
- The project uses `python-dotenv`, so the values are loaded automatically when the scripts start.

## Run the local agent

Start the agent from the `servicenow` folder so the local MCP server can be found correctly:

```bash
cd servicenow
uv run python myagent-local.py
```

You can then enter prompts such as:
- "Create an incident for a failed login"
- "Change the impact to high"
- "Get details for incident INC0010001"
- "Add a work note to incident INC0010001"
- "Resolve incident INC0010001 with a close code and notes"

## Important note

The example MCP server currently includes a placeholder `caller_id` when creating incidents. If your ServiceNow instance requires a different caller value, update it in [servicenow/servicenow_mcp-local.py](servicenow/servicenow_mcp-local.py).
