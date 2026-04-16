from django.db import models
from django.contrib.auth.models import User
import hashlib  # Import hashlib
from django.core.exceptions import ValidationError  # Import ValidationError


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

    # Overriding default save method
    def save(self, *args, **kwargs):
        if self.start_port > self.end_port:
            raise ValidationError(
                "Start port should be less than end port"
            )  # Raise ValidationError if start_port is greater than end_port
        if self.flag:
            if not self.flag.startswith("hashed_"):
                self.flag = (
                    "hashed_" + hashlib.sha256(self.flag.encode("utf-8")).hexdigest()
                )
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

    def __str__(self):
        return f"{self.user.username} - {self.challenge.name}"

# ─── New model: Progress Dashboard ────────────────────────────────────────────

BADGE_CATALOGUE = {
    "first_blood":   {"label": "First Blood",     "icon": "🩸", "desc": "Solved your first challenge"},
    "half_way":      {"label": "Half Way",        "icon": "⚡", "desc": "Solved 50% of all challenges"},
    "completionist": {"label": "Completionist",   "icon": "🏆", "desc": "Solved every challenge"},
    "streak_3":      {"label": "3-Day Streak",    "icon": "🔥", "desc": "Active 3 days in a row"},
    "streak_7":      {"label": "7-Day Streak",    "icon": "💎", "desc": "Active 7 days in a row"},
    "high_scorer":   {"label": "High Scorer",     "icon": "🎯", "desc": "Earned 500+ XP"},
}


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    xp_points = models.IntegerField(default=0)
    streak_days = models.IntegerField(default=0)
    last_active = models.DateField(null=True, blank=True)
    badges = models.JSONField(default=list)

    def __str__(self):
        return f"Profile({self.user.username})"

    def add_xp(self, points):
        self.xp_points += points
        self.save()

    @property
    def xp_level(self):
        return (self.xp_points // 100) + 1

    @property
    def xp_progress_pct(self):
        return self.xp_points % 100

    
    def badge_details(self):
        return [
            {
                "label": BADGE_CATALOGUE[key]["label"],
                "icon": BADGE_CATALOGUE[key]["icon"],
                "desc": BADGE_CATALOGUE[key]["desc"],
            }
            for key in self.badges
            if key in BADGE_CATALOGUE
        ]
