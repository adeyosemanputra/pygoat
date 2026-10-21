from django.utils import timezone

from .models import DifficultyLevel, LabCompletion

CONTENT_TYPES = ("challenge", "lab")


def default_difficulty():
    """Difficulty assigned to content that has none: Medium, else the easiest defined."""
    return (
        DifficultyLevel.objects.filter(name="Medium").first()
        or DifficultyLevel.objects.first()
    )


def start_tracking(user, content_type, content_id):
    """Record that a user started a lab/challenge. Safe to call repeatedly."""
    completion, _ = LabCompletion.objects.get_or_create(
        user=user,
        content_type=content_type,
        content_id=content_id,
        defaults={"started_at": timezone.now()},
    )
    return completion


def complete_tracking(user, content_type, content_id, content_name=""):
    """
    Mark a lab/challenge as completed for the user. The post_save signal on
    LabCompletion computes the score and awards milestones.

    Must only be called server-side after a solve has been verified.
    Returns (completion, newly_completed).
    """
    completion, _ = LabCompletion.objects.get_or_create(
        user=user,
        content_type=content_type,
        content_id=content_id,
        defaults={"started_at": timezone.now()},
    )
    if completion.completed_at:
        return completion, False

    completion.completed_at = timezone.now()
    completion.content_name = content_name or f"{content_type}:{content_id}"
    completion.save()
    return completion, True
