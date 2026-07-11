"""
Tests for Pydantic schemas (Project and WorkPackage).

These tests verify that our models correctly parse OpenProject API responses.
No mocking needed — these are pure unit tests against Pydantic.
"""
import pytest
from pydantic import ValidationError
from src.schema.project import Project, Description
from src.schema.work_package import WorkPackage, WorkPackageDescription


# ============================================================================
# PROJECT TESTS
# ============================================================================

def test_project_creation(sample_project_data):
    """
    Can we create a Project from API data?

    sample_project_data comes from conftest.py (the root-level one).
    pytest sees the parameter name 'sample_project_data', finds the fixture,
    calls it, and passes the result here.
    """
    project = Project(**sample_project_data)

    assert project.id == 1
    assert project.name == "Test Project"
    assert project.identifier == "test-project"
    assert project.active is True
    assert project.public is True


def test_project_aliases(sample_project_data):
    """
    Does the alias mapping work?

    OpenProject API sends 'createdAt' (camelCase).
    Our Pydantic model maps it to 'created_at' (snake_case) via Field(alias="createdAt").
    """
    project = Project(**sample_project_data)

    assert project.created_at is not None
    assert project.updated_at is not None


def test_project_description_nested(sample_project_data):
    """
    Does the nested Description object parse correctly?

    OpenProject sends: {"description": {"format": "markdown", "raw": "...", "html": "..."}}
    Our model has: description: Description | None = None
    """
    project = Project(**sample_project_data)

    assert project.description is not None
    assert isinstance(project.description, Description)
    assert project.description.format == "markdown"
    assert project.description.raw == "A test project"


def test_project_without_description():
    """
    Does Project work when description is missing?

    Some projects have empty descriptions. Our model allows description=None.
    """
    data = {
        "id": 2,
        "identifier": "no-desc",
        "name": "No Description Project",
        "active": True,
        "public": False,
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
    }
    project = Project(**data)

    assert project.description is None


def test_project_rejects_missing_fields():
    """
    Does Pydantic raise an error when required fields are missing?

    This test does NOT use a fixture — it provides its own incomplete data.
    """
    incomplete_data = {
        "id": 1,
        # missing: name, identifier, active, public, createdAt, updatedAt
    }

    with pytest.raises(ValidationError):
        Project(**incomplete_data)


def test_project_rejects_wrong_types():
    """
    Does Pydantic raise an error when field types are wrong?

    'id' should be int, not a string.
    """
    bad_data = {
        "id": "not_an_int",  # should be int
        "identifier": "test",
        "name": "Test",
        "active": True,
        "public": True,
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
    }

    with pytest.raises(ValidationError):
        Project(**bad_data)


# ============================================================================
# WORK PACKAGE TESTS
# ============================================================================

def test_work_package_creation(sample_work_package_data):
    """
    Can we create a WorkPackage from API data?

    sample_work_package_data comes from conftest.py.
    It includes the _links field which maps to our 'links' attribute.
    """
    wp = WorkPackage(**sample_work_package_data)

    assert wp.id == 100
    assert wp.subject == "Test Task"


def test_work_package_links_alias(sample_work_package_data):
    """
    Does the _links → links alias mapping work?

    OpenProject sends: {"_links": {...}}
    Our model has: links: dict = Field(alias="_links")
    """
    wp = WorkPackage(**sample_work_package_data)

    assert isinstance(wp.links, dict)
    assert "status" in wp.links
    assert "assignee" in wp.links


def test_work_package_optional_fields():
    """
    Do optional fields default to None when not provided?
    """
    data = {
        "id": 200,
        "subject": "Minimal Task",
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
        "_links": {},
    }
    wp = WorkPackage(**data)

    assert wp.description is None
    assert wp.startDate is None
    assert wp.dueDate is None
    assert wp.percentageDone is None


def test_work_package_description_nested(sample_work_package_data):
    """
    Does the nested WorkPackageDescription parse correctly?
    """
    wp = WorkPackage(**sample_work_package_data)

    assert isinstance(wp.description, WorkPackageDescription)
    assert wp.description.format == "markdown"
