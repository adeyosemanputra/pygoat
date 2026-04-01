from django.test import TestCase, Client


class IntroductionViewsTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertNotEqual(response.status_code, 500)

    def test_random_page(self):
        response = self.client.get("/introduction/")
        self.assertNotEqual(response.status_code, 500)

    def test_lab_page(self):
        response = self.client.get("/Lab/")
        self.assertNotEqual(response.status_code, 500)

    def test_mitre_page(self):
        response = self.client.get("/mitre/")
        self.assertNotEqual(response.status_code, 500)

    def test_registration_page(self):
        response = self.client.get("/registration/")
        self.assertNotEqual(response.status_code, 500)