# 🐳 Container Supervisor MCP Server

A lightweight [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server built with `FastMCP` that exposes local Docker container management and host system monitoring directly to AI assistants like Claude Desktop, Claude Code or Cursor.

Instead of jumping back and forth to your terminal to check `docker ps`, inspect logs, or restart crashed services, you can interact with Docker in natural language, enabling workflows like:

> *"Check the last 50 lines of logs for the `backend-api` container, figure out why it crashed, and restart it."*

Checkout the `output.md` file for sample interactions in Claude Code

---

### 📦 Exposed Capabilities

| Type | URI / Name | Description |
| :--- | :--- | :--- |
| **Tool** | `list_containers` | Lists active/all containers with human-readable status, uptime, and ports. |
| **Tool** | `get_container_logs` | Pulls trailing stdout/stderr logs from a specified container. |
| **Tool** | `restart_service` | Restarts a container by name or short ID. |
| **Tool** | `stop_service` | Stops a running container safely. |
| **Resource** | `metrics://cpu_ram_usage` | Returns current host system CPU % and RAM metrics. |
| **Resource** | `docker://status` | Provides Docker daemon status and total container counts. |

### How to install and add it to Claude Code
- After `git clone` create a virtual environment and install dependencies. I am using 'uv'

`uv init .`

`uv add mcp psutil docker`

- Add it to Claude Code

`claude mcp add container-supervisor -- uv run --directory /path/to/dir/containing/mcp_file docker_mcp_server.py`

- Verify it was added

`claude mcp list`
