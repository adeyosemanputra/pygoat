from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Challenge, UserChallenge


class DoItFastTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass12345")
        self.client.login(username="tester", password="pass12345")
        self.challenge = Challenge.objects.create(
            name="demo",
            description="demo challenge",
            docker_image="demo/image",
            docker_port=80,
            start_port=8000,
            end_port=8100,
            flag="demo_flag",
            point=10,
        )
        self.url = reverse("do-it-fast", args=[self.challenge.name])

    @patch("challenge.views.get_free_port", return_value=8055)
    @patch("challenge.views.subprocess.run")
    def test_post_docker_failure_does_not_persist(self, mock_run, mock_port):
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        response = self.client.post(self.url)
        self.assertEqual(response.json()["status"], "500")
        self.assertEqual(UserChallenge.objects.count(), 0)

    @patch("challenge.views.get_free_port", return_value=8055)
    @patch("challenge.views.subprocess.run")
    def test_post_docker_success_persists_container(self, mock_run, mock_port):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "container123"
        response = self.client.post(self.url)
        self.assertEqual(response.json()["status"], "200")
        user_chal = UserChallenge.objects.get(user=self.user, challenge=self.challenge)
        self.assertEqual(user_chal.container_id, "container123")

    def test_put_returns_valid_response(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 501)
        self.assertEqual(response.json()["message"], "not implemented")
