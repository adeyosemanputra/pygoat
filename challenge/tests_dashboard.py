import hashlib
import json
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
 
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ValidationError
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse, resolve
 
from challenge.models import Challenge, UserChallenge, UserProfile, BADGE_CATALOGUE
from challenge.signals import update_streak_on_login
from challenge.views import (
    progress_dashboard,
    progress_api,
    submit_flag,
    _award_completion_badges,
)



# Shared test factories

def make_user(username="testuser", password="testpass123"):
    """Create a user; signals auto-create their UserProfile."""
    return User.objects.create_user(username=username, password=password)
 
 
def make_challenge(
    name="sqli_lab",
    point=100,
    flag="SECRET",
    docker_image="pygoat/sqli",
    docker_port=5000,
    start_port=8100,
    end_port=8110,
    description="A test challenge",
):
    """Create a Challenge with a plain-text flag (gets hashed by model.save)."""
    return Challenge.objects.create(
        name=name,
        description=description,
        docker_image=docker_image,
        docker_port=docker_port,
        start_port=start_port,
        end_port=end_port,
        flag=flag,
        point=point,
    )
 
 
def solve_challenge(user, challenge):
    """Helper to mark a challenge as solved without going through the view."""
    uc, _ = UserChallenge.objects.get_or_create(
        user=user,
        challenge=challenge,
        defaults={"container_id": "", "port": 0},
    )
    uc.is_solved = True
    uc.save()
    return uc
 
 
def hashed_flag(plain: str) -> str:
    """Return the stored flag value for a given plain-text flag."""
    return "hashed_" + hashlib.sha256(plain.encode()).hexdigest()
 
 
# 1.Model test -UserProfile

class UserProfileModelTest(TestCase):
    """Unit tests for every method and property on UserProfile."""
 
    def setUp(self):
        self.user = make_user()
        self.profile = UserProfile.objects.get(user=self.user)
 
    #  __str__ 
 
    def test_str_returns_username(self):
        self.assertEqual(str(self.profile), f"Profile({self.user.username})")
 
    # ── award_badge ───────────────────────────────────────────────────────────
 
    def test_award_badge_new_badge_returns_true(self):
        result = self.profile.award_badge("first_blood")
        self.assertTrue(result)
 
    def test_award_badge_stored_in_badges_list(self):
        self.profile.award_badge("first_blood")
        self.profile.refresh_from_db()
        self.assertIn("first_blood", self.profile.badges)
 
    def test_award_badge_duplicate_returns_false(self):
        self.profile.award_badge("first_blood")
        result = self.profile.award_badge("first_blood")
        self.assertFalse(result)
 
    def test_award_badge_duplicate_not_doubled_in_list(self):
        self.profile.award_badge("first_blood")
        self.profile.award_badge("first_blood")
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.badges.count("first_blood"), 1)
 
    def test_award_badge_unknown_key_returns_false(self):
        result = self.profile.award_badge("does_not_exist")
        self.assertFalse(result)
 
    def test_award_badge_unknown_key_not_stored(self):
        self.profile.award_badge("does_not_exist")
        self.profile.refresh_from_db()
        self.assertNotIn("does_not_exist", self.profile.badges)
 
    def test_award_multiple_different_badges(self):
        self.profile.award_badge("first_blood")
        self.profile.award_badge("streak_3")
        self.profile.refresh_from_db()
        self.assertIn("first_blood", self.profile.badges)
        self.assertIn("streak_3", self.profile.badges)
        self.assertEqual(len(self.profile.badges), 2)
 
    def test_all_catalogue_keys_can_be_awarded(self):
        """Every key in BADGE_CATALOGUE must be awardable."""
        for key in BADGE_CATALOGUE:
            result = self.profile.award_badge(key)
            self.assertTrue(result, f"award_badge('{key}') should return True")
 
    # -- badge_details 
    def test_badge_details_empty_when_no_badges(self):
        self.assertEqual(self.profile.badge_details(), [])
 
    def test_badge_details_contains_correct_keys(self):
        self.profile.award_badge("first_blood")
        details = self.profile.badge_details()
        self.assertEqual(len(details), 1)
        self.assertIn("label", details[0])
        self.assertIn("icon", details[0])
        self.assertIn("desc", details[0])
        self.assertIn("key", details[0])
 
    def test_badge_details_key_matches_awarded_badge(self):
        self.profile.award_badge("streak_3")
        details = self.profile.badge_details()
        self.assertEqual(details[0]["key"], "streak_3")
 
    def test_badge_details_skips_unknown_key(self):
        """If a stale/unknown key ends up in the JSON list, it is silently skipped."""
        self.profile.badges = ["first_blood", "legacy_badge_that_no_longer_exists"]
        self.profile.save()
        details = self.profile.badge_details()
        self.assertEqual(len(details), 1)
        self.assertEqual(details[0]["key"], "first_blood")
 
    # -- add_xp
 
    def test_add_xp_increases_xp_points(self):
        self.profile.add_xp(50)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.xp_points, 50)
 
    def test_add_xp_accumulates(self):
        self.profile.add_xp(50)
        self.profile.add_xp(75)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.xp_points, 125)
 
    def test_add_xp_zero_has_no_effect(self):
        self.profile.add_xp(0)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.xp_points, 0)
 
    def test_add_xp_persists_to_database(self):
        self.profile.add_xp(200)
        fresh = UserProfile.objects.get(pk=self.profile.pk)
        self.assertEqual(fresh.xp_points, 200)
 
    # -- xp_level property 
 
    def test_xp_level_starts_at_1(self):
        self.assertEqual(self.profile.xp_level, 1)
 
    def test_xp_level_99_still_level_1(self):
        self.profile.xp_points = 99
        self.assertEqual(self.profile.xp_level, 1)
 
    def test_xp_level_100_is_level_2(self):
        self.profile.xp_points = 100
        self.assertEqual(self.profile.xp_level, 2)
 
    def test_xp_level_199_is_level_2(self):
        self.profile.xp_points = 199
        self.assertEqual(self.profile.xp_level, 2)
 
    def test_xp_level_200_is_level_3(self):
        self.profile.xp_points = 200
        self.assertEqual(self.profile.xp_level, 3)
 
    def test_xp_level_500_is_level_6(self):
        self.profile.xp_points = 500
        self.assertEqual(self.profile.xp_level, 6)
 
    # -- xp_progress_pct property 
 
    def test_xp_progress_pct_zero_xp(self):
        self.assertEqual(self.profile.xp_progress_pct, 0)
 
    def test_xp_progress_pct_50_xp(self):
        self.profile.xp_points = 50
        self.assertEqual(self.profile.xp_progress_pct, 50)
 
    def test_xp_progress_pct_resets_at_level_boundary(self):
        self.profile.xp_points = 100
        self.assertEqual(self.profile.xp_progress_pct, 0)
 
    def test_xp_progress_pct_mid_level(self):
        self.profile.xp_points = 175
        self.assertEqual(self.profile.xp_progress_pct, 75)
 
 

