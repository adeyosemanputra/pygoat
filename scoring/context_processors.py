from django.db import DatabaseError
from django.db.models import Count, Sum


def scoring_user_context(request):
    """
    Provides scoring & progress context variables for the current authenticated user.
    """
    default_context = {
        'user_total_score': 0,
        'user_solved_count': 0,
        'user_achievements_count': 0,
    }

    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return default_context

    from .models import LabScore, UserAchievement
    user = request.user
    try:
        # One LabScore exists per completed LabCompletion
        totals = LabScore.objects.filter(user=user).aggregate(
            total=Sum('final_score'), solved=Count('id')
        )
        achievements_count = UserAchievement.objects.filter(user=user).count()
    except DatabaseError:
        # e.g. migrations not applied yet
        return default_context

    return {
        'user_total_score': totals['total'] or 0,
        'user_solved_count': totals['solved'],
        'user_achievements_count': achievements_count,
    }
