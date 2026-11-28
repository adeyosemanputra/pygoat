from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


def _write_score(completion, base_points, difficulty_multiplier, settings):
    from .models import LabScore
    from .scoring_engine import compute_score

    final_score, time_mult = compute_score(
        base_points, difficulty_multiplier, completion.duration_seconds, settings
    )
    LabScore.objects.update_or_create(
        completion=completion,
        defaults={
            'user': completion.user,
            'base_points': base_points,
            'difficulty_multiplier': difficulty_multiplier,
            'time_multiplier': time_mult,
            'final_score': final_score,
        }
    )


@receiver(post_save, sender='scoring.LabCompletion')
def on_completion_saved(sender, instance, **kwargs):
    """When a LabCompletion is marked complete, compute/update its score."""
    if instance.completed_at is None:
        return  # Not yet completed

    from .models import ScoringSettings
    from .scoring_engine import check_milestones
    from challenge.models import Challenge, Lab

    settings = ScoringSettings.load()

    difficulty_multiplier = 1.0
    base_points = settings.base_points
    if instance.content_type == 'challenge':
        challenge = Challenge.objects.select_related('difficulty').filter(pk=instance.content_id).first()
        if challenge:
            base_points = challenge.point or settings.base_points
            if challenge.difficulty:
                difficulty_multiplier = challenge.difficulty.multiplier
    elif instance.content_type == 'lab':
        lab = Lab.objects.select_related('difficulty').filter(pk=instance.content_id).first()
        if lab and lab.difficulty:
            difficulty_multiplier = lab.difficulty.multiplier

    _write_score(instance, base_points, difficulty_multiplier, settings)
    check_milestones(instance.user)


@receiver(post_save, sender='scoring.DifficultyLevel')
def on_difficulty_changed(sender, instance, **kwargs):
    """When an admin changes a difficulty rating, recalculate all affected scores."""
    from .models import LabCompletion, ScoringSettings
    from challenge.models import Challenge, Lab

    settings = ScoringSettings.load()

    challenge_points = dict(
        Challenge.objects.filter(difficulty=instance).values_list('id', 'point')
    )
    lab_ids = list(
        Lab.objects.filter(difficulty=instance).values_list('id', flat=True)
    )

    affected_completions = LabCompletion.objects.filter(
        completed_at__isnull=False
    ).filter(
        models.Q(content_type='challenge', content_id__in=challenge_points.keys()) |
        models.Q(content_type='lab', content_id__in=lab_ids)
    ).select_related('user')

    for completion in affected_completions:
        base_points = settings.base_points
        if completion.content_type == 'challenge':
            base_points = challenge_points.get(completion.content_id) or base_points
        _write_score(completion, base_points, instance.multiplier, settings)


@receiver(post_save, sender='challenge.Challenge')
@receiver(post_save, sender='challenge.Lab')
def on_content_scoring_changed(sender, instance, update_fields=None, raw=False, **kwargs):
    """Keep earned scores in sync with content points and difficulty assignments."""
    if raw:
        return
    relevant_fields = {'point', 'difficulty', 'difficulty_id'}
    if update_fields is not None and not relevant_fields.intersection(update_fields):
        return

    from .models import LabCompletion, ScoringSettings

    content_type = sender._meta.model_name
    completions = LabCompletion.objects.filter(
        content_type=content_type, content_id=instance.pk, completed_at__isnull=False
    ).select_related('user')
    if not completions.exists():
        return
    # Read persisted values so a partial save cannot use an unrelated, unsaved
    # difficulty assignment still present on the caller's model instance.
    content = sender.objects.select_related('difficulty').get(pk=instance.pk)
    settings = ScoringSettings.load()
    base_points = (content.point or settings.base_points) if content_type == 'challenge' else settings.base_points
    multiplier = content.difficulty.multiplier if content.difficulty else 1.0
    for completion in completions:
        _write_score(completion, base_points, multiplier, settings)
