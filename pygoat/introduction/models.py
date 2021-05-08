from django.db import models
from django.core.validators import MaxValueValidator

# Create your models here.

class FAANG (models.Model):
    company=models.CharField(max_length=200);
    def __str__(self):
        return self.company;

class info(models.Model):
    faang=models.ForeignKey(to=FAANG,on_delete=models.CASCADE)

    ceo=models.CharField(max_length=200)
    about=models.CharField(max_length=200)

class login(models.Model):
    user=models.CharField(max_length=200)
    password=models.CharField(max_length=300)

class comments(models.Model):
    name=models.CharField(max_length=200)
    comment=models.CharField(max_length=600)

class authLogin(models.Model):
    username=models.CharField(max_length=200, unique = True)
    name=models.CharField(max_length=200)
    password=models.CharField(max_length=200)
    userid = models.AutoField(primary_key=True)

class otp(models.Model):
    email=models.CharField(max_length=200)
    otp=models.IntegerField(validators=[MaxValueValidator(300)])
