from django.db import models
from django.core.validators import MaxValueValidator
from django.conf import settings
# Create your models here.

class FAANG (models.Model):
    id = models.AutoField(primary_key=True)
    company=models.CharField(max_length=200);
    def __str__(self):
        return self.company;

class info(models.Model):
    id = models.AutoField(primary_key=True)
    faang=models.ForeignKey(to=FAANG,on_delete=models.CASCADE)

    ceo=models.CharField(max_length=200)
    about=models.CharField(max_length=200)

class login(models.Model):
    id = models.AutoField(primary_key=True)
    user=models.CharField(max_length=200)
    password=models.CharField(max_length=300)

class comments(models.Model):
    id = models.AutoField(primary_key=True)
    name=models.CharField(max_length=200)
    comment=models.CharField(max_length=600)

class authLogin(models.Model):
    username=models.CharField(max_length=200, unique = True)
    name=models.CharField(max_length=200)
    password=models.CharField(max_length=200)
    userid = models.AutoField(primary_key=True)

class otp(models.Model):
    id = models.AutoField(primary_key=True)
    email=models.CharField(max_length=200)
    otp=models.IntegerField(validators=[MaxValueValidator(300)])

class tickits(models.Model):
    id = models.AutoField(primary_key=True)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    tickit=models.CharField(max_length=40, unique = True)

    def __str__(self):
        return self.tickit+ " " + self.user.username; 