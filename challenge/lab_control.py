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

def run(cmd):
    return subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/app"
    )

def start_lab(lab):
    print("LAB REQUESTED =", repr(lab))
    container_name = LAB_PROFILES.get(lab)
    if not container_name:
        return False, "Unknown lab"

    cmd = f"{BASE_CMD} --profile {lab} up -d"
    r = run(cmd)

    if r.returncode == 0:
        return True, "Lab started"
    return False, r.stderr

def stop_lab(lab):
    container_name = LAB_PROFILES.get(lab)
    if not container_name:
        return False, "Unknown lab"

    cmd = f"{BASE_CMD} --profile {lab} stop"
    r = run(cmd)

    if r.returncode == 0:
        return True, "Lab stopped"
    return False, r.stderr

def lab_status(lab):
    container_name = LAB_PROFILES.get(lab)
    if not container_name:
        return False

    cmd = f"docker inspect -f '{{{{.State.Running}}}}' {container_name} 2>/dev/null"
    r = run(cmd)

    return "true" in r.stdout.lower()