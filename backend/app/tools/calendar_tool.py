from typing import Dict, Any
from app.tools.base_tool import BaseTool
from app.integrations.google_calendar import GoogleCalendarIntegration


class CalendarTool(BaseTool):

    def __init__(self):
        self.calendar = GoogleCalendarIntegration()

    @property
    def name(self) -> str:
        return "calendar_tool"

    @property
    def description(self) -> str:
        return "Use this to list, create, update, delete calendar events and check availability"

    @property
    def parameters(self) -> Dict:
        return {
            "action": {
                "type": "string",
                "enum": ["list", "create", "update", "delete", "check_availability"],
                "description": "The calendar action to perform",
                "required": True
            },
            "max_results": {
                "type": "integer",
                "description": "For action=list. Number of events to return. Default 10.",
                "required": False
            },
            "event_id": {
                "type": "string",
                "description": "Required for update and delete actions.",
                "required": False
            },
            "title": {
                "type": "string",
                "description": "Event title. Required for create.",
                "required": False
            },
            "start": {
                "type": "string",
                "description": "Start time in ISO format. Required for create and check_availability.",
                "required": False
            },
            "end": {
                "type": "string",
                "description": "End time in ISO format. Required for create and check_availability.",
                "required": False
            },
            "description": {
                "type": "string",
                "description": "Event description. Optional for create and update.",
                "required": False
            },
            "location": {
                "type": "string",
                "description": "Event location. Optional for create and update.",
                "required": False
            },
            "attendees": {
                "type": "array",
                "description": "List of attendee email addresses. Optional for create.",
                "required": False
            }
        }

    def execute(self, params: Dict) -> Dict[str, Any]:
        action = params.get("action")

        if action == "list":
            max_results = params.get("max_results", 10)
            events = self.calendar.list_events(max_results=max_results)
            return {"success": True, "result": events, "error": None}

        elif action == "create":
            title = params.get("title")
            start = params.get("start")
            end = params.get("end")
            if not all([title, start, end]):
                return {
                    "success": False,
                    "result": None,
                    "error": "title, start, and end are required for action=create"
                }
            result = self.calendar.create_event(
                title=title,
                start=start,
                end=end,
                description=params.get("description", ""),
                location=params.get("location", ""),
                attendees=params.get("attendees", [])
            )
            return {"success": True, "result": result, "error": None}

        elif action == "update":
            event_id = params.get("event_id")
            if not event_id:
                return {
                    "success": False,
                    "result": None,
                    "error": "event_id is required for action=update"
                }
            result = self.calendar.update_event(
                event_id=event_id,
                title=params.get("title"),
                start=params.get("start"),
                end=params.get("end"),
                description=params.get("description"),
                location=params.get("location")
            )
            return {"success": True, "result": result, "error": None}

        elif action == "delete":
            event_id = params.get("event_id")
            if not event_id:
                return {
                    "success": False,
                    "result": None,
                    "error": "event_id is required for action=delete"
                }
            result = self.calendar.delete_event(event_id=event_id)
            return {"success": True, "result": result, "error": None}

        elif action == "check_availability":
            start = params.get("start")
            end = params.get("end")
            if not all([start, end]):
                return {
                    "success": False,
                    "result": None,
                    "error": "start and end are required for action=check_availability"
                }
            result = self.calendar.check_availability(start=start, end=end)
            return {"success": True, "result": result, "error": None}

        return {
            "success": False,
            "result": None,
            "error": f"Unknown action '{action}'"
        }