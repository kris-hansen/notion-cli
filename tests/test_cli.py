"""Tests for notion-cli."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Ensure we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from notioncli.cli import (
    add_block,
    add_todo,
    delete_block,
    delete_todo,
    get_block_by_index,
    get_block_content,
    get_blocks,
    get_config,
    get_page,
    list_all_blocks,
    list_todos,
    mark_todo_checked,
    main,
)


# Sample API responses
SAMPLE_PAGE = {
    "object": "page",
    "id": "test-page-id-123",
    "created_time": "2024-01-01T00:00:00.000Z",
    "last_edited_time": "2024-01-01T00:00:00.000Z",
}

SAMPLE_TODO_BLOCK = {
    "object": "block",
    "id": "block-id-1",
    "type": "to_do",
    "created_time": "2024-01-01T12:00:00.000Z",
    "to_do": {
        "rich_text": [
            {
                "type": "text",
                "text": {"content": "Test task 1"},
                "plain_text": "Test task 1",
            }
        ],
        "checked": False,
    },
}

SAMPLE_TODO_BLOCK_CHECKED = {
    "object": "block",
    "id": "block-id-2",
    "type": "to_do",
    "created_time": "2024-01-02T12:00:00.000Z",
    "to_do": {
        "rich_text": [
            {
                "type": "text",
                "text": {"content": "Completed task"},
                "plain_text": "Completed task",
            }
        ],
        "checked": True,
    },
}

SAMPLE_PARAGRAPH_BLOCK = {
    "object": "block",
    "id": "block-id-3",
    "type": "paragraph",
    "created_time": "2024-01-03T12:00:00.000Z",
    "paragraph": {
        "rich_text": [{"plain_text": "Just a paragraph"}],
    },
}


class TestGetConfig:
    """Tests for get_config function."""

    def test_missing_api_key(self):
        """Test error when NOTION_API_KEY is not set."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SystemExit) as exc_info:
                get_config()
            assert exc_info.value.code == 1

    def test_missing_page_id(self):
        """Test error when NOTION_PAGE_ID is not set."""
        with patch.dict(os.environ, {"NOTION_API_KEY": "test-key"}, clear=True):
            with pytest.raises(SystemExit) as exc_info:
                get_config()
            assert exc_info.value.code == 1

    def test_valid_config(self):
        """Test successful config retrieval."""
        env = {
            "NOTION_API_KEY": "test-api-key",
            "NOTION_PAGE_ID": "test-page-id",
            "LOCAL_TIMEZONE": "America/New_York",
        }
        with patch.dict(os.environ, env, clear=True):
            config = get_config()
            assert config["api_key"] == "test-api-key"
            assert config["page_id"] == "test-page-id"
            assert config["timezone"] == "America/New_York"

    def test_default_timezone(self):
        """Test that timezone defaults to UTC."""
        env = {
            "NOTION_API_KEY": "test-api-key",
            "NOTION_PAGE_ID": "test-page-id",
        }
        with patch.dict(os.environ, env, clear=True):
            config = get_config()
            assert config["timezone"] == "UTC"


class TestGetPage:
    """Tests for get_page function."""

    def test_get_page_success(self):
        """Test successful page retrieval."""
        notion = MagicMock()
        notion.pages.retrieve.return_value = SAMPLE_PAGE

        page = get_page(notion, "test-page-id")

        assert page["id"] == "test-page-id-123"
        notion.pages.retrieve.assert_called_once_with("test-page-id")


class TestGetBlocks:
    """Tests for get_blocks function."""

    def test_get_blocks_success(self):
        """Test successful blocks retrieval."""
        notion = MagicMock()
        notion.blocks.children.list.return_value = {
            "results": [SAMPLE_TODO_BLOCK, SAMPLE_TODO_BLOCK_CHECKED]
        }

        blocks = get_blocks(notion, SAMPLE_PAGE)

        assert len(blocks) == 2
        notion.blocks.children.list.assert_called_once_with(block_id="test-page-id-123")

    def test_get_blocks_empty(self):
        """Test empty blocks list."""
        notion = MagicMock()
        notion.blocks.children.list.return_value = {"results": []}

        blocks = get_blocks(notion, SAMPLE_PAGE)

        assert blocks == []