#2.model test - hallenge & UserChallenge


class ChallengeModelTest(TestCase):
 
    def test_flag_gets_hashed_on_save(self):
        chal = make_challenge(flag="MYSECRET")
        self.assertTrue(chal.flag.startswith("hashed_"))
 
    def test_flag_hash_value_is_correct(self):
        chal = make_challenge(flag="MYSECRET")
        expected = hashed_flag("MYSECRET")
        self.assertEqual(chal.flag, expected)
 
    def test_already_hashed_flag_not_double_hashed(self):
        chal = make_challenge(flag="MYSECRET")
        original_flag = chal.flag
        chal.save()  # second save
        chal.refresh_from_db()
        self.assertEqual(chal.flag, original_flag)
 
    def test_invalid_port_range_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            Challenge.objects.create(
                name="bad_ports",
                description="test",
                docker_image="pygoat/bad",
                docker_port=5000,
                start_port=8200,  # start > end
                end_port=8100,
                flag="FLAG",
                point=50,
            )
 
    def test_equal_ports_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            Challenge.objects.create(
                name="equal_ports",
                description="test",
                docker_image="pygoat/equal",
                docker_port=5000,
                start_port=8100,
                end_port=8099,  # end < start
                flag="FLAG",
                point=50,
            )
 
    def test_str_returns_name(self):
        chal = make_challenge()
        self.assertEqual(str(chal), chal.name)
 
 
class UserChallengeModelTest(TestCase):
 
    def setUp(self):
        self.user = make_user()
        self.chal = make_challenge()
 
    def test_str_format(self):
        uc = UserChallenge.objects.create(
            user=self.user,
            challenge=self.chal,
            container_id="abc123",
            port=8100,
        )
        self.assertEqual(str(uc), f"{self.user.username} - {self.chal.name}")
 
    def test_default_is_solved_false(self):
        uc = UserChallenge.objects.create(
            user=self.user, challenge=self.chal, container_id="x", port=8100,
        )
        self.assertFalse(uc.is_solved)
 
    def test_default_is_live_false(self):
        uc = UserChallenge.objects.create(
            user=self.user, challenge=self.chal, container_id="x", port=8100,
        )
        self.assertFalse(uc.is_live)
 
    def test_default_attempts_zero(self):
        uc = UserChallenge.objects.create(
            user=self.user, challenge=self.chal, container_id="x", port=8100,
        )
        self.assertEqual(uc.no_of_attempt, 0)
 

