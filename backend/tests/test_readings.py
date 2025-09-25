from datetime import datetime, timedelta
from django.utils import timezone
from sensors.models import Sensor, Reading

def test_create_reading(auth_client, user):
    sensor = Sensor.objects.create(name="Test_001", model="Test Sensor", owner=user)
    payload = {
        "temperature": 22.5,
        "humidity": 55.2,
        "timestamp": "2025-09-23T14:00:00"
    }
    response = auth_client.post(f"/sensors/{sensor.id}/readings", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["temperature"] == 22.5
    assert data["sensor"] == sensor.id

def test_list_readings(auth_client, user):
    sensor = Sensor.objects.create(name="Test_002", model="TestSensor", owner=user)
    base = timezone.make_aware(datetime(2025, 9, 20))

    for i in range(5):
        Reading.objects.create(
            sensor=sensor,
            temperature=20+i,
            humidity=50+i,
            timestamp=base + timedelta(days=i)
        )

    response = auth_client.get(f"/sensors/{sensor.id}/readings")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5

def test_list_readings_with_filters(auth_client, user):
    sensor = Sensor.objects.create(name="Test_003", model="TestSensor", owner=user)
    base = timezone.make_aware(datetime(2025, 9, 20))

    for i in range(5):
        Reading.objects.create(
            sensor=sensor,
            temperature=20+i,
            humidity=50+i,
            timestamp=base + timedelta(days=i)
        )

    # Filter readings from 22nd
    ts_from = timezone.make_aware(datetime(2025, 9, 22, 0, 0, 0))
    response = auth_client.get(f"/sensors/{sensor.id}/readings?timestamp_from=2025-09-22T00:00:00")
    assert response.status_code == 200
    data = response.json()
    assert all(datetime.fromisoformat(r["timestamp"]) >= ts_from for r in data)

    # Filter readings up to 21st
    ts_to = timezone.make_aware(datetime(2025, 9, 21, 23, 59, 59))
    response = auth_client.get(f"/sensors/{sensor.id}/readings?timestamp_to=2025-09-21T23:59:59")
    assert response.status_code == 200
    data = response.json()
    assert all(datetime.fromisoformat(r["timestamp"]) <= ts_to for r in data)

def test_user_cannot_create_readings_for_others_sensors(auth_client, other_user):
    other_sensor = Sensor.objects.create(name="Other_001", model="Test Sensor", owner=other_user)
    payload = {
        "temperature": 25.5,
        "humidity": 59.0,
        "timestamp": "2025-09-23T14:00:00"
    }
    response = auth_client.post(f"/sensors/{other_sensor.id}/readings", json=payload)
    assert response.status_code == 403

def test_user_cannot_list_readings_for_others_sensors(auth_client, other_user):
    other_sensor = Sensor.objects.create(name="Other_002", model="Test Sensor", owner=other_user)
    base = timezone.make_aware(datetime(2025, 9, 20))

    for i in range(5):
        Reading.objects.create(
            sensor=other_sensor,
            temperature=20+i,
            humidity=50+i,
            timestamp=base + timedelta(days=i)
        )
    response = auth_client.get(f"/sensors/{other_sensor.id}/readings")
    assert response.status_code == 403