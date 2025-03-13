from django.db import models
from django.contrib.auth.models import User

# Create your models here
class Challenge(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    docker_image = models.CharField(max_length=100, unique=True)
    docker_port = models.IntegerField()
    start_port = models.IntegerField()
    end_port = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    flag = models.CharField(max_length=100)
    point = models.IntegerField()
    
    def __str__(self):
        return self.name
    
    # overwriting default save  method
    def save(self, *args, **kwargs):
        if self.start_port > self.end_port:
            raise Exception("Start port should be less than end port")
        # Here flag need to be hashed
        super(Challenge, self).save(*args, **kwargs)

class UserChallenge(models.Model):
    """
    This is a mapping of user to challenge with proper progress tracking 
    This also allows us to reuse the created container for the user
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    container_id = models.CharField(max_length=100)
    port = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_live = models.BooleanField(default=False)
    no_of_attempt = models.IntegerField(default=0)
    is_solved = models.BooleanField(default=False)
    port = models.IntegerField()
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.name}"