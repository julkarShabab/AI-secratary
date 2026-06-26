import os
from typing import List, Dict, Any
from jira import JIRA


class JiraIntegration:

    def __init__(self):
        url = os.getenv("JIRA_URL")
        email = os.getenv("JIRA_EMAIL")
        token = os.getenv("JIRA_API_TOKEN")

        if not all([url, email, token]):
            raise ValueError("JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN must be set in .env")

        self.client = JIRA(
            server=url,
            basic_auth=(email, token)
        )
        self.project_key = os.getenv("JIRA_PROJECT_KEY", "AS")

    def list_tasks(self, max_results: int = 10) -> List[Dict]:
        """
        Returns open issues assigned to the current user.
        """
        jql = f'project = {self.project_key} AND statusCategory != Done ORDER BY created DESC'
        issues = self.client.search_issues(jql, maxResults=max_results)

        return [
            {
                "id": issue.key,
                "title": issue.fields.summary,
                "status": issue.fields.status.name,
                "priority": issue.fields.priority.name if issue.fields.priority else "None",
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
                "created": str(issue.fields.created)
            }
            for issue in issues
        ]

    def create_task(self, title: str, description: str = "",
                    priority: str = "Medium") -> Dict:
        """
        Creates a new Jira issue.
        Always called after HITL confirmation.
        """
        issue = self.client.create_issue(
            project=self.project_key,
            summary=title,
            description=description,
            issuetype={"name": "Task"},
            priority={"name": priority}
        )

        return {
            "success": True,
            "id": issue.key,
            "url": f"{os.getenv('JIRA_URL')}/browse/{issue.key}"
        }

    def update_task(self, issue_key: str, title: str = None,
                    description: str = None, status: str = None) -> Dict:
        """
        Updates an existing Jira issue.
        Always called after HITL confirmation.
        """
        issue = self.client.issue(issue_key)

        if title or description:
            fields = {}
            if title:
                fields["summary"] = title
            if description:
                fields["description"] = description
            issue.update(fields=fields)

        if status:
            transitions = self.client.transitions(issue)
            for t in transitions:
                if t["name"].lower() == status.lower():
                    self.client.transition_issue(issue, t["id"])
                    break

        return {
            "success": True,
            "id": issue_key
        }

    def get_task(self, issue_key: str) -> Dict:
        """
        Returns details of a specific Jira issue.
        """
        issue = self.client.issue(issue_key)
        return {
            "id": issue.key,
            "title": issue.fields.summary,
            "description": str(issue.fields.description or ""),
            "status": issue.fields.status.name,
            "priority": issue.fields.priority.name if issue.fields.priority else "None",
            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
            "created": str(issue.fields.created)
        }