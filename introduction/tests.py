import datetime

from django.contrib.auth.models import User
from django.test import Client, TestCase


class SSRFLabTests(TestCase):
    """ssrf_lab reads a local file whose path is built from user input."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")

    def test_get_returns_200(self):
        response = self.client.get("/ssrf_lab")
        self.assertEqual(response.status_code, 200)

    def test_nonexistent_file_returns_no_blog_found(self):
        response = self.client.post("/ssrf_lab", {"blog": "does_not_exist.txt"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No blog found")

    def test_path_traversal_reads_arbitrary_file(self):
        # os.path.join(base, absolute_path) discards the base entirely, so
        # submitting an absolute path lets an attacker read any readable file.
        # /etc/hostname is always present and world-readable on Linux.
        import socket
        hostname = socket.gethostname()
        response = self.client.post("/ssrf_lab", {"blog": "/etc/hostname"})
        self.assertEqual(response.status_code, 200)
        # If the traversal works, the response body contains the hostname string.
        self.assertContains(response, hostname)

    def test_unauthenticated_redirects_to_login(self):
        anon = Client()
        response = anon.get("/ssrf_lab")
        self.assertIn(response.status_code, (301, 302))
        self.assertIn("/login/", response["Location"])


class CommandInjectionLabTests(TestCase):
    """cmd_lab passes user-supplied domain to shell=True subprocess."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")

    def test_get_returns_200(self):
        response = self.client.get("/cmd_lab")
        self.assertEqual(response.status_code, 200)

    def test_valid_domain_produces_output(self):
        response = self.client.post("/cmd_lab", {"domain": "localhost", "os": "linux"})
        self.assertEqual(response.status_code, 200)

    def test_shell_injection_via_semicolon(self):
        # The domain value is interpolated directly into "dig {domain}".
        # Appending "; echo INJECTED" causes the shell to run a second command.
        # Because shell=True is used, the output of the injected command appears
        # in the response alongside (or instead of) the dig output.
        payload = "localhost; echo INJECTED"
        response = self.client.post("/cmd_lab", {"domain": payload, "os": "linux"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "INJECTED")

    def test_unauthenticated_redirects_to_login(self):
        anon = Client()
        response = anon.post("/cmd_lab", {"domain": "example.com", "os": "linux"})
        self.assertIn(response.status_code, (301, 302))
        self.assertIn("/login/", response["Location"])


class EvalInjectionLabTests(TestCase):
    """cmd_lab2 passes user input directly to eval(), allowing code execution."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")

    def test_get_returns_200(self):
        response = self.client.get("/cmd_lab2")
        self.assertEqual(response.status_code, 200)

    def test_arithmetic_expression_is_evaluated(self):
        response = self.client.post("/cmd_lab2", {"val": "6 * 7"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "42")

    def test_builtin_call_executes_arbitrary_code(self):
        # eval() can call any Python built-in. __import__ lets an attacker load
        # modules. Here we call __import__('os').getpid() which returns an
        # integer; a non-error response shows the expression was executed.
        response = self.client.post("/cmd_lab2", {"val": "__import__('os').getpid()"})
        self.assertEqual(response.status_code, 200)
        # The PID is a positive integer; confirm digits appear in the output.
        content = response.content.decode()
        self.assertTrue(any(ch.isdigit() for ch in content))

    def test_unauthenticated_redirects_to_login(self):
        anon = Client()
        response = anon.post("/cmd_lab2", {"val": "1+1"})
        self.assertIn(response.status_code, (301, 302))
        self.assertIn("/login/", response["Location"])


class CryptoFailurelab3Tests(TestCase):
    """crypto_failure_lab3 stores an unencrypted cookie that can be forged."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")

    def test_get_without_cookie_returns_login_form(self):
        response = self.client.get("/cryptographic_failure/lab3")
        self.assertEqual(response.status_code, 200)

    def test_valid_credentials_set_plaintext_cookie(self):
        response = self.client.post(
            "/cryptographic_failure/lab3",
            {"username": "User", "password": "P@$$w0rd"},
        )
        self.assertEqual(response.status_code, 200)
        # The cookie is stored as "User|<ISO datetime>" with no signing or
        # encryption, making it trivially readable and forgeable.
        cookie_value = response.cookies.get("cookie")
        self.assertIsNotNone(cookie_value)
        self.assertIn("User", cookie_value.value)

    def test_forged_admin_cookie_grants_admin_access(self):
        # Any client can craft a cookie with "admin" as the first field.
        # The server splits on "|" and checks only the first segment.
        expire = datetime.datetime.now() + datetime.timedelta(minutes=60)
        self.client.cookies["cookie"] = f"admin|{expire.isoformat()}"
        response = self.client.get("/cryptographic_failure/lab3")
        self.assertEqual(response.status_code, 200)
        # The view sets admin=True in context when the cookie starts with "admin".
        self.assertNotContains(response, "success=False")
        content = response.content.decode()
        # Confirm the admin branch was reached (the template renders admin-specific content).
        self.assertTrue("admin" in content.lower())

    def test_wrong_credentials_do_not_set_valid_session(self):
        response = self.client.post(
            "/cryptographic_failure/lab3",
            {"username": "wrong", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "failure")
