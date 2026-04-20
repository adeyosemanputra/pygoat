from datetime import date, timedelta
 
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
 
from .models import UserProfile
 
 
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile row the first time a User is saved."""
    if created:
        UserProfile.objects.get_or_create(user=instance)
 
 
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Keep the UserProfile in sync whenever the User is saved."""
    # get_or_create guards against edge-cases where the profile was deleted.
    UserProfile.objects.get_or_create(user=instance)
 
 
@receiver(user_logged_in)
def update_streak_on_login(sender, request, user, **kwargs):
    """
    Recalculate streak_days and last_active whenever the user logs in.
    Awards streak badges at 3 and 7 consecutive days.
    """
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
 
    today = date.today()
 
    if profile.last_active is None:
        # First ever login
        profile.streak_days = 1
    elif profile.last_active == today:
        # Already logged in today — nothing to update
        return
    elif profile.last_active == today - timedelta(days=1):
        # Consecutive day
        profile.streak_days = profile.streak_days + 1
    else:
        # Streak broken
        profile.streak_days = 1
 
    profile.last_active = today
    profile.save(update_fields=["streak_days", "last_active"])
 
    # Award streak badges (award_badge is idempotent)
    if profile.streak_days >= 3:
        profile.award_badge("streak_3")
    if profile.streak_days >= 7:
        profile.award_badge("streak_7")
 