import pytest
from sensors.models import Sensor

def test_create_sensor(client, user):
    response = client.post("/sensors", json={
        "name": "Test_001",
        "model": "Test Sensor",
        "description": "Test sensor"
    }, user=user)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test_001"
    assert "id" in data

def test_list_sensors(client, user):
    for i in range(15):
        Sensor.objects.create(name=f"Test_00{i}", model="Test Sensor", owner=user)
    
    response = client.get("/sensors?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["count"] == 15

def test_update_sensor(client, user):
    sensor = Sensor.objects.create(name="Old", model="Test Sensor", owner=user)
    response = client.put(f"/sensors/{sensor.id}", json={
        "name": "Updated",
        "model": "Test Sensor 2",
        "description": "Changed"
    })
    assert response.status_code == 200
    sensor.refresh_from_db()
    assert sensor.name == "Updated"

def test_delete_sensor(client, user):
    sensor = Sensor.objects.create(name="ToDelete", model="Test Sensor", owner=user)
    response = client.delete(f"/sensors/{sensor.id}")
    assert response.status_code == 200
    with pytest.raises(Sensor.DoesNotExist):
        sensor.refresh_from_db()
