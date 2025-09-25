from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from sensors.models import Sensor, Reading
from django.utils.dateparse import parse_datetime
import csv
from pathlib import Path

class Command(BaseCommand):
    help = "Seed the database with initial sensors and readings"

    def handle(self, *args, **options):        
        csv_path = Path("seed_data/sensor_readings_wide.csv")

        if not csv_path.exists():
            self.stdout.write(self.style.ERROR(f"CSV not found: {csv_path}"))
            raise CommandError("Seed aborted due to missing csv")
        
        try:
            with transaction.atomic():
                self.stdout.write(self.style.NOTICE("Seeding database..."))

                # 1 User
                User = get_user_model()
                user = User.objects.create_user(username="admin", password="123456")

                # 5 Sensors
                sensors_data = [
                    ("device-001", "EnviroSense"),
                    ("device-002", "ClimaTrack"),
                    ("device-003", "AeroMonitor"),
                    ("device-004", "HydroTherm"),
                    ("device-005", "EcoStat"),
                ]
                for name, model in sensors_data:
                    Sensor.objects.get_or_create(name=name, model=model, owner=user)

                # 5000 Readings
                with csv_path.open() as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            sensor = Sensor.objects.get(name=row["device_id"])
                        except Sensor.DoesNotExist:
                            raise CommandError(f"Sensor with name '{row['device_id']}' not found")

                        Reading.objects.create(
                            timestamp=parse_datetime(row["timestamp"]),
                            sensor=sensor,
                            temperature=float(row["temperature"]),
                            humidity=float(row["humidity"])
                        )

                self.stdout.write(self.style.SUCCESS("Seeding complete"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Seeding failed: {e}"))
            raise
