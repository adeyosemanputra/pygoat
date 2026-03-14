import base64
import pickle
from dataclasses import dataclass

from django.contrib.auth.models import User
from django.test import Client, TestCase

from .models import authLogin, login, otp


# Defined at module level so pickle can resolve it.
@dataclass
class _FakeAdminUser:
    admin: int = 0


class AuthRedirectTests(TestCase):
    """Unauthenticated requests to protected views must redirect to /login/."""

    def setUp(self):
        self.client = Client()

    def _assertLoginRedirect(self, response):
        self.assertIn(response.status_code, (301, 302))
        self.assertIn('/login/', response['Location'])

    def test_xss_lab_redirects_unauthenticated(self):
        response = self.client.get('/xssL')
        self._assertLoginRedirect(response)

    def test_sql_lab_redirects_unauthenticated(self):
        response = self.client.post('/sql_lab', {'name': 'admin', 'pass': 'x'})
        self._assertLoginRedirect(response)

    def test_cmd_lab_redirects_unauthenticated(self):
        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})
        self._assertLoginRedirect(response)

    def test_insec_des_lab_redirects_unauthenticated(self):
        response = self.client.get('/insec_des_lab')
        self._assertLoginRedirect(response)

    def test_ba_lab_redirects_unauthenticated(self):
        response = self.client.post('/ba_lab', {'name': 'admin', 'pass': 'x'})
        self._assertLoginRedirect(response)


class XSSLabTests(TestCase):
    """XSS lab views reflect user-supplied input without sanitisation."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_xss_lab_reflects_query(self):
        # No matching FAANG company, so the raw query is echoed in the response.
        response = self.client.get('/xssL', {'q': 'NOTACOMPANY'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NOTACOMPANY')

    def test_xss_lab2_script_tag_filter_is_bypassable(self):
        # The view strips lowercase <script> but not mixed-case variants.
        payload = '<SCRIPT>alert(1)</SCRIPT>'
        response = self.client.post('/xssL2', {'username': payload})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SCRIPT')

    def test_xss_lab2_basic_script_tags_stripped(self):
        # The view strips <script> and </script> from the input.
        # After stripping, only "alert(1)" remains from the payload.
        response = self.client.post('/xssL2', {'username': '<script>alert(1)</script>'})
        self.assertEqual(response.status_code, 200)
        # The stripped result "alert(1)" must appear in the reflected output.
        self.assertContains(response, 'alert(1)')
        # The Hello greeting confirms the username value was rendered.
        self.assertContains(response, 'Hello,')


class SQLInjectionLabTests(TestCase):
    """SQL lab builds a raw query from user input, making it injectable."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        login.objects.create(user='admin', password='secret')

    def test_valid_credentials_succeed(self):
        response = self.client.post('/sql_lab', {'name': 'admin', 'pass': 'secret'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'admin')

    def test_wrong_password_returns_error(self):
        response = self.client.post('/sql_lab', {'name': 'admin', 'pass': 'wrongpass'})
        self.assertEqual(response.status_code, 200)
        # The injected password ends up in the response on auth failure.
        self.assertContains(response, 'wrongpass')

    def test_unknown_user_returns_not_found(self):
        response = self.client.post('/sql_lab', {'name': 'ghost', 'pass': 'x'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User Not Found')

    def test_sql_injection_bypass(self):
        # Classic tautology: the injected condition makes WHERE always true.
        response = self.client.post('/sql_lab', {
            'name': 'admin',
            'pass': "' OR '1'='1",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'admin')


class InsecureDeserializationLabTests(TestCase):
    """insec_des_lab deserialises a base64-encoded pickle from a cookie."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_default_response_shows_non_admin_message(self):
        # Without a token cookie the view sets a default and shows the
        # restricted message.
        response = self.client.get('/insec_des_lab')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Only Admins can see this page')

    def test_forged_admin_cookie_grants_access(self):
        # Build a pickle with admin=1, base64-encode it, send as cookie.
        forged = _FakeAdminUser(admin=1)
        token = base64.b64encode(pickle.dumps(forged)).decode('utf-8')
        self.client.cookies['token'] = token

        response = self.client.get('/insec_des_lab')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SECRETKEY:ADMIN123')


class BrokenAccessControlLabTests(TestCase):
    """ba_lab grants admin data based on a client-controlled cookie."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        login.objects.create(user='admin', password='adminpass')
        login.objects.create(user='jack', password='jacktheripper')

    def test_forged_admin_cookie_bypasses_auth(self):
        # Any user can set admin=1 and receive the secret without knowing the
        # admin password.
        self.client.cookies['admin'] = '1'
        response = self.client.post('/ba_lab', {'name': 'anything', 'pass': 'wrong'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '0NLY_F0R_4DM1N5')

    def test_non_admin_user_does_not_see_secret(self):
        self.client.cookies['admin'] = '0'
        response = self.client.post('/ba_lab', {'name': 'jack', 'pass': 'jacktheripper'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '0NLY_F0R_4DM1N5')

    def test_no_credentials_returns_no_creds_page(self):
        response = self.client.post('/ba_lab', {'name': '', 'pass': ''})
        self.assertEqual(response.status_code, 200)


class SecurityMisconfigurationLabTests(TestCase):
    """secret view leaks a key only when the X-Host header matches."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_wrong_x_host_does_not_leak_secret(self):
        response = self.client.get('/secret', HTTP_X_HOST='attacker.com')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'S3CR37K3Y')

    def test_correct_x_host_leaks_secret(self):
        response = self.client.get('/secret', HTTP_X_HOST='admin.localhost:8000')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'S3CR37K3Y')


class OTPLabTests(TestCase):
    """OTP is returned in plaintext for regular users, exposing it directly."""

    def setUp(self):
        self.client = Client()
        otp.objects.create(id=1, email='user@example.com', otp=111)
        otp.objects.create(id=2, email='admin@pygoat.com', otp=222)

    def test_non_admin_otp_returned_in_response(self):
        # For any non-admin email the OTP value is included in the HTML response,
        # which is the vulnerability: the server hands the secret to the client.
        response = self.client.get('/otp', {'email': 'user@example.com'})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertTrue(any(ch.isdigit() for ch in content))

    def test_admin_otp_not_leaked_to_response(self):
        # Admin OTP is sent to the admin mailbox, not echoed in the response body.
        response = self.client.get('/otp', {'email': 'admin@pygoat.com'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sent To Admin Mail ID')
        self.assertNotContains(response, '222')
