#!/usr/bin/env python3
"""
Test script for hierarchical tagging system validation.

Demonstrates the three-layer tagging approach on real calendar activities.
Following REGULATION.md principles with atomic functionality.
"""

import sys
import os
import json
from typing import List, Dict, Any

# Add src/backend to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'src', 'backend')
sys.path.append(backend_path)

from agent.tools.tag_generator import TagGenerator
from agent.core.models import RawActivity
from database.access.models import RawActivityDAO


def load_sample_activities(limit: int = 20) -> List[RawActivity]:
    """Load sample activities from database for testing."""
    try:
        raw_dao = RawActivityDAO()
        db_activities = raw_dao.get_recent_activities(limit=limit)
        
        activities = []
        for db_activity in db_activities:
            activity = RawActivity(
                date=db_activity.date,
                time=db_activity.time or "00:00",
                duration_minutes=db_activity.duration_minutes or 30,
                details=db_activity.details,
                source=db_activity.source,
                orig_link=db_activity.orig_link or ""
            )
            activities.append(activity)
        
        return activities
    except Exception as e:
        print(f"Error loading activities from database: {e}")
        return create_test_activities()


def create_test_activities() -> List[RawActivity]:
    """Create test activities for validation."""
    return [
        RawActivity(
            date="2025-09-07",
            time="09:00",
            duration_minutes=60,
            details="bytediff debugging session and code review",
            source="google_calendar",
            orig_link=""
        ),
        RawActivity(
            date="2025-09-07", 
            time="14:00",
            duration_minutes=90,
            details="smartHistory tagging system development",
            source="google_calendar",
            orig_link=""
        ),
        RawActivity(
            date="2025-09-07",
            time="19:00", 
            duration_minutes=120,
            details="Web3 blockchain fundamentals study session",
            source="notion",
            orig_link=""
        ),
        RawActivity(
            date="2025-09-07",
            time="12:30",
            duration_minutes=30,
            details="午休时间 afternoon rest break",
            source="notion",
            orig_link=""
        ),
        RawActivity(
            date="2025-09-07",
            time="18:00",
            duration_minutes=90,
            details="健身房 upper body strength training",
            source="google_calendar", 
            orig_link=""
        ),
        RawActivity(
            date="2025-09-07",
            time="10:00",
            duration_minutes=45,
            details="Weekly team meeting and project sync",
            source="google_calendar",
            orig_link=""
        ),
        RawActivity(
            date="2025-09-07",
            time="16:00",
            duration_minutes=60,
            details="CFA level 1 ethics preparation",
            source="notion",
            orig_link=""
        )
    ]


def print_hierarchical_result(activity: RawActivity, result: Dict[str, Any]) -> None:
    """Print formatted hierarchical tagging result."""
    print(f"\n📅 Activity: {activity.details}")
    print(f"   Source: {activity.source} | Duration: {activity.duration_minutes}min")
    
    tags = result["hierarchical_tags"]
    scores = tags["confidence_scores"]
    
    print(f"   🏷️  Nature: {tags['nature']} (confidence: {scores['nature']:.2f})")
    
    if tags["subject"]:
        print(f"   📂 Subject: {tags['subject']} (confidence: {scores['subject']:.2f})")
    else:
        print(f"   📂 Subject: None")
    
    if tags["project"]:
        print(f"   🎯 Project: {tags['project']} (confidence: {scores['project']:.2f})")
    else:
        print(f"   🎯 Project: None")


def print_summary_stats(summary: Dict[str, Any]) -> None:
    """Print hierarchical tagging summary statistics."""
    print(f"\n📊 HIERARCHICAL TAGGING SUMMARY")
    print(f"=" * 50)
    print(f"Total Activities: {summary['total_activities']}")
    
    # Coverage Statistics
    coverage = summary["coverage_stats"]
    print(f"\n📈 Coverage Statistics:")
    print(f"   Nature Coverage:  {coverage['nature_coverage']:.1f}%")
    print(f"   Subject Coverage: {coverage['subject_coverage']:.1f}%")
    print(f"   Project Coverage: {coverage['project_coverage']:.1f}%")
    
    # Confidence Statistics
    conf_stats = summary["confidence_stats"]
    print(f"\n🎯 Average Confidence Scores:")
    print(f"   Nature:  {conf_stats['avg_nature_confidence']:.2f}")
    print(f"   Subject: {conf_stats['avg_subject_confidence']:.2f}")
    print(f"   Project: {conf_stats['avg_project_confidence']:.2f}")
    
    # Distribution Statistics
    print(f"\n🏷️  Nature Distribution:")
    for nature, count in summary["nature_distribution"].items():
        print(f"   {nature}: {count}")
    
    if summary["subject_distribution"]:
        print(f"\n📂 Subject Distribution:")
        for subject, count in summary["subject_distribution"].items():
            print(f"   {subject}: {count}")
    
    if summary["project_distribution"]:
        print(f"\n🎯 Project Distribution:")
        for project, count in summary["project_distribution"].items():
            print(f"   {project}: {count}")


def test_hierarchical_tagging_system():
    """Main test function for hierarchical tagging system."""
    print("🚀 Testing Hierarchical Tagging System")
    print("=" * 50)
    
    # Initialize TagGenerator
    try:
        tag_generator = TagGenerator()
        print("✅ TagGenerator initialized successfully")
        print(f"   Loaded {len(tag_generator.taxonomy_tags)} taxonomy tags")
        print(f"   Hierarchical taxonomy: {'✅' if tag_generator.hierarchical_taxonomy else '❌'}")
    except Exception as e:
        print(f"❌ Error initializing TagGenerator: {e}")
        return
    
    # Load test activities
    activities = load_sample_activities(limit=10)
    print(f"📚 Loaded {len(activities)} activities for testing")
    
    # Generate hierarchical tags for batch
    try:
        results = tag_generator.generate_hierarchical_tags_batch(activities)
        print("✅ Batch hierarchical tagging completed")
    except Exception as e:
        print(f"❌ Error in batch tagging: {e}")
        return
    
    # Print individual results
    print(f"\n🏷️  INDIVIDUAL TAGGING RESULTS")
    print("=" * 50)
    for i, result in enumerate(results[:7]):  # Show first 7 results
        activity_text = result["activity_text"]
        activity = activities[i]
        print_hierarchical_result(activity, result)
    
    # Generate and print summary
    try:
        summary = tag_generator.get_hierarchical_summary(results)
        print_summary_stats(summary)
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
        return
    
    print(f"\n✅ Hierarchical tagging test completed successfully!")
    print(f"🎉 Three-layer system working: Nature → Subject → Project")


if __name__ == "__main__":
    test_hierarchical_tagging_system()