from django.urls import reverse
from django.contrib import auth
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from introduction.views import *

# Create your tests here.
class TestViews(TestCase):
    """
    Test views.py for introduction
    """
    def setUp(self):
        self.client = Client()

    def test_home_unauthenticated(self):
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code,302)

    def test_ssrf_unauthenticated(self):
        response = self.client.get(reverse('SSRF'))
        self.assertEqual(response.status_code,302)

    def test_ssrf_lab_unauthenticated(self):
        response = self.client.get(reverse('SSRF LAB'))
        self.assertEqual(response.status_code,302)