from ninja import NinjaAPI, Query, Schema, FilterSchema
from ninja.pagination import paginate, PageNumberPagination
from ninja.orm import create_schema
from ninja.security import django_auth
from django.shortcuts import get_object_or_404
from django.db.models import Q
from typing import List, Optional
from datetime import datetime
from django.utils import timezone
from pydantic import ConfigDict
from .models import Sensor, Reading

api = NinjaAPI(urls_namespace="api")

# SENSORS #

SensorSchema = create_schema(Sensor)

class SensorCreateSchema(Schema):
    """Payload to create or update a sensor"""
    name: str
    model: str
    description: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "device_001",
                "model": "EnviroSense",
                "description": "This is a description"
            }
        }
    )

@api.get("/sensors", response=list[SensorSchema])
@paginate(PageNumberPagination, page_size = 10)
def list_sensors(request, q: str = None):
    """
    List sensors, paginated, with optional filtering on name and model.
    """
    qs = Sensor.objects.all()
    if q:
        qs = qs.filter(Q(name__contains=q) | Q(model__contains=q))

    return qs

@api.post("/sensors", response=SensorSchema)
def create_sensor(request, payload: SensorCreateSchema):
    """
    Create a new sensor.
    """
    return Sensor.objects.create(owner=request.user, **payload.dict())

@api.get("/sensors/{sensor_id}", response=SensorSchema)
def get_sensor(request, sensor_id: int):
    """
    Get details for a specific sensor by ID.
    """
    sensor = get_object_or_404(Sensor, id=sensor_id)
    return sensor

@api.put("/sensors/{sensor_id}")
def update_sensor(request, sensor_id: int, payload: SensorCreateSchema):
    """
    Update a sensor by ID.
    """
    sensor = get_object_or_404(Sensor, id=sensor_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(sensor, attr, value)
    sensor.save()
    return {"success": True}

@api.delete("/sensors/{sensor_id}")
def delete_sensor(request, sensor_id: int):
    """
    Delete a sensor by ID.
    """
    sensor = get_object_or_404(Sensor, id=sensor_id)
    sensor.delete()
    return {"success": True}

# READINGS #

ReadingSchema = create_schema(Reading)

class ReadingFilterSchema(FilterSchema):
    timestamp_from: Optional[datetime] = None
    timestamp_to: Optional[datetime] = None
    
    def get_filter_expression(self) -> Q:
        q = Q()
        if self.timestamp_from:
            ts_from = timezone.make_aware(self.timestamp_from)
            q &= Q(timestamp__gte=ts_from)
        if self.timestamp_to:
            ts_to = timezone.make_aware(self.timestamp_to)
            q &= Q(timestamp__lte=ts_to)
        return q

class ReadingCreateSchema(Schema):
    """Payload to create a reading"""
    temperature: float
    humidity: float
    timestamp: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "temperature": 21.5,
                "humidity": 55.2,
                "timestamp": "2025-09-23T14:00:00"
            }
        }
    )

@api.get("/sensors/{sensor_id}/readings", response=List[ReadingSchema])
def list_readings(request, sensor_id: int, filters: ReadingFilterSchema = Query(...)):
    """
    List readings for a specific sensor by ID with optional timestamp filtering.
    """
    sensor = get_object_or_404(Sensor, id=sensor_id)
    qs = Reading.objects.filter(Q(sensor=sensor) & filters.get_filter_expression())
    return list(qs)

@api.post("/sensors/{sensor_id}/readings", response=ReadingSchema)
def create_reading(request, sensor_id: int, payload: ReadingCreateSchema):
    """
    Create a reading for a specific sensor by ID.
    """
    sensor = get_object_or_404(Sensor, id=sensor_id)
    return Reading.objects.create(sensor=sensor, **payload.dict())
