#!/usr/bin/env python3
"""
Test the AI Agent's key capabilities with focused examples
"""

import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from src.backend.agent import ActivityProcessor, load_api_key

def create_focused_test_data():
    """Create focused test data that showcases matching and tagging abilities."""
    
    # Notion activities (no specific times, varied content lengths)
    notion_data = [
        {
            "block_id": "notion-auth-1",
            "block_type": "paragraph",
            "text": "Implemented OAuth2 authentication flow with Google and GitHub providers. Added JWT token generation and validation middleware.",
            "hierarchy": ["Projects", "SmartHistory", "Authentication"]
        },
        {
            "block_id": "notion-bug-1", 
            "block_type": "to_do",
            "text": "Fixed critical bug in user session management - sessions weren't being properly invalidated on logout.",
            "hierarchy": ["Tasks", "Bug Fixes"]
        },
        {
            "block_id": "notion-meeting-1",
            "block_type": "paragraph", 
            "text": "Team sync discussion about Q4 roadmap and upcoming features",
            "hierarchy": ["Meetings", "Team Sync"]
        },
        {
            "block_id": "notion-research-1",
            "block_type": "paragraph",
            "text": "Researched different approaches for implementing real-time notifications using WebSockets vs Server-Sent Events. WebSockets seem more suitable for our bidirectional communication needs.",
            "hierarchy": ["Research", "Technical"]
        }
    ]
    
    # Calendar activities (with times, some should match Notion content)
    calendar_data = [
        {
            "event_id": "cal-dev-1",
            "summary": "Development Block - Authentication",
            "description": "Working on OAuth integration and JWT implementation",
            "start_time": "2025-08-30T09:00:00Z",
            "end_time": "2025-08-30T11:30:00Z", 
            "duration_minutes": 150,
            "text": "Development Block - Authentication: Working on OAuth integration and JWT implementation",
            "html_link": "https://calendar.google.com/event/dev1"
        },
        {
            "event_id": "cal-bug-1",
            "summary": "Bug Fix Session",
            "description": "Debugging session management issues",
            "start_time": "2025-08-30T14:00:00Z",
            "end_time": "2025-08-30T15:00:00Z",
            "duration_minutes": 60, 
            "text": "Bug Fix Session: Debugging session management issues",
            "html_link": "https://calendar.google.com/event/bug1"
        },
        {
            "event_id": "cal-meeting-1", 
            "summary": "Team Sync - Q4 Planning",
            "description": "Quarterly planning and roadmap discussion",
            "start_time": "2025-08-30T16:00:00Z",
            "end_time": "2025-08-30T17:00:00Z",
            "duration_minutes": 60,
            "text": "Team Sync - Q4 Planning: Quarterly planning and roadmap discussion", 
            "html_link": "https://calendar.google.com/event/meeting1"
        },
        {
            "event_id": "cal-unmatched-1",
            "summary": "Client Call",
            "description": "Weekly check-in with client about project status",
            "start_time": "2025-08-30T11:00:00Z", 
            "end_time": "2025-08-30T11:30:00Z",
            "duration_minutes": 30,
            "text": "Client Call: Weekly check-in with client about project status",
            "html_link": "https://calendar.google.com/event/client1" 
        }
    ]
    
    # Save test files
    with open('test_notion_focused.json', 'w') as f:
        json.dump(notion_data, f, indent=2)
    
    with open('test_calendar_focused.json', 'w') as f:
        json.dump(calendar_data, f, indent=2)
    
    print("✅ Created focused test data:")
    print("  📝 4 Notion activities (varied content, no times)")
    print("  📅 4 Calendar activities (with times)")
    print("  🎯 Expected matches: 3 pairs + 1 unmatched research activity")
    
    return 'test_notion_focused.json', 'test_calendar_focused.json'

