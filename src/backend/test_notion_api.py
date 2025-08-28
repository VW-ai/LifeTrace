import os
import json
from notion_client import Client
from dotenv import load_dotenv

def get_blocks_recursive(notion_client, block_id, depth=1):
    if depth <= 0:
        return []

    all_blocks = []
    try:
        response = notion_client.blocks.children.list(block_id=block_id)
        results = response.get('results', [])
        all_blocks.extend(results)

        for i in range(len(all_blocks)):
            block = all_blocks[i]
            if block.get('has_children'):
                # To avoid circular references in JSON, we'll replace the block with a new dict
                # and add the children to it.
                new_block = dict(block)
                new_block['children'] = get_blocks_recursive(notion_client, block['id'], depth - 1)
                all_blocks[i] = new_block

    except Exception as e:
        print(f"An error occurred while fetching blocks for {block_id}: {e}")

    return all_blocks


def main():
    load_dotenv()

    notion_api_key = os.getenv('NOTION_API_KEY')
    diary_page_id = os.getenv('DIARY_PAGE_ID')

    if not notion_api_key or not diary_page_id:
        print("Error: NOTION_API_KEY or DIARY_PAGE_ID not found.")
        return

    notion = Client(auth=notion_api_key)
    output_file = '/Users/bytedance/smartHistory/notion_content.json'

    try:
        print("Retrieving page content (blocks) recursively...")
        blocks = get_blocks_recursive(notion, diary_page_id, depth=4) # Go two levels deep

        print(f"Saving the output to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(blocks, f, ensure_ascii=False, indent=3)

        print("Done.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()