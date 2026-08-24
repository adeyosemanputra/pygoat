from django.contrib import admin
from django.utils.html import format_html
from .models import (
    DifficultyLevel, ScoringSettings, LabCompletion,
    LabScore, AchievementMilestone, UserAchievement
)


@admin.register(DifficultyLevel)
class DifficultyLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'multiplier', 'order', 'affected_content_count')
    list_editable = ('multiplier', 'order')
    ordering = ('order',)

    def affected_content_count(self, obj):
        from challenge.models import Challenge, Lab
        challenges = Challenge.objects.filter(difficulty=obj).count()
        labs = Lab.objects.filter(difficulty=obj).count()
        return format_html(
            '{} challenge(s), {} lab(s)',
            challenges, labs
        )
    affected_content_count.short_description = 'Assigned To'


@admin.register(ScoringSettings)
class ScoringSettingsAdmin(admin.ModelAdmin):
    list_display = ('base_points', 'time_bonus_max', 'time_bonus_window_minutes', 'time_penalty_floor')

    def has_add_permission(self, request):
        # Singleton: only one settings object
        return not ScoringSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LabCompletion)
class LabCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'content_name', 'started_at', 'completed_at', 'duration_display')
    list_filter = ('content_type', 'completed_at')
    search_fields = ('user__username', 'content_name')
    readonly_fields = ('duration_seconds',)

    def duration_display(self, obj):
        if obj.duration_seconds is None:
            return '—'
        mins, secs = divmod(obj.duration_seconds, 60)
        hours, mins = divmod(mins, 60)
        if hours:
            return f'{hours}h {mins}m {secs}s'
        return f'{mins}m {secs}s'
    duration_display.short_description = 'Duration'


@admin.register(LabScore)
class LabScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'completion', 'base_points', 'difficulty_multiplier', 'time_multiplier', 'final_score')
    list_filter = ('user',)
    search_fields = ('user__username',)
    readonly_fields = ('user', 'completion', 'base_points', 'difficulty_multiplier', 'time_multiplier', 'final_score', 'calculated_at')

    def has_add_permission(self, request):
        return False  # Scores are computed, not manually created


@admin.register(AchievementMilestone)
class AchievementMilestoneAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'required_completions', 'content_type_filter', 'is_active', 'earners_count')
    list_editable = ('required_completions', 'is_active')
    list_filter = ('is_active', 'content_type_filter')

    def earners_count(self, obj):
        return UserAchievement.objects.filter(milestone=obj).count()
    earners_count.short_description = 'Earned By'


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'milestone', 'earned_at')
    list_filter = ('milestone',)
    search_fields = ('user__username', 'milestone__name')
    readonly_fields = ('user', 'milestone', 'earned_at')

    def has_add_permission(self, request):
        return False  # Achievements are auto-awarded
