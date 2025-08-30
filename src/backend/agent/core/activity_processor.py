import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from .data_consumer import DataConsumer
from ..tools.tag_generator import TagGenerator
from .activity_matcher import ActivityMatcher
from .models import RawActivity, ProcessedActivity, serialize_activities, serialize_processed_activities

class ActivityProcessor:
    """Main orchestrator for processing activities from raw data to tagged activities."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the activity processor with all components."""
        self.data_consumer = DataConsumer()
        self.tag_generator = TagGenerator(api_key=openai_api_key)
        self.activity_matcher = ActivityMatcher()
        
        # Configuration
        self.enable_system_tag_regeneration = True
        
    def process_daily_activities(self, 
                               notion_file: str = 'parsed_notion_content.json',
                               calendar_file: str = 'parsed_google_calendar_events.json',
                               output_raw_file: str = 'raw_activities.json',
                               output_processed_file: str = 'processed_activities.json') -> Dict[str, Any]:
        """Main entry point for daily activity processing."""
        
        print("=== Starting Daily Activity Processing ===")
        
        # Step 1: Load existing tags
        self.tag_generator.load_existing_tags()
        
        # Step 2: Update data consumer file paths
        self.data_consumer.notion_file = notion_file
        self.data_consumer.calendar_file = calendar_file
        
        # Step 3: Load and convert raw data
        print("\n1. Loading raw data...")
        raw_activities = self.data_consumer.load_all_raw_activities()
        
        if not raw_activities:
            print("No activities found to process")
            return {'status': 'no_data', 'processed_count': 0}
        
        # Step 4: Match and merge activities from different sources
        print("\n2. Matching activities across sources...")
        matched_activities = self.activity_matcher.match_activities(raw_activities)
        matching_stats = self.activity_matcher.get_matching_statistics(matched_activities)
        
        # Step 5: Generate summary
        summary = self.data_consumer.get_activities_summary(matched_activities)
        print(f"\nData Summary:")
        print(f"  Total activities: {summary['total']}")
        print(f"  By source: {summary['by_source']}")
        print(f"  Date range: {summary['date_range']}")
        print(f"  Total duration: {summary['total_duration_hours']} hours")
        print(f"\nMatching Summary:")
        print(f"  Merged activities: {matching_stats['merged_activities']}")
        print(f"  Merge rate: {matching_stats['merge_rate']}%")
        
        # Step 6: Check if system-wide tag regeneration is needed
        if (self.enable_system_tag_regeneration and 
            self.tag_generator.should_regenerate_system_tags(summary['total'])):
            print("\n3. System-wide tag regeneration needed...")
            system_tags = self.tag_generator.regenerate_system_tags(matched_activities)
        
        # Step 7: Generate tags for each activity
        print("\n4. Generating tags for activities...")
        tagged_activities = []
        
        for i, activity in enumerate(matched_activities):
            try:
                tags = self.tag_generator.generate_tags_for_activity(activity)
                
                # Create a copy with tags added to raw_data for tracking
                tagged_activity = RawActivity(
                    date=activity.date,
                    time=activity.time,
                    duration_minutes=activity.duration_minutes,
                    details=activity.details,
                    source=activity.source,
                    orig_link=activity.orig_link,
                    raw_data={**activity.raw_data, 'tags': tags}
                )
                tagged_activities.append(tagged_activity)
                
                if i % 50 == 0:  # Progress update every 50 items
                    print(f"  Processed {i}/{len(matched_activities)} activities")
                    
            except Exception as e:
                print(f"Error processing activity {i}: {e}")
                continue
        
        print(f"  Tag generation complete: {len(tagged_activities)} activities tagged")
        
        # Step 8: Create processed activities (grouping and consolidation)
        print("\n5. Creating processed activities...")
        processed_activities = self._create_processed_activities(tagged_activities)
        
        # Step 9: Save results
        print("\n6. Saving results...")
        serialize_activities(tagged_activities, output_raw_file)
        serialize_processed_activities(processed_activities, output_processed_file)
        
        # Step 10: Save updated tags
        self.tag_generator.save_tags()
        
        # Generate final report
        report = self._generate_processing_report(tagged_activities, processed_activities, summary, matching_stats)
        
        print("\n=== Processing Complete ===")
        print(f"Raw activities saved: {output_raw_file}")
        print(f"Processed activities saved: {output_processed_file}")
        print(f"Total tags in system: {len(self.tag_generator.existing_tags)}")
        
        return report
    
    def _create_processed_activities(self, raw_activities: List[RawActivity]) -> List[ProcessedActivity]:
        """Group and consolidate raw activities into processed activities."""
        # Group by date and similar activities
        date_groups = {}
        
        for activity in raw_activities:
            date = activity.date
            if date not in date_groups:
                date_groups[date] = []
            date_groups[date].append(activity)
        
        processed_activities = []
        
        for date, activities in date_groups.items():
            # For now, create one processed activity per raw activity
            # Future enhancement: smart grouping by tags and time proximity
            
            for activity in activities:
                tags = activity.raw_data.get('tags', [])
                
                processed_activity = ProcessedActivity(
                    date=activity.date,
                    time=activity.time,
                    raw_activity_ids=[f"{activity.source}_{hash(activity.details)}"],  # Simple ID generation
                    tags=tags,
                    total_duration_minutes=activity.duration_minutes,
                    combined_details=activity.details,
                    sources=[activity.source]
                )
                
                processed_activities.append(processed_activity)
        
        return processed_activities
    
    def _generate_processing_report(self, raw_activities: List[RawActivity], 
                                  processed_activities: List[ProcessedActivity],
                                  original_summary: Dict[str, Any],
                                  matching_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive processing report."""
        
        # Collect tag statistics
        all_tags = []
        for activity in raw_activities:
            tags = activity.raw_data.get('tags', [])
            all_tags.extend(tags)
        
        # Tag frequency analysis
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Most common tags
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Duration by tag
        duration_by_tag = {}
        for activity in raw_activities:
            tags = activity.raw_data.get('tags', [])
            duration = activity.duration_minutes
            
            for tag in tags:
                if tag not in duration_by_tag:
                    duration_by_tag[tag] = 0
                duration_by_tag[tag] += duration
        
        return {
            'status': 'success',
            'processing_timestamp': datetime.now().isoformat(),
            'input_summary': original_summary,
            'matching_analysis': matching_stats,
            'processed_counts': {
                'raw_activities': len(raw_activities),
                'processed_activities': len(processed_activities)
            },
            'tag_analysis': {
                'total_unique_tags': len(tag_counts),
                'total_tag_applications': len(all_tags),
                'top_tags': top_tags,
                'average_tags_per_activity': round(len(all_tags) / len(raw_activities), 2) if raw_activities else 0
            },
            'duration_analysis': {
                'total_tracked_minutes': sum(a.duration_minutes for a in raw_activities),
                'duration_by_tag': dict(sorted(duration_by_tag.items(), key=lambda x: x[1], reverse=True)[:10])
            }
        }
    
    def load_processed_activities(self, filepath: str = 'processed_activities.json') -> List[ProcessedActivity]:
        """Load previously processed activities from file."""
        from .models import deserialize_processed_activities
        try:
            return deserialize_processed_activities(filepath)
        except FileNotFoundError:
            print(f"No processed activities file found at {filepath}")
            return []
    
    def get_activity_insights(self, processed_activities: List[ProcessedActivity]) -> Dict[str, Any]:
        """Generate insights from processed activities for frontend consumption."""
        if not processed_activities:
            return {'error': 'No processed activities available'}
        
        # Time distribution by tags
        tag_time_distribution = {}
        total_time = 0
        
        for activity in processed_activities:
            total_time += activity.total_duration_minutes
            
            for tag in activity.tags:
                if tag not in tag_time_distribution:
                    tag_time_distribution[tag] = 0
                tag_time_distribution[tag] += activity.total_duration_minutes
        
        # Convert to percentages
        tag_percentages = {}
        for tag, minutes in tag_time_distribution.items():
            tag_percentages[tag] = round((minutes / total_time) * 100, 1) if total_time > 0 else 0
        
        # Top 5 time-consuming activities
        top_activities = sorted(tag_time_distribution.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_tracked_hours': round(total_time / 60, 2),
            'activity_count': len(processed_activities),
            'tag_time_distribution': tag_time_distribution,
            'tag_percentages': tag_percentages,
            'top_5_activities': [{'tag': tag, 'hours': round(minutes/60, 2)} for tag, minutes in top_activities],
            'unique_tags': len(tag_time_distribution)
        }