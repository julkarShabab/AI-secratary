from typing import Dict, Any
from app.tools.base_tool import BaseTool
from app.integrations.jira import JiraIntegration


class TaskTool(BaseTool):

    def __init__(self):
        self.jira = JiraIntegration()

    @property
    def name(self) -> str:
        return "task_tool"

    @property
    def description(self) -> str:
        return "Use this to list, create, update, or get details of Jira tasks"

    @property
    def parameters(self) -> Dict:
        return {
            "action": {
                "type": "string",
                "enum": ["list", "create", "update", "get"],
                "description": "The task action to perform",
                "required": True
            },
            "issue_key": {
                "type": "string",
                "description": "Required for update and get. Example: AS-1",
                "required": False
            },
            "title": {
                "type": "string",
                "description": "Required for create. Task title.",
                "required": False
            },
            "description": {
                "type": "string",
                "description": "Task description. Optional for create and update.",
                "required": False
            },
            "priority": {
                "type": "string",
                "enum": ["Low", "Medium", "High", "Critical"],
                "description": "Task priority. Default Medium.",
                "required": False
            },
            "status": {
                "type": "string",
                "description": "For update. New status like In Progress or Done.",
                "required": False
            },
            "max_results": {
                "type": "integer",
                "description": "For list. Number of tasks to return. Default 10.",
                "required": False
            }
        }

    def execute(self, params: Dict) -> Dict[str, Any]:
        action = params.get("action")

        if action == "list":
            tasks = self.jira.list_tasks(
                max_results=params.get("max_results", 10)
            )
            return {"success": True, "result": tasks, "error": None}

        elif action == "create":
            title = params.get("title")
            if not title:
                return {
                    "success": False,
                    "result": None,
                    "error": "title is required for action=create"
                }
            result = self.jira.create_task(
                title=title,
                description=params.get("description", ""),
                priority=params.get("priority", "Medium")
            )
            return {"success": True, "result": result, "error": None}

        elif action == "update":
            issue_key = params.get("issue_key")
            if not issue_key:
                return {
                    "success": False,
                    "result": None,
                    "error": "issue_key is required for action=update"
                }
            result = self.jira.update_task(
                issue_key=issue_key,
                title=params.get("title"),
                description=params.get("description"),
                status=params.get("status")
            )
            return {"success": True, "result": result, "error": None}

        elif action == "get":
            issue_key = params.get("issue_key")
            if not issue_key:
                return {
                    "success": False,
                    "result": None,
                    "error": "issue_key is required for action=get"
                }
            task = self.jira.get_task(issue_key=issue_key)
            return {"success": True, "result": task, "error": None}

        return {
            "success": False,
            "result": None,
            "error": f"Unknown action '{action}'"
        }