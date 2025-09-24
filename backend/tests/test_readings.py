import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from sensors.models import Sensor, Reading

def test_create_reading(client, user):
    sensor = Sensor.objects.create(name="Test_001", model="Test Sensor", owner=user)
    payload = {
        "temperature": 22.5,
        "humidity": 55.2,
        "timestamp": "2025-09-23T14:00:00"
    }
    response = client.post(f"/sensors/{sensor.id}/readings", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["temperature"] == 22.5
    assert data["sensor"] == sensor.id

def test_list_readings_with_filters(client, user):
    sensor = Sensor.objects.create(name="Test_002", model="TestSensor", owner=user)
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
    response = client.get(f"/sensors/{sensor.id}/readings?timestamp_from=2025-09-22T00:00:00")
    assert response.status_code == 200
    data = response.json()
    assert all(datetime.fromisoformat(r["timestamp"]) >= ts_from for r in data)

    # Filter readings up to 21st
    ts_to = timezone.make_aware(datetime(2025, 9, 21, 23, 59, 59))
    response = client.get(f"/sensors/{sensor.id}/readings?timestamp_to=2025-09-21T23:59:59")
    assert response.status_code == 200
    data = response.json()
    assert all(datetime.fromisoformat(r["timestamp"]) <= ts_to for r in data)
