import json
from datetime import datetime, timedelta, timezone

def get_plain_text_from_rich_text(rich_text):
    """Extracts plain text from a rich_text array."""
    return "".join([item.get('plain_text', '') for item in rich_text])

def parse_blocks_recursive(blocks, hierarchy, hours_since_last_edit, now=None):
    """Recursively parses a list of blocks."""
    if now is None:
        now = datetime.now(timezone.utc)
    time_threshold = now - timedelta(hours=hours_since_last_edit)

    parsed_data = []

    for block in blocks:
        # First, build the hierarchy for the current level
        current_hierarchy = list(hierarchy)
        block_type = block.get('type')
        if block_type in ['heading_1', 'heading_2', 'heading_3']:
            heading_text = get_plain_text_from_rich_text(block.get(block_type, {}).get('rich_text', []))
            current_hierarchy.append(heading_text)
        elif block_type == 'child_page':
            title = block.get('child_page', {}).get('title', '')
            current_hierarchy.append(title)

        # Second, recurse into children with the updated hierarchy
        if 'children' in block:
            parsed_data.extend(parse_blocks_recursive(block['children'], current_hierarchy, hours_since_last_edit, now=now))

        # Third, process the current block if it meets the criteria
        last_edited_time_str = block.get('last_edited_time')
        if last_edited_time_str:
            last_edited_time = datetime.fromisoformat(last_edited_time_str.replace('Z', '+00:00'))
            if last_edited_time >= time_threshold:
                text_to_add = ''
                if block_type in ['paragraph', 'bulleted_list_item', 'numbered_list_item']:
                    text_to_add = get_plain_text_from_rich_text(block.get(block_type, {}).get('rich_text', []))

                if text_to_add:
                    parsed_data.append({
                        "source": "notion",
                        "block_id": block.get('id'),
                        "block_type": block_type,
                        "text": text_to_add,
                        "hierarchy": hierarchy  # Use the parent's hierarchy
                    })

    return parsed_data

def parse_to_database(input_file='notion_content.json', hours_since_last_edit=24):
    """Parse Notion content and save directly to database."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
        return 0

    parsed_data = parse_blocks_recursive(data, [], hours_since_last_edit)

    # Save directly to database
    try:
        import sys
        from pathlib import Path
        
        # Add project root to path for database imports
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        from src.backend.database import RawActivityDAO, RawActivityDB
        
        activities_saved = 0
        for block in parsed_data:
            try:
                raw_activity = RawActivityDB(
                    date=block.get('date', '2025-08-31'),
                    time=block.get('time'),
                    duration_minutes=block.get('duration_minutes', 30),  # Default 30min for notion blocks
                    details=block.get('text', '')[:500],  # Use 'text' field from parsed data
                    source='notion',
                    orig_link=block.get('url', ''),
                    raw_data=block
                )
                
                RawActivityDAO.create(raw_activity)
                activities_saved += 1
                
            except Exception as e:
                print(f"Warning: Failed to save activity: {e}")
        
        print(f"Successfully parsed and saved {activities_saved} notion activities to database")
        return activities_saved
        
    except Exception as e:
        print(f"Error saving to database: {e}")
        return 0

def main(input_file='notion_content.json', output_file='parsed_notion_content.json', hours_since_last_edit=24):
    """Main function - backwards compatible but now database-first."""
    print("Note: Parser now saves directly to database. JSON output is deprecated.")
    return parse_to_database(input_file, hours_since_last_edit)

if __name__ == '__main__':
    main()