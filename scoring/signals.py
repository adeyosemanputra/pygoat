from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='scoring.LabCompletion')
def on_completion_saved(sender, instance, **kwargs):
    """When a LabCompletion is marked complete, compute/update its score."""
    if instance.completed_at is None:
        return  # Not yet completed

    from .models import LabScore, ScoringSettings
    from .scoring_engine import compute_score, check_milestones
    from challenge.models import Challenge, Lab

    settings = ScoringSettings.load()

    # Resolve difficulty
    difficulty_multiplier = 1.0
    base_points = settings.base_points
    if instance.content_type == 'challenge':
        try:
            challenge = Challenge.objects.get(pk=instance.content_id)
            base_points = challenge.point or settings.base_points
            if hasattr(challenge, 'difficulty') and challenge.difficulty:
                difficulty_multiplier = challenge.difficulty.multiplier
        except Challenge.DoesNotExist:
            pass
    elif instance.content_type == 'lab':
        try:
            lab = Lab.objects.get(pk=instance.content_id)
            if hasattr(lab, 'difficulty') and lab.difficulty:
                difficulty_multiplier = lab.difficulty.multiplier
        except Lab.DoesNotExist:
            pass

    final_score, time_mult = compute_score(
        base_points, difficulty_multiplier, instance.duration_seconds, settings
    )

    LabScore.objects.update_or_create(
        completion=instance,
        defaults={
            'user': instance.user,
            'base_points': base_points,
            'difficulty_multiplier': difficulty_multiplier,
            'time_multiplier': time_mult,
            'final_score': final_score,
        }
    )

    # Check milestones
    check_milestones(instance.user)


@receiver(post_save, sender='scoring.DifficultyLevel')
def on_difficulty_changed(sender, instance, **kwargs):
    """When an admin changes a difficulty rating, recalculate all affected scores."""
    from .models import LabCompletion, ScoringSettings, LabScore
    from .scoring_engine import compute_score
    from challenge.models import Challenge, Lab

    settings = ScoringSettings.load()

    # Find all challenges/labs with this difficulty
    challenge_ids = list(
        Challenge.objects.filter(difficulty=instance).values_list('id', flat=True)
    )
    lab_ids = list(
        Lab.objects.filter(difficulty=instance).values_list('id', flat=True)
    )

    affected_completions = LabCompletion.objects.filter(
        completed_at__isnull=False
    ).filter(
        models.Q(content_type='challenge', content_id__in=challenge_ids) |
        models.Q(content_type='lab', content_id__in=lab_ids)
    )

    for completion in affected_completions:
        base_points = settings.base_points
        if completion.content_type == 'challenge':
            try:
                base_points = Challenge.objects.get(pk=completion.content_id).point or base_points
            except Challenge.DoesNotExist:
                pass

        final_score, time_mult = compute_score(
            base_points, instance.multiplier, completion.duration_seconds, settings
        )

        LabScore.objects.update_or_create(
            completion=completion,
            defaults={
                'user': completion.user,
                'base_points': base_points,
                'difficulty_multiplier': instance.multiplier,
                'time_multiplier': time_mult,
                'final_score': final_score,
            }
        )
