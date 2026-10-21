import json
import os
from unittest.mock import MagicMock, patch

import docker
from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from challenge.models import Challenge, Lab, UserChallenge
from challenge.views import _resolve_build_path, _ensure_image_built, wait_for_health


class DoItFastDockerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="pw")
        self.client.force_login(self.user)
        self.chal = Challenge.objects.create(
            name="do-it-fast", docker_image="img", docker_port=5050, start_port=1,
            end_port=2, flag="flag{x}", point=100,
        )

    @patch("challenge.views.get_free_port", return_value=8001)
    @patch("challenge.views.get_docker_client")
    def test_start_uses_docker_sdk(self, get_client, _port):
        get_client.return_value.containers.run.return_value.id = "abc123"
        resp = self.client.post("/challenge/do-it-fast")
        self.assertEqual(resp.status_code, 200)
        get_client.return_value.containers.run.assert_called_once_with(
            "img", detach=True, ports={"5050/tcp": 8001}
        )
        self.assertEqual(UserChallenge.objects.get().container_id, "abc123")

    @patch("challenge.views.get_free_port", return_value=8001)
    @patch("challenge.views.get_docker_client", return_value=None)
    def test_start_without_docker_returns_503(self, _client, _port):
        self.assertEqual(self.client.post("/challenge/do-it-fast").status_code, 503)

    @patch("challenge.views.get_docker_client")
    def test_stop_removes_container(self, get_client):
        UserChallenge.objects.create(
            user=self.user, challenge=self.chal, container_id="abc123", port=8001, is_live=True
        )
        container = get_client.return_value.containers.get.return_value
        resp = self.client.delete("/challenge/do-it-fast")
        self.assertEqual(resp.status_code, 200)
        container.stop.assert_called_once()
        container.remove.assert_called_once()
        self.assertFalse(UserChallenge.objects.get().is_live)


class CustomLabPermissionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("bob", password="pw")
        self.staff = User.objects.create_user("admin", password="pw", is_staff=True)
        self.lab = Lab.objects.create(name="mine", build_location="dockerized_labs/xss_lab", port=5006)

    def post(self, url, data=None):
        return self.client.post(url, data=json.dumps(data or {}), content_type="application/json")

    def test_non_staff_cannot_create_update_or_delete(self):
        self.client.force_login(self.user)
        data = {"name": "x", "build_location": "dockerized_labs/xss_lab", "port": 1}
        self.assertEqual(self.post("/challenge/custom-labs/create/", data).status_code, 403)
        self.assertEqual(self.post(f"/challenge/custom-labs/update/{self.lab.id}/", data).status_code, 403)
        self.assertEqual(self.post(f"/challenge/custom-labs/delete/{self.lab.id}/").status_code, 403)
        self.assertTrue(Lab.objects.filter(pk=self.lab.pk).exists())

    def test_non_staff_can_still_list(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get("/challenge/custom-labs/list/").status_code, 200)

    def test_staff_cannot_use_paths_outside_lab_dirs(self):
        self.client.force_login(self.staff)
        for bad in ("/etc", "../../etc", "dockerized_labs/../pygoat", "introduction"):
            resp = self.post("/challenge/custom-labs/create/", {"name": "evil", "build_location": bad, "port": 80})
            self.assertEqual(resp.status_code, 400, bad)
        self.assertFalse(Lab.objects.filter(name="evil").exists())

    def test_staff_can_create_with_lab_dir(self):
        self.client.force_login(self.staff)
        resp = self.post("/challenge/custom-labs/create/",
                         {"name": "xss2", "build_location": "dockerized_labs/xss_lab", "port": 5006})
        self.assertEqual(resp.status_code, 200)

    def test_custom_labs_button_hidden_for_non_staff(self):
        self.client.force_login(self.user)
        self.assertNotContains(self.client.get("/"), 'id="custom-labs-btn"')
        self.client.force_login(self.staff)
        self.assertContains(self.client.get("/"), 'id="custom-labs-btn"')


class LabContainerTests(TestCase):
    def test_build_path_accepts_shipped_labs(self):
        for lab in ("dockerized_labs/xss_lab", "challenge/labs/bopla_lab"):
            self.assertTrue(os.path.isdir(_resolve_build_path(lab)))

    def test_build_removes_intermediate_containers(self):
        client = MagicMock()
        client.images.get.side_effect = docker.errors.ImageNotFound("x")
        _ensure_image_built(client, "xss_lab", "dockerized_labs/xss_lab")
        kwargs = client.images.build.call_args.kwargs
        self.assertTrue(kwargs["rm"])
        self.assertTrue(kwargs["forcerm"])

    def test_build_refuses_outside_path(self):
        client = MagicMock()
        client.images.get.side_effect = docker.errors.ImageNotFound("x")
        with self.assertRaises(ValueError):
            _ensure_image_built(client, "evil", "/etc")
        client.images.build.assert_not_called()

    def test_unhealthy_container_is_removed(self):
        container = MagicMock()
        container.attrs = {"State": {"Health": {"Status": "unhealthy"}}}
        with self.assertRaises(RuntimeError):
            wait_for_health(container)
        container.remove.assert_called_once_with(force=True)


@override_settings(LABS_PER_USER_LIMIT=1)
class LabQuotaTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("carol", password="pw")
        self.client.force_login(self.user)
        Lab.objects.create(name="xss_lab", build_location="dockerized_labs/xss_lab", port=5006)

    def _container(self, name, status):
        c = MagicMock()
        c.name, c.status = name, status
        return c

    @patch("challenge.views.check_traefik_reachable", return_value=True)
    @patch("challenge.views.get_docker_client")
    def test_stopped_labs_do_not_count_toward_limit(self, get_client, _traefik):
        client = get_client.return_value
        client.containers.list.return_value = [self._container("lab-carol-sql_injection_lab", "exited")]
        client.containers.get.side_effect = docker.errors.NotFound("x")
        new = client.containers.create.return_value
        new.attrs = {"State": {"Health": {"Status": "healthy"}}}
        resp = self.client.get("/challenge/start-lab/xss_lab/")
        self.assertEqual(resp.status_code, 200, resp.content)
        new.put_archive.assert_called_once()
        new.start.assert_called_once()

    @patch("challenge.views.check_traefik_reachable", return_value=True)
    @patch("challenge.views.get_docker_client")
    def test_running_labs_count_toward_limit(self, get_client, _traefik):
        get_client.return_value.containers.list.return_value = [
            self._container("lab-carol-sql_injection_lab", "running")
        ]
        self.assertEqual(self.client.get("/challenge/start-lab/xss_lab/").status_code, 429)
