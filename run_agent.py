#!/usr/bin/env python3
"""
SmartHistory AI Agent - Main Entry Point

A convenient script to run the AI agent from the project root.
This script handles path setup and provides easy access to agent functionality.

Usage:
    python run_agent.py --help                    # Show help
    python run_agent.py --mode daily             # Process daily activities  
    python run_agent.py --mode insights          # Generate insights
    python run_agent.py --test                   # Run capability test
"""

import os
import sys
import argparse
from pathlib import Path

# Add src to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def run_daily_processing(args):
    """Run daily activity processing."""
    from src.backend.agent.core.agent import run_daily_processing as run_daily
    
    # Convert argparse Namespace to dict-like object for compatibility
    class Args:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    # Create args object with defaults
    agent_args = Args(
        notion_file=args.notion_file or 'parsed_notion_content.json',
        calendar_file=args.calendar_file or 'parsed_google_calendar_events.json', 
        output_dir=args.output_dir or 'agent_output'
    )
    
    return run_daily(agent_args)

def run_insights_generation(args):
    """Run insights generation."""
    from src.backend.agent.core.agent import run_insights_generation as run_insights
    
    class Args:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    agent_args = Args(output_dir=args.output_dir or 'agent_output')
    return run_insights(agent_args)

def run_capability_test():
    """Run the agent capability test."""
    print("Running AI Agent capability test...")
    
    # Change to project root for test
    original_cwd = os.getcwd()
    os.chdir(PROJECT_ROOT)
    
    try:
        # Import and run the capability test
        sys.path.append('src/backend/test_features/agent_tests')
        from test_agent_capabilities import test_agent_capabilities
        
        success = test_agent_capabilities()
        return success
    except Exception as e:
        print(f"Error running capability test: {e}")
        return False
    finally:
        os.chdir(original_cwd)

def check_prerequisites():
    """Check that required files and setup exist."""
    issues = []
    
    # Check for .env file
    env_file = PROJECT_ROOT / '.env'
    if not env_file.exists():
        issues.append("Missing .env file with API keys")
    
    # Check for virtual environment activation
    if not os.environ.get('VIRTUAL_ENV'):
        issues.append("Virtual environment not activated (run: source src/backend/act.sh)")
    
    # Check for required Python packages
    try:
        import openai
        from dotenv import load_dotenv
    except ImportError as e:
        issues.append(f"Missing Python package: {e}")
    
    if issues:
        print("⚠️  Setup Issues Found:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nPlease resolve these issues before running the agent.")
        return False
    
    return True

def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description='SmartHistory AI Agent - Intelligent Activity Processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_agent.py --mode daily              # Process activities with default files
  python run_agent.py --mode insights           # Generate insights from processed data
  python run_agent.py --test                    # Run capability demonstration
  python run_agent.py --mode daily --notion-file custom.json --output-dir results/
        """
    )
    
    parser.add_argument('--mode',
                       choices=['daily', 'insights'],
                       help='Processing mode: daily processing or insights generation')
    
    parser.add_argument('--test',
                       action='store_true',
                       help='Run agent capability test')
    
    parser.add_argument('--notion-file',
                       help='Path to parsed Notion content file')
    
    parser.add_argument('--calendar-file',
                       help='Path to parsed Google Calendar events file')
    
    parser.add_argument('--output-dir',
                       help='Directory for output files')
    
    parser.add_argument('--skip-checks',
                       action='store_true', 
                       help='Skip prerequisite checks')
    
    args = parser.parse_args()
    
    # Show help if no arguments provided
    if not any([args.mode, args.test]):
        parser.print_help()
        return
    
    # Check prerequisites unless skipped
    if not args.skip_checks and not check_prerequisites():
        return
    
    print("🚀 SmartHistory AI Agent")
    print("=" * 50)
    
    try:
        if args.test:
            success = run_capability_test()
            sys.exit(0 if success else 1)
            
        elif args.mode == 'daily':
            report = run_daily_processing(args)
            if report and report.get('status') == 'success':
                print("\n✅ Daily processing completed successfully!")
                print(f"📊 Processed {report['processed_counts']['raw_activities']} activities")
                print(f"🏷️ Generated {report['tag_analysis']['total_unique_tags']} unique tags")
            else:
                print("\n❌ Daily processing failed or returned no data")
                sys.exit(1)
                
        elif args.mode == 'insights':
            run_insights_generation(args)
            print("\n✅ Insights generation completed!")
            
    except KeyboardInterrupt:
        print("\n\n⏸️ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()