import os
from typing import List, Dict, Any
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar"
]

TOKEN_FILE = "gmail_token.json"
CREDENTIALS_FILE = "credentials.json"


class GoogleCalendarIntegration:

    def __init__(self):
        self.service = self._authenticate()

    def _authenticate(self):
        """
        Reuses the same token file as Gmail.
        If token doesn't have calendar scope, re-authenticates.
        """
        creds = None

        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())

        return build("calendar", "v3", credentials=creds)

    def list_events(self, max_results: int = 10) -> List[Dict]:
        """
        Returns upcoming calendar events starting from now.
        """
        now = datetime.now(timezone.utc).isoformat()

        results = self.service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = results.get("items", [])
        output = []

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))
            output.append({
                "id": event["id"],
                "title": event.get("summary", "No title"),
                "start": start,
                "end": end,
                "location": event.get("location", ""),
                "description": event.get("description", ""),
                "attendees": [
                    a["email"] for a in event.get("attendees", [])
                ]
            })

        return output

    def create_event(self, title: str, start: str, end: str,
                     description: str = "", location: str = "",
                     attendees: List[str] = []) -> Dict:
        """
        Creates a new calendar event.
        start and end must be ISO format: "2026-06-20T10:00:00+06:00"
        Always called after HITL confirmation.
        """
        event = {
            "summary": title,
            "location": location,
            "description": description,
            "start": {"dateTime": start, "timeZone": "Asia/Dhaka"},
            "end": {"dateTime": end, "timeZone": "Asia/Dhaka"},
            "attendees": [{"email": email} for email in attendees]
        }

        result = self.service.events().insert(
            calendarId="primary",
            body=event
        ).execute()

        return {
            "success": True,
            "event_id": result["id"],
            "link": result.get("htmlLink", "")
        }

    def update_event(self, event_id: str, title: str = None,
                     start: str = None, end: str = None,
                     description: str = None, location: str = None) -> Dict:
        """
        Updates an existing calendar event by ID.
        Always called after HITL confirmation.
        """
        event = self.service.events().get(
            calendarId="primary",
            eventId=event_id
        ).execute()

        if title:
            event["summary"] = title
        if start:
            event["start"] = {"dateTime": start, "timeZone": "Asia/Dhaka"}
        if end:
            event["end"] = {"dateTime": end, "timeZone": "Asia/Dhaka"}
        if description:
            event["description"] = description
        if location:
            event["location"] = location

        result = self.service.events().update(
            calendarId="primary",
            eventId=event_id,
            body=event
        ).execute()

        return {
            "success": True,
            "event_id": result["id"],
            "link": result.get("htmlLink", "")
        }

    def delete_event(self, event_id: str) -> Dict:
        """
        Deletes a calendar event by ID.
        Always called after HITL confirmation.
        """
        self.service.events().delete(
            calendarId="primary",
            eventId=event_id
        ).execute()

        return {
            "success": True,
            "event_id": event_id
        }

    def check_availability(self, start: str, end: str) -> Dict:
        """
        Checks if there are any conflicts in a given time range.
        """
        results = self.service.events().list(
            calendarId="primary",
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = results.get("items", [])

        return {
            "available": len(events) == 0,
            "conflicts": [e.get("summary", "No title") for e in events]
        }