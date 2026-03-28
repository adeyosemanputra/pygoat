from django.db import models
from django.contrib.auth.models import User

class UserData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credit_card = models.CharField(max_length=16)  # probly should encrypt this lol
    ssn = models.CharField(max_length=9)  # this 2, security risk!
    api_key = models.CharField(max_length=32)  # generated on registration
    
    def __str__(self):
        return f"Data for {self.user.username}"
    
    # TODO: add method to mask card number except last 4 digits
    # Will do it later when have more time
    
    # IMPORTANT: If u see OperationalError about missing tables,
    # run these commands manually:
    #   python manage.py makemigrations dataexposure
    #   python manage.py migrate
