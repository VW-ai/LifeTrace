#!/usr/bin/env python3
"""Debug why activity matching isn't working"""

import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from src.backend.agent import ActivityMatcher, RawActivity

def debug_matching():
    """Debug the matching process step by step."""
    
    print("🔍 DEBUGGING ACTIVITY MATCHING")
    print("="*50)
    
    # Create the same test activities
    notion_activity = RawActivity(
        date="2025-08-30",  # Note: estimated date from data consumer
        time=None,
        duration_minutes=0,
        details="[Projects > SmartHistory > Authentication] Implemented OAuth2 authentication flow with Google and GitHub providers. Added JWT token generation and validation middleware.",
        source="notion",
        raw_data={'block_id': 'notion-auth-1'}
    )
    
    calendar_activity = RawActivity(
        date="2024-08-30",
        time="09:00", 
        duration_minutes=150,
        details="Development Block - Authentication: Working on OAuth integration and JWT implementation",
        source="google_calendar",
        raw_data={'event_id': 'cal-dev-1'}
    )
    
    print(f"📝 Notion activity:")
    print(f"   Date: {notion_activity.date}")
    print(f"   Details: {notion_activity.details[:80]}...")
    
    print(f"\n📅 Calendar activity:")
    print(f"   Date: {calendar_activity.date}")
    print(f"   Time: {calendar_activity.time}")
    print(f"   Details: {calendar_activity.details[:80]}...")
    
    # Test matching
    matcher = ActivityMatcher()
    
    # Test date proximity
    date_match = matcher._dates_within_window(notion_activity.date, calendar_activity.date, days=1)
    print(f"\n🗓️ Date proximity test:")
    print(f"   Notion: {notion_activity.date}")
    print(f"   Calendar: {calendar_activity.date}")  
    print(f"   Within 1 day: {date_match}")
    
    if not date_match:
        print("❌ ISSUE FOUND: Dates are not within matching window!")
        print("   The data consumer is creating different dates for Notion vs Calendar")
        return False
    
    # Test content similarity  
    content_sim = matcher._calculate_content_similarity(notion_activity, calendar_activity)
    print(f"\n📝 Content similarity test:")
    print(f"   Similarity score: {content_sim:.3f}")
    print(f"   Threshold needed: > 0.3")
    
    if content_sim <= 0.3:
        print("❌ ISSUE: Content similarity too low")
    else:
        print("✅ Content similarity sufficient")
    
    # Test time confidence
    time_conf = matcher._calculate_time_confidence(notion_activity, calendar_activity)
    print(f"\n⏰ Time confidence test:")
    print(f"   Time confidence: {time_conf:.3f}")
    
    # Test overall matching
    match_result = matcher._find_best_calendar_match(notion_activity, [calendar_activity])
    
    if match_result:
        matched_activity, confidence = match_result
        print(f"\n✅ Match found!")
        print(f"   Overall confidence: {confidence:.3f}")
        print(f"   Threshold: > 0.3")
        print(f"   Would match: {'Yes' if confidence > 0.3 else 'No'}")
    else:
        print(f"\n❌ No match found")
    
    return match_result is not None

if __name__ == "__main__":
    debug_matching()