from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class DifficultyLevel(models.Model):
    """Admin-defined difficulty tiers (e.g. Easy, Medium, Hard, Expert)."""
    name = models.CharField(max_length=50, unique=True)
    multiplier = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.1), MaxValueValidator(10.0)],
        help_text="Score multiplier applied to base points (0.1–10.0)"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display ordering (lower = easier)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} (×{self.multiplier})"


class ScoringSettings(models.Model):
    """Singleton-style global scoring configuration."""
    base_points = models.PositiveIntegerField(
        default=100,
        help_text="Default base points before multipliers"
    )
    time_bonus_max = models.FloatField(
        default=2.0,
        help_text="Maximum time bonus multiplier (for fastest solves)"
    )
    time_bonus_window_minutes = models.PositiveIntegerField(
        default=30,
        help_text="Solves within this many minutes get max time bonus"
    )
    time_penalty_floor = models.FloatField(
        default=0.5,
        help_text="Minimum time multiplier (for slowest solves)"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Scoring Settings'
        verbose_name_plural = 'Scoring Settings'

    def save(self, *args, **kwargs):
        # Enforce singleton — always use pk=1
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Global Scoring Settings"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class LabCompletion(models.Model):
    """Tracks when a user starts and completes a lab or challenge."""
    CONTENT_TYPE_CHOICES = [
        ('challenge', 'Challenge'),
        ('lab', 'Lab'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lab_completions')
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES)
    content_id = models.PositiveIntegerField(
        help_text="PK of the Challenge or Lab"
    )
    content_name = models.CharField(
        max_length=100, blank=True,
        help_text="Denormalized name for display"
    )
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Computed: completed_at - started_at in seconds"
    )

    class Meta:
        unique_together = ['user', 'content_type', 'content_id']
        indexes = [
            models.Index(fields=['user', 'content_type']),
            models.Index(fields=['completed_at']),
        ]

    def save(self, *args, **kwargs):
        if self.completed_at and self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_seconds = max(0, int(delta.total_seconds()))
        super().save(*args, **kwargs)

    def __str__(self):
        status = "[Completed]" if self.completed_at else "[In Progress]"
        return f"{status} {self.user.username} - {self.content_type}:{self.content_name}"


class LabScore(models.Model):
    """Computed score for a specific user + lab/challenge completion."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lab_scores')
    completion = models.OneToOneField(LabCompletion, on_delete=models.CASCADE, related_name='score')
    base_points = models.PositiveIntegerField()
    difficulty_multiplier = models.FloatField()
    time_multiplier = models.FloatField()
    final_score = models.PositiveIntegerField()
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-final_score']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.final_score} pts"


class AchievementMilestone(models.Model):
    """Admin-defined milestone achievements (e.g. 'Solved 5 labs')."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=50, default='fas fa-trophy',
        help_text="FontAwesome icon class for display (e.g. fas fa-trophy)"
    )
    required_completions = models.PositiveIntegerField(
        help_text="Number of completed labs/challenges required"
    )
    content_type_filter = models.CharField(
        max_length=10, blank=True,
        choices=[('', 'Any'), ('challenge', 'Challenges only'), ('lab', 'Labs only')],
        default='',
        help_text="Restrict to a specific content type, or leave blank for any"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['required_completions']

    def __str__(self):
        return f"{self.name} ({self.required_completions} completions)"


class UserAchievement(models.Model):
    """Records when a user earns a milestone achievement."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    milestone = models.ForeignKey(AchievementMilestone, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'milestone']

    def __str__(self):
        return f"{self.user.username} earned {self.milestone.name}"
