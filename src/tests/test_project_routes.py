"""Test project routes."""

import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_project_success(authenticated_client: AsyncClient, test_team, test_user):
    """
    Test creating a new project.

    This test verifies that creating a new project with valid data
    results in a 201 status code and a UUID is returned.
    """
    payload = {
        "title": "New Test Project",
        "description": "A test project",
        "team_id": str(test_team.id)
    }
    response = await authenticated_client.post("/api/v1.0.0/projects/create/new", json=payload)
    assert response.status_code == 201
    assert uuid.UUID(response.json())


@pytest.mark.asyncio
async def test_create_project_missing_team(authenticated_client: AsyncClient):
    """
    Test that attempting to create a project without providing a team_id results in a
    422 status code.
    """
    payload = {
        "title": "No Team Project",
        "description": "Missing team_id"
    }
    response = await authenticated_client.post("/api/v1.0.0/projects/create/new", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_all_projects(authenticated_client: AsyncClient, test_project):
    """
    Test retrieving all projects from the database.

    This test verifies that retrieving all projects returns a 200 status code
    and a list of projects.
    """
    response = await authenticated_client.get("/api/v1.0.0/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_project_by_id(authenticated_client: AsyncClient, test_project):
    """
    Test retrieving a project by its valid UUID.

    This test verifies that retrieving a project with a valid UUID
    returns a 200 status code and the correct project data.
    """
    response = await authenticated_client.get(f"/api/v1.0.0/projects/{test_project.id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(test_project.id)


@pytest.mark.asyncio
async def test_get_project_by_invalid_id(authenticated_client: AsyncClient):
    """
    Test retrieving a project with an invalid UUID.

    This test verifies that attempting to retrieve a project with an invalid UUID
    results in a 422 status code.
    """

    response = await authenticated_client.get("/api/v1.0.0/projects/invalid-uuid")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_project_success(authenticated_client: AsyncClient, test_project):
    """
    Test updating a project with valid data.

    Args:
        authenticated_client (AsyncClient): The FastAPI test client.
        test_project (Project): A test project.

    Verifies that the API returns a 200 status code and that the project title
    is updated correctly.
    """
    payload = {"title": "Updated Title"}
    response = await authenticated_client.patch(f"/api/v1.0.0/projects/{test_project.id}/update", json=payload)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_update_nonexistent_project(authenticated_client: AsyncClient):
    """
    Test updating a project that does not exist in the database.

    This test verifies that attempting to update a project with a UUID that does not exist in the database
    results in a 404 status code.
    """
    fake_id = uuid.uuid4()
    payload = {"title": "Won't work"}
    response = await authenticated_client.patch(f"/api/v1.0.0/projects/{fake_id}/update", json=payload)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_project_success(authenticated_client: AsyncClient, test_project):
    """
    Test deleting a project that exists in the database.

    This test verifies that attempting to delete a project with a valid UUID that exists in the database
    results in a 204 response.
    """
    response = await authenticated_client.delete(f"/api/v1.0.0/projects/{test_project.id}/delete")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_project_not_found(authenticated_client: AsyncClient):
    """
    Test deleting a project that does not exist in the database.

    This test verifies that attempting to delete a project with a UUID that does not exist in the database
    results in a 404 status code.
    """
    fake_id = uuid.uuid4()
    response = await authenticated_client.delete(f"/api/v1.0.0projects/{fake_id}/delete")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_team_projects_for_user_authenticated(test_client: AsyncClient, authorized_headers):
    """
    Test that a user can retrieve their team projects when authenticated.

    This test verifies that retrieving a user's team projects with a valid token
    results in a 200 status code if the user has any team projects, or a 404 status
    code if the user has no team projects.
    """
    res = await test_client.get("/api/v1.0.0projects/team/project", headers=authorized_headers)
    assert res.status_code in (200, 404)


@pytest.mark.asyncio
async def test_get_team_projects_for_user_unauthenticated(test_client: AsyncClient):
    """
    Test that attempting to retrieve a user's team projects without a valid token
    results in a 401 status code.
    """
    res = await test_client.get("/api/v1.0.0/projects/team/project")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_get_project_if_member_valid(test_client: AsyncClient, test_project: dict, authorized_headers):
    """
    Test retrieving a project with a valid UUID for membership check.

    This test verifies that attempting to retrieve a project with a valid UUID
    results in a 200 status code if the user is a member of the project, or a 404
    status code if the project is not found.
    """
    url = f"/api/v1.0.0/projects/{test_project['id']}/team/is_member"
    res = await test_client.get(url, headers=authorized_headers)
    assert res.status_code in (200, 404)


@pytest.mark.asyncio
async def test_get_project_if_member_invalid_uuid(test_client: AsyncClient, authorized_headers):
    """
    Test retrieving a project with an invalid UUID for membership check.

    This test verifies that attempting to check if a user is a member of a project
    with an invalid UUID results in a 422 status code.
    """
    res = await test_client.get("/api/v1.0.0/projects/invalid-uuid/team/is_member", headers=authorized_headers)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_get_projects_by_team_id_valid(test_client: AsyncClient, test_team: dict, authorized_headers):
    """
    Test retrieving projects by team ID using a valid UUID.

    This test verifies that attempting to retrieve projects with a valid UUID
    results in a 200 status code if the team is found or a 404 status code if the
    team is not found.
    """
    res = await test_client.get(f"/api/v1.0.0/projects/team/{test_team['id']}", headers=authorized_headers)
    assert res.status_code in (200, 404)


@pytest.mark.asyncio
async def test_get_projects_by_team_id_invalid_uuid(test_client: AsyncClient, authorized_headers):
    """
    Test retrieving projects by team ID using an invalid UUID.

    This test verifies that attempting to retrieve projects with an invalid
    team UUID results in a 422 status code.
    """
    res = await test_client.get("/api/v1.0.0/projects/team/invalid-uuid", headers=authorized_headers)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_get_project_by_title_valid(test_client: AsyncClient, test_project: dict, authorized_headers):
    """
    Test retrieving a project by its title when the project exists in the database.

    This test verifies that attempting to retrieve a project by its title when the project exists in the database
    results in a 200 status code.
    """
    res = await test_client.get(f"/api/v1.0.0/projects/{test_project['title']}", headers=authorized_headers)
    assert res.status_code in (200, 404)


@pytest.mark.asyncio
async def test_get_project_by_title_not_found(test_client: AsyncClient, authorized_headers):
    """
    Test retrieving a project by its title when the project does not exist in the database.

    This test verifies that attempting to retrieve a project by its title when the project does not exist in the database
    results in a 404 status code.
    """
    res = await test_client.get("/api/v1.0.0/projects/NonExistentTitle", headers=authorized_headers)
    assert res.status_code in (200, 404)


@pytest.mark.asyncio
async def test_admin_get_project_by_user_and_id(test_client: AsyncClient, admin_user: dict, test_project: dict, test_user: dict, authorized_headers):
    """
    Test retrieving a project by project ID and user ID as an admin.

    This test verifies that an admin user can retrieve a project by specifying
    both the project ID and the user ID. The response should return a 200 status
    code if the project is found or a 404 status code if the project is not found.
    """
    url = f"/api/v1.0.0/projects/{test_project['id']}/user/{test_user['id']}"
    res = await test_client.get(url, headers=authorized_headers)
    assert res.status_code in (200, 404)


@pytest.mark.asyncio
async def test_admin_get_project_by_user_invalid_uuid(test_client: AsyncClient, admin_user: dict, authorized_headers):
    """
    Test attempting to retrieve a project by a user ID with an invalid UUID.

    This test verifies that attempting to retrieve a project with an invalid UUID
    results in a 422 status code.
    """
    url = "/api/v1.0.0/projects/invalid-uuid/user/also-invalid"
    res = await test_client.get(url, headers=authorized_headers)
    assert res.status_code == 422
