import json

from django.contrib.auth.models import User
from django.test import TestCase

from challenge.models import Lab


class CustomLabJsonInputTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user("lab-admin", password="pw", is_staff=True)
        self.client.force_login(self.staff)
        self.lab = Lab.objects.create(
            name="existing", build_location="dockerized_labs/xss_lab", port=5006
        )

    def test_invalid_json_bodies_return_400_without_changing_labs(self):
        bodies = (b"{", b"\xff", b"[]", b"null", b"123", b'"text"')
        urls = (
            "/challenge/custom-labs/create/",
            f"/challenge/custom-labs/update/{self.lab.pk}/",
        )
        for body in bodies:
            for url in urls:
                with self.subTest(body=body, url=url):
                    response = self.client.post(
                        url, data=body, content_type="application/json"
                    )
                    self.assertEqual(response.status_code, 400, response.content)
                    self.lab.refresh_from_db()
                    self.assertEqual(self.lab.name, "existing")
                    self.assertEqual(Lab.objects.count(), 1)

    def test_valid_json_objects_can_still_create_and_update_labs(self):
        data = {
            "name": "new-lab",
            "build_location": "dockerized_labs/xss_lab",
            "port": 5006,
        }
        response = self.client.post(
            "/challenge/custom-labs/create/",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        lab_id = response.json()["lab"]["id"]
        data["name"] = "updated-lab"
        response = self.client.post(
            f"/challenge/custom-labs/update/{lab_id}/",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(Lab.objects.filter(pk=lab_id, name="updated-lab").exists())
