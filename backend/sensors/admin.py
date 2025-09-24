from django.contrib import admin
from .models import User, Sensor, Reading

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')
    search_fields = ('username', 'email')

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'name', 'description', 'model')
    search_fields = ('name', 'model', 'owner__username')
    list_filter = ('owner',)

@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ('id', 'sensor', 'temperature', 'humidity', 'timestamp')
    list_filter = ('sensor',)

