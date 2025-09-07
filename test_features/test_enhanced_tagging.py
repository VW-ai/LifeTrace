#!/usr/bin/env python3
"""
Test script for the enhanced AI-native tagging system with taxonomy-first approach.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'backend'))

from agent.tools.tag_generator import TagGenerator
from agent.core.models import RawActivity


def test_enhanced_tagging():
    """Test the enhanced tagging system with sample activities."""
    
    print("=== Testing Enhanced AI-Native Tagging System ===\n")
    
    # Initialize the enhanced tag generator
    tag_generator = TagGenerator()
    
    # Sample activities with various patterns from the proposal
    test_activities = [
        RawActivity(
            date="2025-09-07",
            time="14:30",
            duration_minutes=90,
            details="bytediff debug CI/CD pipeline issues",
            source="google_calendar",
            orig_link=""
        ),
        RawActivity(
            date="2025-09-07",
            time="12:00", 
            duration_minutes=30,
            details="吃午饭 with team members",
            source="notion",
            orig_link=""
        ),
        RawActivity(
            date="2025-09-07",
            time="16:45",
            duration_minutes=15,
            details="厕所 break and quick rest",
            source="notion", 
            orig_link=""
        ),
        RawActivity(
            date="2025-09-07",
            time="10:00",
            duration_minutes=60,
            details="smartHistory开发 frontend dashboard improvements",
            source="google_calendar",
            orig_link=""
        ),
        RawActivity(
            date="2025-09-07", 
            time="09:00",
            duration_minutes=45,
            details="周会 discussing sprint planning and goals",
            source="google_calendar",
            orig_link=""
        )
    ]
    
    print("Testing taxonomy-first tagging on sample activities:\n")
    
    for i, activity in enumerate(test_activities, 1):
        print(f"Activity {i}: {activity.details}")
        print(f"Source: {activity.source} | Duration: {activity.duration_minutes}min")
        
        # Test regular tagging
        tags = tag_generator.generate_tags_for_activity(activity)
        print(f"Generated tags: {tags}")
        
        # Test confidence-based tagging
        tags_with_conf = tag_generator.generate_tags_with_confidence_for_activity(activity)
        print(f"Tags with confidence: {tags_with_conf}")
        
        # Test synonym matching
        synonym_matches = tag_generator.find_matching_taxonomy_tags(activity.details)
        print(f"Synonym matches: {synonym_matches}")
        
        print("-" * 60)
    
    print("\n=== Testing Taxonomy and Synonym Loading ===")
    print(f"Loaded taxonomy categories: {len(tag_generator.taxonomy_tags)}")
    print(f"Available categories: {', '.join(tag_generator.taxonomy_tags)}")
    
    print(f"\nSynonym mappings available: {len(tag_generator.synonyms.get('synonyms', {}))}")
    print(f"Personal shortcuts: {len(tag_generator.synonyms.get('personal_shortcuts', {}))}")
    
    print("\n=== Test Completed Successfully ===")


if __name__ == "__main__":
    test_enhanced_tagging()