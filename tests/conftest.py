"""Pytest configuration and shared fixtures."""

import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def clean_env():
    """Ensure clean environment for each test."""
    # Store original env
    original_env = os.environ.copy()
    
    # Remove notion-related env vars
    for key in ["NOTION_API_KEY", "NOTION_PAGE_ID", "LOCAL_TIMEZONE"]:
        os.environ.pop(key, None)
    
    yield
    
    # Restore original env
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_notion():
    """Create a mock Notion client."""
    notion = MagicMock()
    return notion


@pytest.fixture
def sample_page():
    """Sample Notion page response."""
    return {
        "object": "page",
        "id": "test-page-id-123",
        "created_time": "2024-01-01T00:00:00.000Z",
        "last_edited_time": "2024-01-01T00:00:00.000Z",
    }


@pytest.fixture
def sample_todo():
    """Sample todo block."""
    return {
        "object": "block",
        "id": "block-id-1",
        "type": "to_do",
        "created_time": "2024-01-01T12:00:00.000Z",
        "to_do": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "Test task"},
                    "plain_text": "Test task",
                }
            ],
            "checked": False,
        },
    }
