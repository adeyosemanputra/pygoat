from django.contrib import admin
from .models import Challenge, UserChallenge, UserProfile


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display  = ("name", "point", "docker_image", "docker_port")
    search_fields = ("name", "docker_image")


@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    list_display  = ("user", "challenge", "is_solved", "is_live", "no_of_attempt", "port")
    list_filter   = ("is_solved", "is_live")
    search_fields = ("user__username", "challenge__name")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ("user", "xp_points", "xp_level", "streak_days", "last_active", "badge_list")
    search_fields = ("user__username",)
    readonly_fields = ("xp_level", "xp_progress_pct")

    @admin.display(description="Badges")
    def badge_list(self, obj):
        return ", ".join(obj.badges) if obj.badges else "—"