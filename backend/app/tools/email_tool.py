from typing import Dict, Any
from sqlalchemy.orm import Session
from app.tools.base_tool import BaseTool
from app.integrations.gmail import GmailIntegration
from app.integrations.google_auth import get_credentials_for_user
from app.db import models


class EmailTool(BaseTool):

    def __init__(self, user_id: int, db: Session):
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        credentials = get_credentials_for_user(user, db)
        self.gmail = GmailIntegration(credentials)

    @property
    def name(self) -> str:
        return "email_tool"

    @property
    def description(self) -> str:
        return "Use this to list emails, read a specific email, or send an email via Gmail"

    @property
    def parameters(self) -> Dict:
        return {
            "action": {
                "type": "string",
                "enum": ["list", "read", "send"],
                "description": "The email action to perform",
                "required": True
            },
            "email_id": {
                "type": "string",
                "description": "Required for action=read. The ID of the email to read.",
                "required": False
            },
            "to": {
                "type": "string",
                "description": "Required for action=send. Recipient email address.",
                "required": False
            },
            "subject": {
                "type": "string",
                "description": "Required for action=send. Email subject line.",
                "required": False
            },
            "body": {
                "type": "string",
                "description": "Required for action=send. Email body content.",
                "required": False
            },
            "max_results": {
                "type": "integer",
                "description": "For action=list. Number of emails to return. Default 10.",
                "required": False
            }
        }

    def execute(self, params: Dict) -> Dict[str, Any]:
        action = params.get("action")

        if action == "list":
            max_results = int(params.get("max_results", 10))
            emails = self.gmail.list_emails(max_results=max_results)
            return {
                "success": True,
                "result": emails,
                "error": None
            }

        elif action == "read":
            email_id = params.get("email_id")
            if not email_id:
                return {
                    "success": False,
                    "result": None,
                    "error": "email_id is required for action=read"
                }
            email = self.gmail.read_email(email_id=email_id)
            return {
                "success": True,
                "result": email,
                "error": None
            }

        elif action == "send":
            to = params.get("to")
            subject = params.get("subject")
            body = params.get("body")

            if not all([to, subject, body]):
                return {
                    "success": False,
                    "result": None,
                    "error": "to, subject, and body are all required for action=send"
                }

            result = self.gmail.send_email(to=to, subject=subject, body=body)
            return {
                "success": True,
                "result": result,
                "error": None
            }

        return {
            "success": False,
            "result": None,
            "error": f"Unknown action '{action}'"
        }