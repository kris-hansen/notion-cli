"""Notion CLI - Manage tasks and more from the command line."""

import argparse
import os
import sys
from datetime import datetime

import pytz
from notion_client import Client
from termcolor import colored, cprint


# Supported block types and their display info
BLOCK_TYPES = {
    "paragraph": {"icon": "¶", "color": "white"},
    "heading_1": {"icon": "H1", "color": "cyan"},
    "heading_2": {"icon": "H2", "color": "cyan"},
    "heading_3": {"icon": "H3", "color": "cyan"},
    "bulleted_list_item": {"icon": "•", "color": "white"},
    "numbered_list_item": {"icon": "#", "color": "white"},
    "to_do": {"icon": "☐", "color": "green"},
    "toggle": {"icon": "▸", "color": "magenta"},
    "quote": {"icon": "❝", "color": "yellow"},
    "callout": {"icon": "💡", "color": "yellow"},
    "divider": {"icon": "—", "color": "white"},
    "code": {"icon": "<>", "color": "blue"},
}


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


def get_block_content(block):
    """Extract text content from any block type."""
    block_type = block.get("type", "unknown")
    
    if block_type == "divider":
        return "───────────"
    
    # Most block types store content in rich_text
    block_data = block.get(block_type, {})
    rich_text = block_data.get("rich_text", [])
    
    if rich_text:
        return rich_text[0].get("plain_text", "(empty)")
    
    # Some blocks might have different structures
    return "(empty)"


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


def list_all_blocks(notion, page, timezone, filter_type=None):
    """List all blocks from a page, optionally filtered by type."""
    local_tz = pytz.timezone(timezone)
    block_list = []

    blocks = get_blocks(notion, page)

    for index, item in enumerate(blocks, start=1):
        block_type = item.get("type", "unknown")
        
        # Apply filter if specified
        if filter_type and block_type != filter_type:
            continue
        
        created_time = datetime.fromisoformat(item["created_time"].rstrip("Z"))
        created_time_local = created_time.astimezone(local_tz)
        created_time_formatted = created_time_local.strftime("%Y-%m-%d %H:%M")
        
        content = get_block_content(item)
        
        # Get display info for this block type
        type_info = BLOCK_TYPES.get(block_type, {"icon": "?", "color": "white"})
        icon = type_info["icon"]
        
        # Special handling for to-dos
        if block_type == "to_do":
            checked = item["to_do"].get("checked", False)
            icon = "☑" if checked else "☐"
        
        block_list.append({
            "index": index,
            "type": block_type,
            "content": content,
            "created": created_time_formatted,
            "icon": icon,
            "color": type_info["color"],
        })

    return block_list


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


def add_block(notion, content, parent_id, block_type="paragraph"):
    """Add a new block of any type to the specified page."""
    
    if block_type == "divider":
        # Divider has no content
        new_block = {
            "object": "block",
            "type": "divider",
            "divider": {},
        }
    elif block_type == "to_do":
        new_block = {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [{"type": "text", "text": {"content": content}}],
                "checked": False,
            },
        }
    else:
        # Standard block with rich_text
        new_block = {
            "object": "block",
            "type": block_type,
            block_type: {
                "rich_text": [{"type": "text", "text": {"content": content}}],
            },
        }
    
    notion.blocks.children.append(parent_id, children=[new_block])
    
    type_info = BLOCK_TYPES.get(block_type, {"icon": "?"})
    print(colored(f"✓ Added {block_type}: {content if block_type != 'divider' else '(divider)'}", "green"))


def get_block_by_index(notion, page, index):
    """Retrieve a block by its display index."""
    blocks = get_blocks(notion, page)
    try:
        return blocks[index - 1]
    except IndexError:
        print(colored(f"Error: Block {index} not found", "red"))
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


def delete_block(notion, page, index):
    """Delete any block by index."""
    block = get_block_by_index(notion, page, index)
    content = get_block_content(block)
    block_type = block.get("type", "unknown")
    
    notion.blocks.delete(block["id"])
    print(colored(f"✓ Deleted {block_type}: {content}", "yellow"))


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="notion",
        description="Manage Notion tasks and content from the command line.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  notion list                           List all tasks (to-dos)
  notion add "Buy groceries"            Add a new task
  notion done 3                         Mark task #3 as complete
  notion delete 2                       Delete task #2

  notion blocks list                    List all blocks on the page
  notion blocks list --type heading_1   List only H1 headings
  notion blocks add "Hello world"       Add a paragraph
  notion blocks add "Title" -t heading_1   Add a heading
  notion blocks delete 5                Delete block #5

