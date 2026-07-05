
class TestAuth:
    def test_protected_endpoint_requires_token(self, client):
        response = client.post("/tasks/", json={
            "title": "No Auth",
            "description": "No description",
            "due_date": "2024-12-31T23:59:59",
            "completed": False
        })
        assert response.status_code in (401, 403)
