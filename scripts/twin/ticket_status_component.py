import re

from lfx.custom.custom_component.component import Component
from lfx.inputs.inputs import MessageTextInput
from lfx.io import Output
from lfx.schema.data import Data


class TicketStatusComponent(Component):
    display_name = "Ticket Status"
    description = "Look up the current status of an internal support ticket by its ID."
    icon = "ticket"

    # Mock ticketing system: stand-in for a real ITSM API (Jira / ServiceNow).
    # In a production twin this method would call that API instead.
    MOCK_TICKETS: dict[str, dict] = {
        "101": {
            "status": "Open",
            "priority": "High",
            "assignee": "Alice Martin",
            "summary": "OpenSearch cluster returns 503 under load",
            "updated": "2026-08-20",
        },
        "102": {
            "status": "In Progress",
            "priority": "Medium",
            "assignee": "Bob Chen",
            "summary": "Add hybrid search to the product catalog index",
            "updated": "2026-08-21",
        },
        "103": {
            "status": "Resolved",
            "priority": "Low",
            "assignee": "Carla Diaz",
            "summary": "Dashboards login redirect loop",
            "updated": "2026-08-18",
        },
    }

    inputs = [
        MessageTextInput(
            name="ticket_id",
            display_name="Ticket ID",
            info="The support ticket identifier, e.g. 'TICKET-101' or '#101'.",
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(display_name="Ticket", name="result", type_=Data, method="get_ticket_status"),
    ]

    def _normalize_id(self, raw: str) -> str | None:
        """Extract the numeric ticket id from free-form input like '#101' or 'TICKET-101'."""
        if raw is None:
            return None
        match = re.search(r"\d+", str(raw))
        return match.group(0) if match else None

    def get_ticket_status(self) -> Data:
        """Return the mock status for the requested support ticket."""
        key = self._normalize_id(self.ticket_id)
        if key is None:
            self.status = "no id"
            return Data(data={"error": "No ticket id found in the request.", "input": self.ticket_id})

        ticket = self.MOCK_TICKETS.get(key)
        if ticket is None:
            self.status = f"TICKET-{key}: not found"
            return Data(
                data={
                    "ticket_id": f"TICKET-{key}",
                    "found": False,
                    "message": f"No ticket TICKET-{key} exists in the system.",
                }
            )

        self.status = f"TICKET-{key}: {ticket['status']}"
        return Data(data={"ticket_id": f"TICKET-{key}", "found": True, **ticket})

    def build(self):
        return self.get_ticket_status
