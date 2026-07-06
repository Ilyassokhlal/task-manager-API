
class TestCreateTask:
    """Tests for POST /tasks"""

    def test_create_task_success(self, client, auth_headers):
        response = client.post("/tasks", json={
            "title": "test task",
            "description": "test description",
            "due_date": "2024-12-31T23:59:59",
            "completed": False
        }, headers = auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "test task"
        assert data["description"] == "test description"
        assert data["due_date"] == "2024-12-31T23:59:59"
        assert data["completed"] == False
        assert "id" in data

    def test_create_task_invalid_title(self, client, auth_headers):
        response = client.post("/tasks", json={"title": "", "description": "test description", "due_date": "2024-12-31T23:59:59", "completed": False}, headers=auth_headers)
        assert response.status_code == 422

    def test_create_task_invalid_due_date(self, client, auth_headers):
        response = client.post("/tasks", json={"title": "test task", "description": "test description", "due_date": "", "completed": False}, headers=auth_headers)
        assert response.status_code == 422


class TestReadTasks:
    """Tests for GET /tasks and GET /tasks/{id}"""
    def test_list_tasks_empty(self, client, auth_headers):
        response = client.get("/tasks/", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_tasks_with_data(self, client, sample_task, auth_headers):
        response = client.get(f"/tasks/", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_task_by_id_found(self, client, sample_task, auth_headers):
        response = client.get(f"/tasks/{sample_task['id']}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["title"] == "Test Task"

    def test_get_task_by_id_not_found(self, client, auth_headers):
        response = client.get(f"/tasks/9999", headers=auth_headers)
        assert response.status_code == 404


class TestUpdateTask:
    """Tests for PUT /tasks/{id}"""
    def test_full_update_task_success(self, client, sample_task, auth_headers):
        response = client.put(f"/tasks/{sample_task['id']}", json={
            "title": "Updated Task",
            "description": "Updated description",
            "due_date": "2024-12-31T23:59:59",
            "completed": True,
            "priority": "medium"
            }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["description"] == "Updated description"
        assert data["due_date"] == "2024-12-31T23:59:59"
        assert data["completed"] == True

    def test_full_update_task_not_found(self, client, auth_headers):
        response = client.put("/tasks/9999", json={
            "title": "Updated Task",
            "description": "Updated description",
            "due_date": "2024-12-31T23:59:59",
            "completed": True,
            "priority": "medium"
        }, headers=auth_headers)
        assert response.status_code == 404

    def test_partial_update_task_success(self, client, sample_task, auth_headers):
        response = client.patch(f"/tasks/{sample_task['id']}", json={
            "description": "Updated description"

        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    def test_partial_update_task_not_found(self, client, auth_headers):
        response = client.patch("/tasks/9999", json={
            "description": "Updated description"
        }, headers=auth_headers)
        assert response.status_code == 404

class TestDeleteTask:
    """Tests for DELETE /tasks/{id}"""
    def test_delete_task(self, client, sample_task, auth_headers):
        client.patch(f"/tasks/{sample_task['id']}", json={"completed": True}, headers=auth_headers)
        response = client.delete(f"/tasks/{sample_task['id']}", headers=auth_headers)
        assert response.status_code == 204
        # Verifying it is gone
        response = client.get(f"/tasks/{sample_task['id']}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_nonexistent_task(self, client, auth_headers):
        response = client.delete("/tasks/9999", headers=auth_headers)
        assert response.status_code == 404
