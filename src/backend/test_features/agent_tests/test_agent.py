#!/usr/bin/env python3
"""
Quick test script for the AI Agent
"""
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from src.backend.agent import ActivityProcessor

def test_agent_basic():
    """Test the agent with basic functionality (without OpenAI API)."""
    print("=== Testing SmartHistory AI Agent ===\n")
    
    # Initialize processor without API key (uses fallback functionality)
    processor = ActivityProcessor(openai_api_key=None)
    
    # Check if input files exist
    notion_file = "parsed_notion_content.json"
    calendar_file = "parsed_google_calendar_events.json"
    
    if not os.path.exists(notion_file):
        print(f"❌ Missing: {notion_file}")
        print("Run the Notion parser first:")
        print("  python -m src.backend.notion_parser.parser notion_content.json")
        return
    
    if not os.path.exists(calendar_file):
        print(f"❌ Missing: {calendar_file}")
        print("This should exist from your previous parsing.")
        return
    
    print(f"✅ Found input files:")
    print(f"  - {notion_file}")
    print(f"  - {calendar_file}")
    
    # Create output directory
    output_dir = "agent_test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n🚀 Running agent (using fallback tag generation)...")
    
    try:
        # Run the agent
        report = processor.process_daily_activities(
            notion_file=notion_file,
            calendar_file=calendar_file,
            output_raw_file=f"{output_dir}/raw_activities.json",
            output_processed_file=f"{output_dir}/processed_activities.json"
        )
        
        print(f"\n✅ Agent completed successfully!")
        print(f"📊 Results:")
        print(f"  - Status: {report['status']}")
        print(f"  - Raw activities: {report['processed_counts']['raw_activities']}")
        print(f"  - Processed activities: {report['processed_counts']['processed_activities']}")
        print(f"  - Unique tags: {report['tag_analysis']['total_unique_tags']}")
        print(f"  - Merged activities: {report['matching_analysis']['merged_activities']}")
        print(f"  - Merge rate: {report['matching_analysis']['merge_rate']}%")
        
        print(f"\n📁 Output files created in: {output_dir}/")
        print(f"  - raw_activities.json (tagged activities)")
        print(f"  - processed_activities.json (final processed activities)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_insights():
    """Test insights generation."""
    print(f"\n=== Testing Insights Generation ===")
    
    processed_file = "agent_test_output/processed_activities.json"
    if not os.path.exists(processed_file):
        print("❌ No processed activities found. Run basic test first.")
        return
    
    processor = ActivityProcessor()
    
    try:
        from src.backend.agent.models import deserialize_processed_activities
        activities = deserialize_processed_activities(processed_file)
        
        insights = processor.get_activity_insights(activities)
        
        print(f"✅ Insights generated:")
        print(f"  - Total tracked time: {insights['total_tracked_hours']} hours")
        print(f"  - Activity count: {insights['activity_count']}")
        print(f"  - Unique activity types: {insights['unique_tags']}")
        
        print(f"\n🏆 Top activities by time:")
        for activity in insights['top_5_activities'][:3]:
            print(f"    {activity['tag']}: {activity['hours']} hours")
            
        return True
        
    except Exception as e:
        print(f"❌ Error generating insights: {e}")
        return False

if __name__ == "__main__":
    print("SmartHistory AI Agent Test Script")
    print("=" * 50)
    
    # Test basic functionality
    if test_agent_basic():
        # Test insights if basic test succeeded
        test_insights()
    
    print(f"\n" + "=" * 50)
    print("Test complete!")
    print(f"\nTo run with OpenAI API:")
    print(f"  1. Set OPENAI_API_KEY environment variable")
    print(f"  2. Re-run the agent for better tag generation")