#3. signals tests
class SignalUserProfileCreationTest(TestCase):
    """post_save on User → auto-create UserProfile."""
 
    def test_profile_created_on_user_create(self):
        user = make_user()
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
 
    def test_only_one_profile_per_user(self):
        user = make_user()
        # Saving user again must not create a second profile
        user.save()
        count = UserProfile.objects.filter(user=user).count()
        self.assertEqual(count, 1)
 
    def test_profile_accessible_via_reverse_relation(self):
        user = make_user()
        profile = user.profile
        self.assertIsInstance(profile, UserProfile)
 
    def test_profile_initial_xp_zero(self):
        user = make_user()
        self.assertEqual(user.profile.xp_points, 0)
 
    def test_profile_initial_streak_zero(self):
        user = make_user()
        self.assertEqual(user.profile.streak_days, 0)
 
    def test_profile_initial_badges_empty(self):
        user = make_user()
        self.assertEqual(user.profile.badges, [])
 
 
class StreakSignalTest(TestCase):
    """update_streak_on_login signal handler tests."""
 
    def setUp(self):
        self.user = make_user()
        self.profile = self.user.profile
        self.factory = RequestFactory()
 
    def _fire_login_signal(self):
        """Manually fire the user_logged_in signal."""
        request = self.factory.get("/")
        request.user = self.user
        update_streak_on_login(sender=User, request=request, user=self.user)
        self.profile.refresh_from_db()
 
    # -- First login --
 
    def test_first_login_sets_streak_to_1(self):
        self.profile.last_active = None
        self.profile.save()
        self._fire_login_signal()
        self.assertEqual(self.profile.streak_days, 1)
 
    def test_first_login_sets_last_active_to_today(self):
        self.profile.last_active = None
        self.profile.save()
        self._fire_login_signal()
        self.assertEqual(self.profile.last_active, date.today())
 
    # -- Same-day idempotency --
 
    def test_second_login_same_day_does_not_increment_streak(self):
        self.profile.last_active = date.today()
        self.profile.streak_days = 5
        self.profile.save()
        self._fire_login_signal()
        self.assertEqual(self.profile.streak_days, 5)
 
    # -- Consecutive day 

    def test_consecutive_day_increments_streak(self):
        self.profile.last_active = date.today() - timedelta(days=1)
        self.profile.streak_days = 2
        self.profile.save()
        self._fire_login_signal()
        self.assertEqual(self.profile.streak_days, 3)
 
    def test_consecutive_day_updates_last_active(self):
        self.profile.last_active = date.today() - timedelta(days=1)
        self.profile.streak_days = 2
        self.profile.save()
        self._fire_login_signal()
        self.assertEqual(self.profile.last_active, date.today())
 
    # -- Broken streak 
 
    def test_broken_streak_resets_to_1(self):
        self.profile.last_active = date.today() - timedelta(days=3)
        self.profile.streak_days = 10
        self.profile.save()
        self._fire_login_signal()
        self.assertEqual(self.profile.streak_days, 1)
 
    def test_gap_of_exactly_2_days_breaks_streak(self):
        self.profile.last_active = date.today() - timedelta(days=2)
        self.profile.streak_days = 4
        self.profile.save()
        self._fire_login_signal()
        self.assertEqual(self.profile.streak_days, 1)
 
    # -- Streak badges

    def test_streak_3_badge_awarded_at_3_days(self):
        self.profile.last_active = date.today() - timedelta(days=1)
        self.profile.streak_days = 2
        self.profile.save()
        self._fire_login_signal()
        self.profile.refresh_from_db()
        self.assertIn("streak_3", self.profile.badges)
 
    def test_streak_3_badge_not_awarded_before_3_days(self):
        self.profile.last_active = date.today() - timedelta(days=1)
        self.profile.streak_days = 1
        self.profile.save()
        self._fire_login_signal()
        self.profile.refresh_from_db()
        self.assertNotIn("streak_3", self.profile.badges)
 
    def test_streak_7_badge_awarded_at_7_days(self):
        self.profile.last_active = date.today() - timedelta(days=1)
        self.profile.streak_days = 6
        self.profile.save()
        self._fire_login_signal()
        self.profile.refresh_from_db()
        self.assertIn("streak_7", self.profile.badges)
 
    def test_streak_7_badge_not_awarded_before_7_days(self):
        self.profile.last_active = date.today() - timedelta(days=1)
        self.profile.streak_days = 5
        self.profile.save()
        self._fire_login_signal()
        self.profile.refresh_from_db()
        self.assertNotIn("streak_7", self.profile.badges)
 
    def test_streak_badges_awarded_only_once(self):
        """Fire signal twice at streak=6→7; streak_7 must appear exactly once."""
        self.profile.last_active = date.today() - timedelta(days=1)
        self.profile.streak_days = 6
        self.profile.save()
        self._fire_login_signal()
        # Force another consecutive-day scenario next day
        self.profile.last_active = date.today() - timedelta(days=1)
        self.profile.save()
        self._fire_login_signal()
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.badges.count("streak_7"), 1)
 
    def test_missing_profile_created_by_signal(self):
        """Signal creates a UserProfile if it was deleted before login."""
        self.profile.delete()
        request = self.factory.get("/")
        request.user = self.user
        update_streak_on_login(sender=User, request=request, user=self.user)
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
 

 #4. Helper Function Tests - _award_completion_badges


