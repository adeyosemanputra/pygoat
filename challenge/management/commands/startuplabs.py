import os

from django.conf import settings
from django.core.management.base import BaseCommand
import docker

from challenge.models import Lab


class Command(BaseCommand):
	help = (
		"Prebuilds all lab Docker images on startup when "
		"PREBUILD_LABS_ON_STARTUP is enabled."
	)

	def handle(self, *args, **options):
		prebuild_enabled = os.getenv("PREBUILD_LABS_ON_STARTUP", "false").lower() == "true"
		if not prebuild_enabled:
			self.stdout.write("PREBUILD_LABS_ON_STARTUP is disabled. Skipping prebuild.")
			return

		try:
			client = docker.from_env()
		except Exception as exc:
			self.stderr.write(self.style.ERROR(f"Failed to connect to Docker daemon: {exc}"))
			return

		labs = Lab.objects.all()
		if not labs.exists():
			self.stdout.write("No labs found in database. Nothing to build.")
			return

		for lab in labs:
			image = lab.name
			build_location = lab.build_location
			if not image or not build_location:
				self.stderr.write(self.style.WARNING("Skipping invalid lab entry without name/build_location."))
				continue

			try:
				client.images.get(image)
				self.stdout.write(f"Image '{image}' already exists. Skipping build.")
				continue
			except docker.errors.ImageNotFound:
				pass
			except Exception as exc:
				self.stderr.write(self.style.ERROR(f"Failed to check image '{image}': {exc}"))
				continue

			build_path = os.path.join(settings.BASE_DIR, build_location)
			if not os.path.exists(build_path):
				self.stderr.write(self.style.ERROR(f"Build path not found for '{image}': {build_path}"))
				continue

			self.stdout.write(f"Building image '{image}' from {build_path}...")
			try:
				client.images.build(path=build_path, tag=image)
				self.stdout.write(self.style.SUCCESS(f"Built image '{image}' successfully."))
			except Exception as exc:
				self.stderr.write(self.style.ERROR(f"Failed to build image '{image}': {exc}"))

