"""
Tests for tool functions (list_openproject_projects, list_project_workpackages).

Concepts learned:
- Mocking HTTP responses: simulate what the API returns without network calls
- @pytest.mark.asyncio: tells pytest this is an async test
- Mock chaining: mock_client.get_client().get() — one mock calls another
- Asserting on mocks: verifying the right API calls were made
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from src.tools.list_project import list_openproject_projects
from src.tools.list_work_packages import list_project_workpackages
from src.schema.project import Project
from src.schema.work_package import WorkPackage


# ============================================================================
# HELPER: Create a mock client
# ============================================================================

def make_mock_client(json_data):
    """
    Create a mock OpenProjectClient that returns specific JSON data.

    This helper builds the mock chain:
      mock_client.get_client() → mock_http
      mock_http.get() → mock_response
      mock_response.json() → json_data
    """
    mock_response = MagicMock()
    mock_response.json.return_value = json_data
    mock_response.raise_for_status = MagicMock()

    mock_http = AsyncMock()
    mock_http.get.return_value = mock_response

    mock_client = MagicMock()
    mock_client.get_client.return_value = mock_http

    return mock_client, mock_http


# ============================================================================
# LIST PROJECTS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_list_projects_returns_projects(sample_project_data):
    """
    Does list_openproject_projects return a list of Project objects?

    We mock the HTTP response to return one project, then verify
    the function parses it into a Project Pydantic model.
    """
    api_response = {
        "_embedded": {
            "elements": [sample_project_data]
        }
    }
    mock_client, mock_http = make_mock_client(api_response)

    projects = await list_openproject_projects(mock_client)

    # Should return a list with one Project
    assert len(projects) == 1
    assert isinstance(projects[0], Project)
    assert projects[0].id == 1
    assert projects[0].name == "Test Project"


@pytest.mark.asyncio
async def test_list_projects_empty_response():
    """
    Does list_openproject_projects handle an empty elements list?

    Some projects might have no work packages or the API returns empty.
    """
    api_response = {"_embedded": {"elements": []}}
    mock_client, mock_http = make_mock_client(api_response)

    projects = await list_openproject_projects(mock_client)

    assert projects == []
    assert isinstance(projects, list)


@pytest.mark.asyncio
async def test_list_projects_calls_correct_url():
    """
    Does list_openproject_projects call the correct API endpoint?

    It should call GET /api/v3/projects.
    """
    api_response = {"_embedded": {"elements": []}}
    mock_client, mock_http = make_mock_client(api_response)

    await list_openproject_projects(mock_client)

    # Verify the correct URL was called
    mock_http.get.assert_called_once_with("/api/v3/projects")


@pytest.mark.asyncio
async def test_list_projects_multiple_projects(sample_project_data):
    """
    Does list_openproject_projects handle multiple projects?
    """
    second_project = {
        "id": 2,
        "identifier": "second-project",
        "name": "Second Project",
        "active": False,
        "public": True,
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
    }
    api_response = {
        "_embedded": {
            "elements": [sample_project_data, second_project]
        }
    }
    mock_client, mock_http = make_mock_client(api_response)

    projects = await list_openproject_projects(mock_client)

    assert len(projects) == 2
    assert projects[0].name == "Test Project"
    assert projects[1].name == "Second Project"


@pytest.mark.asyncio
async def test_list_projects_http_error():
    """
    Does list_openproject_projects propagate HTTP errors?

    When the API returns a 4xx or 5xx status, raise_for_status() raises.
    This test verifies the error is NOT swallowed — it bubbles up.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("404 Not Found")

    mock_http = AsyncMock()
    mock_http.get.return_value = mock_response

    mock_client = MagicMock()
    mock_client.get_client.return_value = mock_http

    with pytest.raises(Exception, match="404 Not Found"):
        await list_openproject_projects(mock_client)


# ============================================================================
# LIST WORK PACKAGES TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_list_work_packages_returns_list(sample_work_package_data):
    """
    Does list_project_workpackages return a list of WorkPackage objects?
    """
    api_response = {
        "_embedded": {
            "elements": [sample_work_package_data]
        }
    }
    mock_client, mock_http = make_mock_client(api_response)

    work_packages = await list_project_workpackages(mock_client, project_id=1)

    assert len(work_packages) == 1
    assert isinstance(work_packages[0], WorkPackage)
    assert work_packages[0].id == 100
    assert work_packages[0].subject == "Test Task"


@pytest.mark.asyncio
async def test_list_work_packages_correct_url():
    """
    Does list_project_workpackages call the correct API endpoint?

    It should call GET /api/v3/projects/{project_id}/work_packages.
    """
    api_response = {"_embedded": {"elements": []}}
    mock_client, mock_http = make_mock_client(api_response)

    await list_project_workpackages(mock_client, project_id=42)

    mock_http.get.assert_called_once_with("/api/v3/projects/42/work_packages")


@pytest.mark.asyncio
async def test_list_work_packages_empty_response():
    """
    Does list_project_workpackages handle an empty elements list?
    """
    api_response = {"_embedded": {"elements": []}}
    mock_client, mock_http = make_mock_client(api_response)

    work_packages = await list_project_workpackages(mock_client, project_id=1)

    assert work_packages == []
