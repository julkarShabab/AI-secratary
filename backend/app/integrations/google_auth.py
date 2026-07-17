from datetime import datetime, timezone, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from sqlalchemy.orm import Session
from app.db import models

TOKEN_URI = "https://oauth2.googleapis.com/token"


def get_credentials_for_user(user: "models.User", db: Session) -> Credentials:
    """
    Builds a google.oauth2.credentials.Credentials object from tokens stored
    on the user record (set during /api/auth/google/callback). Refreshes the
    access token if expired and persists the new one back to the DB.

    Raises ValueError if the user never granted Gmail/Calendar access (e.g.
    they signed up with email/password, or logged in before these scopes
    were added) — callers should catch this and surface a clear message.
    """
    import os
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not user.google_refresh_token:
        raise ValueError(
            "No Google account connected with Gmail/Calendar access. "
            "Please log in with Google to enable email and calendar features."
        )

    scopes = (user.google_scopes or "").split() or None

    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri=TOKEN_URI,
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes,
    )

    expiry = user.google_token_expiry
    if expiry and expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    expired = not expiry or expiry <= datetime.now(timezone.utc)

    if expired:
        creds.refresh(Request())
        user.google_access_token = creds.token
        user.google_token_expiry = datetime.now(timezone.utc) + timedelta(seconds=3600)
        db.commit()

    return creds