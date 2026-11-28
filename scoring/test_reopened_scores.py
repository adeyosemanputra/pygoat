from datetime import timedelta
import json

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.utils import timezone

from scoring.models import LabCompletion, LabScore
from scoring.views import user_scores


class ReopenedScoreTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("score-user")
        self.completion = LabCompletion.objects.create(
            user=self.user, content_type="lab", content_id=999,
            started_at=timezone.now()-timedelta(minutes=5), completed_at=timezone.now(),
        )
        self.assertTrue(LabScore.objects.filter(completion=self.completion).exists())

    def test_reopening_removes_score_from_scoreboard(self):
        self.completion.completed_at = None
        self.completion.save()
        self.assertFalse(LabScore.objects.filter(completion=self.completion).exists())
        request = RequestFactory().get("/scoring/scores/")
        request.user = self.user
        payload = json.loads(user_scores(request).content)
        self.assertEqual(payload["total_score"], 0)
        self.assertEqual(payload["scores"], [])

    def test_reopening_preserves_other_completion_scores(self):
        other = LabCompletion.objects.create(
            user=self.user, content_type="lab", content_id=1000,
            started_at=timezone.now()-timedelta(minutes=5), completed_at=timezone.now(),
        )
        self.completion.completed_at = None
        self.completion.save()
        self.assertEqual(list(LabScore.objects.values_list("completion_id", flat=True)), [other.pk])

    def test_completing_again_creates_one_score(self):
        self.completion.completed_at = None
        self.completion.save()
        self.completion.completed_at = timezone.now()
        self.completion.save()
        self.assertEqual(LabScore.objects.filter(completion=self.completion).count(), 1)

    def test_unrelated_partial_save_does_not_reopen_completion(self):
        self.completion.completed_at = None
        self.completion.content_name = "new name"
        self.completion.save(update_fields=["content_name"])
        self.completion.refresh_from_db()
        self.assertIsNotNone(self.completion.completed_at)
        self.assertTrue(LabScore.objects.filter(completion=self.completion).exists())