class AwardCompletionBadgesTest(TestCase):
 
    def setUp(self):
        self.user = make_user()
        self.profile = self.user.profile
 
    def test_first_blood_at_first_solve(self):
        _award_completion_badges(self.profile, solved_count=1, total=10)
        self.profile.refresh_from_db()
        self.assertIn("first_blood", self.profile.badges)
 
    def test_first_blood_not_awarded_if_not_first_solve(self):
        _award_completion_badges(self.profile, solved_count=2, total=10)
        self.profile.refresh_from_db()
        self.assertNotIn("first_blood", self.profile.badges)
 
    def test_half_way_badge_at_exactly_50_percent(self):
        # solved=5 out of total=10 → 50 %
        _award_completion_badges(self.profile, solved_count=5, total=10)
        self.profile.refresh_from_db()
        self.assertIn("half_way", self.profile.badges)
 
    def test_half_way_badge_not_awarded_below_50_percent(self):
        _award_completion_badges(self.profile, solved_count=4, total=10)
        self.profile.refresh_from_db()
        self.assertNotIn("half_way", self.profile.badges)
 
    def test_half_way_badge_awarded_above_50_percent(self):
        _award_completion_badges(self.profile, solved_count=7, total=10)
        self.profile.refresh_from_db()
        self.assertIn("half_way", self.profile.badges)
 
    def test_completionist_badge_at_100_percent(self):
        _award_completion_badges(self.profile, solved_count=10, total=10)
        self.profile.refresh_from_db()
        self.assertIn("completionist", self.profile.badges)
 
    def test_completionist_not_awarded_below_100_percent(self):
        _award_completion_badges(self.profile, solved_count=9, total=10)
        self.profile.refresh_from_db()
        self.assertNotIn("completionist", self.profile.badges)
 
    def test_high_scorer_badge_awarded_at_500_xp(self):
        self.profile.xp_points = 500
        self.profile.save()
        _award_completion_badges(self.profile, solved_count=1, total=10)
        self.profile.refresh_from_db()
        self.assertIn("high_scorer", self.profile.badges)
 
    def test_high_scorer_not_awarded_below_500_xp(self):
        self.profile.xp_points = 499
        self.profile.save()
        _award_completion_badges(self.profile, solved_count=1, total=10)
        self.profile.refresh_from_db()
        self.assertNotIn("high_scorer", self.profile.badges)
 
    def test_badges_are_idempotent(self):
        """Calling twice should not duplicate any badge."""
        _award_completion_badges(self.profile, solved_count=1, total=10)
        _award_completion_badges(self.profile, solved_count=1, total=10)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.badges.count("first_blood"), 1)
 
    def test_zero_total_does_not_error(self):
        """Guard against division when challenge list is empty."""
        try:
            _award_completion_badges(self.profile, solved_count=0, total=0)
        except Exception as exc:
            self.fail(f"_award_completion_badges raised {exc} with total=0")
 
    def test_multiple_badges_awarded_in_single_call(self):
        """At solved=1 with only 1 total and xp>=500, three badges fire."""
        self.profile.xp_points = 500
        self.profile.save()
        _award_completion_badges(self.profile, solved_count=1, total=1)
        self.profile.refresh_from_db()
        self.assertIn("first_blood",    self.profile.badges)
        self.assertIn("half_way",       self.profile.badges)
        self.assertIn("completionist",  self.profile.badges)
        self.assertIn("high_scorer",    self.profile.badges)
 
 

#5. -- view tests 

