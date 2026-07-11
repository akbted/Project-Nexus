import pytest

@pytest.fixture
def sample_project_data():
    """Sample OpenProject project data matching API response."""
    return {
        "id": 1,
        "identifier": "test-project",
        "name": "Test Project",
        "active": True,
        "public": True,
        "description": {
            "format": "markdown",
            "raw": "A test project",
            "html": "<p>A test project</p>",
        },
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
    }

@pytest.fixture
def sample_work_package_data():
    """Sample OpenProject work package data matching API response."""
    return {
        "id": 100,
        "subject": "Test Task",
        "description": {"format": "markdown", "raw": "", "html": ""},
        "startDate": None,
        "dueDate": None,
        "percentageDone": None,
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
        "_links": {
            "status": {"href": "/api/v3/statuses/1", "title": "New"},
            "priority": {"href": "/api/v3/priorities/1", "title": "Normal"},
            "assignee": {"href": "/api/v3/users/1", "title": "Test User"},
            "author": {"href": "/api/v3/users/1", "title": "Test User"},
            "parent": {"href": None, "title": None},
            "children": [],
            "project": {"href": "/api/v3/projects/1", "title": "Test Project"},
        },
    }

@pytest.fixture
def mock_httpx_response():
    """Factory fixture for creating mock HTTP responses."""
    def _make_response(json_data, status_code=200):
        from unittest.mock import MagicMock
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = json_data
        response.raise_for_status = MagicMock()
        return response
    return _make_response