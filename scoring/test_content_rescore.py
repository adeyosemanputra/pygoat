from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from challenge.models import Challenge, Lab
from scoring.models import DifficultyLevel, LabCompletion, LabScore


class ContentRescoreTests(TestCase):
    def setUp(self):
        normal = DifficultyLevel.objects.create(name="Normal", multiplier=1)
        self.hard = DifficultyLevel.objects.create(name="Hard", multiplier=2)
        self.user = User.objects.create_user("rescore-user")
        self.challenge = Challenge.objects.create(
            name="challenge", docker_image="image", docker_port=80,
            start_port=8000, end_port=8010, flag="flag", point=100, difficulty=normal,
        )
        self.lab = Lab.objects.create(name="lab", build_location="test", port=8000, difficulty=normal)
        now = timezone.now()
        self.completions = {}
        for kind, content in [("challenge", self.challenge), ("lab", self.lab)]:
            self.completions[kind] = LabCompletion.objects.create(
                user=self.user, content_type=kind, content_id=content.pk,
                started_at=now-timedelta(minutes=30), completed_at=now,
            )

    def score(self, kind):
        return LabScore.objects.get(completion=self.completions[kind])

    def test_challenge_points_update_existing_score(self):
        self.challenge.point = 250
        self.challenge.save(update_fields=["point"])
        self.assertEqual(self.score("challenge").base_points, 250)
        self.assertEqual(self.score("challenge").final_score, 250)
        self.assertEqual(self.score("lab").final_score, 100)

    def test_challenge_difficulty_assignment_updates_score(self):
        self.challenge.difficulty = self.hard
        self.challenge.save(update_fields=["difficulty"])
        self.assertEqual(self.score("challenge").final_score, 200)
        self.assertEqual(self.score("lab").final_score, 100)

    def test_lab_difficulty_assignment_updates_only_lab_score(self):
        self.lab.difficulty = self.hard
        self.lab.save(update_fields=["difficulty"])
        self.assertEqual(self.score("lab").final_score, 200)
        self.assertEqual(self.score("challenge").final_score, 100)

    def test_unfinished_content_does_not_receive_a_score(self):
        other_user = User.objects.create_user("unfinished-user")
        incomplete = LabCompletion.objects.create(
            user=other_user, content_type="lab", content_id=self.lab.pk, started_at=timezone.now(),
        )
        self.lab.difficulty = self.hard
        self.lab.save(update_fields=["difficulty"])
        self.assertFalse(LabScore.objects.filter(completion=incomplete).exists())
