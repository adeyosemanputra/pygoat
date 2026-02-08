import os
import subprocess

LAB_PROFILES = {
    "xss": "xss-lab",
    "ssrf": "ssrf-lab",
    "bopla": "bopla-lab",
    "business-logic": "business-logic-lab",
    "security-headers": "security-headers-lab",
    "sql-injection": "sql-injection-lab",
    "command-injection": "command-injection-lab",
    "broken-auth": "broken-auth-lab",
    "broken-access": "broken-access-lab",
    "crypto-failure": "crypto-failure-lab",
    "insecure-design": "insecure-design-lab",
    "insec-des": "insec-des-lab",
    "sec-misconfig": "sec-misconfig-lab",
    "sensitive-data-exposure": "sensitive-data-exposure-lab",
    "auth-failure": "auth-failure-lab",
    "software-integrity": "software-integrity-lab",
    "insufficient-logging": "insufficient-logging-lab",
    "sde": "sde-lab",
    "template-injection": "template-injection-lab",
    "xxe": "xxe-lab",
    "a9-uckv": "a9-uckv-lab",
}

BASE_CMD = "docker compose -f docker-compose.labs.yml"
RUNNING_IN_DOCKER = os.path.exists("/.dockerenv")


def _disabled():
    return False, "Lab control is disabled in local development mode. Use docker-compose to manage labs."


def run(cmd):
    return subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.getcwd() if not RUNNING_IN_DOCKER else "/app"
    )


def start_lab(lab):
    if not RUNNING_IN_DOCKER:
        return _disabled()

    if lab not in LAB_PROFILES:
        return False, "Unknown lab"

    r = run(f"{BASE_CMD} --profile {lab} up -d")
    return (True, "Lab started") if r.returncode == 0 else (False, r.stderr)


def stop_lab(lab):
    if not RUNNING_IN_DOCKER:
        return _disabled()

    if lab not in LAB_PROFILES:
        return False, "Unknown lab"

    r = run(f"{BASE_CMD} --profile {lab} stop")
    return (True, "Lab stopped") if r.returncode == 0 else (False, r.stderr)


def lab_status(lab):
    """Check if a lab container is running - works in both Docker and local dev"""
    if lab not in LAB_PROFILES:
        return False

    r = run(f"docker inspect -f '{{{{.State.Running}}}}' {LAB_PROFILES[lab]}")
    return "true" in r.stdout.lower()