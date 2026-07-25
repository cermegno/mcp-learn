import sys
import json
import psutil
from typing import Dict, Any
import docker
from docker.errors import DockerException, NotFound, APIError
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("ContainerSupervisor")

# Helper function to get Docker client safely
def get_docker_client() -> docker.DockerClient:
    try:
        return docker.from_env()
    except DockerException as e:
        # Standard error printing is required so stdio stream isn't corrupted
        sys.stderr.write(f"Docker connection error: {e}\n")
        raise RuntimeError(f"Could not connect to Docker daemon: {e}")


# ==========================================
# MCP TOOLS
# ==========================================

@mcp.tool()
def list_containers(all_containers: bool = True) -> str:
    """List Docker containers with their status, uptime, IDs, ports, and image names."""
    try:
        client = get_docker_client()
        containers = client.containers.list(all=all_containers)
        
        result = []
        for c in containers:
            # High-level summary string from Docker (e.g., "Up 3 hours", "Exited (0) 10 minutes ago")
            status_summary = c.status
            if "Status" in c.attrs.get("State", {}):
                # Using the raw Docker API 'Status' field if available gives human-readable uptime
                status_summary = c.attrs["State"]["Status"]
            
            # Formatted ports
            ports = [f"{k}->{v}" for k, v in c.ports.items()] if c.ports else []
            
            result.append({
                "id": c.short_id,
                "name": c.name,
                "state": c.status,                       # e.g., "running", "exited"
                "status_uptime": c.attrs["State"].get("Status", c.status), # e.g., "running" or full status
                "created_at": c.attrs.get("Created", ""), # ISO timestamp
                "image": c.image.tags[0] if c.image.tags else c.image.short_id,
                "ports": ", ".join(ports) if ports else "None"
            })
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error listing containers: {str(e)}"

@mcp.tool()
def get_container_logs(name: str, lines: int = 50) -> str:
    """Fetch recent stdout/stderr logs from a specific container."""
    try:
        client = get_docker_client()
        container = client.containers.get(name)
        logs = container.logs(tail=lines, stdout=True, stderr=True)
        return logs.decode("utf-8", errors="replace")
    except NotFound:
        return f"Error: Container '{name}' not found."
    except APIError as e:
        return f"Docker API error fetching logs for '{name}': {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def restart_service(service_name: str) -> str:
    """Safely restart a container by name or ID."""
    try:
        client = get_docker_client()
        container = client.containers.get(service_name)
        container.restart()
        return f"Successfully restarted service '{service_name}' (ID: {container.short_id})."
    except NotFound:
        return f"Error: Cannot restart. Service/container '{service_name}' not found."
    except Exception as e:
        return f"Error restarting service '{service_name}': {str(e)}"


@mcp.tool()
def stop_service(service_name: str) -> str:
    """Stop a running container by name or ID."""
    try:
        client = get_docker_client()
        container = client.containers.get(service_name)
        container.stop()
        return f"Successfully stopped service '{service_name}' (ID: {container.short_id})."
    except NotFound:
        return f"Error: Cannot stop. Service/container '{service_name}' not found."
    except Exception as e:
        return f"Error stopping service '{service_name}': {str(e)}"


# ==========================================
# MCP RESOURCES
# ==========================================

@mcp.resource("metrics://cpu_ram_usage")
def get_system_metrics() -> str:
    """Real-time host system resource metrics (CPU and RAM utilization)."""
    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory_info = psutil.virtual_memory()
    
    metrics = {
        "cpu_usage_percent": cpu_percent,
        "ram_usage_percent": memory_info.percent,
        "ram_used_gb": round(memory_info.used / (1024**3), 2),
        "ram_total_gb": round(memory_info.total / (1024**3), 2)
    }
    return json.dumps(metrics, indent=2)


@mcp.resource("docker://status")
def get_docker_status() -> str:
    """Summary of Docker daemon state and container status counts."""
    try:
        client = get_docker_client()
        all_containers = client.containers.list(all=True)
        
        status_counts: Dict[str, int] = {}
        for c in all_containers:
            status_counts[c.status] = status_counts.get(c.status, 0) + 1
            
        summary = {
            "total_containers": len(all_containers),
            "status_breakdown": status_counts,
            "docker_version": client.version().get("Version", "Unknown")
        }
        return json.dumps(summary, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to query Docker daemon: {str(e)}"})


if __name__ == "__main__":
    mcp.run()