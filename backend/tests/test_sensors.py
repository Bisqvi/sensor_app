import pytest
from sensors.models import Sensor, Reading
from django.utils import timezone

def test_create_sensor(auth_client, user):
    response = auth_client.post("/sensors", json={
        "name": "Test_001",
        "model": "Test Sensor",
        "description": "Test sensor"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test_001"

def test_list_sensors(auth_client, user):
    for i in range(15):
        Sensor.objects.create(name=f"Test_00{i}", model="Test Sensor", owner=user)
    
    response = auth_client.get("/sensors?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["count"] == 15

def test_get_sensor_details(auth_client, user):
    sensor = Sensor.objects.create(name="Test_002", model="Test Sensor", description="Test desc", owner=user)
    response = auth_client.get(f"/sensors/{sensor.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test_002"
    assert data["model"] == "Test Sensor"
    assert data["description"] == "Test desc"

def test_update_sensor(auth_client, user):
    sensor = Sensor.objects.create(name="Old", model="Test Sensor", owner=user)
    response = auth_client.put(f"/sensors/{sensor.id}", json={
        "name": "Updated",
        "model": "Test Sensor 2",
        "description": "Changed"
    })
    assert response.status_code == 200
    sensor.refresh_from_db()
    assert sensor.name == "Updated"
    assert sensor.model == "Test Sensor 2"
    assert sensor.description == "Changed"

def test_partially_update_sensor(auth_client, user):
    sensor = Sensor.objects.create(name="Old", model="Test Sensor", owner=user)
    response = auth_client.put(f"/sensors/{sensor.id}", json={
        "name": "Updated"
    })
    assert response.status_code == 200
    sensor.refresh_from_db()
    assert sensor.name == "Updated"

def test_delete_sensor(auth_client, user):
    sensor = Sensor.objects.create(name="ToDelete", model="Test Sensor", owner=user)
    response = auth_client.delete(f"/sensors/{sensor.id}")
    assert response.status_code == 200
    with pytest.raises(Sensor.DoesNotExist):
        sensor.refresh_from_db()

def test_delete_sensor_cascades_readings(auth_client, user):
    sensor = Sensor.objects.create(name="CascadeTest", model="Test Sensor", owner=user)
    Reading.objects.create(sensor=sensor, temperature=20, humidity=50, timestamp=timezone.now())
    Reading.objects.create(sensor=sensor, temperature=22, humidity=55, timestamp=timezone.now())

    response = auth_client.delete(f"/sensors/{sensor.id}")
    assert response.status_code == 200
    assert Reading.objects.filter(sensor_id=sensor.id).count() == 0

def test_user_cannot_list_others_sensors(auth_client, user, other_user):
    other_sensor = Sensor.objects.create(name="Other_001", model="Other Sensor", owner=other_user)
    response = auth_client.get("/sensors")
    assert response.status_code == 200
    data = response.json()
    assert all(s["id"] != other_sensor.id for s in data["items"])
    assert all(s["owner"] == user.id for s in data["items"])

def test_user_cannot_get_others_sensors(auth_client, other_user):
    other_sensor = Sensor.objects.create(name="Other_002", model="Other Sensor", owner=other_user)
    response = auth_client.get(f"/sensors/{other_sensor.id}")
    assert response.status_code == 403

def test_user_cannot_update_others_sensors(auth_client, other_user):
    other_sensor = Sensor.objects.create(name="Other_002", model="Other Sensor", owner=other_user)
    response = auth_client.put(f"/sensors/{other_sensor.id}", json={
        "name": "Updated"
    })
    assert response.status_code == 403
    other_sensor.refresh_from_db()
    assert other_sensor.name == "Other_002"

def test_user_cannot_delete_others_sensors(auth_client, other_user):
    other_sensor = Sensor.objects.create(name="Other_003", model="Other Sensor", owner=other_user)
    response = auth_client.delete(f"/sensors/{other_sensor.id}")
    assert response.status_code == 403
    other_sensor.refresh_from_db()
    assert other_sensor.name == "Other_003"

def test_unauthorized_response(client):
    response = client.post("/api/sensors", json={
        "name": "Test_005",
        "model": "Test Sensor",
        "description": "Test sensor"
    })
    assert response.status_code == 401
