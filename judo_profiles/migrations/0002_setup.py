import csv
from pathlib import Path

from django.db import migrations


class Migration(migrations.Migration):
    def importcsv(apps, schema):
        Technique = apps.get_model("judo_profiles", "Technique")
        csv_file = Path(__file__).parent.parent / "resources/techniques.csv"

        with open(csv_file, "r") as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                Technique.objects.get_or_create(
                    codename=row[0], name=row[1], type=row[2]
                )

    def create_server(apps, schema):
        Server = apps.get_model("judo_profiles", "Server")
        Server(id=1).save()

    dependencies = [
        ("judo_profiles", "0001_initial"),
    ]

    operations = [migrations.RunPython(importcsv), migrations.RunPython(create_server)]
