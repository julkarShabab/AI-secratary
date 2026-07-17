import base64
from email.mime.text import MIMEText
from typing import List, Dict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


class GmailIntegration:

    def __init__(self, credentials: Credentials):
        self.service = build("gmail", "v1", credentials=credentials)

    def list_emails(self, max_results: int = 10) -> List[Dict]:
        """
        Returns the latest emails from inbox.
        """
        results = self.service.users().messages().list(
            userId="me",
            maxResults=max_results,
            labelIds=["INBOX"]
        ).execute()

        messages = results.get("messages", [])
        emails = []

        for msg in messages:
            detail = self.service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"]
            ).execute()

            headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
            emails.append({
                "id": msg["id"],
                "from": headers.get("From", ""),
                "subject": headers.get("Subject", ""),
                "date": headers.get("Date", ""),
                "snippet": detail.get("snippet", "")
            })

        return emails

    def read_email(self, email_id: str) -> Dict:
        """
        Returns the full content of a single email by ID.
        """
        detail = self.service.users().messages().get(
            userId="me",
            id=email_id,
            format="full"
        ).execute()

        headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
        body = ""

        if "parts" in detail["payload"]:
            for part in detail["payload"]["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data", "")
                    body = base64.urlsafe_b64decode(data).decode("utf-8")
                    break
        elif "body" in detail["payload"]:
            data = detail["payload"]["body"].get("data", "")
            if data:
                body = base64.urlsafe_b64decode(data).decode("utf-8")

        return {
            "id": email_id,
            "from": headers.get("From", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "body": body
        }

    def send_email(self, to: str, subject: str, body: str) -> Dict:
        """
        Sends an email via Gmail.
        Always called after HITL confirmation.
        """
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        result = self.service.users().messages().send(
            userId="me",
            body={"raw": raw}
        ).execute()

        return {
            "success": True,
            "message_id": result["id"]
        }