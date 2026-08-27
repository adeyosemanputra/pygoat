from django.test import TestCase
from django.urls import reverse
from challenge.models import Challenge


class DoItFastPutDispatchTest(TestCase):
    def setUp(self):
        self.challenge = Challenge.objects.create(
            name="test-challenge",
            docker_image="test-image",
            docker_port=8080,
        )
        self.url = reverse("do-it-fast", kwargs={"challenge": self.challenge.name})

    def test_put_dispatch_accepts_challenge_kwarg(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"not implemented", response.content)