class ProgressDashboardViewTest(TestCase):
 
    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.url = "/challenge/progress/"
 
    # -- Auth guard ==
    def test_unauthenticated_redirects_to_login(self):
        resp = self.client.get(self.url)
        self.assertIn(resp.status_code, [302, 301])
        self.assertIn("/login", resp["Location"])
 
    # --Empty state 

    def test_authenticated_returns_200(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
 
    def test_uses_correct_template(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, "introduction/progress_dashboard.html")
 
    def test_context_has_required_keys(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        for key in ("challenges_data", "stats", "badges", "badge_wall"):
            self.assertIn(key, resp.context, f"Context missing key: {key}")
 
    def test_stats_keys_present(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        stats = resp.context["stats"]
        for key in (
            "total_count", "solved_count", "started_count",
            "completion_pct", "total_points", "xp_points",
            "xp_level", "xp_progress_pct", "streak_days",
        ):
            self.assertIn(key, stats, f"stats missing key: {key}")
 
    def test_no_challenges_gives_zero_counts(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        stats = resp.context["stats"]
        self.assertEqual(stats["total_count"], 0)
        self.assertEqual(stats["solved_count"], 0)
        self.assertEqual(stats["completion_pct"], 0)
 
    # -- With challenges

    def test_challenges_data_length_matches_challenge_count(self):
        make_challenge(name="c1", docker_image="pygoat/c1")
        make_challenge(name="c2", docker_image="pygoat/c2", start_port=8120, end_port=8130)
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        self.assertEqual(len(resp.context["challenges_data"]), 2)
 
    def test_unsolved_challenge_shows_not_solved(self):
        make_challenge()
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        item = resp.context["challenges_data"][0]
        self.assertFalse(item["is_solved"])
        self.assertFalse(item["started"])
 
    def test_solved_challenge_reflected_in_stats(self):
        chal = make_challenge()
        solve_challenge(self.user, chal)
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        stats = resp.context["stats"]
        self.assertEqual(stats["solved_count"], 1)
        self.assertEqual(stats["total_points"], chal.point)
 
    def test_completion_percentage_calculated_correctly(self):
        c1 = make_challenge(name="c1", docker_image="pygoat/c1")
        make_challenge(name="c2", docker_image="pygoat/c2", start_port=8120, end_port=8130)
        solve_challenge(self.user, c1)
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        self.assertEqual(resp.context["stats"]["completion_pct"], 50)
 
    def test_in_progress_challenge_counted_in_started(self):
        chal = make_challenge()
        UserChallenge.objects.create(
            user=self.user, challenge=chal,
            container_id="x", port=8100, is_solved=False,
        )
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        self.assertEqual(resp.context["stats"]["started_count"], 1)
 
    # -- XP sync --
    def test_xp_syncs_with_solved_points_on_load(self):
        """If profile XP is stale (0) but user has solved challenges, it must sync."""
        chal = make_challenge(point=150)
        solve_challenge(self.user, chal)
        # Force XP to be wrong
        self.user.profile.xp_points = 0
        self.user.profile.save()
 
        self.client.login(username="testuser", password="testpass123")
        self.client.get(self.url)  # sync happens here
 
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.xp_points, 150)
 
    # -- Badge wall

    def test_badge_wall_contains_all_catalogue_entries(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        self.assertEqual(len(resp.context["badge_wall"]), len(BADGE_CATALOGUE))
 
    def test_badge_wall_marks_unearned_badges_as_not_earned(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        for badge in resp.context["badge_wall"]:
            self.assertFalse(badge["earned"])
 
    def test_badge_wall_marks_earned_badge_correctly(self):
        self.user.profile.award_badge("first_blood")
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        earned = [b for b in resp.context["badge_wall"] if b["key"] == "first_blood"]
        self.assertTrue(earned[0]["earned"])
 
 

 #6. view tests -- progress_api

class ProgressAPIViewTest(TestCase):
 
    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.url = "/challenge/progress/api/"
 
    def test_unauthenticated_redirects(self):
        resp = self.client.get(self.url)
        self.assertIn(resp.status_code, [302, 301])
 
    def test_authenticated_returns_200(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
 
    def test_response_is_json(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        self.assertEqual(resp["Content-Type"], "application/json")
 
    def test_response_contains_required_keys(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        data = json.loads(resp.content)
        for key in ("solved", "in_progress", "not_started", "total", "xp_points", "streak_days"):
            self.assertIn(key, data, f"API response missing key: {key}")
 
    def test_empty_challenge_list_returns_all_zeros(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        data = json.loads(resp.content)
        self.assertEqual(data["total"], 0)
        self.assertEqual(data["solved"], 0)
        self.assertEqual(data["in_progress"], 0)
        self.assertEqual(data["not_started"], 0)
 
    def test_not_started_count_correct(self):
        make_challenge(name="c1", docker_image="pygoat/c1")
        make_challenge(name="c2", docker_image="pygoat/c2", start_port=8120, end_port=8130)
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        data = json.loads(resp.content)
        self.assertEqual(data["not_started"], 2)
        self.assertEqual(data["total"], 2)
 
    def test_solved_count_correct(self):
        chal = make_challenge()
        solve_challenge(self.user, chal)
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        data = json.loads(resp.content)
        self.assertEqual(data["solved"], 1)
        self.assertEqual(data["not_started"], 0)
 
    def test_in_progress_count_correct(self):
        chal = make_challenge()
        UserChallenge.objects.create(
            user=self.user, challenge=chal,
            container_id="x", port=8100, is_solved=False,
        )
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        data = json.loads(resp.content)
        self.assertEqual(data["in_progress"], 1)
        self.assertEqual(data["solved"], 0)
 
    def test_counts_sum_to_total(self):
        c1 = make_challenge(name="c1", docker_image="pygoat/c1")
        c2 = make_challenge(name="c2", docker_image="pygoat/c2", start_port=8120, end_port=8130)
        make_challenge(name="c3", docker_image="pygoat/c3", start_port=8140, end_port=8150)
        solve_challenge(self.user, c1)
        UserChallenge.objects.create(
            user=self.user, challenge=c2, container_id="x", port=8100
        )
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        data = json.loads(resp.content)
        self.assertEqual(
            data["solved"] + data["in_progress"] + data["not_started"],
            data["total"],
        )
 
    def test_xp_points_in_response(self):
        self.user.profile.xp_points = 250
        self.user.profile.save()
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        data = json.loads(resp.content)
        self.assertEqual(data["xp_points"], 250)
 
    def test_streak_days_in_response(self):
        self.user.profile.streak_days = 5
        self.user.profile.save()
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        data = json.loads(resp.content)
        self.assertEqual(data["streak_days"], 5)
 
#-----------------------------
# 7. view tests - submit_flag
#-----------------------------
class SubmitFlagViewTest(TestCase):
 
    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.chal = make_challenge(flag="CORRECT_FLAG", point=100)
        self.url = "/challenge/progress/flag/"
 
    def _post(self, challenge_id=None, flag=None):
        payload = {}
        if challenge_id is not None:
            payload["challenge_id"] = challenge_id
        if flag is not None:
            payload["flag"] = flag
        return self.client.post(self.url, payload)
 
    # -- Auth & method guards 
 
    def test_unauthenticated_redirects(self):
        resp = self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        self.assertIn(resp.status_code, [302, 301])
 
    def test_get_request_returns_405(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 405)
 
    # -- Input validation --
    def test_missing_challenge_id_returns_400(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self._post(flag="some_flag")
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.content)
        self.assertFalse(data["success"])
 
    def test_missing_flag_returns_400(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self._post(challenge_id=self.chal.pk)
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.content)
        self.assertFalse(data["success"])
 
    def test_empty_flag_returns_400(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self._post(challenge_id=self.chal.pk, flag="   ")
        self.assertEqual(resp.status_code, 400)
 
    def test_non_integer_challenge_id_returns_404(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self._post(challenge_id="not_a_number", flag="FLAG")
        self.assertEqual(resp.status_code, 404)
 
    def test_nonexistent_challenge_id_returns_404(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self._post(challenge_id=99999, flag="FLAG")
        self.assertEqual(resp.status_code, 404)
 
    # -- Wrong flag 
    def test_wrong_flag_returns_success_false(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self._post(challenge_id=self.chal.pk, flag="WRONG_FLAG")
        data = json.loads(resp.content)
        self.assertFalse(data["success"])
 
    def test_wrong_flag_increments_attempt_counter(self):
        self.client.login(username="testuser", password="testpass123")
        self._post(challenge_id=self.chal.pk, flag="WRONG")
        uc = UserChallenge.objects.get(user=self.user, challenge=self.chal)
        self.assertEqual(uc.no_of_attempt, 1)
 
    def test_wrong_flag_does_not_mark_solved(self):
        self.client.login(username="testuser", password="testpass123")
        self._post(challenge_id=self.chal.pk, flag="WRONG")
        uc = UserChallenge.objects.get(user=self.user, challenge=self.chal)
        self.assertFalse(uc.is_solved)
 
    def test_wrong_flag_does_not_award_xp(self):
        self.client.login(username="testuser", password="testpass123")
        self._post(challenge_id=self.chal.pk, flag="WRONG")
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.xp_points, 0)
 
    def test_multiple_wrong_flags_accumulate_attempts(self):
        self.client.login(username="testuser", password="testpass123")
        self._post(challenge_id=self.chal.pk, flag="WRONG1")
        self._post(challenge_id=self.chal.pk, flag="WRONG2")
        self._post(challenge_id=self.chal.pk, flag="WRONG3")
        uc = UserChallenge.objects.get(user=self.user, challenge=self.chal)
        self.assertEqual(uc.no_of_attempt, 3)
 
    # -- Correct flag — first solve-- 
    def test_correct_flag_returns_success_true(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        data = json.loads(resp.content)
        self.assertTrue(data["success"])
 
    def test_correct_flag_returns_200(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        self.assertEqual(resp.status_code, 200)
 
    def test_correct_flag_awards_correct_xp_amount(self):
        self.client.login(username="testuser", password="testpass123")
        resp = self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        data = json.loads(resp.content)
        self.assertEqual(data["xp_awarded"], self.chal.point)
 
    def test_correct_flag_marks_challenge_solved(self):
        self.client.login(username="testuser", password="testpass123")
        self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        uc = UserChallenge.objects.get(user=self.user, challenge=self.chal)
        self.assertTrue(uc.is_solved)
 
    def test_correct_flag_increments_attempt_counter(self):
        self.client.login(username="testuser", password="testpass123")
        self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        uc = UserChallenge.objects.get(user=self.user, challenge=self.chal)
        self.assertEqual(uc.no_of_attempt, 1)
 
    def test_correct_flag_increases_xp_in_profile(self):
        self.client.login(username="testuser", password="testpass123")
        self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.xp_points, self.chal.point)
 
    def test_correct_flag_awards_first_blood_badge(self):
        self.client.login(username="testuser", password="testpass123")
        self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        self.user.profile.refresh_from_db()
        self.assertIn("first_blood", self.user.profile.badges)
 
     
    # -- Correct flag — already solved 
    def test_repeat_correct_flag_returns_success_true(self):
        self.client.login(username="testuser", password="testpass123")
        self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        resp = self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        data = json.loads(resp.content)
        self.assertTrue(data["success"])
 
    def test_repeat_correct_flag_awards_zero_xp(self):
        self.client.login(username="testuser", password="testpass123")
        self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        resp = self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        data = json.loads(resp.content)
        self.assertEqual(data["xp_awarded"], 0)
 
    def test_xp_not_doubled_on_second_correct_submission(self):
        self.client.login(username="testuser", password="testpass123")
        self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.xp_points, self.chal.point)
 
    def test_attempt_counter_increments_on_repeat_correct(self):
        self.client.login(username="testuser", password="testpass123")
        self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        uc = UserChallenge.objects.get(user=self.user, challenge=self.chal)
        self.assertEqual(uc.no_of_attempt, 2)
 
    # -- Mixed wrong/correct 
    def test_wrong_then_correct_still_marks_solved(self):
        self.client.login(username="testuser", password="testpass123")
        self._post(challenge_id=self.chal.pk, flag="WRONG")
        self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        uc = UserChallenge.objects.get(user=self.user, challenge=self.chal)
        self.assertTrue(uc.is_solved)
        self.assertEqual(uc.no_of_attempt, 2)
 
    # -- Half-way and completionist badges 
    def test_half_way_badge_awarded_at_50_percent(self):
        c2 = make_challenge(
            name="c2", docker_image="pygoat/c2",
            flag="FLAG2", point=100, start_port=8120, end_port=8130
        )
        self.client.login(username="testuser", password="testpass123")
        self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        self._post(challenge_id=c2.pk, flag="FLAG2")
        self.user.profile.refresh_from_db()
        self.assertIn("half_way", self.user.profile.badges)
 
    def test_completionist_badge_awarded_on_last_challenge(self):
        self.client.login(username="testuser", password="testpass123")
        # There is exactly 1 challenge (setUp only creates self.chal)
        self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        self.user.profile.refresh_from_db()
        self.assertIn("completionist", self.user.profile.badges)
 
    def test_high_scorer_badge_awarded_at_500_xp(self):
        # Make challenges totalling 500 points
        chals = [self.chal]
        pts = [100]
        for i in range(4):
            c = make_challenge(
                name=f"c{i}", docker_image=f"pygoat/c{i}",
                flag=f"FLAG{i}", point=100,
                start_port=8120 + i * 20, end_port=8130 + i * 20,
            )
            chals.append(c)
            pts.append(100)
 
        self.client.login(username="testuser", password="testpass123")
        self._post(challenge_id=self.chal.pk, flag="CORRECT_FLAG")
        for i, c in enumerate(chals[1:]):
            self._post(challenge_id=c.pk, flag=f"FLAG{i}")
 
        self.user.profile.refresh_from_db()
        self.assertIn("high_scorer", self.user.profile.badges)
 
 
# 8. url routing test
class DashboardURLTest(TestCase):
 
    def test_progress_dashboard_url_resolves(self):
        found = resolve("/challenge/progress/")
        self.assertEqual(found.func, progress_dashboard)
 
    def test_progress_api_url_resolves(self):
        found = resolve("/challenge/progress/api/")
        self.assertEqual(found.func, progress_api)
 
    def test_submit_flag_url_resolves(self):
        found = resolve("/challenge/progress/flag/")
        self.assertEqual(found.func, submit_flag)
 
    def test_progress_dashboard_reverse(self):
        url = reverse("progress_dashboard")
        self.assertEqual(url, "/challenge/progress/")
 
    def test_progress_api_reverse(self):
        url = reverse("progress_api")
        self.assertEqual(url, "/challenge/progress/api/")
 
    def test_submit_flag_reverse(self):
        url = reverse("submit_flag")
        self.assertEqual(url, "/challenge/progress/flag/")
 
 
 # 9,integration test -  end-to-end user journeys

class ProgressDashboardIntegrationTest(TestCase):
    """
    End-to-end flow tests that exercise multiple components together.
    """
 
    def setUp(self):
        self.client = Client()
 
    # ---new user journery
    def test_new_user_has_empty_dashboard(self):
        user = make_user(username="alice")
        make_challenge()
        self.client.login(username="alice", password="testpass123")
        resp = self.client.get("/challenge/progress/")
        stats = resp.context["stats"]
        self.assertEqual(stats["solved_count"], 0)
        self.assertEqual(stats["total_points"], 0)
        self.assertEqual(stats["xp_points"], 0)
 
    def test_full_solve_flow_updates_dashboard(self):
        user = make_user(username="bob")
        chal = make_challenge(flag="FLAGB", point=150)
        self.client.login(username="bob", password="testpass123")
 
        # Submit correct flag
        self.client.post("/challenge/progress/flag/", {
            "challenge_id": chal.pk,
            "flag": "FLAGB",
        })
 
        # Dashboard must reflect the solve
        resp = self.client.get("/challenge/progress/")
        stats = resp.context["stats"]
        self.assertEqual(stats["solved_count"], 1)
        self.assertEqual(stats["total_points"], 150)
        self.assertEqual(stats["completion_pct"], 100)
 
    def test_api_and_html_dashboard_return_consistent_counts(self):
        user = make_user(username="carol")
        c1 = make_challenge(name="c1", docker_image="pygoat/c1", flag="F1")
        c2 = make_challenge(
            name="c2", docker_image="pygoat/c2", flag="F2",
            start_port=8120, end_port=8130
        )
        self.client.login(username="carol", password="testpass123")
        self.client.post("/challenge/progress/flag/", {"challenge_id": c1.pk, "flag": "F1"})
 
        html_resp = self.client.get("/challenge/progress/")
        api_resp  = self.client.get("/challenge/progress/api/")
        api_data  = json.loads(api_resp.content)
 
        html_solved = html_resp.context["stats"]["solved_count"]
        self.assertEqual(html_solved, api_data["solved"])
 
    def test_two_users_progress_does_not_interfere(self):
        u1 = make_user(username="u1")
        u2 = make_user(username="u2")
        chal = make_challenge()
 
        # u1 solves the challenge
        c1 = Client()
        c1.login(username="u1", password="testpass123")
        c1.post("/challenge/progress/flag/", {
            "challenge_id": chal.pk, "flag": "SECRET"
        })
 
        # u2 dashboard should still show 0 solved
        c2 = Client()
        c2.login(username="u2", password="testpass123")
        resp = c2.get("/challenge/progress/api/")
        data = json.loads(resp.content)
        self.assertEqual(data["solved"], 0)
 
    def test_streak_accumulates_across_login_days(self):
        """Simulate 3 consecutive daily logins using mocked date.today()."""
        from challenge import signals as sig_module
 
        user = make_user(username="dave")
        profile = user.profile
 
        factory = RequestFactory()
        request = factory.get("/")
        request.user = user
 
        base = date(2025, 6, 1)
 
        for day_offset in range(3):
            simulated_date = base + timedelta(days=day_offset)
            with patch("challenge.signals.date") as mock_date:
                mock_date.today.return_value = simulated_date
                mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
                update_streak_on_login(sender=User, request=request, user=user)
            profile.refresh_from_db()
 
        self.assertEqual(profile.streak_days, 3)
        self.assertIn("streak_3", profile.badges)
 
    def test_xp_badge_and_progress_all_consistent_after_multiple_solves(self):
        user = make_user(username="eve")
        chals = []
        for i in range(5):
            chals.append(make_challenge(
                name=f"lab{i}", docker_image=f"pygoat/lab{i}",
                flag=f"FLAG{i}", point=100,
                start_port=8200 + i * 20, end_port=8210 + i * 20,
            ))
 
        c = Client()
        c.login(username="eve", password="testpass123")
        for i, ch in enumerate(chals):
            c.post("/challenge/progress/flag/", {
                "challenge_id": ch.pk, "flag": f"FLAG{i}"
            })
 
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.xp_points, 500)
        self.assertIn("first_blood",   user.profile.badges)
        self.assertIn("half_way",      user.profile.badges)
        self.assertIn("completionist", user.profile.badges)
        self.assertIn("high_scorer",   user.profile.badges)
 
        api_resp = c.get("/challenge/progress/api/")
        data = json.loads(api_resp.content)
        self.assertEqual(data["solved"], 5)
        self.assertEqual(data["xp_points"], 500)
 
    def test_wrong_attempts_before_solve_not_double_counted(self):
        user = make_user(username="frank")
        chal = make_challenge(flag="RIGHT")
        c = Client()
        c.login(username="frank", password="testpass123")
 
        c.post("/challenge/progress/flag/", {"challenge_id": chal.pk, "flag": "WRONG"})
        c.post("/challenge/progress/flag/", {"challenge_id": chal.pk, "flag": "WRONG"})
        c.post("/challenge/progress/flag/", {"challenge_id": chal.pk, "flag": "RIGHT"})
 
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.xp_points, chal.point)  # not tripled
 
        uc = UserChallenge.objects.get(user=user, challenge=chal)
        self.assertEqual(uc.no_of_attempt, 3)
        self.assertTrue(uc.is_solved)
 