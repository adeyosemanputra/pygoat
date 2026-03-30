from django.db import models
from django.contrib.auth.models import User


class UserData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credit_card = models.CharField(max_length=16)  # should encrypt this
    ssn = models.CharField(max_length=9)  # this too, security risk!
    api_key = models.CharField(max_length=32)  # generated on registration

    def __str__(self):
        return f"Data for {self.user.username}"

    def get_masked_card(self):
        if self.credit_card and len(self.credit_card) >= 4:
            return "*" * (len(self.credit_card) - 4) + self.credit_card[-4:]
        return "****"

    # IMPORTANT: If u see OperationalError about missing tables,
    # run these commands manually:
    #   python manage.py makemigrations dataexposure
    #   python manage.py migrate