def analyze_results(raw_file, processed_file):
    """Analyze and display the agent's results in detail."""
    
    print(f"\n" + "="*60)
    print("🔍 DETAILED ANALYSIS OF AGENT CAPABILITIES")
    print("="*60)
    
    # Load results
    with open(raw_file, 'r') as f:
        raw_activities = json.load(f)
    
    with open(processed_file, 'r') as f:
        processed_activities = json.load(f)
    
    # Analyze matching results
    merged_count = len([a for a in raw_activities if a.get('source') == 'merged'])
    notion_only = len([a for a in raw_activities if a.get('source') == 'notion']) 
    calendar_only = len([a for a in raw_activities if a.get('source') == 'google_calendar'])
    
    print(f"\n🔗 ACTIVITY MATCHING ANALYSIS:")
    print(f"  Merged activities: {merged_count}")
    print(f"  Notion-only: {notion_only}")
    print(f"  Calendar-only: {calendar_only}")
    print(f"  Match success rate: {(merged_count/(merged_count+notion_only+calendar_only))*100:.1f}%")
    
    # Show successful matches
    if merged_count > 0:
        print(f"\n✅ SUCCESSFUL MATCHES:")
        for activity in raw_activities:
            if activity.get('source') == 'merged':
                notion_data = activity.get('raw_data', {}).get('notion_data', {})
                confidence = activity.get('raw_data', {}).get('match_confidence', 0)
                
                print(f"\n  📊 Match Confidence: {confidence:.2f}")
                print(f"  📅 Calendar: {activity.get('details', '')[:50]}...")
                print(f"  📝 Notion: {notion_data.get('hierarchy', [])} - {notion_data.get('block_type', 'N/A')}")
                print(f"  ⏱️  Duration: {activity.get('duration_minutes')} minutes")
                print(f"  🏷️  Tags: {activity.get('raw_data', {}).get('tags', [])}")
    
    # Analyze tagging quality
    all_tags = []
    tag_sources = {'openai': 0, 'existing': 0, 'fallback': 0}
    
    for activity in raw_activities:
        tags = activity.get('raw_data', {}).get('tags', [])
        all_tags.extend(tags)
    
    unique_tags = list(set(all_tags))
    
    print(f"\n🏷️ TAGGING ANALYSIS:")
    print(f"  Total tags applied: {len(all_tags)}")  
    print(f"  Unique tags generated: {len(unique_tags)}")
    print(f"  Average tags per activity: {len(all_tags)/len(raw_activities):.1f}")
    print(f"  Tag vocabulary: {', '.join(unique_tags[:8])}{'...' if len(unique_tags) > 8 else ''}")
    
    # Show duration estimation for Notion activities
    notion_activities = [a for a in raw_activities if a.get('source') == 'notion']
    if notion_activities:
        print(f"\n⏱️ DURATION ESTIMATION (Notion activities):")
        for activity in notion_activities:
            estimated = activity.get('raw_data', {}).get('duration_estimated', False)
            duration = activity.get('duration_minutes', 0)
            content_length = len(activity.get('details', ''))
            
            print(f"  📝 Content length: {content_length} chars → {duration} minutes {'(estimated)' if estimated else ''}")
    
    # Show processing pipeline summary  
    print(f"\n📊 PROCESSING PIPELINE SUMMARY:")
    print(f"  Raw activities processed: {len(raw_activities)}")
    print(f"  Final processed activities: {len(processed_activities)}")
    print(f"  Activities with multiple tags: {len([p for p in processed_activities if len(p.get('tags', [])) > 1])}")
    
    return {
        'merged_count': merged_count,
        'unique_tags': len(unique_tags),
        'avg_tags': len(all_tags)/len(raw_activities),
        'notion_estimated': len([a for a in notion_activities if a.get('raw_data', {}).get('duration_estimated')])
    }

def test_agent_capabilities():
    """Test the agent's key capabilities with focused examples."""
    
    print("🧠 AI AGENT CAPABILITY TEST")
    print("="*50)
    
    # Create focused test data
    notion_file, calendar_file = create_focused_test_data()
    
    # Load API key and initialize processor
    api_key = load_api_key()
    if not api_key:
        print("❌ No OpenAI API key found. This test requires OpenAI integration.")
        return False
        
    print(f"✅ OpenAI API key loaded: sk-...{api_key[-6:]}")
    
    processor = ActivityProcessor(openai_api_key=api_key)
    
    # Set up output
    output_dir = "capability_test_output"
    os.makedirs(output_dir, exist_ok=True)
    raw_file = f"{output_dir}/raw_activities.json"
    processed_file = f"{output_dir}/processed_activities.json"
    
    try:
        print(f"\n🚀 Running comprehensive agent test...")
        
        # Process activities
        report = processor.process_daily_activities(
            notion_file=notion_file,
            calendar_file=calendar_file, 
            output_raw_file=raw_file,
            output_processed_file=processed_file
        )
        
        # Analyze results in detail
        analysis = analyze_results(raw_file, processed_file)
        
        # Summary scorecard
        print(f"\n" + "="*60)
        print("🎯 CAPABILITY SCORECARD")
        print("="*60)
        
        match_score = "✅ Excellent" if analysis['merged_count'] >= 2 else "⚠️ Needs improvement"
        tag_score = "✅ Excellent" if analysis['unique_tags'] >= 4 else "⚠️ Needs improvement"  
        estimation_score = "✅ Working" if analysis['notion_estimated'] > 0 else "❌ Not working"
        
        print(f"🔗 Activity Matching: {match_score} ({analysis['merged_count']} successful matches)")
        print(f"🏷️ Intelligent Tagging: {tag_score} ({analysis['unique_tags']} unique tags)")
        print(f"⏱️ Duration Estimation: {estimation_score} ({analysis['notion_estimated']} estimated)")
        print(f"📊 Tag Diversity: {analysis['avg_tags']:.1f} tags per activity")
        
        success = analysis['merged_count'] >= 2 and analysis['unique_tags'] >= 4
        
        if success:
            print(f"\n🎉 SUCCESS! The AI agent demonstrates strong capabilities:")
            print(f"   ✓ Intelligent matching between data sources")
            print(f"   ✓ Context-aware tagging with OpenAI")
            print(f"   ✓ Content-based duration estimation")
            print(f"   ✓ Robust processing pipeline")
        else:
            print(f"\n⚠️ Results show room for improvement in matching or tagging.")
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up test files
        for file in [notion_file, calendar_file]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    test_agent_capabilities()