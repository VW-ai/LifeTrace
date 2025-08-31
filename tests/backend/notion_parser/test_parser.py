
import json
import os
from datetime import datetime, timedelta, timezone
from src.backend.parsers.notion.parser import parse_blocks_recursive

def setup_test_data(now):
    """Set up test data with a specific 'now' timestamp."""
    return [
      {
        "object": "block",
        "id": "block1",
        "type": "heading_1",
        "last_edited_time": (now - timedelta(days=2)).isoformat().replace('+00:00', 'Z'),
        "heading_1": {
          "rich_text": [{ "plain_text": "Test Heading 1" }]
        },
        "has_children": True,
        "children": [
          {
            "object": "block",
            "id": "block2",
            "type": "paragraph",
            "last_edited_time": (now - timedelta(hours=1)).isoformat().replace('+00:00', 'Z'),
            "paragraph": {
              "rich_text": [{ "plain_text": "This is a recent paragraph." }]
            },
            "has_children": False
          },
          {
            "object": "block",
            "id": "block3",
            "type": "paragraph",
            "last_edited_time": (now - timedelta(days=2)).isoformat().replace('+00:00', 'Z'),
            "paragraph": {
              "rich_text": [{ "plain_text": "This is an old paragraph." }]
            },
            "has_children": False
          }
        ]
      }
    ]

def test_time_based_filtering():
    """Test that only recently edited blocks are parsed."""
    now = datetime.now(timezone.utc)
    test_data = setup_test_data(now)
    parsed_data = parse_blocks_recursive(test_data, [], 24, now=now)
    assert len(parsed_data) == 1
    assert parsed_data[0]['block_id'] == 'block2'
    assert parsed_data[0]['text'] == 'This is a recent paragraph.'

def test_hierarchy():
    """Test that the hierarchy is correctly extracted."""
    now = datetime.now(timezone.utc)
    test_data = setup_test_data(now)
    parsed_data = parse_blocks_recursive(test_data, [], 48, now=now)
    assert len(parsed_data) == 2
    recent_paragraph = next(item for item in parsed_data if item["block_id"] == "block2")
    assert recent_paragraph['hierarchy'] == ['Test Heading 1']
    old_paragraph = next(item for item in parsed_data if item["block_id"] == "block3")
    assert old_paragraph['hierarchy'] == ['Test Heading 1']
