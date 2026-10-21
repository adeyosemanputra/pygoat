from django.apps import AppConfig


class ScoringConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scoring"
    verbose_name = "Scoring & Achievements"

    def ready(self):
        import scoring.signals  # noqa: F401
