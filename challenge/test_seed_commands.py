import json
import os
import tempfile
from io import StringIO

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from challenge.models import Challenge


class PopulateChallengesPathTests(TestCase):
    def setUp(self):
        with open(os.path.join(settings.BASE_DIR, "challenge", "challenge.json")) as source:
            self.expected_names = {item["name"] for item in json.load(source)}

    def seed_from(self, directory):
        original_directory = os.getcwd()
        try:
            os.chdir(directory)
            call_command("populate_challenges", stdout=StringIO(), stderr=StringIO())
        finally:
            os.chdir(original_directory)

    def test_seeds_project_challenges_from_another_working_directory(self):
        with tempfile.TemporaryDirectory(prefix="pygoat seed ") as directory:
            self.seed_from(directory)
        self.assertSetEqual(set(Challenge.objects.values_list("name", flat=True)), self.expected_names)

    def test_ignores_a_different_dataset_in_the_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            os.mkdir(os.path.join(directory, "challenge"))
            with open(os.path.join(directory, "challenge", "challenge.json"), "w") as local_source:
                json.dump([], local_source)
            self.seed_from(directory)
        self.assertSetEqual(set(Challenge.objects.values_list("name", flat=True)), self.expected_names)

    def test_repeated_seeding_from_another_directory_does_not_duplicate_challenges(self):
        with tempfile.TemporaryDirectory() as directory:
            self.seed_from(directory)
            self.seed_from(directory)
        self.assertEqual(Challenge.objects.count(), len(self.expected_names))
