from django.db import models


class CSRF_user_tbl(models.Model):
	username = models.CharField(max_length=200)
	password = models.CharField(max_length=200)
	balance = models.IntegerField(default=0)
	is_loggedin = models.BooleanField(default=False)
