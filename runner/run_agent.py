#!/usr/bin/env python3
"""
SmartHistory Agent Runner (DB-first)

Modern entry that delegates to the processing service and database-first
pipeline. Prefer `runner/sh.py process` for richer controls; this script
remains as a convenience wrapper to run DB-backed processing.

Usage:
    python runner/run_agent.py --start YYYY-MM-DD --end YYYY-MM-DD [--regenerate-system-tags]
    python runner/run_agent.py --test
"""

import os
import sys
import argparse
from pathlib import Path

# Add src to Python path
PROJECT_ROOT = Path(__file__).parent.parent  # Go up one level to actual project root
sys.path.insert(0, str(PROJECT_ROOT))

def run_daily_processing(args):
    """Run processing via API service (DB-first)."""
    import asyncio
    from src.backend.api.dependencies import get_processing_service
    processing = get_processing_service()
    res = asyncio.run(
        processing.reprocess_date_range(
            date_start=args.start or "0001-01-01",
            date_end=args.end or "9999-12-31",
            regenerate_system_tags=bool(args.regenerate_system_tags),
        )
    )
    return res

def run_insights_generation(args):
    """Deprecated: insights moved to dashboards. Placeholder."""
    print("Insights generation is deprecated in this runner. Use API/Frontend dashboards.")
    return None

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
    
    # .env is optional if environment already configured
    env_file = PROJECT_ROOT / '.env'
    if not env_file.exists():
        issues.append(".env not found (optional if env vars set)")
    
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
        description='SmartHistory Agent Runner (DB-first processing)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_agent.py --mode daily              # Process activities from database (recommended)
  python run_agent.py --mode insights           # Generate insights from processed data
  python run_agent.py --test                    # Run capability demonstration
  python run_agent.py --mode daily --output-dir results/  # Save outputs to custom directory
        """
    )
    
    parser.add_argument('--test',
                       action='store_true',
                       help='Run agent capability test')
    parser.add_argument('--start', help='Start date YYYY-MM-DD (optional)')
    parser.add_argument('--end', help='End date YYYY-MM-DD (optional)')
    parser.add_argument('--regenerate-system-tags', action='store_true')
    
    parser.add_argument('--skip-checks',
                       action='store_true', 
                       help='Skip prerequisite checks')
    
    args = parser.parse_args()
    
    # Default to processing full range if no args
    if not any([args.test, args.start, args.end]):
        args.start = "0001-01-01"
        args.end = "9999-12-31"
    
    # Check prerequisites unless skipped
    if not args.skip_checks and not check_prerequisites():
        return
    
    print("🚀 SmartHistory AI Agent")
    print("=" * 50)
    
    try:
        if args.test:
            success = run_capability_test()
            sys.exit(0 if success else 1)
        else:
            report = run_daily_processing(args)
            if report and report.get('status') == 'success':
                print("\n✅ Processing completed!")
                print(f"📊 Deleted prior processed in window: {report.get('deleted_processed')} ")
                counts = report.get('processed_counts', {})
                print(f"📊 Processed raw: {counts.get('raw_activities')} | processed: {counts.get('processed_activities')}")
                tags = report.get('tag_analysis', {})
                print(f"🏷️ Unique tags: {tags.get('total_unique_tags')} | Avg per activity: {tags.get('average_tags_per_activity')} ")
            else:
                print("\n❌ Processing failed or returned no data")
                sys.exit(1)
            
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
