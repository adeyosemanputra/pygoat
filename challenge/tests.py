from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, SimpleTestCase

from .views import DoItFast


class DoItFastDispatchTests(SimpleTestCase):
	def setUp(self):
		self.factory = RequestFactory()

	def test_put_accepts_challenge_kwarg(self):
		request = self.factory.put("/challenge/test-lab")
		request.user = AnonymousUser()

		response = DoItFast.as_view()(request, challenge="test-lab")

		self.assertEqual(response, "not implemented")
