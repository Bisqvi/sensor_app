from ninja import NinjaAPI, Query, Schema, FilterSchema
from ninja.pagination import paginate, PageNumberPagination
from ninja.orm import create_schema
from ninja.security import HttpBearer
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from typing import List, Optional
from datetime import datetime
from django.utils import timezone
from pydantic import ConfigDict
from .models import Sensor, Reading

class JWTBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str):
        """
        Validate JWT token from Authorization header.
        Returns (user, token) if valid, None if invalid.
        """
        try:
            payload = AccessToken(token)
            User = get_user_model()
            user = User.objects.get(id=payload["user_id"])
            request.user = user
            return user
        except Exception:
            return None

api = NinjaAPI(urls_namespace="api", auth=JWTBearer())

# SENSORS #

SensorSchema = create_schema(Sensor)

class SensorCreateSchema(Schema):
    """Payload to create a sensor"""
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

class SensorUpdateSchema(Schema):
    """Payload to update a sensor"""
    name: Optional[str] = None
    model: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "description": "Updated description"
            }
        }
    )

@api.get("/sensors", response=list[SensorSchema])
@paginate(PageNumberPagination, page_size = 10)
def list_sensors(request, q: str = None):
    """
    List user's sensors, paginated, with optional filtering on name and model.
    """
    qs = Sensor.objects.filter(owner=request.user)
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
    Get details for a specific sensor by ID. Only the owner can access it.
    """
    sensor = get_object_or_404(Sensor, id=sensor_id)
    if sensor.owner != request.user:
        raise HttpError(403, "Forbidden")
    return sensor

@api.put("/sensors/{sensor_id}")
def update_sensor(request, sensor_id: int, payload: SensorUpdateSchema):
    """
    Update a sensor by ID.
    """
    sensor = get_object_or_404(Sensor, id=sensor_id)
    if sensor.owner != request.user:
        raise HttpError(403, "Forbidden")
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
    if sensor.owner != request.user:
        raise HttpError(403, "Forbidden")
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
    if sensor.owner != request.user:
        raise HttpError(403, "Forbidden")
    qs = Reading.objects.filter(Q(sensor=sensor) & filters.get_filter_expression())
    return list(qs)

@api.post("/sensors/{sensor_id}/readings", response=ReadingSchema)
def create_reading(request, sensor_id: int, payload: ReadingCreateSchema):
    """
    Create a reading for a specific sensor by ID.
    """
    sensor = get_object_or_404(Sensor, id=sensor_id)
    if sensor.owner != request.user:
        raise HttpError(403, "Forbidden")
    return Reading.objects.create(sensor=sensor, **payload.dict())
