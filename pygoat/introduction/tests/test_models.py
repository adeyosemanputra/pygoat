from django.test import TestCase
from introduction.models import *
from django.conf import settings
from django.contrib.auth.models import User

class ModelTests(TestCase):
    
    # Create a FAANG Model
    def test_faang_creation(self):
        f = FAANG.objects.create(company="Google")
        self.assertTrue(isinstance(f, FAANG))
        self.assertEqual(f.__str__(), f.company)

    # Create `info` Model
    def test_info_creation(self):
        f = FAANG.objects.create(company="Google")
        i = info.objects.create(ceo="SPichai", about="Google CEO", faang=f)
        self.assertTrue(isinstance(i, info))

    # Create a `login` Model
    def test_login_creation(self):
        l = login.objects.create(user="admin", password="password")
        self.assertTrue(isinstance(l, login))

    # Create a `comments` Model
    def test_comments_creation(self):
        c = comments.objects.create(name="John Doe", comment="Test Comment")
        self.assertTrue(isinstance(c, comments))

    # Create a `authLogin` model
    def test_authLogin_creation(self):
        a = authLogin.objects.create(username="testuser", name="John Doe", password="password")
        self.assertTrue(isinstance(a, authLogin))

    # Create a `otp` Model
    def test_otp_creation(self):
        o = otp.objects.create(email="john@doe.com", otp=69)
        self.assertTrue(isinstance(o, otp))

    # Create a `tickits` Model
    def test_tickits_creation(self):
        user = User.objects.create_user(username="john doe", password="password")
        t = tickits.objects.create(user=user, tickit="abcd")
        self.assertTrue(isinstance(t, tickits))
        self.assertEqual(t.__str__(), f"{t.tickit} {t.user.username}" )

    # Create a `sql_lab_table` Model
    def test_sql_lab_table_creation(self):
        s = sql_lab_table.objects.create(password="password")
        self.assertTrue(isinstance(s, sql_lab_table))