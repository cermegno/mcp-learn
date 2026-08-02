# Remote ServiceNow MCP

This folder is intended as a learning example for running an MCP server remotely. The goal is to show how a local agent can connect to a ServiceNow MCP server over HTTP, rather than to provide a full ServiceNow automation platform.

## What this project does

- Exposes a single MCP tool: `create_incident`
- Lets an agent create a ServiceNow incident remotely through an HTTP MCP endpoint
- Keeps the client/server connection based on IP address and port, so it can be used across machines
- Keeps the scope intentionally small so the remote MCP pattern is easy to understand

> This project is intentionally minimal. If you want broader ServiceNow functionality, see the [servicenow](../servicenow) folder.

## Files

- `servicenow_mcp-remote.py` — the remote MCP server
- `myagent-remote.py` — the client agent that connects to the server over HTTP

## Prerequisites

Before running anything, make sure you have:

- Python 3.12 or newer
- `uv` installed
- Access to a ServiceNow instance with valid credentials
- Ollama installed and running locally if you want to use the agent with a local model

## Environment variables

Create a `.env` file in this folder (or in the repository root if you prefer to keep it there) with your ServiceNow credentials:

```env
SN_INSTANCE=your-instance-name
SN_USERNAME=your-service-now-username
SN_PASSWORD=your-service-now-password
```

If you want to connect to a different host than `127.0.0.1`, you can also set:

```env
SERVER_IP=your-server-ip
```

## Install dependencies

From the repository root, run:

```bash
uv sync
```

## Run the remote MCP server

Start the server with:

```bash
uv run fastmcp run .\servicenow_mcp-remote.py --transport http --host 0.0.0.0 --port 8000
```

This exposes the MCP endpoint at:

```text
http://0.0.0.0:8000/mcp
```

## Run the agent client

In another terminal, run:

```bash
uv run python myagent-remote.py
```

The agent will connect to the server using the `SERVER_IP` value from `.env` (default: `127.0.0.1`) and prompt you for a request such as:

- "Create an incident for a printer issue"
- "Open a ServiceNow incident for a failed VPN login"

## Why run MCP remotely?

Running an MCP server remotely can be advantageous when:

- you want to keep the tool logic or ServiceNow integration in a separate service instead of bundling everything into the client
- multiple agents or applications need to share the same MCP endpoint
- you want to deploy the server on a different machine, container, or network location while keeping the client lightweight
- you are testing distributed architectures or learning how MCP works across services

## Notes

- The server currently supports only incident creation.
- If your ServiceNow instance requires a different caller or field mapping, update the payload in `servicenow_mcp-remote.py` accordingly.
