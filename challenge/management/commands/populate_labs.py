from django.core.management.base import BaseCommand
from challenge.models import Lab, LabCategoryMapping


class Command(BaseCommand):
    help = (
        "Populates default labs in the database. Uses get_or_create "
        "to prevent duplicates and updates attributes if they change."
    )

    def handle(self, *args, **options):
        default_labs = [
            {"name": "bopla_lab", "build_location": "challenge/labs/bopla_lab", "port": 8080},
            {"name": "business_logic_lab", "build_location": "challenge/labs/business_logic_lab", "port": 5010},
            {"name": "security_headers_lab", "build_location": "challenge/labs/security_headers_lab", "port": 5011},
            {"name": "a9_uckv_lab", "build_location": "dockerized_labs/a9_uckv_lab", "port": 9000},
            {"name": "auth_failure_lab", "build_location": "dockerized_labs/auth_failure_lab", "port": 5007},
            {"name": "broken_access_lab", "build_location": "dockerized_labs/broken_access_lab", "port": 8080},
            {"name": "broken_auth_lab", "build_location": "dockerized_labs/broken_auth_lab", "port": 5000},
            {"name": "command_injection_lab", "build_location": "dockerized_labs/command_injection_lab", "port": 5013},
            {"name": "crypto_failure_lab", "build_location": "dockerized_labs/crypto_failure_lab", "port": 5000},
            {"name": "insec_des_lab", "build_location": "dockerized_labs/insec_des_lab", "port": 8080},
            {"name": "insecure_design_lab", "build_location": "dockerized_labs/insecure_design_lab", "port": 5008},
            {"name": "insufficient_logging_lab", "build_location": "dockerized_labs/insufficient_logging_lab", "port": 5014},
            {"name": "sde", "build_location": "dockerized_labs/sde", "port": 5100},
            {"name": "sec_misconfig", "build_location": "dockerized_labs/sec_misconfig", "port": 5009},
            {"name": "sensitive_data_exposure", "build_location": "dockerized_labs/sensitive_data_exposure", "port": 8000},
            {"name": "software_integrity_lab", "build_location": "dockerized_labs/software_integrity_lab", "port": 5011},
            {"name": "sql_injection_lab", "build_location": "dockerized_labs/sql_injection_lab", "port": 5012},
            {"name": "ssrf_lab", "build_location": "dockerized_labs/ssrf_lab", "port": 5000},
            {"name": "template_injection_lab", "build_location": "dockerized_labs/template_injection_lab", "port": 5015},
            {"name": "xss_lab", "build_location": "dockerized_labs/xss_lab", "port": 5006},
            {"name": "xxe_lab", "build_location": "dockerized_labs/xxe_lab", "port": 5010},
            {"name": "dependency_attack_lab", "build_location": "dockerized_labs/dependency_attack_lab", "port": 5020},
            {"name": "package_injection_lab", "build_location": "dockerized_labs/package_injection_lab", "port": 5021},
            {"name": "open_source_library_attack_lab", "build_location": "dockerized_labs/open_source_library_attack_lab", "port": 5022}
        ]

        for lab_data in default_labs:
            lab, created = Lab.objects.get_or_create(
                name=lab_data["name"],
                defaults={
                    "build_location": lab_data["build_location"],
                    "port": lab_data["port"],
                    "is_custom": False
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Lab '{lab.name}' created.")
                )
            else:
                updated = False
                if lab.build_location != lab_data["build_location"]:
                    lab.build_location = lab_data["build_location"]
                    updated = True
                if lab.port != lab_data["port"]:
                    lab.port = lab_data["port"]
                    updated = True
                if lab.is_custom:
                    lab.is_custom = False
                    updated = True

                if updated:
                    lab.save()
                    self.stdout.write(
                        self.style.SUCCESS(f"Lab '{lab.name}' updated.")
                    )
                else:
                    self.stdout.write(f"Lab '{lab.name}' already exists and is up to date.")

        self.stdout.write(
            self.style.SUCCESS("Lab data has been populated successfully.")
        )

        # --- Seed sidebar category mappings ---
        self._populate_category_mappings()

    def _populate_category_mappings(self):
        """Seed LabCategoryMapping entries for sidebar navigation."""

        # Each entry: (lab_name, category, subcategory, display_name, sort_order, overview_url_name)
        category_mappings = [
            # === OWASP TOP 10 2025 ===
            ("dependency_attack_lab", "owasp_2025", "A03:2025 - Software Supply Chain Failures",
             "Dependency Attack Lab", 1, "supply_chain_failures"),
            ("package_injection_lab", "owasp_2025", "A03:2025 - Software Supply Chain Failures",
             "Package Injection Lab", 2, ""),
            ("open_source_library_attack_lab", "owasp_2025", "A03:2025 - Software Supply Chain Failures",
             "Open Source Library Attack Lab", 3, ""),

            # === OWASP TOP 10 2021 ===
            ("broken_access_lab", "owasp_2021", "", "A1: Broken Access Control", 1, ""),
            ("crypto_failure_lab", "owasp_2021", "", "A2: Cryptographic Failures", 2, ""),
            ("sql_injection_lab", "owasp_2021", "A3: Injection", "SQL Injection", 3, ""),
            ("command_injection_lab", "owasp_2021", "A3: Injection", "Command Injection", 4, ""),
            ("template_injection_lab", "owasp_2021", "A3: Injection", "Template Injection", 5, ""),
            ("insecure_design_lab", "owasp_2021", "", "A4: Insecure Design", 6, ""),
            ("sec_misconfig", "owasp_2021", "", "A5: Security Misconfiguration", 7, ""),
            ("a9_uckv_lab", "owasp_2021", "", "A6: Vulnerable and Outdated Components", 8, ""),
            ("auth_failure_lab", "owasp_2021", "", "A7: Identification and Authentication Failures", 9, ""),
            ("software_integrity_lab", "owasp_2021", "", "A8: Software and Data Integrity Failures", 10, ""),
            ("insufficient_logging_lab", "owasp_2021", "", "A9: Security Logging and Monitoring Failures", 11, ""),
            ("ssrf_lab", "owasp_2021", "", "A10: Server-Side Request Forgery", 12, ""),

            # === OWASP TOP 10 2017 ===
            ("sql_injection_lab", "owasp_2017", "A1: Injection", "SQL Injection", 1, ""),
            ("command_injection_lab", "owasp_2017", "A1: Injection", "Command Injection", 2, ""),
            ("broken_auth_lab", "owasp_2017", "", "A2: Broken Authentication", 3, ""),
            ("sensitive_data_exposure", "owasp_2017", "", "A3: Sensitive Data Exposure", 4, ""),
            ("xxe_lab", "owasp_2017", "", "A4: XML External Entities (XXE)", 5, ""),
            ("broken_access_lab", "owasp_2017", "", "A5: Broken Access Control", 6, ""),
            ("sec_misconfig", "owasp_2017", "", "A6: Security Misconfiguration", 7, ""),
            ("xss_lab", "owasp_2017", "", "A7: Cross Site Scripting", 8, ""),
            ("insec_des_lab", "owasp_2017", "", "A8: Insecure Deserialization", 9, ""),
            ("a9_uckv_lab", "owasp_2017", "", "A9: Using Components with Known Vulnerabilities", 10, ""),
            ("insufficient_logging_lab", "owasp_2017", "", "A10: Insufficient Logging & Monitoring", 11, ""),

            # === Challenges ===
            ("bopla_lab", "challenges", "", "Challenge 1", 1, ""),
            ("business_logic_lab", "challenges", "", "Challenge 2", 2, ""),
            ("security_headers_lab", "challenges", "", "Challenge 3", 3, ""),
        ]

        created_count = 0
        updated_count = 0

        for lab_name, category, subcategory, display_name, sort_order, overview_url_name in category_mappings:
            try:
                lab = Lab.objects.get(name=lab_name)
            except Lab.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"Lab '{lab_name}' not found, skipping category mapping."
                    )
                )
                continue

            mapping, created = LabCategoryMapping.objects.get_or_create(
                lab=lab,
                category=category,
                subcategory=subcategory,
                defaults={
                    "display_name": display_name,
                    "sort_order": sort_order,
                    "overview_url_name": overview_url_name,
                }
            )

            if created:
                created_count += 1
            else:
                changed = False
                if mapping.display_name != display_name:
                    mapping.display_name = display_name
                    changed = True
                if mapping.sort_order != sort_order:
                    mapping.sort_order = sort_order
                    changed = True
                if mapping.overview_url_name != overview_url_name:
                    mapping.overview_url_name = overview_url_name
                    changed = True
                if changed:
                    mapping.save()
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Category mappings: {created_count} created, {updated_count} updated."
            )
        )
