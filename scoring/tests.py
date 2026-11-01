from io import StringIO
import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import NoReverseMatch, reverse

from challenge.models import Challenge, Lab, UserChallenge
from scoring.models import (
    AchievementMilestone, DifficultyLevel, LabScore, ScoringSettings, UserAchievement,
)
from scoring.scoring_engine import compute_score
from scoring.services import complete_tracking, start_tracking


class ComputeScoreTests(TestCase):
    def setUp(self):
        self.settings = ScoringSettings.load()

    def test_instant_solve_gets_max_time_bonus(self):
        score, mult = compute_score(100, 1.0, 1, self.settings)
        self.assertAlmostEqual(mult, self.settings.time_bonus_max, places=1)
        self.assertGreater(score, 190)

    def test_slow_solve_floors_at_penalty(self):
        _, mult = compute_score(100, 1.0, 10 * 3600, self.settings)
        self.assertEqual(mult, self.settings.time_penalty_floor)

    def test_difficulty_multiplier_applies(self):
        easy, _ = compute_score(100, 0.8, None, self.settings)
        hard, _ = compute_score(100, 2.5, None, self.settings)
        self.assertEqual(easy, 80)
        self.assertEqual(hard, 250)

    def test_score_never_below_one(self):
        score, _ = compute_score(0, 1.0, None, self.settings)
        self.assertEqual(score, 1)

    def test_zero_time_window_uses_neutral_time_multiplier(self):
        self.settings.time_bonus_window_minutes = 0
        score, mult = compute_score(100, 1.5, 60, self.settings)
        self.assertEqual(score, 150)
        self.assertEqual(mult, 1.0)

    def test_zero_time_window_is_rejected_by_validation(self):
        self.settings.time_bonus_window_minutes = 0
        with self.assertRaises(ValidationError) as raised:
            self.settings.full_clean()
        self.assertIn("time_bonus_window_minutes", raised.exception.message_dict)


class SeedAndDefaultsTests(TestCase):
    def test_seed_scoring_is_idempotent(self):
        call_command("seed_scoring", stdout=StringIO())
        call_command("seed_scoring", stdout=StringIO())
        self.assertEqual(DifficultyLevel.objects.count(), 4)
        self.assertEqual(AchievementMilestone.objects.count(), 7)

    def test_new_challenge_and_lab_default_to_medium(self):
        call_command("seed_scoring", stdout=StringIO())
        medium = DifficultyLevel.objects.get(name="Medium")
        chal = Challenge.objects.create(
            name="c", docker_image="img", docker_port=1, start_port=1,
            end_port=2, flag="flag{x}", point=50,
        )
        lab = Lab.objects.create(name="l", build_location="x", port=1)
        self.assertEqual(chal.difficulty, medium)
        self.assertEqual(lab.difficulty, medium)


class ChallengeSolveTests(TestCase):
    def setUp(self):
        call_command("seed_scoring", stdout=StringIO())
        self.user = User.objects.create_user("alice", password="pw")
        self.hard = DifficultyLevel.objects.get(name="Hard")
        self.chal = Challenge.objects.create(
            name="do-it-fast", docker_image="img", docker_port=1, start_port=1,
            end_port=2, flag="flag{secret}", point=100, difficulty=self.hard,
        )
        self.client.force_login(self.user)
        self.url = "/challenge/do-it-fast"

    def _start(self):
        with patch("challenge.views.get_docker_client") as get_client:
            container = get_client.return_value.containers.run.return_value
            container.id = "cid"
            container.ports = {"1/tcp": [{"HostPort": "8001"}]}
            return self.client.post(self.url)

    def _submit(self, flag):
        return self.client.put(
            self.url, data=json.dumps({"flag": flag}), content_type="application/json"
        )

    def test_tracking_endpoints_are_not_client_callable(self):
        for name in ("start_tracking", "complete_tracking"):
            with self.assertRaises(NoReverseMatch):
                reverse(f"scoring:{name}", args=["challenge", self.chal.id])
        self.assertEqual(self.client.post(f"/scoring/complete/challenge/{self.chal.id}/").status_code, 404)

    def test_starting_challenge_records_start(self):
        self._start()
        self.assertTrue(self.user.lab_completions.filter(content_type="challenge", completed_at=None).exists())

    def test_flag_requires_started_challenge(self):
        resp = self._submit("flag{secret}")
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(LabScore.objects.exists())

    def test_wrong_flag_awards_nothing(self):
        self._start()
        resp = self._submit("flag{nope}")
        self.assertFalse(resp.json()["correct"])
        self.assertFalse(LabScore.objects.exists())
        self.assertEqual(UserChallenge.objects.get().no_of_attempt, 1)

    def test_correct_flag_scores_with_difficulty(self):
        self._start()
        resp = self._submit("flag{secret}")
        data = resp.json()
        self.assertTrue(data["correct"])
        score = LabScore.objects.get()
        self.assertEqual(score.base_points, 100)
        self.assertEqual(score.difficulty_multiplier, self.hard.multiplier)
        self.assertEqual(score.final_score, data["final_score"])
        self.assertTrue(UserChallenge.objects.get().is_solved)
        self.assertTrue(UserAchievement.objects.filter(user=self.user, milestone__name="First Blood").exists())

    def test_resubmitting_does_not_double_score(self):
        self._start()
        self._submit("flag{secret}")
        self._submit("flag{secret}")
        self.assertEqual(LabScore.objects.count(), 1)

    def test_anonymous_cannot_submit(self):
        self.client.logout()
        self.assertEqual(self._submit("flag{secret}").status_code, 401)

    def test_changing_difficulty_multiplier_rescores(self):
        self._start()
        self._submit("flag{secret}")
        before = LabScore.objects.get().final_score
        self.hard.multiplier = self.hard.multiplier * 2
        self.hard.save()
        self.assertGreater(LabScore.objects.get().final_score, before)

    def test_dashboard_and_nav_show_score(self):
        self._start()
        self._submit("flag{secret}")
        pts = LabScore.objects.get().final_score
        self.assertContains(self.client.get("/scoring/dashboard/"), "do-it-fast")
        self.assertContains(self.client.get("/"), f"{pts} pts")


class ServiceTests(TestCase):
    def test_complete_without_start_gets_no_time_bonus_and_is_idempotent(self):
        user = User.objects.create_user("bob", password="pw")
        completion, first = complete_tracking(user, "lab", 1, content_name="x")
        _, second = complete_tracking(user, "lab", 1)
        self.assertTrue(first)
        self.assertFalse(second)
        self.assertEqual(start_tracking(user, "lab", 1).pk, completion.pk)
