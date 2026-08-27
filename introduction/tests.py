from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from introduction.models import (
    login,
    FAANG,
    info,
    comments,
    otp,
    CF_user,
    CSRF_user_tbl,
)


class LabSeederTests(TestCase):
    def test_seed_labs_populates_all_tables(self):
        out = StringIO()
        call_command("seed_labs", stdout=out)

        # Assert all required lab tables have records populated
        self.assertGreater(login.objects.count(), 0)
        self.assertGreater(FAANG.objects.count(), 0)
        self.assertGreater(info.objects.count(), 0)
        self.assertGreater(comments.objects.count(), 0)
        self.assertGreater(otp.objects.count(), 0)
        self.assertGreater(CF_user.objects.count(), 0)
        self.assertGreater(CSRF_user_tbl.objects.count(), 0)

        # Assert specific key baseline records exist
        self.assertTrue(login.objects.filter(user="admin").exists())
        self.assertTrue(login.objects.filter(user="user1").exists())
        self.assertTrue(FAANG.objects.filter(company="Google").exists())
        self.assertTrue(comments.objects.filter(name="System").exists())
        self.assertTrue(otp.objects.filter(email="admin@pygoat.com").exists())
        self.assertTrue(CF_user.objects.filter(username="admin").exists())
        self.assertTrue(CSRF_user_tbl.objects.filter(username="alice").exists())

    def test_seed_labs_is_idempotent(self):
        out = StringIO()
        call_command("seed_labs", stdout=out)

        counts_first_run = {
            "login": login.objects.count(),
            "faang": FAANG.objects.count(),
            "info": info.objects.count(),
            "comments": comments.objects.count(),
            "otp": otp.objects.count(),
            "cf_user": CF_user.objects.count(),
            "csrf_user": CSRF_user_tbl.objects.count(),
        }

        # Run command a second time
        call_command("seed_labs", stdout=out)

        counts_second_run = {
            "login": login.objects.count(),
            "faang": FAANG.objects.count(),
            "info": info.objects.count(),
            "comments": comments.objects.count(),
            "otp": otp.objects.count(),
            "cf_user": CF_user.objects.count(),
            "csrf_user": CSRF_user_tbl.objects.count(),
        }

        self.assertEqual(counts_first_run, counts_second_run)
