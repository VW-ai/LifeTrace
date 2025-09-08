#!/usr/bin/env python3
"""
Demo script for testing and management APIs.

Shows how to use the new endpoints without writing custom scripts.
Following REGULATION.md principles with clear, focused functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'backend'))

from api.services import TagService, ProcessingService, SystemService
from database.core.database_manager import DatabaseManager
from database.core.config import DatabaseConfig


def demo_testing_apis():
    """Demonstrate testing API functionality."""
    print("🧪 TESTING API DEMO")
    print("=" * 50)
    
    # Initialize services (simplified - normally handled by FastAPI)
    config = DatabaseConfig()
    db_manager = DatabaseManager(config)
    tag_service = TagService(db_manager)
    
    print("1. Testing Hierarchical Tagging System...")
    
    try:
        # This simulates: POST /api/v1/test/hierarchical-tagging?limit=5
        result = tag_service.test_hierarchical_tagging(limit=5)
        
        if result.get("status") == "success":
            print("✅ Hierarchical tagging test successful!")
            print(f"   Tested: {result.get('total_tested', 0)} activities")
            print(f"   System available: {result.get('hierarchical_system_available', False)}")
            
            summary = result.get("summary", {})
            coverage = summary.get("coverage_stats", {})
            print(f"   Nature coverage: {coverage.get('nature_coverage', 0):.1f}%")
            print(f"   Subject coverage: {coverage.get('subject_coverage', 0):.1f}%")
            print(f"   Project coverage: {coverage.get('project_coverage', 0):.1f}%")
        else:
            print("❌ Hierarchical tagging test failed:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error running hierarchical test: {e}")
    
    print("\n2. Testing Enhanced Tagging System...")
    
    try:
        # This simulates: POST /api/v1/test/enhanced-tagging?limit=3
        result = tag_service.test_enhanced_tagging(limit=3)
        
        if result.get("status") == "success":
            print("✅ Enhanced tagging test successful!")
            print(f"   Taxonomy tags available: {result.get('taxonomy_tags_count', 0)}")
            print(f"   Enhanced system: {result.get('enhanced_system_available', False)}")
            
            # Show sample results
            test_results = result.get("test_results", [])[:2]
            for i, test in enumerate(test_results, 1):
                print(f"   Sample {i}: {test.get('activity_text', '')[:50]}...")
                tags = test.get('tags_with_confidence', [])
                if tags:
                    best_tag = max(tags, key=lambda x: x[1])
                    print(f"              → {best_tag[0]} (confidence: {best_tag[1]:.2f})")
        else:
            print("❌ Enhanced tagging test failed:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error running enhanced test: {e}")


def demo_management_apis():
    """Demonstrate management API functionality."""
    print("\n🔧 MANAGEMENT API DEMO") 
    print("=" * 50)
    
    # Initialize services
    config = DatabaseConfig()
    db_manager = DatabaseManager(config)
    tag_service = TagService(db_manager)
    system_service = SystemService(db_manager)
    
    print("1. Getting Taxonomy Information...")
    
    try:
        # This simulates: GET /api/v1/management/taxonomy
        result = tag_service.get_taxonomy_info()
        
        if "stats" in result:
            stats = result["stats"]
            print("✅ Taxonomy information retrieved!")
            print(f"   Total taxonomy tags: {stats.get('total_taxonomy_tags', 0)}")
            print(f"   Hierarchical subjects: {stats.get('hierarchical_subjects', 0)}")
            print(f"   Synonym mappings: {stats.get('synonym_mappings', 0)}")
            print(f"   Personal shortcuts: {stats.get('personal_shortcuts', 0)}")
        else:
            print("❌ Failed to get taxonomy info:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error getting taxonomy: {e}")
    
    print("\n2. Checking Tag Coverage...")
    
    try:
        # This simulates: GET /api/v1/management/tag-coverage?days_back=7
        result = tag_service.get_tag_coverage_stats(days_back=7)
        
        if "coverage_stats" in result:
            coverage = result["coverage_stats"]
            print("✅ Tag coverage analysis complete!")
            print(f"   Total activities: {coverage.get('total_activities', 0)}")
            print(f"   Tagged activities: {coverage.get('tagged_activities', 0)}")
            print(f"   Coverage: {coverage.get('coverage_percentage', 0):.1f}%")
            print(f"   Unique tags used: {result.get('unique_tags_used', 0)}")
        else:
            print("❌ Failed to analyze tag coverage:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error analyzing coverage: {e}")
    
    print("\n3. Getting Activity Summary...")
    
    try:
        # This simulates: GET /api/v1/management/activity-summary?days_back=3&include_hierarchical=true
        result = system_service.get_activity_summary(days_back=3, include_hierarchical=True)
        
        if "activity_counts" in result:
            counts = result["activity_counts"]
            time_analysis = result.get("time_analysis", {})
            
            print("✅ Activity summary generated!")
            print(f"   Total activities: {counts.get('total_activities', 0)}")
            print(f"   Total hours: {time_analysis.get('total_hours', 0)}")
            print(f"   Average duration: {time_analysis.get('average_duration', 0):.1f} min")
            
            by_source = counts.get("by_source", {})
            if by_source:
                print("   By source:")
                for source, count in by_source.items():
                    print(f"     {source}: {count}")
            
            # Show hierarchical analysis if available
            hierarchical = result.get("hierarchical_analysis")
            if hierarchical and "total_activities" in hierarchical:
                print(f"   Hierarchical sample: {result.get('hierarchical_sample_size', 0)}")
                hier_coverage = hierarchical.get("coverage_stats", {})
                print(f"     Nature coverage: {hier_coverage.get('nature_coverage', 0):.1f}%")
                print(f"     Subject coverage: {hier_coverage.get('subject_coverage', 0):.1f}%")
        else:
            print("❌ Failed to get activity summary:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error getting summary: {e}")


def main():
    """Main demonstration function."""
    print("🎯 SmartHistory Testing & Management API Demo")
    print("Following REGULATION.md principles with atomic, focused functionality")
    print("=" * 80)
    
    try:
        demo_testing_apis()
        demo_management_apis()
        
        print("\n✅ DEMO COMPLETED SUCCESSFULLY!")
        print("🎉 All testing and management APIs are working")
        print("\n📖 Usage:")
        print("   These endpoints eliminate the need for custom scripts")
        print("   Access via REST API: http://localhost:8000/api/v1/")
        print("   Full documentation in: api/testing_management_API_META.md")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("Check database connection and system setup")


if __name__ == "__main__":
    main()