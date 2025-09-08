#!/usr/bin/env python3
"""
Regenerate tags for calendar events from the last 3 months using enhanced AI-native tagging system.
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'backend'))

from agent.tools.tag_generator import TagGenerator
from agent.core.models import RawActivity
from database.access.models import (
    RawActivityDAO, ProcessedActivityDAO, TagDAO, ActivityTagDAO, 
    RawActivityDB, ProcessedActivityDB, TagDB, ActivityTagDB
)


def get_all_calendar_activities() -> List[RawActivity]:
    """Get all calendar activities from the database."""
    print("Retrieving all calendar activities from database...")
    
    # Get all calendar activities from database
    raw_activities_db = RawActivityDAO.get_by_date_range(
        '2025-01-01',  # Start of year to get all recent data  
        '2025-12-31',  # End of year
        source='google_calendar'
    )
    
    # Convert to agent RawActivity format
    calendar_activities = []
    for db_activity in raw_activities_db:
        raw_activity = RawActivity(
            date=db_activity.date,
            time=db_activity.time or "",
            duration_minutes=db_activity.duration_minutes,
            details=db_activity.details,
            source=db_activity.source,
            orig_link=db_activity.orig_link
        )
        # Store database ID for reference
        raw_activity.id = db_activity.id
        calendar_activities.append(raw_activity)
    
    print(f"Found {len(calendar_activities)} calendar activities in the specified date range")
    return calendar_activities


def generate_personalized_taxonomy(activities: List[RawActivity]) -> None:
    """Generate personalized taxonomy from user's activity data."""
    print("\n=== Analyzing User Data to Generate Personalized Taxonomy ===")
    
    tag_generator = TagGenerator()
    
    # Generate personalized taxonomy and synonyms
    tag_generator.update_taxonomy_from_data(activities)
    
    print("✅ Personalized taxonomy and synonyms generated successfully!")
    return tag_generator


def regenerate_activity_tags(activities: List[RawActivity], tag_generator: TagGenerator) -> Dict[str, Any]:
    """Regenerate tags for all activities using enhanced system."""
    print(f"\n=== Regenerating Tags for {len(activities)} Activities ===")
    
    results = {
        "total_activities": len(activities),
        "successfully_tagged": 0,
        "high_confidence_tags": 0,
        "low_confidence_tags": 0,
        "tag_distribution": {},
        "confidence_scores": [],
        "failed_activities": []
    }
    
    for i, activity in enumerate(activities):
        try:
            print(f"Processing activity {i+1}/{len(activities)}: {activity.details[:50]}...")
            
            # Generate tags with confidence scores
            tags_with_confidence = tag_generator.generate_tags_with_confidence_for_activity(activity)
            
            if tags_with_confidence:
                results["successfully_tagged"] += 1
                
                # Find or create processed activity for this raw activity
                # First search for existing processed activity that includes this raw activity
                processed_activity = None
                
                # For simplicity, create a new processed activity for each raw activity
                # In production, you'd want to implement better matching logic
                new_processed = ProcessedActivityDB(
                    date=activity.date,
                    time=activity.time,
                    total_duration_minutes=activity.duration_minutes,
                    combined_details=activity.details,
                    raw_activity_ids=[activity.id],
                    sources=[activity.source]
                )
                
                processed_activity_id = ProcessedActivityDAO.create(new_processed)
                
                # Add new tags with confidence scores
                for tag_name, confidence in tags_with_confidence:
                    # Get or create tag
                    existing_tag = TagDAO.get_by_name(tag_name)
                    if not existing_tag:
                        new_tag = TagDB(
                            name=tag_name,
                            description=f"Auto-generated tag for {tag_name}",
                            usage_count=0
                        )
                        tag_id = TagDAO.create(new_tag)
                    else:
                        tag_id = existing_tag.id
                    
                    # Create activity-tag relationship with confidence
                    activity_tag = ActivityTagDB(
                        processed_activity_id=processed_activity_id,
                        tag_id=tag_id,
                        confidence_score=confidence
                    )
                    ActivityTagDAO.create(activity_tag)
                    
                    # Track results
                    if confidence >= 0.7:
                        results["high_confidence_tags"] += 1
                    elif confidence < 0.5:
                        results["low_confidence_tags"] += 1
                    
                    results["confidence_scores"].append(confidence)
                    
                    # Update tag distribution
                    if tag_name not in results["tag_distribution"]:
                        results["tag_distribution"][tag_name] = 0
                    results["tag_distribution"][tag_name] += 1
                
                print(f"  ✅ Tagged with {len(tags_with_confidence)} tags: {[f'{tag}({conf:.2f})' for tag, conf in tags_with_confidence]}")
            
        except Exception as e:
            print(f"  ❌ Failed to process activity {getattr(activity, 'id', 'unknown')}: {str(e)}")
            results["failed_activities"].append({
                "id": getattr(activity, 'id', 'unknown'),
                "details": activity.details,
                "error": str(e)
            })
    
    return results


