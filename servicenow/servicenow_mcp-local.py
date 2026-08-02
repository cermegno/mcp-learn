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


def _get_auth():
    return (username, password)


@mcp.tool()
def create_incident(
    description:str, short_description: str, urgency: str = "2", impact: str = "2"
) -> dict:
    """Create an incident in ServiceNow using description, urgency, and impact.
    Urgency/Impact values: 1 (High), 2 (Medium), 3 (Low)
    """
    url = f"https://{instance}.service-now.com/api/now/table/incident"
    payload = {
        "caller_id": "37f2c9802faacf108853dc7a6fa4e33f", # Replace with the actual caller_id for the user creating the incident
        "description": description,
        "short_description": short_description,
        "urgency": urgency,
        "impact": impact,
    }

    response = requests.post(
        url, auth=_get_auth(), headers=headers, json=payload
    )
    if response.status_code != 201:
        raise RuntimeError(
            f"ServiceNow API error ({response.status_code}): {response.text}"
        )

    result = response.json()["result"]
    return {"number": result["number"], "sys_id": result["sys_id"]}


@mcp.tool()
def get_incident(incident_number: str) -> dict:
    """Get details of an incident by its number (e.g., INC0010001)."""
    url = f"https://{instance}.service-now.com/api/now/table/incident?sysparm_query=number={incident_number}&sysparm_limit=1"
    response = requests.get(url, auth=_get_auth(), headers=headers)

    if response.status_code != 200:
        raise RuntimeError(
            f"ServiceNow API error ({response.status_code}): {response.text}"
        )

    data = response.json().get("result", [])
    if not data:
        raise RuntimeError(f"No incident found for {incident_number}")

    result = data[0]
    return {
        "number": result.get("number"),
        "sys_id": result.get("sys_id"),
        "short_description": result.get("short_description"),
        "urgency": result.get("urgency"),
        "impact": result.get("impact"),
        "state": result.get("state"),
    }


@mcp.tool()
def get_incident_activity(sys_id: str) -> list[dict]:
    """Retrieve the full activity log (work notes and customer comments) for an incident using its sys_id."""
    url = (
        f"https://{instance}.service-now.com/api/now/table/sys_journal_field"
        f"?sysparm_query=element_id={sys_id}^elementINwork_notes,comments"
        f"&sysparm_orderby=sys_created_on"
    )

    response = requests.get(url, auth=_get_auth(), headers=headers)
    if response.status_code != 200:
        raise RuntimeError(
            f"ServiceNow API error ({response.status_code}): {response.text}"
        )

    entries = response.json().get("result", [])
    return [
        {
            "created_on": entry.get("sys_created_on"),
            "created_by": entry.get("sys_created_by"),
            "type": entry.get("element"),  # 'work_notes' or 'comments'
            "entry": entry.get("value"),
        }
        for entry in entries
    ]


@mcp.tool()
def add_work_note(sys_id: str, note: str, is_public: bool = False) -> dict:
    """Add activity updates, troubleshooting steps, or status notes to an incident.

    Args:
        sys_id: The unique system identifier of the incident.
        note: The activity update or troubleshooting text to log.
        is_public: If True, adds as a customer-visible comment. If False (default), adds as internal work notes.
    """
    url = f"https://{instance}.service-now.com/api/now/table/incident/{sys_id}"

    field_name = "comments" if is_public else "work_notes"
    payload = {field_name: note}

    response = requests.patch(
        url, auth=_get_auth(), headers=headers, json=payload
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"ServiceNow API error ({response.status_code}): {response.text}"
        )

    result = response.json()["result"]
    return {
        "number": result["number"],
        "sys_id": result["sys_id"],
        "status": "Activity note added successfully",
    }


@mcp.tool()
def update_incident(
    sys_id: str,
    short_description: str = None,
    urgency: str = None,
    impact: str = None,
    state: str = None,
) -> dict:
    """Update general fields of an incident (e.g., description, urgency, impact, or state).
    Do NOT use this tool to resolve/close an incident—use resolve_incident instead.
    State values: 1 (New), 2 (In Progress), 3 (On Hold), 8 (Canceled)
    """
    url = f"https://{instance}.service-now.com/api/now/table/incident/{sys_id}"
    payload = {}

    if short_description is not None:
        payload["short_description"] = short_description
    if urgency is not None:
        payload["urgency"] = urgency
    if impact is not None:
        payload["impact"] = impact
    if state is not None:
        payload["state"] = state

    if not payload:
        raise ValueError("At least one parameter must be provided for update.")

    response = requests.patch(
        url, auth=_get_auth(), headers=headers, json=payload
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"ServiceNow API error ({response.status_code}): {response.text}"
        )

    result = response.json()["result"]
    return {
        "number": result["number"],
        "sys_id": result["sys_id"],
        "state": result["state"],
        "short_description": result["short_description"],
    }


@mcp.tool()
def resolve_incident(sys_id: str, close_code: str, close_notes: str) -> dict:
    """Resolve/close an incident in ServiceNow. Both resolution code and resolution notes are strictly required.

    Args:
        sys_id: The unique system ID of the incident.
        close_code: Common values include 'Workaround provided', 'Resolved by change', 'Solution provided', or 'Resolved by caller'.
        close_notes: Explanation of how the issue was resolved or fixed.
    """
    url = f"https://{instance}.service-now.com/api/now/table/incident/{sys_id}"

    payload = {
        "state": "6",  # 6 = Resolved
        "close_code": close_code,
        "close_notes": close_notes,
    }

    response = requests.patch(
        url, auth=_get_auth(), headers=headers, json=payload
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"ServiceNow API error ({response.status_code}): {response.text}"
        )

    result = response.json()["result"]
    return {
        "number": result["number"],
        "sys_id": result["sys_id"],
        "state": result["state"],
        "close_code": result.get("close_code"),
        "close_notes": result.get("close_notes"),
    }


if __name__ == "__main__":
    mcp.run()