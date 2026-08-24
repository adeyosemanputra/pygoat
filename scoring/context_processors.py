from django.db.models import Sum


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

    try:
        from .models import LabScore, LabCompletion, UserAchievement
        user = request.user
        total_score = LabScore.objects.filter(user=user).aggregate(
            total=Sum('final_score')
        )['total'] or 0

        solved_count = LabCompletion.objects.filter(
            user=user, completed_at__isnull=False
        ).count()

        achievements_count = UserAchievement.objects.filter(user=user).count()

        return {
            'user_total_score': total_score,
            'user_solved_count': solved_count,
            'user_achievements_count': achievements_count,
        }
    except Exception:
        return default_context
