from django.core.management.base import BaseCommand
from scoring.models import DifficultyLevel, AchievementMilestone, ScoringSettings


class Command(BaseCommand):
    help = 'Seed default difficulty levels, milestones, and scoring settings'

    def handle(self, *args, **options):
        # Scoring settings
        ScoringSettings.load()
        self.stdout.write(self.style.SUCCESS('Scoring settings initialized'))

        # Difficulty levels
        defaults = [
            ('Easy', 0.8, 1),
            ('Medium', 1.0, 2),
            ('Hard', 1.5, 3),
            ('Expert', 2.5, 4),
        ]
        for name, mult, order in defaults:
            obj, created = DifficultyLevel.objects.get_or_create(
                name=name,
                defaults={'multiplier': mult, 'order': order}
            )
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {obj}')

        # Milestones with FontAwesome icon classes
        milestones = [
            ('First Blood', 'Complete your first lab or challenge', 'fas fa-tint', 1, ''),
            ('Getting Started', 'Complete 5 labs or challenges', 'fas fa-rocket', 5, ''),
            ('Dedicated Learner', 'Complete 10 labs or challenges', 'fas fa-book-open', 10, ''),
            ('Security Apprentice', 'Complete 25 labs or challenges', 'fas fa-shield-alt', 25, ''),
            ('Pentester', 'Complete all 50 labs and challenges', 'fas fa-trophy', 50, ''),
            ('Lab Rat', 'Complete 10 labs', 'fas fa-flask', 10, 'lab'),
            ('Challenge Hunter', 'Complete 5 challenges', 'fas fa-crosshairs', 5, 'challenge'),
        ]
        for name, desc, icon, count, ct_filter in milestones:
            obj, created = AchievementMilestone.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'icon': icon,
                    'required_completions': count,
                    'content_type_filter': ct_filter,
                }
            )
            if not created and obj.icon != icon:
                obj.icon = icon
                obj.description = desc
                obj.required_completions = count
                obj.content_type_filter = ct_filter
                obj.save()
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status}: {obj}')

        self.stdout.write(self.style.SUCCESS('Scoring data seeded successfully'))
