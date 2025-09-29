#!/usr/bin/env python3
"""
Tag Cleanup Runner

Standalone script to analyze and clean meaningless tags from the database.
Uses AI to identify system artifacts, meaningless tags, and merge opportunities.

Usage:
  python runner/run_tag_cleanup.py --dry-run  # Analyze only, don't make changes
  python runner/run_tag_cleanup.py --clean    # Actually remove and merge tags
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None  # type: ignore

from src.backend.database import get_db_manager
from src.backend.agent.tools.tag_cleaner import TagCleaner


def main():
    parser = argparse.ArgumentParser(description="Clean and merge meaningless tags in database")
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Analyze tags without making changes"
    )
    parser.add_argument(
        "--clean", 
        action="store_true", 
        help="Actually remove meaningless tags and merge similar ones"
    )
    parser.add_argument(
        "--start",
        help="Optional start date YYYY-MM-DD to scope cleanup to activities in range"
    )
    parser.add_argument(
        "--end",
        help="Optional end date YYYY-MM-DD to scope cleanup to activities in range"
    )
    parser.add_argument(
        "--removal-threshold",
        type=float,
        default=0.8,
        help="Minimum confidence threshold to remove tags (default: 0.6)"
    )
    parser.add_argument(
        "--merge-threshold",
        type=float,
        default=0.6,
        help="Minimum confidence threshold to merge tags (default: 0.8)"
    )
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.clean:
        print("Must specify either --dry-run or --clean")
        sys.exit(1)
    
    # Load environment
    if load_dotenv is not None:
        env_path = PROJECT_ROOT / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            print(f"Loaded .env from {env_path}")
        else:
            print(f"Warning: .env file not found at {env_path}")
    else:
        print("Warning: python-dotenv not available")
    
    # Verify API key is loaded
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"OpenAI API key loaded: {api_key[:10]}...")
    else:
        print("Warning: OPENAI_API_KEY not found in environment")
    
    # Initialize components
    db = get_db_manager()
    tag_cleaner = TagCleaner()
    
    print("🧹 AI-Powered Tag Cleanup & Merge")
    print("=" * 50)
    print(f"Mode: {'DRY RUN (analysis only)' if args.dry_run else 'LIVE (will modify database)'}")
    print(f"Removal Threshold: {args.removal_threshold}")
    print(f"Merge Threshold: {args.merge_threshold}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run cleanup analysis
    try:
        results = tag_cleaner.clean_meaningless_tags(
            db_manager=db,
            dry_run=args.dry_run,
            removal_threshold=args.removal_threshold,
            merge_threshold=args.merge_threshold,
            date_start=args.start,
            date_end=args.end,
        )
        
        # Display results
        print("📊 ANALYSIS RESULTS")
        print("-" * 30)
        print(f"Total tags analyzed: {results['total_analyzed']}")
        print(f"Tags marked for removal: {results['marked_for_removal']}")
        print(f"Tags marked for merge: {results['marked_for_merge']}")
        
        if not args.dry_run:
            print(f"Tags actually removed: {results['removed']}")
            print(f"Tags actually merged: {results['merged']}")
        
        print()
        
        # Show removal actions
        if results['tags_to_remove']:
            print("🗑️  MEANINGLESS TAGS TO REMOVE")
            print("-" * 40)
            for tag_info in results['tags_to_remove']:
                status = "REMOVED" if not args.dry_run else "WOULD REMOVE"
                print(f"[{status}] '{tag_info['name']}'")
                print(f"  Reason: {tag_info['reason']}")
                print(f"  Confidence: {tag_info['confidence']:.1%}")
                print()
        
        # Show merge actions
        if results['tags_to_merge']:
            print("🔀 TAG MERGE OPERATIONS")
            print("-" * 40)
            for merge_info in results['tags_to_merge']:
                status = "MERGED" if not args.dry_run else "WOULD MERGE"
                print(f"[{status}] '{merge_info['source']}' → '{merge_info['target']}'")
                print(f"  Reason: {merge_info['reason']}")
                print(f"  Confidence: {merge_info['confidence']:.1%}")
                print()
        
        if not results['tags_to_remove'] and not results['tags_to_merge']:
            print("✅ No cleanup actions needed - your tag set looks well-organized!")
        
        print("✨ Tag cleanup analysis completed successfully!")
        
        if args.dry_run:
            print("\n💡 To actually perform these actions, run with --clean flag")
    
    except Exception as e:
        print(f"❌ Error during tag cleanup: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
