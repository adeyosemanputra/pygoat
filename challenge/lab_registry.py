"""
Lab Registry - Central configuration for all dockerized labs
"""

LAB_REGISTRY = {
    "bopla": {
        "service_name": "bopla-lab",
        "internal_port": 8080,
        "path_prefix": "/labs/bopla",
        "container_name": "bopla-lab"
    },
    "business_logic": {
        "service_name": "business-logic-lab",
        "internal_port": 5010,
        "path_prefix": "/labs/business-logic",
        "container_name": "business-logic-lab"
    },
    "security_headers": {
        "service_name": "security-headers-lab",
        "internal_port": 5011,
        "path_prefix": "/labs/security-headers",
        "container_name": "security-headers-lab"
    },
    "xss": {
        "service_name": "xss-lab",
        "internal_port": 5006,
        "path_prefix": "/labs/xss",
        "container_name": "xss-lab"
    },
    "ssrf": {
        "service_name": "ssrf-lab",
        "internal_port": 5000,
        "path_prefix": "/labs/ssrf",
        "container_name": "ssrf-lab"
    },
    "sql_injection": {
        "service_name": "sql-injection-lab",
        "internal_port": 5012,
        "path_prefix": "/labs/sql-injection",
        "container_name": "sql-injection-lab"
    },
    "command_injection": {
        "service_name": "command-injection-lab",
        "internal_port": 5013,
        "path_prefix": "/labs/command-injection",
        "container_name": "command-injection-lab"
    },
    "broken_auth": {
        "service_name": "broken-auth-lab",
        "internal_port": 5000,
        "path_prefix": "/labs/broken-auth",
        "container_name": "broken-auth-lab"
    },
    "broken_access": {
        "service_name": "broken-access-lab",
        "internal_port": 8080,
        "path_prefix": "/labs/broken-access",
        "container_name": "broken-access-lab"
    },
    "crypto_failure": {
        "service_name": "crypto-failure-lab",
        "internal_port": 5000,
        "path_prefix": "/labs/crypto-failure",
        "container_name": "crypto-failure-lab"
    },
    "insecure_design": {
        "service_name": "insecure-design-lab",
        "internal_port": 5008,
        "path_prefix": "/labs/insecure-design",
        "container_name": "insecure-design-lab"
    },
    "insec_des": {
        "service_name": "insec-des-lab",
        "internal_port": 8080,
        "path_prefix": "/labs/insec-des",
        "container_name": "insec-des-lab"
    },
    "sec_misconfig": {
        "service_name": "sec-misconfig-lab",
        "internal_port": 5009,
        "path_prefix": "/labs/sec-misconfig",
        "container_name": "sec-misconfig-lab"
    },
    "sensitive_data_exposure": {
        "service_name": "sensitive-data-exposure-lab",
        "internal_port": 8000,
        "path_prefix": "/labs/sensitive-data",
        "container_name": "sensitive-data-exposure-lab"
    },
    "auth_failure": {
        "service_name": "auth-failure-lab",
        "internal_port": 5007,
        "path_prefix": "/labs/auth-failure",
        "container_name": "auth-failure-lab"
    },
    "software_integrity": {
        "service_name": "software-integrity-lab",
        "internal_port": 5011,
        "path_prefix": "/labs/software-integrity",
        "container_name": "software-integrity-lab"
    },
    "insufficient_logging": {
        "service_name": "insufficient-logging-lab",
        "internal_port": 5014,
        "path_prefix": "/labs/insufficient-logging",
        "container_name": "insufficient-logging-lab"
    },
    "sde": {
        "service_name": "sde-lab",
        "internal_port": 5100,
        "path_prefix": "/labs/sde",
        "container_name": "sde-lab"
    },
    "template_injection": {
        "service_name": "template-injection-lab",
        "internal_port": 5015,
        "path_prefix": "/labs/template-injection",
        "container_name": "template-injection-lab"
    },
    "xxe": {
        "service_name": "xxe-lab",
        "internal_port": 5010,
        "path_prefix": "/labs/xxe",
        "container_name": "xxe-lab"
    },
    "a9_uckv": {
        "service_name": "a9-uckv-lab",
        "internal_port": 9000,
        "path_prefix": "/labs/a9-uckv",
        "container_name": "a9-uckv-lab"
    },
}

def get_lab_url(lab_name):
    """Get the public URL path for a lab"""
    lab = LAB_REGISTRY.get(lab_name)
    if lab:
        return lab['path_prefix']
    return None

def get_lab_internal_url(lab_name):
    """Get the internal Docker network URL for a lab"""
    lab = LAB_REGISTRY.get(lab_name)
    if lab:
        return f"http://{lab['service_name']}:{lab['internal_port']}"
    return None

def list_all_labs():
    """Return list of all available labs"""
    return list(LAB_REGISTRY.keys())
