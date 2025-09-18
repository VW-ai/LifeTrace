#!/usr/bin/env python3
"""
Google Calendar API Ingestion (DB-only)

Reads events from Google Calendar API in a date range and writes them to
raw_activities via DAO. Supports multiple calendars.

Credentials:
- credentials.json and token.json at repo root (OAuth client flow)
- or service account (not covered here)

Env:
- SMARTHISTORY_DB_PATH (optional DB path)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional
import json
import os
import sys
from pathlib import Path

# Project root for DB imports
PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from google.oauth2.credentials import Credentials  # type: ignore
    from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
    from google.auth.transport.requests import Request  # type: ignore
    from googleapiclient.discovery import build  # type: ignore
    from googleapiclient.errors import HttpError  # type: ignore
except Exception:
    Credentials = None  # type: ignore
    InstalledAppFlow = None  # type: ignore
    build = None  # type: ignore
    HttpError = Exception  # type: ignore

from src.backend.database import RawActivityDAO, RawActivityDB, get_db_manager


SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def _rfc3339(date_str: str, end_of_day: bool = False) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if end_of_day:
        dt = dt + timedelta(hours=23, minutes=59, seconds=59)
    return dt.isoformat().replace("+00:00", "Z")


def _ensure_creds() -> Optional[Credentials]:  # type: ignore
    if Credentials is None or InstalledAppFlow is None or build is None:
        print("[ERROR] google-api-python-client and auth libraries not installed.")
        return None

    creds: Optional[Credentials] = None
    token_path = PROJECT_ROOT / "token.json"
    cred_path = PROJECT_ROOT / "credentials.json"

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"[WARN] Token refresh failed: {e}")
                creds = None
        if not creds:
            if not cred_path.exists():
                print(f"[ERROR] credentials.json not found at {cred_path}")
                print("Create an OAuth Client ID of type 'Desktop app' in Google Cloud Console, download JSON as credentials.json.")
                return None
            try:
                flow = InstalledAppFlow.from_client_secrets_file(str(cred_path), SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print("[ERROR] OAuth login failed. If you see redirect_uri_mismatch:")
                print(" - Ensure your OAuth client is of type 'Desktop app' (not 'Web application').")
                print(" - Recreate credentials in Google Cloud Console → OAuth client ID → Desktop app.")
                print(" - Delete token.json and retry.")
                print(f"Details: {e}")
                return None
        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return creds


def ingest_to_database(start_date: str, end_date: str, calendar_ids: Optional[List[str]] = None) -> int:
    """Ingest events for [start_date, end_date] inclusive into raw_activities.

    Args:
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
        calendar_ids: list of calendar IDs (default: ["primary"])  
    Returns:
        Number of events ingested
    """
    creds = _ensure_creds()
    if creds is None:
        return 0

    try:
        service = build("calendar", "v3", credentials=creds)
    except Exception as e:
        print(f"[ERROR] Failed to build Calendar service: {e}")
        return 0

    calendar_ids = calendar_ids or ["primary"]
    time_min = _rfc3339(start_date)
    time_max = _rfc3339(end_date, end_of_day=True)

    total = 0
    db = get_db_manager()
    for cal_id in calendar_ids:
        page_token = None
        while True:
            try:
                events_result = (
                    service.events()
                    .list(calendarId=cal_id, timeMin=time_min, timeMax=time_max, singleEvents=True, orderBy="startTime", pageToken=page_token)
                    .execute()
                )
                items = events_result.get("items", [])
                for ev in items:
                    # Parse start/end
                    start = ev.get("start", {}).get("dateTime") or ev.get("start", {}).get("date")
                    end = ev.get("end", {}).get("dateTime") or ev.get("end", {}).get("date")
                    if not start:
                        continue
                    try:
                        if len(start) == 10:  # date only
                            date = start
                            time = None
                            duration_minutes = 0
                        else:
                            sdt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                            edt = datetime.fromisoformat((end or start).replace("Z", "+00:00"))
                            date = sdt.strftime("%Y-%m-%d")
                            time = sdt.strftime("%H:%M")
                            duration_minutes = max(0, int((edt - sdt).total_seconds() // 60))
                    except Exception:
                        continue

                    details = ev.get("summary") or ev.get("description") or ""
                    raw = RawActivityDB(
                        date=date,
                        time=time,
                        duration_minutes=duration_minutes,
                        details=details[:1000],
                        source="google_calendar",
                        orig_link=ev.get("htmlLink", ""),
                        raw_data=ev,
                    )
                    try:
                        # Deduplicate by event id and start time (or htmlLink)
                        ev_id = ev.get('id')
                        params = [
                            "google_calendar",
                            ev_id,
                            ev.get("htmlLink", ""),
                            date,
                            time,
                            time,
                        ]
                        rows = db.execute_query(
                            """
                            SELECT id FROM raw_activities
                            WHERE source = ?
                              AND (json_extract(raw_data, '$.id') = ? OR orig_link = ?)
                              AND date = ?
                              AND (time IS ? OR time = ?)
                            LIMIT 1
                            """,
                            params,
                        )
                        if rows:
                            # Update existing
                            existing_id = rows[0]['id']
                            db.execute_update(
                                """
                                UPDATE raw_activities
                                SET duration_minutes=?, details=?, orig_link=?, raw_data=?
                                WHERE id=?
                                """,
                                (
                                    raw.duration_minutes,
                                    raw.details,
                                    raw.orig_link,
                                    json.dumps(raw.raw_data),
                                    existing_id,
                                ),
                            )
                        else:
                            RawActivityDAO.create(raw)
                            total += 1
                    except Exception as e:
                        print(f"[WARN] Failed to upsert event: {e}")

                page_token = events_result.get("nextPageToken")
                if not page_token:
                    break
            except HttpError as e:  # type: ignore
                print(f"[ERROR] Google API error: {e}")
                break
    print(f"Ingested {total} calendar events into database")
    return total


__all__ = ["ingest_to_database"]
