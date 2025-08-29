# Notion Parser (`notion_parser.py`)

## Purpose
This script is a component of the SmartHistory project's backend. Its sole purpose is to parse the raw, nested JSON data fetched from the Notion API (`notion_content.json`) and transform it into a clean, structured, and "flattened" format that is easy for the AI agent to process.

## Core Logic
The parser recursively traverses the block structure of the Notion page content. It identifies different block types (headings, paragraphs, lists, etc.), extracts the plain text content, and preserves the hierarchical context of each piece of text.

A key feature of this parser is its ability to filter content based on when it was last edited. It accepts an `hours_since_last_edit` parameter (defaulting to 24) to process only the most recent changes, making the system efficient for daily updates.

## Inputs
-   `notion_content.json`: The raw JSON file containing the content of the Notion page, fetched by the `test_notion_api.py` script.

## Outputs
-   `parsed_notion_content.json`: A JSON file containing a list of "document" objects. Each object represents a piece of text from the Notion page and includes the following fields:
    -   `source`: "notion"
    -   `block_id`: The unique ID of the Notion block.
    -   `block_type`: The original type of the content (e.g., `paragraph`).
    -   `text`: The clean, extracted text content.
    -   `hierarchy`: An array of parent headings and page titles, which preserves the context of the text.

## How it Interacts with Other Parts
This parser is the first step in the data processing pipeline. Its output is designed to be consumed by the AI agent, which will then use this structured data to identify and categorize activities.
