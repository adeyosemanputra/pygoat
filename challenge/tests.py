import json
import hashlib
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Challenge, UserChallenge


class ChallengeModelTest(TestCase):
    """Tests for the Challenge model flag hashing behaviour."""

    def setUp(self):
        self.challenge = Challenge.objects.create(
            name="test-challenge",
            description="A test challenge",
            docker_image="test/image:latest",
            docker_port=5000,
            start_port=8001,
            end_port=8100,
            flag="supersecretflag",
            point=100,
        )

    def test_flag_is_hashed_on_save(self):
        """Flag should be stored as hashed_ + sha256 hex, never plaintext."""
        expected = "hashed_" + hashlib.sha256("supersecretflag".encode("utf-8")).hexdigest()
        self.assertEqual(self.challenge.flag, expected)

    def test_flag_not_double_hashed(self):
        """Saving again should not re-hash an already hashed flag."""
        flag_before = self.challenge.flag
        self.challenge.save()
        self.assertEqual(self.challenge.flag, flag_before)

    def test_invalid_port_range_raises(self):
        """start_port > end_port should raise ValidationError."""
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            Challenge.objects.create(
                name="bad-ports",
                description="Bad port range",
                docker_image="test/bad:latest",
                docker_port=5000,
                start_port=9000,
                end_port=8000,
                flag="flag",
                point=50,
            )


class FlagValidationTest(TestCase):
    """Tests for the PUT /challenge/<n> flag submission endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.challenge = Challenge.objects.create(
            name="flag-test",
            description="Flag test challenge",
            docker_image="test/flag:latest",
            docker_port=5000,
            start_port=8001,
            end_port=8100,
            flag="correctflag",
            point=200,
        )
        self.user_chal = UserChallenge.objects.create(
            user=self.user,
            challenge=self.challenge,
            container_id="abc123def456",
            port=8001,
            is_live=True,
        )
        self.client.login(username="testuser", password="testpass123")

    def test_correct_flag_marks_solved(self):
        """Submitting the correct flag should set is_solved=True and return correct."""
        url = reverse("do-it-fast", kwargs={"challenge": self.challenge.name})
        response = self.client.put(
            url,
            data=json.dumps({"flag": "correctflag"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["message"], "correct")
        self.assertEqual(data["points"], 200)
        self.user_chal.refresh_from_db()
        self.assertTrue(self.user_chal.is_solved)

    def test_wrong_flag_increments_attempts(self):
        """Submitting a wrong flag should increment no_of_attempt."""
        url = reverse("do-it-fast", kwargs={"challenge": self.challenge.name})
        response = self.client.put(
            url,
            data=json.dumps({"flag": "wrongflag"}),
            content_type="application/json",
        )
        data = json.loads(response.content)
        self.assertEqual(data["message"], "incorrect")
        self.user_chal.refresh_from_db()
        self.assertEqual(self.user_chal.no_of_attempt, 1)
        self.assertFalse(self.user_chal.is_solved)

    def test_empty_flag_returns_400(self):
        """Submitting an empty flag should return status 400."""
        url = reverse("do-it-fast", kwargs={"challenge": self.challenge.name})
        response = self.client.put(
            url,
            data=json.dumps({"flag": ""}),
            content_type="application/json",
        )
        data = json.loads(response.content)
        self.assertEqual(data["status"], "400")

    def test_unauthenticated_put_returns_401(self):
        """Unauthenticated PUT should return 401."""
        self.client.logout()
        url = reverse("do-it-fast", kwargs={"challenge": self.challenge.name})
        response = self.client.put(
            url,
            data=json.dumps({"flag": "correctflag"}),
            content_type="application/json",
        )
        data = json.loads(response.content)
        self.assertEqual(data["status"], "401")

    def test_invalid_json_returns_400(self):
        """Malformed JSON body should return status 400."""
        url = reverse("do-it-fast", kwargs={"challenge": self.challenge.name})
        response = self.client.put(
            url,
            data="not-json-at-all",
            content_type="application/json",
        )
        data = json.loads(response.content)
        self.assertEqual(data["status"], "400")


class ContainerReuseTest(TestCase):
    """Tests for the container reuse logic in POST /challenge/<n>."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="reuseuser", password="testpass123"
        )
        self.challenge = Challenge.objects.create(
            name="reuse-test",
            description="Container reuse test",
            docker_image="test/reuse:latest",
            docker_port=5000,
            start_port=8001,
            end_port=8100,
            flag="reuseflag",
            point=100,
        )
        self.client.login(username="reuseuser", password="testpass123")

    @patch("challenge.views.subprocess.Popen")
    @patch("challenge.views.get_free_port")
    def test_existing_stopped_container_is_restarted(self, mock_port, mock_popen):
        """When a stopped container exists, docker start should be attempted first."""
        user_chal = UserChallenge.objects.create(
            user=self.user,
            challenge=self.challenge,
            container_id="existingcontainer123",
            port=8010,
            is_live=False,
        )
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"existingcontainer123", b"")
        mock_popen.return_value = mock_process

        url = reverse("do-it-fast", kwargs={"challenge": self.challenge.name})
        self.client.post(url)

        call_args = mock_popen.call_args[0][0]
        self.assertIn("start", call_args)
        user_chal.refresh_from_db()
        self.assertTrue(user_chal.is_live)
        mock_port.assert_not_called()

    @patch("challenge.views.subprocess.Popen")
    @patch("challenge.views.get_free_port")
    def test_dead_container_falls_back_to_new(self, mock_port, mock_popen):
        """When docker start fails, a new container should be created."""
        UserChallenge.objects.create(
            user=self.user,
            challenge=self.challenge,
            container_id="deadcontainer456",
            port=8010,
            is_live=False,
        )
        mock_port.return_value = 8020

        fail_process = MagicMock()
        fail_process.returncode = 1
        fail_process.communicate.return_value = (b"", b"No such container")

        success_process = MagicMock()
        success_process.returncode = 0
        success_process.communicate.return_value = (b"newcontainer789", b"")

        mock_popen.side_effect = [fail_process, success_process]

        url = reverse("do-it-fast", kwargs={"challenge": self.challenge.name})
        response = self.client.post(url)
        mock_port.assert_called_once()
        data = json.loads(response.content)
        self.assertEqual(data["message"], "success")
