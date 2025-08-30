#!/usr/bin/env python3
"""
Main Agent Entry Point for smartHistory Activity Processing

This script serves as the primary interface for running the AI agent that processes
Notion and Google Calendar data into structured activity records with intelligent tagging.

Usage:
    python agent.py [--notion-file FILE] [--calendar-file FILE] [--output-dir DIR]
"""

import argparse
import os
import sys
from typing import Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .activity_processor import ActivityProcessor
from .models import deserialize_processed_activities

def load_api_key() -> Optional[str]:
    """Load OpenAI API key from environment or .env file."""
    # Try environment variable first
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        # Try loading from .env file
        try:
            from dotenv import load_dotenv
            # Try to load .env from current directory first, then project root
            if os.path.exists('.env'):
                load_dotenv('.env')
            else:
                # Load .env from project root
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                env_path = os.path.join(project_root, '.env')
                load_dotenv(env_path)
            api_key = os.getenv('OPENAI_API_KEY')
        except ImportError:
            pass
    
    if not api_key:
        print("Warning: No OpenAI API key found. Agent will use fallback tag generation.")
        print("Set OPENAI_API_KEY environment variable for full LLM functionality.")
    
    return api_key

def run_daily_processing(args) -> None:
    """Run the daily activity processing workflow."""
    print(f"SmartHistory AI Agent - Daily Processing")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Load API key
    api_key = load_api_key()
    
    # Initialize processor
    processor = ActivityProcessor(openai_api_key=api_key)
    
    # Set file paths
    notion_file = args.notion_file
    calendar_file = args.calendar_file
    output_dir = args.output_dir
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Set output file paths
    raw_output = os.path.join(output_dir, 'raw_activities.json')
    processed_output = os.path.join(output_dir, 'processed_activities.json')
    
    # Run processing
    try:
        report = processor.process_daily_activities(
            notion_file=notion_file,
            calendar_file=calendar_file,
            output_raw_file=raw_output,
            output_processed_file=processed_output
        )
        
        # Print summary
        print("\n" + "="*50)
        print("PROCESSING SUMMARY")
        print("="*50)
        print(f"Status: {report['status']}")
        print(f"Raw activities processed: {report['processed_counts']['raw_activities']}")
        print(f"Processed activities created: {report['processed_counts']['processed_activities']}")
        print(f"Unique tags generated: {report['tag_analysis']['total_unique_tags']}")
        print(f"Average tags per activity: {report['tag_analysis']['average_tags_per_activity']}")
        print(f"Total tracked time: {round(report['duration_analysis']['total_tracked_minutes']/60, 1)} hours")
        
        print("\nTop 5 Tags by Frequency:")
        for tag, count in report['tag_analysis']['top_tags'][:5]:
            print(f"  {tag}: {count} activities")
        
        print("\nTop 5 Tags by Duration:")
        for tag, minutes in list(report['duration_analysis']['duration_by_tag'].items())[:5]:
            hours = round(minutes/60, 1)
            print(f"  {tag}: {hours} hours")
        
        print(f"\nOutput files:")
        print(f"  Raw activities: {raw_output}")
        print(f"  Processed activities: {processed_output}")
        
        return report
        
    except Exception as e:
        print(f"\nERROR: Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_insights_generation(args) -> None:
    """Generate insights from existing processed activities."""
    print("SmartHistory AI Agent - Insights Generation")
    print("-" * 50)
    
    processed_file = os.path.join(args.output_dir, 'processed_activities.json')
    
    # Load processed activities
    try:
        activities = deserialize_processed_activities(processed_file)
        print(f"Loaded {len(activities)} processed activities")
    except FileNotFoundError:
        print(f"Error: No processed activities found at {processed_file}")
        print("Run daily processing first with --mode daily")
        return
    
    # Generate insights
    processor = ActivityProcessor()
    insights = processor.get_activity_insights(activities)
    
    if 'error' in insights:
        print(f"Error generating insights: {insights['error']}")
        return
    
    print("\n" + "="*50)
    print("ACTIVITY INSIGHTS")
    print("="*50)
    print(f"Total tracked time: {insights['total_tracked_hours']} hours")
    print(f"Number of activities: {insights['activity_count']}")
    print(f"Unique activity types: {insights['unique_tags']}")
    
    print("\nTop 5 Time-Consuming Activities:")
    for activity in insights['top_5_activities']:
        print(f"  {activity['tag']}: {activity['hours']} hours")
    
    print(f"\nTime Distribution by Activity:")
    for tag, percentage in sorted(insights['tag_percentages'].items(), 
                                key=lambda x: x[1], reverse=True)[:10]:
        hours = insights['tag_time_distribution'][tag] / 60
        print(f"  {tag}: {percentage}% ({hours:.1f} hours)")

def main():
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description='SmartHistory AI Agent for Activity Processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run daily processing with default files
  python agent.py --mode daily
  
  # Run with custom input files  
  python agent.py --mode daily --notion-file custom_notion.json --calendar-file custom_calendar.json
  
  # Generate insights from processed data
  python agent.py --mode insights
        """
    )
    
    parser.add_argument('--mode', 
                       choices=['daily', 'insights'],
                       default='daily',
                       help='Processing mode: daily processing or insights generation')
    
    parser.add_argument('--notion-file',
                       default='parsed_notion_content.json',
                       help='Path to parsed Notion content file')
    
    parser.add_argument('--calendar-file', 
                       default='parsed_google_calendar_events.json',
                       help='Path to parsed Google Calendar events file')
    
    parser.add_argument('--output-dir',
                       default='agent_output',
                       help='Directory for output files')
    
    args = parser.parse_args()
    
    if args.mode == 'daily':
        run_daily_processing(args)
    elif args.mode == 'insights':
        run_insights_generation(args)

if __name__ == '__main__':
    main()