from django.core.management.base import BaseCommand
from introduction.models import (
    login,
    FAANG,
    info,
    comments,
    otp,
    CF_user,
    CSRF_user_tbl,
)


class Command(BaseCommand):
    help = (
        "Seeds baseline datasets required by PyGoat educational labs "
        "(SQL Injection, XSS, XXE, Broken Auth / OTP, CSRF, Cryptographic Failures). "
        "Uses get_or_create to ensure idempotency."
    )

    def handle(self, *args, **options):
        self.stdout.write("Starting lab dataset seeding...")

        # 1. SQL Injection / Login Table
        users_data = [
            {"user": "admin", "password": "supersecretadminpassword123"},
            {"user": "user1", "password": "password123"},
        ]
        for user_entry in users_data:
            obj, created = login.objects.get_or_create(
                user=user_entry["user"],
                defaults={"password": user_entry["password"]},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created login user: {obj.user}"))
            else:
                self.stdout.write(f"Login user '{obj.user}' already exists.")

        # 2. Reflected XSS: FAANG Companies & Executive Info
        faang_data = [
            {
                "company": "Google",
                "ceo": "Sundar Pichai",
                "about": (
                    "Google is an American multinational technology company focusing on search "
                    "engine technology, online advertising, cloud computing, computer software, "
                    "quantum computing, e-commerce, artificial intelligence, and consumer electronics."
                ),
            },
            {
                "company": "Meta",
                "ceo": "Mark Zuckerberg",
                "about": (
                    "Meta Platforms, Inc. is an American multinational technology conglomerate "
                    "based in Menlo Park, California, and is the parent organization of Facebook, "
                    "Instagram, and WhatsApp."
                ),
            },
            {
                "company": "Apple",
                "ceo": "Tim Cook",
                "about": (
                    "Apple Inc. is an American multinational technology company specializing in "
                    "consumer electronics, software, and online services."
                ),
            },
            {
                "company": "Amazon",
                "ceo": "Andy Jassy",
                "about": (
                    "Amazon.com, Inc. is an American multinational technology company focusing on "
                    "e-commerce, cloud computing, online advertising, digital streaming, and artificial intelligence."
                ),
            },
            {
                "company": "Netflix",
                "ceo": "Ted Sarandos and Greg Peters",
                "about": (
                    "Netflix is an American subscription video on-demand over-the-top streaming service "
                    "and production company."
                ),
            },
        ]
        for item in faang_data:
            faang_obj, f_created = FAANG.objects.get_or_create(
                company=item["company"]
            )
            if f_created:
                self.stdout.write(self.style.SUCCESS(f"Created FAANG company: {faang_obj.company}"))
            else:
                self.stdout.write(f"FAANG company '{faang_obj.company}' already exists.")

            info_obj, i_created = info.objects.get_or_create(
                faang=faang_obj,
                defaults={"ceo": item["ceo"], "about": item["about"]},
            )
            if i_created:
                self.stdout.write(self.style.SUCCESS(f"Created info for company: {faang_obj.company}"))
            else:
                self.stdout.write(f"Info for company '{faang_obj.company}' already exists.")

        # 3. XXE: Default comments record
        comment_obj, c_created = comments.objects.get_or_create(
            name="System",
            defaults={"comment": "Welcome to the XXE challenge discussions"},
        )
        if c_created:
            self.stdout.write(self.style.SUCCESS(f"Created default comment by {comment_obj.name}"))
        else:
            self.stdout.write(f"Default comment by '{comment_obj.name}' already exists.")

        # 4. Broken Authentication: OTP records
        otp_records = [
            {"email": "user@pygoat.com", "otp": 100},
            {"email": "admin@pygoat.com", "otp": 123},
        ]
        for otp_entry in otp_records:
            matching_otp = otp.objects.filter(email=otp_entry["email"])
            if matching_otp.exists():
                self.stdout.write(f"OTP record for '{otp_entry['email']}' already exists.")
            else:
                otp_obj = otp.objects.create(
                    email=otp_entry["email"],
                    otp=otp_entry["otp"],
                )
                self.stdout.write(self.style.SUCCESS(f"Created OTP record for: {otp_obj.email}"))

        # 5. Cryptographic Failures: CF_user records
        cf_users = [
            {
                "username": "admin",
                "password": "c93ccd78b2076528346216b3b2f701e6",
                "password2": "d953b4a47ce307fcb8b1b85fc6a0d34aea5585b6ad9188beb94c1eea9bbb5c7a",
            },
            {
                "username": "alex",
                "password": "9d6edee6ce9312981084bd98eb3751ee",
                "password2": "2a280ba4ff0f8c763c5b0606f40effc3319dbc4c91d4361a39990292d4b7b0cd",
            },
            {
                "username": "rupak",
                "password": "5ee3547adb4481902349bdd0f2ffba93",
                "password2": "c17cde8d179a37cad4bd93e55355fdf240eb52d585e428c1cdfecc68123e192a",
            },
        ]
        for cf in cf_users:
            matching_cf = CF_user.objects.filter(username=cf["username"])
            if matching_cf.exists():
                first_record = matching_cf.first()
                first_record.password = cf["password"]
                first_record.password2 = cf["password2"]
                first_record.save()
                # Clean up duplicates if created by historic migration scripts
                matching_cf.exclude(id=first_record.id).delete()
                self.stdout.write(f"CF_user '{cf['username']}' already exists, updated/deduplicated.")
            else:
                cf_obj = CF_user.objects.create(
                    username=cf["username"],
                    password=cf["password"],
                    password2=cf["password2"],
                )
                self.stdout.write(self.style.SUCCESS(f"Created CF_user: {cf_obj.username}"))

        # 6. CSRF: CSRF_user_tbl records
        csrf_users = [
            {"username": "alice", "password": "password123", "balance": 1000, "is_loggedin": False},
            {"username": "bob", "password": "password123", "balance": 500, "is_loggedin": False},
        ]
        for cu in csrf_users:
            cu_obj, cu_created = CSRF_user_tbl.objects.get_or_create(
                username=cu["username"],
                defaults={
                    "password": cu["password"],
                    "balance": cu["balance"],
                    "is_loggedin": cu["is_loggedin"],
                },
            )
            if cu_created:
                self.stdout.write(self.style.SUCCESS(f"Created CSRF user: {cu_obj.username}"))
            else:
                self.stdout.write(f"CSRF user '{cu_obj.username}' already exists.")

        self.stdout.write(self.style.SUCCESS("All baseline lab datasets seeded successfully."))
