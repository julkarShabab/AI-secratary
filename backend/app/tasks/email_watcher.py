from app.integrations.gmail import GmailIntegration


def watch_emails():
    """
    Polls Gmail inbox every 10 minutes.
    Checks for new unread emails and logs them.
    In production this will trigger notifications to the user.
    """
    try:
        gmail = GmailIntegration()
        emails = gmail.list_emails(max_results=5)

        if not emails:
            print("[EmailWatcher] No new emails found.")
            return {"status": "ok", "new_emails": 0}

        print(f"[EmailWatcher] Found {len(emails)} emails.")
        for email in emails:
            print(f"  From: {email['from']} | Subject: {email['subject']}")

        return {
            "status": "ok",
            "new_emails": len(emails),
            "emails": emails
        }

    except Exception as e:
        print(f"[EmailWatcher] Error: {str(e)}")
        return {"status": "error", "error": str(e)}