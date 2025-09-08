#!/usr/bin/env python3
"""
Import recent Google Calendar events directly from API into database.
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import List

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'backend'))

# Google Calendar API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Database imports
from database.access.models import RawActivityDAO, RawActivityDB

# Scopes for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate_google_calendar():
    """Authenticate with Google Calendar API."""
    creds = None
    
    # Check if token.json exists (stored credentials)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("Starting OAuth flow for Google Calendar access...")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            print("✅ Credentials saved to token.json")
    
    return creds

def fetch_calendar_events(months_back: int = 3):
    """Fetch calendar events from Google Calendar API."""
    print(f"📅 Fetching calendar events from the last {months_back} months...")
    
    try:
        creds = authenticate_google_calendar()
        service = build('calendar', 'v3', credentials=creds)
        
        # Calculate date range
        now = datetime.utcnow()
        time_min = (now - timedelta(days=months_back * 30)).isoformat() + 'Z'
        time_max = now.isoformat() + 'Z'
        
        print(f"Date range: {time_min} to {time_max}")
        
        # Fetch events
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=2500,  # Increased to get more events
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"✅ Fetched {len(events)} calendar events from Google API")
        
        return events
        
    except HttpError as error:
        print(f"❌ Google Calendar API error: {error}")
        return []
    except Exception as e:
        print(f"❌ Error fetching calendar events: {e}")
        return []

def convert_to_raw_activities(events: List) -> List[RawActivityDB]:
    """Convert Google Calendar events to RawActivityDB format."""
    print(f"🔄 Converting {len(events)} events to database format...")
    
    raw_activities = []
    
    for event in events:
        try:
            # Extract basic info
            event_id = event.get('id', '')
            summary = event.get('summary', 'Untitled Event')
            description = event.get('description', '')
            
            # Extract time information
            start_info = event.get('start', {})
            end_info = event.get('end', {})
            
            # Handle both dateTime and date formats
            start_time = start_info.get('dateTime') or start_info.get('date')
            end_time = end_info.get('dateTime') or end_info.get('date')
            
            if not start_time:
                continue  # Skip events without start time
            
            # Parse dates
            if 'T' in start_time:  # dateTime format
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                date_str = start_dt.strftime('%Y-%m-%d')
                time_str = start_dt.strftime('%H:%M')
            else:  # date format (all-day event)
                start_dt = datetime.fromisoformat(start_time)
                date_str = start_dt.strftime('%Y-%m-%d')
                time_str = None
            
            # Calculate duration
            duration_minutes = 0
            if start_time and end_time:
                try:
                    if 'T' in start_time and 'T' in end_time:
                        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                        duration = end_dt - start_dt
                        duration_minutes = int(duration.total_seconds() / 60)
                    elif 'T' not in start_time and 'T' not in end_time:
                        # All-day events - calculate days
                        start_dt = datetime.fromisoformat(start_time)
                        end_dt = datetime.fromisoformat(end_time)
                        duration = end_dt - start_dt
                        duration_minutes = int(duration.total_seconds() / 60)
                except:
                    duration_minutes = 0
            
            # Build combined details text
            details = summary
            if description:
                details += f" - {description}"
            
            # Create raw activity
            raw_activity = RawActivityDB(
                date=date_str,
                time=time_str,
                duration_minutes=duration_minutes,
                details=details,
                source='google_calendar',
                orig_link=event.get('htmlLink', ''),
                raw_data={
                    'event_id': event_id,
                    'summary': summary,
                    'description': description,
                    'start': start_info,
                    'end': end_info,
                    'location': event.get('location', ''),
                    'attendees': event.get('attendees', []),
                    'created': event.get('created'),
                    'updated': event.get('updated'),
                    'status': event.get('status', ''),
                    'recurrence': event.get('recurrence', [])
                }
            )
            
            raw_activities.append(raw_activity)
            
        except Exception as e:
            print(f"⚠️ Error processing event {event.get('id', 'unknown')}: {e}")
            continue
    
    print(f"✅ Converted {len(raw_activities)} events to raw activities")
    return raw_activities

def import_to_database(raw_activities: List[RawActivityDB]) -> int:
    """Import raw activities into the database."""
    print(f"💾 Importing {len(raw_activities)} activities to database...")
    
    imported_count = 0
    skipped_count = 0
    
    for activity in raw_activities:
        try:
            # Check if this event already exists (by event_id and date)
            event_id = activity.raw_data.get('event_id')
            existing_activities = RawActivityDAO.get_by_date_range(activity.date, activity.date, 'google_calendar')
            
            # Simple duplicate check - skip if exact same event_id exists on same date
            duplicate = False
            for existing in existing_activities:
                if existing.raw_data.get('event_id') == event_id:
                    duplicate = True
                    break
            
            if duplicate:
                skipped_count += 1
                continue
            
            # Create new activity
            activity_id = RawActivityDAO.create(activity)
            imported_count += 1
            
            if imported_count % 50 == 0:
                print(f"  Progress: {imported_count} imported...")
                
        except Exception as e:
            print(f"❌ Error importing activity: {e}")
            continue
    
    print(f"✅ Import complete: {imported_count} new activities, {skipped_count} duplicates skipped")
    return imported_count

def main():
    """Main execution function."""
    print("🚀 Google Calendar Data Import to SmartHistory Database")
    print("=" * 60)
    
    try:
        # Step 1: Fetch events from Google Calendar API
        events = fetch_calendar_events(months_back=3)
        
        if not events:
            print("❌ No events found or API fetch failed")
            return
        
        # Step 2: Convert to database format
        raw_activities = convert_to_raw_activities(events)
        
        if not raw_activities:
            print("❌ No activities converted successfully")
            return
        
        # Step 3: Import to database
        imported_count = import_to_database(raw_activities)
        
        # Step 4: Show summary
        print("\n" + "=" * 60)
        print("📊 IMPORT SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully imported {imported_count} calendar activities")
        
        # Show database stats
        all_activities = RawActivityDAO.get_all()
        calendar_activities = [a for a in all_activities if a.source == 'google_calendar']
        print(f"📈 Total calendar activities in database: {len(calendar_activities)}")
        
        # Show date range of imported data
        if calendar_activities:
            dates = [a.date for a in calendar_activities]
            print(f"📅 Date range: {min(dates)} to {max(dates)}")
            
        print(f"\n🎯 Ready for enhanced AI tagging processing!")
        
    except Exception as e:
        print(f"❌ Error during import: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()