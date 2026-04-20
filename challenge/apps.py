from django.apps import AppConfig
 
 
class ChallengeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "challenge"
 
    def ready(self):
        # Import signals module so all @receiver decorators are registered.
        import challenge.signals  # noqa: F401
 