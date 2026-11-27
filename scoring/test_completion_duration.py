from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from scoring.models import LabCompletion


class CompletionDurationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("duration-user")
        self.started_at = timezone.now() - timedelta(minutes=10)
        self.completion = LabCompletion.objects.create(
            user=self.user, content_type="lab", content_id=999,
            started_at=self.started_at,
        )

    def test_partial_completion_save_persists_duration(self):
        self.completion.completed_at = self.started_at + timedelta(seconds=90)
        self.completion.save(update_fields=["completed_at"])
        self.completion.refresh_from_db()
        self.assertEqual(self.completion.duration_seconds, 90)

    def test_partial_start_time_save_recomputes_duration(self):
        self.completion.completed_at = self.started_at + timedelta(seconds=90)
        self.completion.save()
        self.completion.started_at = self.started_at + timedelta(seconds=30)
        self.completion.save(update_fields={"started_at"})
        self.completion.refresh_from_db()
        self.assertEqual(self.completion.duration_seconds, 60)

    def test_reopening_completion_clears_duration(self):
        self.completion.completed_at = self.started_at + timedelta(seconds=90)
        self.completion.save()
        self.completion.completed_at = None
        self.completion.save(update_fields=["completed_at"])
        self.completion.refresh_from_db()
        self.assertIsNone(self.completion.duration_seconds)

    def test_full_save_of_reopened_completion_clears_duration(self):
        self.completion.completed_at = self.started_at + timedelta(seconds=90)
        self.completion.save()
        self.completion.completed_at = None
        self.completion.save()
        self.completion.refresh_from_db()
        self.assertIsNone(self.completion.duration_seconds)

    def test_unrelated_partial_save_does_not_persist_unsaved_timestamps(self):
        self.completion.completed_at = self.started_at + timedelta(seconds=90)
        self.completion.content_name = "renamed"
        self.completion.save(update_fields=["content_name"])
        self.completion.refresh_from_db()
        self.assertEqual(self.completion.content_name, "renamed")
        self.assertIsNone(self.completion.completed_at)
        self.assertIsNone(self.completion.duration_seconds)

    def test_empty_update_fields_remains_a_no_op(self):
        self.completion.completed_at = self.started_at + timedelta(seconds=90)
        self.completion.save(update_fields=[])
        self.completion.refresh_from_db()
        self.assertIsNone(self.completion.completed_at)
        self.assertIsNone(self.completion.duration_seconds)

    def test_negative_duration_is_still_clamped_to_zero(self):
        self.completion.completed_at = self.started_at - timedelta(seconds=1)
        self.completion.save(update_fields=["completed_at"])
        self.completion.refresh_from_db()
        self.assertEqual(self.completion.duration_seconds, 0)
