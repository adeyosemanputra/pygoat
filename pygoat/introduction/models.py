from django.db import models

# Create your models here.

class FAANG (models.Model):
    company=models.CharField(max_length=200);
    def __str__(self):
        return self.company;

class info(models.Model):
    faang=models.ForeignKey(to=FAANG,on_delete=models.CASCADE)
    ceo=models.CharField(max_length=200)
    about=models.CharField(max_length=200)



