from django.test import TestCase, Client
from django.urls import reverse


class A10LabTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('a10_exception_lab')

    def test_vulnerable_mode_leaks_db_error(self):
        # Sending a single quote triggers a syntax error in the raw SQL
        response = self.client.get(self.url, {'id': "'"})
        self.assertEqual(response.status_code, 200)
        
        # Check for DB-specific error keywords (SQLite/Postgres common terms)
        content = response.content.decode().lower()
        self.assertTrue(
            'syntax' in content or 'error' in content,
            "Response should leak raw exception details in vulnerable mode"
        )

    def test_secure_mode_hides_error(self):
        response = self.client.get(self.url, {'id': "'", 'secure': 'true'})
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode()
        self.assertIn("An internal error occurred", content)
        self.assertNotIn("syntax error", content.lower())
