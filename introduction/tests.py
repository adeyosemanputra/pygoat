from io import StringIO
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client, TestCase
from introduction.models import (
    login,
    FAANG,
    info,
    comments,
    otp,
    CF_user,
    CSRF_user_tbl,
)


class LabSeederTests(TestCase):
    def test_seed_labs_populates_all_tables(self):
        out = StringIO()
        call_command("seed_labs", stdout=out)

        # Assert all required lab tables have records populated
        self.assertGreater(login.objects.count(), 0)
        self.assertGreater(FAANG.objects.count(), 0)
        self.assertGreater(info.objects.count(), 0)
        self.assertGreater(comments.objects.count(), 0)
        self.assertGreater(otp.objects.count(), 0)
        self.assertGreater(CF_user.objects.count(), 0)
        self.assertGreater(CSRF_user_tbl.objects.count(), 0)

        # Assert specific key baseline records exist
        self.assertTrue(login.objects.filter(user="admin").exists())
        self.assertTrue(login.objects.filter(user="user1").exists())
        self.assertTrue(FAANG.objects.filter(company="Google").exists())
        self.assertTrue(comments.objects.filter(name="System").exists())
        self.assertTrue(otp.objects.filter(email="admin@pygoat.com").exists())
        self.assertTrue(CF_user.objects.filter(username="admin").exists())
        self.assertTrue(CSRF_user_tbl.objects.filter(username="alice").exists())

    def test_seed_labs_is_idempotent(self):
        out = StringIO()
        call_command("seed_labs", stdout=out)

        counts_first_run = {
            "login": login.objects.count(),
            "faang": FAANG.objects.count(),
            "info": info.objects.count(),
            "comments": comments.objects.count(),
            "otp": otp.objects.count(),
            "cf_user": CF_user.objects.count(),
            "csrf_user": CSRF_user_tbl.objects.count(),
        }

        # Run command a second time
        call_command("seed_labs", stdout=out)

        counts_second_run = {
            "login": login.objects.count(),
            "faang": FAANG.objects.count(),
            "info": info.objects.count(),
            "comments": comments.objects.count(),
            "otp": otp.objects.count(),
            "cf_user": CF_user.objects.count(),
            "csrf_user": CSRF_user_tbl.objects.count(),
        }

        self.assertEqual(counts_first_run, counts_second_run)


class AuthenticationViewRoutingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
            email="testuser@pygoat.local"
        )

    def test_unauthenticated_login_get_returns_200_without_sidebar(self):
        """Unauthenticated GET to /login returns 200 and does NOT contain sidebar navigation elements."""
        for path in ["/login", "/login/"]:
            response = self.client.get(path, follow=True)
            self.assertEqual(response.status_code, 200)
            content = response.content.decode("utf-8")
            self.assertNotIn('<nav id="sidebar"', content)
            self.assertNotIn('id="sidebar-home"', content)
            self.assertNotIn('class="sidebarClass"', content)

    def test_unauthenticated_register_get_returns_200_without_sidebar(self):
        """Unauthenticated GET to /register returns 200 and does NOT contain sidebar navigation elements."""
        response = self.client.get("/register", follow=True)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertNotIn('<nav id="sidebar"', content)
        self.assertNotIn('id="sidebar-home"', content)
        self.assertNotIn('class="sidebarClass"', content)

    def test_unauthenticated_homepage_get_redirects_to_login(self):
        """Unauthenticated GET to / redirects to /login."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/login"))

    def test_authenticated_homepage_get_returns_200_with_welcome_and_sidebar(self):
        """Authenticated GET to / returns 200 and contains the Welcome header and sidebar."""
        self.client.force_login(self.user)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("Welcome to PyGoat", content)
        self.assertIn('<nav id="sidebar"', content)


class LabRouteAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="labsecuser",
            password="labpassword123",
            email="labuser@pygoat.local"
        )
        self.key_lab_routes = [
            "/xss",
            "/xssL",
            "/sql",
            "/sql_lab",
            "/insec_des",
            "/insec_des_lab",
            "/xxe",
            "/xxe_lab",
            "/auth",
            "/auth_lab",
            "/ba",
            "/ba_lab",
            "/cmd",
            "/cmd_lab",
            "/sec_mis",
            "/sec_mis_lab",
            "/a9",
            "/a9_lab",
            "/a10",
            "/a10_lab",
            "/broken_access_control",
            "/broken_access_lab_1",
            "/ssrf",
            "/ssrf_lab",
            "/injection",
            "/injection_sql_lab",
            "/ssti",
            "/ssti/lab",
            "/cryptographic_failure",
            "/cryptographic_failure/lab",
            "/auth_failure",
            "/mitre/1",
            "/mitre/2",
            "/mitre/3",
        ]

    def test_unauthenticated_lab_routes_safely_redirect_without_500(self):
        """Unauthenticated access to key lab routes must redirect to login or handle safely without 500 crashes."""
        for route in self.key_lab_routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertNotEqual(
                    response.status_code,
                    500,
                    f"Route {route} raised a 500 Internal Server Error when accessed unauthenticated."
                )
                self.assertIn(
                    response.status_code,
                    [200, 302, 400, 401, 403, 404],
                    f"Route {route} returned unexpected status code {response.status_code}."
                )
                if response.status_code == 302:
                    self.assertTrue(
                        response.url.startswith("/login"),
                        f"Route {route} redirected to {response.url} instead of login."
                    )

    def test_authenticated_lab_routes_accessible_with_sidebar(self):
        """Authenticated users can access key lab routes with 200 response and sidebar navigation."""
        self.client.force_login(self.user)
        routes_to_check = [
            "/xss",
            "/sql",
            "/insec_des",
            "/xxe",
            "/auth",
            "/ba",
            "/cmd",
            "/sec_mis",
            "/a9",
            "/a10",
            "/broken_access_control",
            "/ssrf",
            "/injection",
            "/ssti",
            "/cryptographic_failure",
            "/auth_failure",
            "/mitre/1",
        ]
        for route in routes_to_check:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(
                    response.status_code,
                    200,
                    f"Authenticated access to route {route} failed with status {response.status_code}."
                )
                content = response.content.decode("utf-8")
                self.assertIn(
                    '<nav id="sidebar"',
                    content,
                    f"Route {route} does not include sidebar navigation for authenticated user."
                )

