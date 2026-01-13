from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models

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

class sql_lab_table(models.Model):
    id = models.CharField(primary_key = True, max_length=200)
    password = models.CharField(max_length=200)

class Blogs(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
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
    last_login = models.DateTimeField(blank= True, null = True)
    logged_in = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    failattempt = models.IntegerField(default=0)
    lockout_cooldown = models.DateTimeField(blank= True, null = True)

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

class PaymentAccount(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    is_premium = models.BooleanField(default=False)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username} - {self.account_number}"

class PaymentTransaction(models.Model):
    id = models.AutoField(primary_key=True)
    from_account = models.ForeignKey(PaymentAccount, related_name='outgoing_transactions', on_delete=models.CASCADE)
    to_account_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True)

    def __str__(self):
        return f"Transaction {self.id}: {self.amount}"

class PaymentAPIKey(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=40, unique=True)
    is_admin = models.BooleanField(default=False)
def __str__(self):
        return f"{self.user.username} - ****{self.api_key[-4:]}"