class TestListTodos:
    """Tests for list_todos function."""

    def test_list_todos_success(self):
        """Test listing todos."""
        notion = MagicMock()
        notion.blocks.children.list.return_value = {
            "results": [SAMPLE_TODO_BLOCK, SAMPLE_TODO_BLOCK_CHECKED]
        }

        todos = list_todos(notion, SAMPLE_PAGE, "UTC")

        assert len(todos) == 2
        assert todos[0]["content"] == "Test task 1"
        assert todos[0]["checked"] is False
        assert todos[1]["content"] == "Completed task"
        assert todos[1]["checked"] is True

    def test_list_todos_empty(self):
        """Test empty todo list."""
        notion = MagicMock()
        notion.blocks.children.list.return_value = {"results": []}

        todos = list_todos(notion, SAMPLE_PAGE, "UTC")

        assert todos == []

    def test_list_todos_filters_non_todos(self):
        """Test that non-todo blocks are filtered out."""
        notion = MagicMock()
        notion.blocks.children.list.return_value = {
            "results": [SAMPLE_TODO_BLOCK, SAMPLE_PARAGRAPH_BLOCK]
        }

        todos = list_todos(notion, SAMPLE_PAGE, "UTC")

        assert len(todos) == 1
        assert todos[0]["content"] == "Test task 1"


class TestAddTodo:
    """Tests for add_todo function."""

    def test_add_todo_success(self, capsys):
        """Test adding a todo."""
        notion = MagicMock()

        add_todo(notion, "New task", "test-page-id")

        notion.blocks.children.append.assert_called_once()
        call_args = notion.blocks.children.append.call_args
        assert call_args[0][0] == "test-page-id"
        
        children = call_args[1]["children"]
        assert len(children) == 1
        assert children[0]["to_do"]["rich_text"][0]["text"]["content"] == "New task"
        assert children[0]["to_do"]["checked"] is False

        captured = capsys.readouterr()
        assert "New task" in captured.out


class TestGetBlockByIndex:
    """Tests for get_block_by_index function."""

    def test_get_block_by_index_success(self):
        """Test getting block by index."""
        notion = MagicMock()
        notion.blocks.children.list.return_value = {
            "results": [SAMPLE_TODO_BLOCK, SAMPLE_TODO_BLOCK_CHECKED]
        }

        block = get_block_by_index(notion, SAMPLE_PAGE, 1)

        assert block["id"] == "block-id-1"

    def test_get_block_by_index_second(self):
        """Test getting second block."""
        notion = MagicMock()
        notion.blocks.children.list.return_value = {
            "results": [SAMPLE_TODO_BLOCK, SAMPLE_TODO_BLOCK_CHECKED]
        }

        block = get_block_by_index(notion, SAMPLE_PAGE, 2)

        assert block["id"] == "block-id-2"

    def test_get_block_by_index_not_found(self):
        """Test error when index is out of range."""
        notion = MagicMock()
        notion.blocks.children.list.return_value = {
            "results": [SAMPLE_TODO_BLOCK]
        }

        with pytest.raises(SystemExit) as exc_info:
            get_block_by_index(notion, SAMPLE_PAGE, 99)
        assert exc_info.value.code == 1