def print_regeneration_summary(results: Dict[str, Any]) -> None:
    """Print a comprehensive summary of the tag regeneration results."""
    print("\n" + "="*60)
    print("🎯 TAG REGENERATION SUMMARY")
    print("="*60)
    
    print(f"📊 **Processing Results:**")
    print(f"   • Total Activities Processed: {results['total_activities']}")
    print(f"   • Successfully Tagged: {results['successfully_tagged']}")
    print(f"   • Failed: {len(results['failed_activities'])}")
    
    if results['confidence_scores']:
        avg_confidence = sum(results['confidence_scores']) / len(results['confidence_scores'])
        print(f"\n🎯 **Confidence Analysis:**")
        print(f"   • Average Confidence: {avg_confidence:.3f}")
        print(f"   • High Confidence Tags (≥0.7): {results['high_confidence_tags']}")
        print(f"   • Low Confidence Tags (<0.5): {results['low_confidence_tags']} (flagged for review)")
        
        high_conf_percentage = (results['high_confidence_tags'] / len(results['confidence_scores'])) * 100
        print(f"   • High Confidence Rate: {high_conf_percentage:.1f}%")
    
    print(f"\n🏷️ **Tag Distribution:**")
    sorted_tags = sorted(results['tag_distribution'].items(), key=lambda x: x[1], reverse=True)
    for tag, count in sorted_tags[:10]:  # Show top 10 tags
        percentage = (count / results['successfully_tagged']) * 100
        print(f"   • {tag}: {count} activities ({percentage:.1f}%)")
    
    if len(sorted_tags) > 10:
        print(f"   ... and {len(sorted_tags) - 10} more tags")
    
    if results['failed_activities']:
        print(f"\n❌ **Failed Activities:**")
        for failed in results['failed_activities'][:5]:  # Show first 5 failures
            print(f"   • ID {failed['id']}: {failed['details'][:50]}... - {failed['error']}")
        if len(results['failed_activities']) > 5:
            print(f"   ... and {len(results['failed_activities']) - 5} more failures")
    
    print("\n✅ **Tag regeneration completed successfully!**")


def main():
    """Main execution function."""
    print("🚀 Starting Enhanced AI-Native Tag Regeneration for Calendar Events")
    print("="*70)
    
    try:
        # Step 1: Get all calendar activities from database
        activities = get_all_calendar_activities()
        
        if not activities:
            print("❌ No calendar activities found in the specified date range.")
            return
        
        # Step 2: Generate personalized taxonomy from user data
        tag_generator = generate_personalized_taxonomy(activities)
        
        # Step 3: Regenerate tags for all activities
        results = regenerate_activity_tags(activities, tag_generator)
        
        # Step 4: Print comprehensive summary
        print_regeneration_summary(results)
        
        # Step 5: Save results to file
        results_file = f"tag_regeneration_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            # Convert any non-serializable objects to strings
            serializable_results = json.loads(json.dumps(results, default=str))
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
    except Exception as e:
        print(f"❌ Error during tag regeneration: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()