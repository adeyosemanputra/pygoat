from django.conf import settings
from django.db import models

# Create your models here.


class sql_lab_table(models.Model):
    id = models.CharField(primary_key=True, max_length=200)
    password = models.CharField(max_length=200)


class Blogs(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    blog_id = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.blog_id


class CF_user(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    password2 = models.CharField(max_length=64)

    def __str__(self):
        return self.username


class AF_admin(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    session_id = models.CharField(max_length=200)
    last_login = models.DateTimeField(blank=True, null=True)
    logged_in = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    failattempt = models.IntegerField(default=0)
    lockout_cooldown = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.username


class AF_session_id(models.Model):
    id = models.AutoField(primary_key=True)
    session_id = models.CharField(max_length=200)
    user = models.CharField(max_length=200)

    def __str__(self):
        return self.user


class CSRF_user_tbl(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    balance = models.IntegerField(default=0)
    is_loggedin = models.BooleanField(default=False)

    def __str__(self):
        return self.username
