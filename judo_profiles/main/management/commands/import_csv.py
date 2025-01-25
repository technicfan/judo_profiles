import csv
from django.core.management.base import BaseCommand
from main.models import Technique

class Command(BaseCommand):
    help = "Import data from CSV file into Technique model"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="The CSV file to be imported")

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]

        with open(csv_file, "r") as file:
            reader = csv.reader(file)
            next(reader)

            imported = 0
            duplicates = 0
            for row in reader:
                _, created = Technique.objects.get_or_create(
                    codename=row[0],
                    name=row[1],
                    type=row[2]
                )
                if created:
                    imported += 1
                else:
                    duplicates += 1

        if imported > 0:
            self.stdout.write(f"Successfully imported {imported} Techniques")
        if duplicates > 0:
            self.stdout.write(f"{duplicates} Techniques did already exsist")