class TestMarkTodoChecked:
    """Tests for mark_todo_checked function."""

    def test_mark_todo_checked_success(self, capsys):
        """Test marking todo as checked."""
        notion = MagicMock()
        notion.blocks.children.list.return_value = {
            "results": [SAMPLE_TODO_BLOCK]
        }

        mark_todo_checked(notion, SAMPLE_PAGE, 1)

        notion.blocks.update.assert_called_once_with(
            "block-id-1", to_do={"checked": True}
        )

        captured = capsys.readouterr()
        assert "Completed" in captured.out

    def test_mark_non_todo_fails(self):
        """Test error when trying to mark non-todo as checked."""
        notion = MagicMock()
        notion.blocks.children.list.return_value = {
            "results": [SAMPLE_PARAGRAPH_BLOCK]
        }

        with pytest.raises(SystemExit) as exc_info:
            mark_todo_checked(notion, SAMPLE_PAGE, 1)
        assert exc_info.value.code == 1


class TestDeleteTodo:
    """Tests for delete_todo function."""

    def test_delete_todo_success(self, capsys):
        """Test deleting a todo."""
        notion = MagicMock()
        notion.blocks.children.list.return_value = {
            "results": [SAMPLE_TODO_BLOCK]
        }

        delete_todo(notion, SAMPLE_PAGE, 1)

        notion.blocks.delete.assert_called_once_with("block-id-1")

        captured = capsys.readouterr()
        assert "Deleted" in captured.out


