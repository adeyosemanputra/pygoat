from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from challenge.models import Lab


@override_settings(LAB_DOMAIN="lvh.me")
class TraefikAuthVerifyTests(TestCase):
    url = "/auth/verify/"

    def setUp(self):
        Lab.objects.create(name="xss_lab", build_location="x", port=5000, is_custom=False)
        Lab.objects.create(name="sql_injection_lab", build_location="x", port=5001, is_custom=False)
        self.alice = User.objects.create_user("alice", password="pw")
        self.alice_bob = User.objects.create_user("alice-bob", password="pw")

    def verify(self, host, user=None):
        if user:
            self.client.force_login(user)
        return self.client.get(self.url, HTTP_X_FORWARDED_HOST=host)

    def test_owner_is_allowed(self):
        resp = self.verify("lab-alice-xss_lab.lvh.me", self.alice)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["X-Forwarded-User"], "alice")

    def test_host_with_port_and_mixed_case_is_allowed(self):
        resp = self.verify("LAB-Alice-XSS_lab.lvh.me:80", self.alice)
        self.assertEqual(resp.status_code, 200)

    def test_anonymous_is_rejected(self):
        self.assertEqual(self.verify("lab-alice-xss_lab.lvh.me").status_code, 401)

    def test_other_users_lab_is_forbidden(self):
        resp = self.verify("lab-alice-bob-xss_lab.lvh.me", self.alice)
        self.assertEqual(resp.status_code, 403)

    def test_hyphenated_username_owner_is_allowed(self):
        resp = self.verify("lab-alice-bob-xss_lab.lvh.me", self.alice_bob)
        self.assertEqual(resp.status_code, 200)

    def test_hyphenated_user_cannot_reach_prefix_user(self):
        resp = self.verify("lab-alice-xss_lab.lvh.me", self.alice_bob)
        self.assertEqual(resp.status_code, 403)

    def test_unknown_lab_is_forbidden(self):
        resp = self.verify("lab-alice-not_a_lab.lvh.me", self.alice)
        self.assertEqual(resp.status_code, 403)

    def test_foreign_domain_is_rejected(self):
        resp = self.verify("lab-alice-xss_lab.evil.com", self.alice)
        self.assertEqual(resp.status_code, 400)

    def test_missing_forwarded_host_is_rejected(self):
        self.client.force_login(self.alice)
        self.assertEqual(self.client.get(self.url).status_code, 400)


class RegistrationAndRobotsTests(TestCase):
    def test_register_creates_and_logs_in_user(self):
        resp = self.client.post("/register", {
            "username": "newbie", "email": "n@example.com",
            "password1": "Sup3r-Secret-pw!", "password2": "Sup3r-Secret-pw!",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(username="newbie").exists())
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_robots_redirects_anonymous_instead_of_500(self):
        self.assertEqual(self.client.get("/robots.txt").status_code, 302)

    def test_robots_served_to_logged_in_user(self):
        self.client.force_login(User.objects.create_user("u", password="pw"))
        resp = self.client.get("/robots.txt")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "text/plain")
