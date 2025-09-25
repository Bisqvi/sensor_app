def test_register(client):
    response = client.post("/api/auth/register/", data={
        "username": "testuser",
        "email": "test@example.com",
        "password": "pass1234"
    }, content_type="application/json")
    assert response.status_code == 201
    assert "token" in response.json()
    assert response.json()["user"]["username"] == "testuser"

def test_login(client, django_user_model):
    django_user_model.objects.create_user(username="testuser", email="test@example.com", password="pass1234")
    response = client.post("/api/auth/token/", data={
        "username": "testuser",
        "password": "pass1234"
    }, content_type="application/json")
    assert response.status_code == 200
    assert "access" in response.json()

