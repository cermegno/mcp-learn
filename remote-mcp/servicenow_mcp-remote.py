#### RUN ME LIKE THIS
#### uv run fastmcp run .\servicenow_mcp-remote.py --transport http --host 0.0.0.0 --port 8000
import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

instance = os.getenv("SN_INSTANCE")
username = os.getenv("SN_USERNAME")
password = os.getenv("SN_PASSWORD")

mcp = FastMCP("servicenow")

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}


@mcp.tool()
def create_incident(
    short_description: str,
    description: str = "",
    urgency: str = "2",
    impact: str = "2",
) -> dict:
    """Create a ServiceNow incident with a short description and optional details."""
    url = f"https://{instance}.service-now.com/api/now/table/incident"

    # Add also caller_id if you want to specify the user creating the incident. You can get the sys_id of a user from ServiceNow.
    payload = {
        "short_description": short_description,
        "urgency": urgency,
        "impact": impact,
    }
    if description:
        payload["description"] = description

    response = requests.post(
        url,
        auth=(username, password),
        headers=headers,
        json=payload,
    )

    if response.status_code != 201:
        raise RuntimeError(
            f"ServiceNow API error ({response.status_code}): {response.text}"
        )

    result = response.json()["result"]
    return {
        "number": result["number"],
        "sys_id": result["sys_id"],
    }


if __name__ == "__main__":
    mcp.run(transport="http")