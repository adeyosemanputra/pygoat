from django.utils import timezone


def compute_score(base_points, difficulty_multiplier, duration_seconds, settings):
    """
    Compute final score using weighted formula:
      final = base_points × difficulty_multiplier × time_multiplier

    Time multiplier ranges from settings.time_bonus_max (fast) to
    settings.time_penalty_floor (slow), linearly interpolated based on
    duration_seconds relative to settings.time_bonus_window_minutes.
    """
    window_seconds = settings.time_bonus_window_minutes * 60

    if duration_seconds is None or duration_seconds <= 0:
        time_multiplier = 1.0
    elif duration_seconds <= window_seconds:
        # Linear interpolation: fast → max bonus
        ratio = 1.0 - (duration_seconds / window_seconds)
        time_multiplier = 1.0 + ratio * (settings.time_bonus_max - 1.0)
    else:
        # Decay toward floor for slow solves (capped at 4× the window)
        overshoot = (duration_seconds - window_seconds) / (window_seconds * 3)
        overshoot = min(overshoot, 1.0)
        time_multiplier = 1.0 - overshoot * (1.0 - settings.time_penalty_floor)

    raw = base_points * difficulty_multiplier * time_multiplier
    return max(1, round(raw)), round(time_multiplier, 3)


def check_milestones(user):
    """
    Check all active milestones and award any the user has newly earned.
    Returns a list of newly awarded milestone names.
    """
    from .models import AchievementMilestone, UserAchievement, LabCompletion

    completions_any = LabCompletion.objects.filter(
        user=user, completed_at__isnull=False
    ).count()
    completions_challenge = LabCompletion.objects.filter(
        user=user, completed_at__isnull=False, content_type='challenge'
    ).count()
    completions_lab = LabCompletion.objects.filter(
        user=user, completed_at__isnull=False, content_type='lab'
    ).count()

    already_earned = set(
        UserAchievement.objects.filter(user=user).values_list('milestone_id', flat=True)
    )
    active_milestones = AchievementMilestone.objects.filter(is_active=True).exclude(
        id__in=already_earned
    )

    newly_awarded = []
    for milestone in active_milestones:
        if milestone.content_type_filter == 'challenge':
            count = completions_challenge
        elif milestone.content_type_filter == 'lab':
            count = completions_lab
        else:
            count = completions_any

        if count >= milestone.required_completions:
            UserAchievement.objects.create(user=user, milestone=milestone)
            newly_awarded.append(milestone.name)

    return newly_awarded
