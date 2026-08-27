import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Challenge, UserChallenge


class ChallengeFlagVerificationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testsecuser", password="securepassword123")
        self.raw_flag = "pygoat{sql_inj3ct10n_m4st3r}"
        
        # Creating a test challenge (flag gets auto-hashed via model save)
        self.challenge = Challenge.objects.create(
            name="sqli-docker-lab",
            description="Exploit the vulnerable SQL container",
            docker_image="pygoat/sqli-lab:latest",
            docker_port=8080,
            start_port=8000,
            end_port=8100,
            flag=self.raw_flag,
            point=100
        )
        self.url = f"/challenge/{self.challenge.name}"

    def test_unauthenticated_put_rejected(self):
        """Unauthenticated requests should receive a 401 response."""
        response = self.client.put(
            self.url,
            data=json.dumps({"flag": self.raw_flag}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["status"], "401")

    def test_challenge_not_found(self):
        """Requests for a non-existent challenge should return 404."""
        self.client.force_login(self.user)
        response = self.client.put(
            "/challenge/non-existent-lab",
            data=json.dumps({"flag": "random_flag"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["status"], "404")

    def test_invalid_json_body(self):
        """Invalid JSON bodies should return a 400 bad request."""
        self.client.force_login(self.user)
        response = self.client.put(
            self.url,
            data="not a json string",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["message"], "Invalid JSON body")

    def test_empty_flag_rejected(self):
        """Submitting an empty flag should return 400."""
        self.client.force_login(self.user)
        response = self.client.put(
            self.url,
            data=json.dumps({"flag": "   "}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["message"], "Flag is required")

    def test_incorrect_flag_increments_attempts(self):
        """Incorrect flag submissions should increment attempt count and not mark challenge as solved."""
        self.client.force_login(self.user)
        response = self.client.put(
            self.url,
            data=json.dumps({"flag": "pygoat{wrong_flag}"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["is_solved"])
        self.assertEqual(data["attempts"], 1)

        user_chal = UserChallenge.objects.get(user=self.user, challenge=self.challenge)
        self.assertFalse(user_chal.is_solved)
        self.assertEqual(user_chal.no_of_attempt, 1)

    def test_correct_flag_solves_challenge(self):
        """Submitting the correct flag should mark challenge solved and return HTTP 200."""
        self.client.force_login(self.user)
        response = self.client.put(
            self.url,
            data=json.dumps({"flag": self.raw_flag}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_solved"])
        self.assertEqual(data["message"], "Correct flag! Challenge completed.")

        user_chal = UserChallenge.objects.get(user=self.user, challenge=self.challenge)
        self.assertTrue(user_chal.is_solved)
        self.assertEqual(user_chal.no_of_attempt, 1)
