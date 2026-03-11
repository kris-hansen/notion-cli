"""Notion CLI - Manage tasks and more from the command line."""

import argparse
import os
import sys
from datetime import datetime

import pytz
from notion_client import Client
from termcolor import colored, cprint


def get_config():
    """Get configuration from environment variables."""
    config = {}
    
    api_key = os.environ.get("NOTION_API_KEY")
    if not api_key:
        print(colored("Error: NOTION_API_KEY environment variable not set", "red"))
        print("Set it with: export NOTION_API_KEY='your-api-key'")
        sys.exit(1)
    config["api_key"] = api_key
    
    page_id = os.environ.get("NOTION_PAGE_ID")
    if not page_id:
        print(colored("Error: NOTION_PAGE_ID environment variable not set", "red"))
        print("Set it with: export NOTION_PAGE_ID='your-page-id'")
        sys.exit(1)
    config["page_id"] = page_id
    
    # Timezone is optional, defaults to UTC
    config["timezone"] = os.environ.get("LOCAL_TIMEZONE", "UTC")
    
    return config


def get_page(notion, page_id):
    """Retrieve a page with the specified ID."""
    return notion.pages.retrieve(page_id)


def get_blocks(notion, page):
    """Retrieve all blocks under a given page parent."""
    blocks = notion.blocks.children.list(block_id=page["id"])
    return blocks.get("results", [])


def list_todos(notion, page, timezone):
    """List all to-do items from a page."""
    local_tz = pytz.timezone(timezone)
    todo_list = []

    blocks = get_blocks(notion, page)

    for index, item in enumerate(blocks, start=1):
        if item["type"] == "to_do":
            created_time = datetime.fromisoformat(item["created_time"].rstrip("Z"))
            created_time_local = created_time.astimezone(local_tz)
            created_time_formatted = created_time_local.strftime("%Y-%m-%d %H:%M:%S %Z")
            
            checked = item["to_do"].get("checked", False)
            box = "[X]" if checked else "[ ]"
            
            rich_text = item["to_do"].get("rich_text", [])
            content = rich_text[0]["plain_text"] if rich_text else "(empty)"
            
            todo_list.append({
                "index": index,
                "checked": checked,
                "content": content,
                "created": created_time_formatted,
                "display": f"{index} - {box} {content} ({created_time_formatted})"
            })

    return todo_list


def add_todo(notion, content, parent_id):
    """Add a new to-do item to the specified page."""
    new_item = {
        "object": "block",
        "to_do": {
            "rich_text": [{"type": "text", "text": {"content": content}}],
            "checked": False,
        },
    }

    notion.blocks.children.append(parent_id, children=[new_item])
    print(colored(f"✓ Added: {content}", "green"))


def get_block_by_index(notion, page, index):
    """Retrieve a block by its display index."""
    blocks = get_blocks(notion, page)
    try:
        return blocks[index - 1]
    except IndexError:
        print(colored(f"Error: Task {index} not found", "red"))
        sys.exit(1)


def mark_todo_checked(notion, page, index):
    """Mark a to-do item as complete."""
    block = get_block_by_index(notion, page, index)
    
    if block["type"] != "to_do":
        print(colored(f"Error: Item {index} is not a to-do item", "red"))
        sys.exit(1)
    
    notion.blocks.update(block["id"], to_do={"checked": True})
    
    rich_text = block["to_do"].get("rich_text", [])
    content = rich_text[0]["plain_text"] if rich_text else "(empty)"
    print(colored(f"✓ Completed: {content}", "green"))


def delete_todo(notion, page, index):
    """Delete a to-do item."""
    block = get_block_by_index(notion, page, index)
    
    rich_text = block.get("to_do", {}).get("rich_text", [])
    content = rich_text[0]["plain_text"] if rich_text else "(item)"
    
    notion.blocks.delete(block["id"])
    print(colored(f"✓ Deleted: {content}", "yellow"))


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="notion",
        description="Manage Notion tasks from the command line.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  notion list                    List all tasks
  notion add "Buy groceries"     Add a new task
  notion done 3                  Mark task #3 as complete
  notion delete 2                Delete task #2

Environment variables:
  NOTION_API_KEY     Your Notion integration API key (required)
  NOTION_PAGE_ID     The ID of your tasks page (required)
  LOCAL_TIMEZONE     Your timezone, e.g., America/New_York (optional, defaults to UTC)
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    subparsers.add_parser("list", aliases=["ls"], help="List all to-do items")

    # Add command
    add_parser = subparsers.add_parser("add", aliases=["a"], help="Add a new to-do item")
    add_parser.add_argument("content", help="The content of the to-do item")

    # Mark done command
    done_parser = subparsers.add_parser("done", aliases=["check", "complete"], help="Mark a to-do item as complete")
    done_parser.add_argument("index", type=int, help="The task number to mark as complete")

    # Delete command
    delete_parser = subparsers.add_parser("delete", aliases=["del", "rm"], help="Delete a to-do item")
    delete_parser.add_argument("index", type=int, help="The task number to delete")

    # Version
    parser.add_argument("--version", action="version", version="%(prog)s 1.1.0")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Get configuration and initialize client
    config = get_config()
    notion = Client(auth=config["api_key"])
    page = get_page(notion, config["page_id"])

    # Execute command
    if args.command in ("list", "ls"):
        todos = list_todos(notion, page, config["timezone"])
        if not todos:
            print(colored("No tasks found.", "yellow"))
        else:
            print()
            for todo in todos:
                color = "white" if not todo["checked"] else "green"
                attrs = ["bold"] if not todo["checked"] else ["dark"]
                cprint(f"  {todo['display']}", color, attrs=attrs)
            print()
            
            pending = sum(1 for t in todos if not t["checked"])
            completed = sum(1 for t in todos if t["checked"])
            print(f"  {pending} pending, {completed} completed")
            print()

    elif args.command in ("add", "a"):
        add_todo(notion, args.content, config["page_id"])

    elif args.command in ("done", "check", "complete"):
        mark_todo_checked(notion, page, args.index)

    elif args.command in ("delete", "del", "rm"):
        delete_todo(notion, page, args.index)


if __name__ == "__main__":
    main()
