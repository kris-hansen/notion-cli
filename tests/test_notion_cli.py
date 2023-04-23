import os
import sys
from unittest.mock import MagicMock

from notion_client import Client
import pytest
import pytz

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from notioncli.cli import add_block
from notioncli.cli import add_todo
from notioncli.cli import delete_block
from notioncli.cli import delete_todo
from notioncli.cli import get_block
from notioncli.cli import get_block_by_index
from notioncli.cli import get_blocks
from notioncli.cli import get_page
from notioncli.cli import list_todos
from notioncli.cli import mark_checked
from notioncli.cli import mark_todo_checked

# Set up environment variables
os.environ["NOTION_API_KEY"] = "fake_api_key"
os.environ["NOTION_PAGE_ID"] = "fake_page_id"
os.environ["LOCAL_TIMEZONE"] = "America/Los_Angeles"

print("API key: " + os.environ["NOTION_API_KEY"])
# Mock Notion API client
notion = notion = MagicMock()
# Mock Notion API response for get_page
notion.pages.retrieve.return_value = {
    "object": "page",
    "id": "2cbe873c-2459-409f-afe3-e73e750115ac",
    # Add any additional fields as needed
}
# Mock Notion API response for get_blocks
notion.blocks.children.list.return_value = {
    "results": [
        {
            "object": "block",
            "id": "e8f27210-12a7-4ecc-a584-960532543426",
            "parent": {
                "type": "page_id",
                "page_id": "2cbe873c-2459-409f-afe3-e73e750115ac",
            },
            "created_time": "2023-04-22T21:05:00.000Z",
            "last_edited_time": "2023-04-22T21:05:00.000Z",
            "created_by": {
                "object": "user",
                "id": "f3ce58ba-d7a0-4f03-939d-dabf09400f92",
            },
            "last_edited_by": {
                "object": "user",
                "id": "f3ce58ba-d7a0-4f03-939d-dabf09400f92",
            },
            "has_children": False,
            "archived": False,
            "type": "to_do",
            "to_do": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Test to-do content",
                            "link": None,
                        },
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default",
                        },
                        "plain_text": "Test to-do content",
                        "href": None,
                    }
                ],
                "checked": False,
                "color": "default",
            },
        }
    ]
}
notion.blocks.children.append = MagicMock()
notion.blocks.update = MagicMock()
notion.blocks.delete = MagicMock()
notion.blocks.retrieve = MagicMock(
    return_value={
        "id": "fake_block_id",
        "type": "to_do",
        "created_time": "2023-04-22T21:18:00.000Z",
        "to_do": {
            "checked": False,
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "Test to-do item"},
                },
            ],
        },
    }
)


def test_get_page():
    page = get_page(notion)
    assert page["id"] == "2cbe873c-2459-409f-afe3-e73e750115ac"


def test_get_blocks():
    page = get_page(notion)
    blocks = get_blocks(notion, page)
    assert len(blocks) == 1
    assert blocks[0]["id"] == "e8f27210-12a7-4ecc-a584-960532543426"


def test_list_todos():
    page = get_page(notion)
    todos = list_todos(notion, page)
    assert len(todos) == 1
    assert "Test to-do content" in todos[0]


def test_add_block():
    add_block(notion, "fake_page_id", "Test block content")
    notion.blocks.children.append.assert_called_once()


def test_add_todo():
    notion.reset_mock()  # Reset the mock call count
    content = "Test new to-do item"
    page = get_page(notion)
    add_todo(notion, content, parent_id=page["id"])
    notion.blocks.children.append.assert_called_once()


def test_mark_checked():
    notion.reset_mock()
    mark_checked(notion, "fake_block_id")
    notion.blocks.update.assert_called_once()


def test_get_block_by_index():
    block = get_block_by_index(notion, 1)
    assert block["id"] == "e8f27210-12a7-4ecc-a584-960532543426"
    assert block["type"] == "to_do"


def test_mark_todo_checked():
    notion.reset_mock()
    mark_todo_checked(notion, 1)
    notion.blocks.update.assert_called_once()


def test_delete_block():
    delete_block(notion, "fake_block_id")
    notion.blocks.delete.assert_called_once()


def test_delete_todo():
    notion.reset_mock()
    delete_todo(notion, 1)
    notion.blocks.delete.assert_called_once()