class TestMain:
    """Tests for main CLI function."""

    @pytest.fixture
    def mock_env(self):
        """Set up environment variables for tests."""
        env = {
            "NOTION_API_KEY": "test-api-key",
            "NOTION_PAGE_ID": "test-page-id",
        }
        with patch.dict(os.environ, env, clear=True):
            yield

    def test_main_no_command(self, mock_env, capsys):
        """Test main with no command shows help."""
        with patch("sys.argv", ["notion"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_main_list_command(self, mock_env, capsys):
        """Test main with list command."""
        with patch("sys.argv", ["notion", "list"]):
            with patch("notioncli.cli.Client") as mock_client:
                mock_notion = MagicMock()
                mock_client.return_value = mock_notion
                mock_notion.pages.retrieve.return_value = SAMPLE_PAGE
                mock_notion.blocks.children.list.return_value = {
                    "results": [SAMPLE_TODO_BLOCK]
                }

                main()

                captured = capsys.readouterr()
                assert "Test task 1" in captured.out
                assert "1 pending" in captured.out

    def test_main_add_command(self, mock_env, capsys):
        """Test main with add command."""
        with patch("sys.argv", ["notion", "add", "New task"]):
            with patch("notioncli.cli.Client") as mock_client:
                mock_notion = MagicMock()
                mock_client.return_value = mock_notion
                mock_notion.pages.retrieve.return_value = SAMPLE_PAGE

                main()

                mock_notion.blocks.children.append.assert_called_once()
                captured = capsys.readouterr()
                assert "New task" in captured.out

    def test_main_done_command(self, mock_env, capsys):
        """Test main with done command."""
        with patch("sys.argv", ["notion", "done", "1"]):
            with patch("notioncli.cli.Client") as mock_client:
                mock_notion = MagicMock()
                mock_client.return_value = mock_notion
                mock_notion.pages.retrieve.return_value = SAMPLE_PAGE
                mock_notion.blocks.children.list.return_value = {
                    "results": [SAMPLE_TODO_BLOCK]
                }

                main()

                mock_notion.blocks.update.assert_called_once()

    def test_main_delete_command(self, mock_env, capsys):
        """Test main with delete command."""
        with patch("sys.argv", ["notion", "delete", "1"]):
            with patch("notioncli.cli.Client") as mock_client:
                mock_notion = MagicMock()
                mock_client.return_value = mock_notion
                mock_notion.pages.retrieve.return_value = SAMPLE_PAGE
                mock_notion.blocks.children.list.return_value = {
                    "results": [SAMPLE_TODO_BLOCK]
                }

                main()

                mock_notion.blocks.delete.assert_called_once()

    def test_main_aliases_work(self, mock_env):
        """Test that command aliases work."""
        aliases = [
            (["notion", "ls"], "list"),
            (["notion", "a", "task"], "add"),
            (["notion", "rm", "1"], "delete"),
            (["notion", "check", "1"], "done"),
        ]

        for argv, expected_cmd in aliases:
            with patch("sys.argv", argv):
                with patch("notioncli.cli.Client") as mock_client:
                    mock_notion = MagicMock()
                    mock_client.return_value = mock_notion
                    mock_notion.pages.retrieve.return_value = SAMPLE_PAGE
                    mock_notion.blocks.children.list.return_value = {
                        "results": [SAMPLE_TODO_BLOCK]
                    }

                    # Should not raise
                    main()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_todo_content(self):
        """Test handling of empty todo content."""
        notion = MagicMock()
        empty_todo = {
            "object": "block",
            "id": "empty-block",
            "type": "to_do",
            "created_time": "2024-01-01T12:00:00.000Z",
            "to_do": {
                "rich_text": [],
                "checked": False,
            },
        }
        notion.blocks.children.list.return_value = {"results": [empty_todo]}

        todos = list_todos(notion, SAMPLE_PAGE, "UTC")

        assert len(todos) == 1
        assert todos[0]["content"] == "(empty)"

    def test_timezone_conversion(self):
        """Test timezone is properly applied."""
        notion = MagicMock()
        notion.blocks.children.list.return_value = {
            "results": [SAMPLE_TODO_BLOCK]
        }

        todos_utc = list_todos(notion, SAMPLE_PAGE, "UTC")
        todos_la = list_todos(notion, SAMPLE_PAGE, "America/Los_Angeles")

        # Both should have the same task but different timestamps
        assert todos_utc[0]["content"] == todos_la[0]["content"]
        assert "UTC" in todos_utc[0]["created"]
        assert "PST" in todos_la[0]["created"] or "PDT" in todos_la[0]["created"]


# === New Block Types Tests ===

SAMPLE_HEADING_BLOCK = {
    "object": "block",
    "id": "heading-block-1",
    "type": "heading_1",
    "created_time": "2024-01-04T12:00:00.000Z",
    "heading_1": {
        "rich_text": [{"plain_text": "My Heading"}],
    },
}

SAMPLE_BULLET_BLOCK = {
    "object": "block",
    "id": "bullet-block-1",
    "type": "bulleted_list_item",
    "created_time": "2024-01-05T12:00:00.000Z",
    "bulleted_list_item": {
        "rich_text": [{"plain_text": "Bullet point"}],
    },
}

SAMPLE_DIVIDER_BLOCK = {
    "object": "block",
    "id": "divider-block-1",
    "type": "divider",
    "created_time": "2024-01-06T12:00:00.000Z",
    "divider": {},
}


class TestGetBlockContent:
    """Tests for get_block_content function."""

    def test_get_todo_content(self):
        """Test extracting content from to-do block."""
        content = get_block_content(SAMPLE_TODO_BLOCK)
        assert content == "Test task 1"

    def test_get_paragraph_content(self):
        """Test extracting content from paragraph block."""
        content = get_block_content(SAMPLE_PARAGRAPH_BLOCK)
        assert content == "Just a paragraph"

    def test_get_heading_content(self):
        """Test extracting content from heading block."""
        content = get_block_content(SAMPLE_HEADING_BLOCK)
        assert content == "My Heading"

    def test_get_divider_content(self):
        """Test extracting content from divider block."""
        content = get_block_content(SAMPLE_DIVIDER_BLOCK)
        assert "─" in content  # Divider line

    def test_get_empty_content(self):
        """Test extracting content from block with no text."""
        empty_block = {
            "type": "paragraph",
            "paragraph": {"rich_text": []},
        }
        content = get_block_content(empty_block)
        assert content == "(empty)"


class TestListAllBlocks:
    """Tests for list_all_blocks function."""

    def test_list_all_blocks_success(self):
        """Test listing all blocks."""
        notion = MagicMock()
        notion.blocks.children.list.return_value = {
            "results": [SAMPLE_TODO_BLOCK, SAMPLE_PARAGRAPH_BLOCK, SAMPLE_HEADING_BLOCK]
        }

        blocks = list_all_blocks(notion, SAMPLE_PAGE, "UTC")

        assert len(blocks) == 3
        assert blocks[0]["type"] == "to_do"
        assert blocks[1]["type"] == "paragraph"
        assert blocks[2]["type"] == "heading_1"

    def test_list_all_blocks_with_filter(self):
        """Test listing blocks with type filter."""
        notion = MagicMock()
        notion.blocks.children.list.return_value = {
            "results": [SAMPLE_TODO_BLOCK, SAMPLE_PARAGRAPH_BLOCK, SAMPLE_HEADING_BLOCK]
        }

        blocks = list_all_blocks(notion, SAMPLE_PAGE, "UTC", filter_type="heading_1")

        assert len(blocks) == 1
        assert blocks[0]["type"] == "heading_1"
        assert blocks[0]["content"] == "My Heading"

    def test_list_all_blocks_empty(self):
        """Test empty blocks list."""
        notion = MagicMock()
        notion.blocks.children.list.return_value = {"results": []}

        blocks = list_all_blocks(notion, SAMPLE_PAGE, "UTC")

        assert blocks == []

    def test_list_all_blocks_includes_icons(self):
        """Test that blocks have correct icons."""
        notion = MagicMock()
        notion.blocks.children.list.return_value = {
            "results": [SAMPLE_TODO_BLOCK, SAMPLE_HEADING_BLOCK]
        }

        blocks = list_all_blocks(notion, SAMPLE_PAGE, "UTC")

        assert blocks[0]["icon"] == "☐"  # Unchecked to-do
        assert blocks[1]["icon"] == "H1"  # Heading 1


class TestAddBlock:
    """Tests for add_block function."""

    def test_add_paragraph(self, capsys):
        """Test adding a paragraph block."""
        notion = MagicMock()

        add_block(notion, "Hello world", "test-page-id", "paragraph")

        notion.blocks.children.append.assert_called_once()
        call_args = notion.blocks.children.append.call_args
        children = call_args[1]["children"]
        
        assert children[0]["type"] == "paragraph"
        assert children[0]["paragraph"]["rich_text"][0]["text"]["content"] == "Hello world"

        captured = capsys.readouterr()
        assert "paragraph" in captured.out
        assert "Hello world" in captured.out

    def test_add_heading(self, capsys):
        """Test adding a heading block."""
        notion = MagicMock()

        add_block(notion, "My Title", "test-page-id", "heading_1")

        call_args = notion.blocks.children.append.call_args
        children = call_args[1]["children"]
        
        assert children[0]["type"] == "heading_1"
        assert children[0]["heading_1"]["rich_text"][0]["text"]["content"] == "My Title"

    def test_add_divider(self, capsys):
        """Test adding a divider block."""
        notion = MagicMock()

        add_block(notion, "", "test-page-id", "divider")

        call_args = notion.blocks.children.append.call_args
        children = call_args[1]["children"]
        
        assert children[0]["type"] == "divider"
        assert "divider" in children[0]

    def test_add_bulleted_list(self, capsys):
        """Test adding a bulleted list item."""
        notion = MagicMock()

        add_block(notion, "List item", "test-page-id", "bulleted_list_item")

        call_args = notion.blocks.children.append.call_args
        children = call_args[1]["children"]
        
        assert children[0]["type"] == "bulleted_list_item"


class TestDeleteBlock:
    """Tests for delete_block function."""

    def test_delete_block_success(self, capsys):
        """Test deleting any block type."""
        notion = MagicMock()
        notion.blocks.children.list.return_value = {
            "results": [SAMPLE_PARAGRAPH_BLOCK]
        }

        delete_block(notion, SAMPLE_PAGE, 1)

        notion.blocks.delete.assert_called_once_with("block-id-3")

        captured = capsys.readouterr()
        assert "Deleted" in captured.out
        assert "paragraph" in captured.out


class TestBlocksCommands:
    """Tests for blocks subcommand in main."""

    @pytest.fixture
    def mock_env(self):
        """Set up environment variables for tests."""
        env = {
            "NOTION_API_KEY": "test-api-key",
            "NOTION_PAGE_ID": "test-page-id",
        }
        with patch.dict(os.environ, env, clear=True):
            yield

    def test_blocks_list(self, mock_env, capsys):
        """Test blocks list command."""
        with patch("sys.argv", ["notion", "blocks", "list"]):
            with patch("notioncli.cli.Client") as mock_client:
                mock_notion = MagicMock()
                mock_client.return_value = mock_notion
                mock_notion.pages.retrieve.return_value = SAMPLE_PAGE
                mock_notion.blocks.children.list.return_value = {
                    "results": [SAMPLE_TODO_BLOCK, SAMPLE_PARAGRAPH_BLOCK]
                }

                main()

                captured = capsys.readouterr()
                assert "to_do" in captured.out
                assert "paragraph" in captured.out

    def test_blocks_list_with_filter(self, mock_env, capsys):
        """Test blocks list with type filter."""
        with patch("sys.argv", ["notion", "blocks", "list", "--type", "to_do"]):
            with patch("notioncli.cli.Client") as mock_client:
                mock_notion = MagicMock()
                mock_client.return_value = mock_notion
                mock_notion.pages.retrieve.return_value = SAMPLE_PAGE
                mock_notion.blocks.children.list.return_value = {
                    "results": [SAMPLE_TODO_BLOCK, SAMPLE_PARAGRAPH_BLOCK]
                }

                main()

                captured = capsys.readouterr()
                assert "to_do" in captured.out
                # Paragraph should be filtered out (not in summary)

    def test_blocks_add_paragraph(self, mock_env, capsys):
        """Test blocks add command for paragraph."""
        with patch("sys.argv", ["notion", "blocks", "add", "New paragraph"]):
            with patch("notioncli.cli.Client") as mock_client:
                mock_notion = MagicMock()
                mock_client.return_value = mock_notion
                mock_notion.pages.retrieve.return_value = SAMPLE_PAGE

                main()

                mock_notion.blocks.children.append.assert_called_once()
                captured = capsys.readouterr()
                assert "paragraph" in captured.out

    def test_blocks_add_heading(self, mock_env, capsys):
        """Test blocks add command for heading."""
        with patch("sys.argv", ["notion", "blocks", "add", "My Heading", "-t", "heading_1"]):
            with patch("notioncli.cli.Client") as mock_client:
                mock_notion = MagicMock()
                mock_client.return_value = mock_notion
                mock_notion.pages.retrieve.return_value = SAMPLE_PAGE

                main()

                call_args = mock_notion.blocks.children.append.call_args
                children = call_args[1]["children"]
                assert children[0]["type"] == "heading_1"

    def test_blocks_delete(self, mock_env, capsys):
        """Test blocks delete command."""
        with patch("sys.argv", ["notion", "blocks", "delete", "1"]):
            with patch("notioncli.cli.Client") as mock_client:
                mock_notion = MagicMock()
                mock_client.return_value = mock_notion
                mock_notion.pages.retrieve.return_value = SAMPLE_PAGE
                mock_notion.blocks.children.list.return_value = {
                    "results": [SAMPLE_PARAGRAPH_BLOCK]
                }

                main()

                mock_notion.blocks.delete.assert_called_once()

    def test_blocks_alias_works(self, mock_env, capsys):
        """Test that 'b' alias works for blocks."""
        with patch("sys.argv", ["notion", "b", "list"]):
            with patch("notioncli.cli.Client") as mock_client:
                mock_notion = MagicMock()
                mock_client.return_value = mock_notion
                mock_notion.pages.retrieve.return_value = SAMPLE_PAGE
                mock_notion.blocks.children.list.return_value = {
                    "results": [SAMPLE_TODO_BLOCK]
                }

                main()

                captured = capsys.readouterr()
                assert "to_do" in captured.out
