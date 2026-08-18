from django.contrib import admin
from .models import Challenge, UserChallenge, Lab, LabCategoryMapping

# Register your models here.


@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ("name", "build_location", "port")
    search_fields = ("name",)
    empty_value_display = "-empty-"


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ("name", "docker_image", "start_port", "end_port", "point")
    search_fields = ("name", "docker_image")
    empty_value_display = "-empty-"


@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "challenge",
        "container_id",
        "port",
        "no_of_attempt",
        "is_solved",
    )
    search_fields = ("user__username", "challenge__name")
    empty_value_display = "-empty-"


@admin.register(LabCategoryMapping)
class LabCategoryMappingAdmin(admin.ModelAdmin):
    list_display = ("lab", "category", "subcategory", "display_name", "sort_order")
    list_filter = ("category",)
    search_fields = ("lab__name", "display_name")