Block types: paragraph, heading_1, heading_2, heading_3, bulleted_list_item,
             numbered_list_item, to_do, toggle, quote, callout, divider, code

Environment variables:
  NOTION_API_KEY     Your Notion integration API key (required)
  NOTION_PAGE_ID     The ID of your tasks page (required)
  LOCAL_TIMEZONE     Your timezone, e.g., America/New_York (optional, defaults to UTC)
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # === Legacy to-do commands (backward compatible) ===
    
    # List command
    subparsers.add_parser("list", aliases=["ls"], help="List all to-do items")

    # Add command
    add_parser = subparsers.add_parser("add", aliases=["a"], help="Add a new to-do item")
    add_parser.add_argument("content", help="The content of the to-do item")

    # Mark done command
    done_parser = subparsers.add_parser("done", aliases=["check", "complete"], help="Mark a to-do item as complete")
    done_parser.add_argument("index", type=int, help="The task number to mark as complete")

    # Delete command (for to-dos)
    delete_parser = subparsers.add_parser("delete", aliases=["del", "rm"], help="Delete a to-do item")
    delete_parser.add_argument("index", type=int, help="The task number to delete")

    # === New blocks subcommand ===
    
    blocks_parser = subparsers.add_parser("blocks", aliases=["b"], help="Manage all block types")
    blocks_subparsers = blocks_parser.add_subparsers(dest="blocks_command", help="Block commands")
    
    # blocks list
    blocks_list_parser = blocks_subparsers.add_parser("list", aliases=["ls"], help="List all blocks")
    blocks_list_parser.add_argument(
        "--type", "-t",
        choices=list(BLOCK_TYPES.keys()),
        help="Filter by block type"
    )
    
    # blocks add
    blocks_add_parser = blocks_subparsers.add_parser("add", aliases=["a"], help="Add a new block")
    blocks_add_parser.add_argument("content", nargs="?", default="", help="The content of the block")
    blocks_add_parser.add_argument(
        "--type", "-t",
        choices=list(BLOCK_TYPES.keys()),
        default="paragraph",
        help="Block type (default: paragraph)"
    )
    
    # blocks delete
    blocks_delete_parser = blocks_subparsers.add_parser("delete", aliases=["del", "rm"], help="Delete a block")
    blocks_delete_parser.add_argument("index", type=int, help="The block number to delete")

    # Version
    parser.add_argument("--version", action="version", version="%(prog)s 1.2.0")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Get configuration and initialize client
    config = get_config()
    notion = Client(auth=config["api_key"])
    page = get_page(notion, config["page_id"])

    # === Execute legacy to-do commands ===
    
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

    # === Execute blocks commands ===
    
    elif args.command in ("blocks", "b"):
        if not args.blocks_command:
            blocks_parser.print_help()
            sys.exit(0)
        
        if args.blocks_command in ("list", "ls"):
            filter_type = getattr(args, "type", None)
            blocks = list_all_blocks(notion, page, config["timezone"], filter_type)
            
            if not blocks:
                msg = f"No {filter_type} blocks found." if filter_type else "No blocks found."
                print(colored(msg, "yellow"))
            else:
                print()
                for block in blocks:
                    icon = block["icon"]
                    idx = block["index"]
                    content = block["content"][:60] + "..." if len(block["content"]) > 60 else block["content"]
                    block_type = block["type"]
                    
                    cprint(f"  {idx:3} {icon:2} [{block_type:20}] {content}", block["color"])
                print()
                
                # Summary by type
                type_counts = {}
                for b in blocks:
                    t = b["type"]
                    type_counts[t] = type_counts.get(t, 0) + 1
                
                summary = ", ".join(f"{count} {t}" for t, count in sorted(type_counts.items()))
                print(f"  {len(blocks)} blocks: {summary}")
                print()
        
        elif args.blocks_command in ("add", "a"):
            block_type = args.type
            content = args.content
            
            if block_type != "divider" and not content:
                print(colored("Error: Content required for this block type", "red"))
                sys.exit(1)
            
            add_block(notion, content, config["page_id"], block_type)
        
        elif args.blocks_command in ("delete", "del", "rm"):
            delete_block(notion, page, args.index)


if __name__ == "__main__":
    main()
