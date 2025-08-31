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
    """Test the agent with basic functionality (database-first)."""
    print("=== Testing SmartHistory AI Agent (Database-First) ===\n")
    
    # Initialize processor without API key (uses fallback functionality)
    processor = ActivityProcessor(openai_api_key=None)
    
    # Check if database has data
    try:
        from src.backend.database import RawActivityDAO
        activities = RawActivityDAO.get_all()
        
        if not activities:
            print("❌ No raw activities found in database.")
            print("Run the parsers first:")
            print("  python run_parsers.py")
            return False
        
        print(f"✅ Found {len(activities)} raw activities in database")
        
        # Show data sources
        sources = {}
        for activity in activities:
            sources[activity.source] = sources.get(activity.source, 0) + 1
        
        for source, count in sources.items():
            print(f"  - {source}: {count} activities")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("Make sure database is initialized and parsers have run.")
        return False
    
    # Create output directory
    output_dir = "agent_test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n🚀 Running agent (database-first with fallback tag generation)...")
    
    try:
        # Run the agent using database
        report = processor.process_daily_activities(
            use_database=True,  # Use database-first approach
            output_raw_file=f"{output_dir}/raw_activities.json",  # Optional legacy output
            output_processed_file=f"{output_dir}/processed_activities.json"  # Optional legacy output
        )
        
        print(f"\n✅ Agent completed successfully!")
        print(f"📊 Results:")
        print(f"  - Status: {report['status']}")
        print(f"  - Raw activities: {report['processed_counts']['raw_activities']}")
        print(f"  - Processed activities: {report['processed_counts']['processed_activities']}")
        print(f"  - Unique tags: {report['tag_analysis']['total_unique_tags']}")
        print(f"  - Merged activities: {report['matching_analysis']['merged_activities']}")
        print(f"  - Merge rate: {report['matching_analysis']['merge_rate']}%")
        
        print(f"\n💾 Results saved to database and optional JSON files in: {output_dir}/")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_insights():
    """Test insights generation (database-first)."""
    print(f"\n=== Testing Insights Generation (Database-First) ===")
    
    # Try to load processed activities from database first
    try:
        from src.backend.database import ProcessedActivityDAO
        processed_activities_db = ProcessedActivityDAO.get_all()
        
        if not processed_activities_db:
            print("❌ No processed activities found in database. Run basic test first.")
            return False
        
        print(f"✅ Found {len(processed_activities_db)} processed activities in database")
        
        # Convert database models to agent models for insights
        from src.backend.agent.core.models import ProcessedActivity
        activities = []
        for activity_db in processed_activities_db:
            # Get tags for this activity
            from src.backend.database import ActivityTagDAO, TagDAO
            activity_tags = ActivityTagDAO.get_by_processed_activity_id(activity_db.id)
            tag_names = []
            for at in activity_tags:
                tag = TagDAO.get_by_id(at.tag_id)
                if tag:
                    tag_names.append(tag.name)
            
            processed_activity = ProcessedActivity(
                date=activity_db.date,
                time=activity_db.time,
                raw_activity_ids=activity_db.raw_activity_ids,
                tags=tag_names,
                total_duration_minutes=activity_db.total_duration_minutes,
                combined_details=activity_db.combined_details,
                sources=activity_db.sources
            )
            activities.append(processed_activity)
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("Falling back to JSON file approach...")
        
        # Fallback to JSON file
        processed_file = "agent_test_output/processed_activities.json"
        if not os.path.exists(processed_file):
            print("❌ No processed activities found in database or files.")
            return False
        
        try:
            from src.backend.agent.core.models import deserialize_processed_activities
            activities = deserialize_processed_activities(processed_file)
        except Exception as e2:
            print(f"❌ Error loading from file: {e2}")
            return False
    
    processor = ActivityProcessor()
    
    try:
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