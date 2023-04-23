import argparse
from datetime import datetime
import os
import sys

from notion_client import Client
import pytz
from termcolor import colored
from termcolor import cprint

# Set up environment variables
if not os.environ.get("NOTION_PAGE_ID"):
    print(colored("NOTION_PAGE_ID environment variable not set", "red"))
    sys.exit(1)
else:
    # Set the page as the default parent
    NOTION_PAGE_ID = os.environ["NOTION_PAGE_ID"]
if not os.environ.get("LOCAL_TIMEZONE"):
    print(colored("LOCAL_TIMEZONE environment variable not set", "red"))
    sys.exit(1)
else:
    # Set the timezone
    local_timezone = os.environ["LOCAL_TIMEZONE"]


def get_page(notion, page_id=NOTION_PAGE_ID):
    """Retrieve a page with the specified ID."""

    page = notion.pages.retrieve(page_id)
    return page


def get_blocks(notion, page):
    """Retrieve all blocks under a given page parent."""

    # Retrieve blocks from the Notion API
    blocks = notion.blocks.children.list(block_id=page["id"])
    return blocks.get("results")


def list_todos(notion, page):
    local_tz = pytz.timezone(local_timezone)
    todo_list = []

    blocks = get_blocks(notion, page)

    for index, item in enumerate(blocks, start=1):
        if item["type"] == "to_do":
            created_time = datetime.fromisoformat(item["created_time"].rstrip("Z"))
            created_time_local = created_time.astimezone(local_tz)
            created_time_formatted = created_time_local.strftime("%Y-%m-%d %H:%M:%S %Z")
            box = "[ ]" if not item["to_do"]["checked"] else "[X]"
            content = item["to_do"]["rich_text"][0]["plain_text"]
            todo_list.append(f"{index} - {box} {content} ({created_time_formatted})")

    return todo_list


def add_block(notion, parent_id, content, block_type="paragraph"):
    """Add a new block to the specified parent."""

    # Prepare the block content
    new_block = {
        "object": "block",
        block_type: {"text": [{"type": "text", "text": {"content": content}}]},
    }

    # Create the new block
    notion.blocks.children.append(parent_id, children=[new_block])
    print(
        f"Added {block_type} block with content: '{content}' to Parent ID '{parent_id}'"
    )


def add_todo(notion, content, parent_id=NOTION_PAGE_ID):
    """Add a new to-do item to the specified to-do block."""

    # Prepare the to-do item
    new_item = {
        "object": "block",
        "to_do": {
            "rich_text": [{"type": "text", "text": {"content": content}}],
            "checked": False,
        },
    }

    # Create the new to-do item
    notion.blocks.children.append(parent_id, children=[new_item])
    print(f"Added to-do item with content: '{content}' to Parent ID '{parent_id}'")


def mark_checked(notion, block_id):
    """Mark a to-do item as complete."""

    notion.blocks.update(block_id, to_do={"checked": True})
    print(f"Marked to-do item with ID '{block_id}' as complete")


def get_block_by_index(notion, index):
    """Retrieve a block with the specified index."""
    page = get_page(notion)
    blocks = get_blocks(notion, page)
    try:
        block = blocks[index - 1]
    except IndexError:
        print(colored(f"Task {index} not found", "red"))
        sys.exit(1)
    return block


def mark_todo_checked(notion, index):
    """Mark a to-do item as complete."""
    block = get_block_by_index(notion, index)
    return mark_checked(notion, block["id"])


def delete_block(notion, block_id):
    """Delete a block with the specified ID."""

    notion.blocks.delete(block_id)
    print(f"Deleted block with ID '{block_id}'")


def get_block(notion, block_id):
    """Retrieve a block with the specified ID."""

    block = notion.blocks.retrieve(block_id)
    print(f"Block ID '{block_id}':")
    print(block)


def delete_todo(notion, index):
    """Remove a to-do item from a to-do block."""
    block_id = get_block_by_index(notion, index)["id"]
    notion.blocks.delete(block_id)
    print(f"Deleted to-do item with ID '{block_id}'")


def main():
    # Initialize the Notion API client
    if not os.environ.get("NOTION_API_KEY"):
        print(colored("NOTION_API_KEY environment variable not set", "red"))
        sys.exit(1)
    else:
        notion = Client(auth=os.environ["NOTION_API_KEY"])
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Manage ToDo blocks using the Notion API in your CLI."
    )
    subparsers = parser.add_subparsers(dest="command")

    # Help command
    help_parser = subparsers.add_parser("help", help="Show this help message and exit")

    # Add to-do item command
    add_todo_parser = subparsers.add_parser(
        "add_todo", help="Add a new to-do item to the specified to-do block"
    )
    add_todo_parser.add_argument("content", help="The content of the to-do item")

    # List to-do items command
    list_todos_parser = subparsers.add_parser(
        "list_todos", help="List all to-do items in a to-do block"
    )

    # Mark to-do item as complete command
    mark_checked_parser = subparsers.add_parser(
        "mark_checked", help="Mark a to-do item as complete"
    )
    mark_checked_parser.add_argument(
        "index", help="The item number of the to-do item to mark as complete", type=int
    )

    # Delete to-do item command
    delete_todo_parser = subparsers.add_parser(
        "del_todo", help="Remove a to-do item from a to-do block"
    )
    delete_todo_parser.add_argument(
        "index", help="The ID of the to-do item to remove", type=int
    )

    # Parse arguments
    args = parser.parse_args()

    # Execute the corresponding command
    if args.command == "help":
        parser.print_help()
    elif args.command == "add_todo":
        add_todo(notion, args.content)
    elif args.command == "mark_checked":
        mark_todo_checked(notion, args.index)
    elif args.command == "list_todos":
        page = get_page(notion)
        for todo in list_todos(notion, page):
            cprint(todo + "\n", "green", attrs=["bold"])
    elif args.command == "del_todo":
        delete_todo(notion, args.index)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
