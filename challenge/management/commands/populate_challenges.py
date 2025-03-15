import json
import os
from django.core.management.base import BaseCommand
from challenge.models import Challenge

class Command(BaseCommand):
    help = (
        "Reads challenge data from 'challenge/challenge.json' and populates the "
        "Challenge table in the database. Uses get_or_create to prevent duplicates "
        "and handles JSON errors gracefully."
    )

    def handle(self, *args, **options):
        file_path = os.path.join('challenge', 'challenge.json')

        try:
            with open(file_path, 'r') as json_file:
                challenges_data = json.load(json_file)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"JSON file not found: {file_path}"))
            return
        except json.JSONDecodeError as e:
            self.stderr.write(self.style.ERROR(f"Error decoding JSON: {e}"))
            return

        for item in challenges_data:
            challenge, created = Challenge.objects.get_or_create(
                name=item.get("name"),
                defaults={
                    "description": item.get("description", ""),
                    "docker_image": item.get("docker_image", ""),
                    "docker_port": item.get("docker_port", 0),
                    "start_port": item.get("start_port", 0),
                    "end_port": item.get("end_port", 0),
                    "flag": item.get("flag", ""),
                    "point": item.get("point", 0)
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Challenge '{challenge.name}' created."))
            else:
                self.stdout.write(f"Challenge '{challenge.name}' already exists.")

        self.stdout.write(self.style.SUCCESS("Challenge data has been populated successfully."))
