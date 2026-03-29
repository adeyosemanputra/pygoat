from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase
from types import SimpleNamespace

from .views import DoItFast


class DoItFastDispatchTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_put_redirects_anonymous_user(self):
        request = self.factory.put("/challenge/test-lab")
        request.user = AnonymousUser()

        response = DoItFast.as_view()(request, challenge="test-lab")

        self.assertEqual(response.status_code, 302)

    def test_put_accepts_challenge_kwarg_for_authenticated_user(self):
        request = self.factory.put("/challenge/test-lab")
        request.user = SimpleNamespace(is_authenticated=True)

        response = DoItFast.as_view()(request, challenge="test-lab")

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 501)
        self.assertJSONEqual(
            response.content.decode(),
            {'message': 'not implemented'},
        )
