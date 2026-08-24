from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import (
    LabCompletion, LabScore, UserAchievement,
    AchievementMilestone, DifficultyLevel
)


@login_required
@require_POST
def start_tracking(request, content_type, content_id):
    """Record that a user has started a lab/challenge. Called when lab is launched."""
    if content_type not in ('challenge', 'lab'):
        return JsonResponse({'status': 'error', 'message': 'Invalid content type'}, status=400)

    completion, created = LabCompletion.objects.get_or_create(
        user=request.user,
        content_type=content_type,
        content_id=content_id,
        defaults={'started_at': timezone.now()}
    )

    if not created and completion.completed_at:
        return JsonResponse({
            'status': 'already_completed',
            'message': 'This content was already completed'
        })

    return JsonResponse({
        'status': 'tracking' if created else 'resumed',
        'started_at': completion.started_at.isoformat()
    })


@login_required
@require_POST
def complete_tracking(request, content_type, content_id):
    """Mark a lab/challenge as completed. Triggers score calculation via signal."""
    if content_type not in ('challenge', 'lab'):
        return JsonResponse({'status': 'error', 'message': 'Invalid content type'}, status=400)

    try:
        completion = LabCompletion.objects.get(
            user=request.user,
            content_type=content_type,
            content_id=content_id
        )
    except LabCompletion.DoesNotExist:
        # Auto-create with started_at = now (no time bonus)
        completion = LabCompletion(
            user=request.user,
            content_type=content_type,
            content_id=content_id,
            started_at=timezone.now()
        )

    if completion.completed_at:
        score = getattr(completion, 'score', None)
        return JsonResponse({
            'status': 'already_completed',
            'final_score': score.final_score if score else 0
        })

    completion.completed_at = timezone.now()
    # Denormalize content name
    try:
        if content_type == 'challenge':
            from challenge.models import Challenge
            completion.content_name = Challenge.objects.get(pk=content_id).name
        else:
            from challenge.models import Lab
            completion.content_name = Lab.objects.get(pk=content_id).name
    except Exception:
        completion.content_name = f'{content_type}:{content_id}'

    completion.save()  # Triggers signal → score computation → milestone check

    score = getattr(completion, 'score', None)
    if score is None:
        try:
            score = LabScore.objects.get(completion=completion)
        except LabScore.DoesNotExist:
            score = None

    achievements = list(
        UserAchievement.objects.filter(user=request.user)
        .order_by('-earned_at')[:5]
        .values('milestone__name', 'milestone__icon', 'earned_at')
    )

    return JsonResponse({
        'status': 'completed',
        'final_score': score.final_score if score else 0,
        'time_multiplier': score.time_multiplier if score else 1.0,
        'difficulty_multiplier': score.difficulty_multiplier if score else 1.0,
        'duration_seconds': completion.duration_seconds,
        'recent_achievements': achievements
    })


@login_required
@require_GET
def user_scores(request):
    """Get the current user's total score and recent scores."""
    scores = LabScore.objects.filter(user=request.user).order_by('-calculated_at')
    total = sum(s.final_score for s in scores)

    return JsonResponse({
        'status': 'success',
        'total_score': total,
        'scores': [
            {
                'content': s.completion.content_name,
                'type': s.completion.content_type,
                'final_score': s.final_score,
                'time_multiplier': s.time_multiplier,
                'difficulty_multiplier': s.difficulty_multiplier,
                'completed_at': s.completion.completed_at.isoformat() if s.completion.completed_at else None,
                'duration_seconds': s.completion.duration_seconds,
            }
            for s in scores[:20]
        ]
    })


@login_required
@require_GET
def user_achievements(request):
    """Get the current user's achievements."""
    achievements = UserAchievement.objects.filter(user=request.user).select_related('milestone')

    return JsonResponse({
        'status': 'success',
        'achievements': [
            {
                'name': a.milestone.name,
                'description': a.milestone.description,
                'icon': a.milestone.icon,
                'earned_at': a.earned_at.isoformat(),
            }
            for a in achievements
        ]
    })


@login_required
def dashboard(request):
    """Full-page user scoreboard, stats, and achievements."""
    user = request.user
    scores = LabScore.objects.filter(user=user).select_related('completion').order_by('-calculated_at')
    total_score = scores.aggregate(total=Sum('final_score'))['total'] or 0

    completions = LabCompletion.objects.filter(user=user, completed_at__isnull=False)
    solved_count = completions.count()

    # Achievements progress
    user_achievements = {
        ua.milestone_id: ua.earned_at
        for ua in UserAchievement.objects.filter(user=user)
    }
    all_milestones = AchievementMilestone.objects.filter(is_active=True).order_by('required_completions')

    milestone_data = []
    completed_challenges_count = completions.filter(content_type='challenge').count()
    completed_labs_count = completions.filter(content_type='lab').count()

    for m in all_milestones:
        is_earned = m.id in user_achievements
        if m.content_type_filter == 'challenge':
            current_progress = completed_challenges_count
        elif m.content_type_filter == 'lab':
            current_progress = completed_labs_count
        else:
            current_progress = solved_count

        progress_pct = min(100, int((current_progress / m.required_completions) * 100)) if m.required_completions > 0 else 100

        milestone_data.append({
            'milestone': m,
            'is_earned': is_earned,
            'earned_at': user_achievements.get(m.id),
            'current_progress': current_progress,
            'required': m.required_completions,
            'progress_pct': progress_pct,
        })

    # Formatted score records
    score_details = []
    for s in scores:
        dur_str = '—'
        if s.completion.duration_seconds is not None:
            mins, secs = divmod(s.completion.duration_seconds, 60)
            hours, mins = divmod(mins, 60)
            if hours:
                dur_str = f"{hours}h {mins}m {secs}s"
            else:
                dur_str = f"{mins}m {secs}s"

        score_details.append({
            'content_name': s.completion.content_name,
            'content_type': s.completion.content_type,
            'base_points': s.base_points,
            'difficulty_multiplier': s.difficulty_multiplier,
            'time_multiplier': s.time_multiplier,
            'final_score': s.final_score,
            'completed_at': s.completion.completed_at,
            'duration_formatted': dur_str,
        })

    context = {
        'total_score': total_score,
        'solved_count': solved_count,
        'achievements_count': len(user_achievements),
        'total_achievements': all_milestones.count(),
        'scores': score_details,
        'milestones': milestone_data,
    }
    return render(request, 'scoring/dashboard.html', context)
