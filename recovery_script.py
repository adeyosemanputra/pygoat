#!/usr/bin/env python3
"""
COMPLETE RECOVERY SCRIPT
Recreates ALL files for hardcoded ports fix
"""
import os
from pathlib import Path

def create_file(path, content):
    """Create file with content, making directories if needed"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
    print(f"✅ Created: {path}")

# ============================================================================
# 1. NGINX CONFIGURATION
# ============================================================================
nginx_conf = """events {
    worker_connections 1024;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    resolver 127.0.0.11 valid=10s;
    resolver_timeout 5s;
    
    map $lab $lab_port {
        default 5000;
        xss 5006;
        ssrf 5000;
        xxe 5010;
        template-injection 5015;
        sql-injection 5012;
        software-integrity 5011;
        insecure-design 5008;
        insufficient-logging 5014;
        sde 5100;
        broken-auth 5000;
        broken-access 8080;
        insec-des 8080;
        a9-uckv 9000;
        command-injection 5013;
        crypto-failure 5000;
        sec-misconfig 5009;
        sensitive-data 8000;
        auth-failure 5007;
        bopla 8080;
        business-logic 5010;
        security-headers 5011;
    }
    
    server {
        listen 8000;
        server_name localhost;
        
        client_max_body_size 100M;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        location ~ ^/labs/(?<lab>[^/]+)/static/ {
            set $upstream "${lab}-lab:$lab_port";
            proxy_pass http://$upstream$request_uri;
        }

        location ~ ^/labs/(?<lab>[^/]+)(/.*)?$ {
            set $upstream "${lab}-lab:$lab_port";
            rewrite ^/labs/[^/]+(/.*)$ $1 break;
            rewrite ^/labs/[^/]+$ / break;
            proxy_pass http://$upstream;
        }
        
        location / {
            proxy_pass http://pygoat-web:8000;
        }
    }
}
"""

# ============================================================================
# 2. DOCKER COMPOSE - MAIN
# ============================================================================
docker_compose_main = """version: "3.9"

services:
  nginx:
    image: nginx:alpine
    container_name: nginx-proxy
    ports:
      - "8000:8000"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - my_network
    depends_on:
      - web
    restart: unless-stopped

  migration:
    build: .
    command: >
      sh -c "python manage.py migrate --noinput &&
             python manage.py populate_challenges"
    volumes:
      - .:/app
    networks:
      - my_network

  web:
    build: .
    command: gunicorn --bind 0.0.0.0:8000 --workers 6 pygoat.wsgi
    container_name: pygoat-web
    volumes:
      - .:/app
    depends_on:
      migration:
        condition: service_completed_successfully
    networks:
      - my_network
    restart: unless-stopped

networks:
  my_network:
    driver: bridge
"""

# ============================================================================
# 3. DOCKER COMPOSE - LABS
# ============================================================================
docker_compose_labs = """version: "3.9"

services:
  # Challenge Labs
  bopla-lab:
    build:
      context: challenge/labs/bopla_lab/
    container_name: bopla-lab
    networks:
      - my_network
    profiles:
      - labs
      - bopla

  business-logic-lab:
    build:
      context: challenge/labs/business_logic_lab/
    container_name: business-logic-lab
    networks:
      - my_network
    profiles:
      - labs
      - business-logic

  security-headers-lab:
    build:
      context: challenge/labs/security_headers_lab/
    container_name: security-headers-lab
    networks:
      - my_network
    profiles:
      - labs
      - security-headers

  # Dockerized Labs
  xss-lab:
    build:
      context: dockerized_labs/xss_lab/
    container_name: xss-lab
    networks:
      - my_network
    profiles:
      - labs
      - xss

  ssrf-lab:
    build:
      context: dockerized_labs/ssrf_lab/
    container_name: ssrf-lab
    networks:
      - my_network
    profiles:
      - labs
      - ssrf

  sql-injection-lab:
    build:
      context: dockerized_labs/sql_injection_lab/
    container_name: sql-injection-lab
    networks:
      - my_network
    profiles:
      - labs
      - sql-injection

  command-injection-lab:
    build:
      context: dockerized_labs/command_injection_lab/
    container_name: command-injection-lab
    networks:
      - my_network
    profiles:
      - labs
      - command-injection

  broken-auth-lab:
    build:
      context: dockerized_labs/broken_auth_lab/
    container_name: broken-auth-lab
    networks:
      - my_network
    profiles:
      - labs
      - broken-auth

  broken-access-lab:
    build:
      context: dockerized_labs/broken_access_lab/
    container_name: broken-access-lab
    networks:
      - my_network
    profiles:
      - labs
      - broken-access

  crypto-failure-lab:
    build:
      context: dockerized_labs/crypto_failure_lab/
    container_name: crypto-failure-lab
    networks:
      - my_network
    profiles:
      - labs
      - crypto-failure

  insecure-design-lab:
    build:
      context: dockerized_labs/insecure_design_lab/
    container_name: insecure-design-lab
    networks:
      - my_network
    profiles:
      - labs
      - insecure-design

  insec-des-lab:
    build:
      context: dockerized_labs/insec_des_lab/
    container_name: insec-des-lab
    networks:
      - my_network
    profiles:
      - labs
      - insec-des

  sec-misconfig-lab:
    build:
      context: dockerized_labs/sec_misconfig_lab/
    container_name: sec-misconfig-lab
    networks:
      - my_network
    profiles:
      - labs
      - sec-misconfig

  sensitive-data-exposure-lab:
    build:
      context: dockerized_labs/sensitive_data_exposure_lab/
    container_name: sensitive-data-exposure-lab
    networks:
      - my_network
    profiles:
      - labs
      - sensitive-data

  auth-failure-lab:
    build:
      context: dockerized_labs/auth_failure_lab/
    container_name: auth-failure-lab
    networks:
      - my_network
    profiles:
      - labs
      - auth-failure

  software-integrity-lab:
    build:
      context: dockerized_labs/software_integrity_lab/
    container_name: software-integrity-lab
    networks:
      - my_network
    profiles:
      - labs
      - software-integrity

  insufficient-logging-lab:
    build:
      context: dockerized_labs/insufficient_logging_lab/
    container_name: insufficient-logging-lab
    networks:
      - my_network
    profiles:
      - labs
      - insufficient-logging

  sde-lab:
    build:
      context: dockerized_labs/sde_lab/
    container_name: sde-lab
    networks:
      - my_network
    profiles:
      - labs
      - sde

  template-injection-lab:
    build:
      context: dockerized_labs/template_injection_lab/
    container_name: template-injection-lab
    networks:
      - my_network
    profiles:
      - labs
      - template-injection

  xxe-lab:
    build:
      context: dockerized_labs/xxe_lab/
    container_name: xxe-lab
    networks:
      - my_network
    profiles:
      - labs
      - xxe

  a9-uckv-lab:
    build:
      context: dockerized_labs/a9_uckv_lab/
    container_name: a9-uckv-lab
    networks:
      - my_network
    profiles:
      - labs
      - a9-uckv

networks:
  my_network:
    driver: bridge
"""

# ============================================================================
# 4. LAB REGISTRY
# ============================================================================
lab_registry = '''"""
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
'''

# ============================================================================
# 5. CHALLENGE VIEWS UPDATE
# ============================================================================
views_update = '''from django.shortcuts import redirect
from django.http import HttpResponse
from .lab_registry import get_lab_url

def bopla_lab(request):
    """Redirect to Bopla lab via Nginx"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    lab_url = get_lab_url('bopla')
    if lab_url:
        return redirect(lab_url)
    else:
        return HttpResponse(
            "Lab not available. Please ensure the lab is running with: "
            "docker-compose --profile bopla up", 
            status=503
        )

def business_logic_lab(request):
    """Redirect to Business Logic lab via Nginx"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    lab_url = get_lab_url('business_logic')
    if lab_url:
        return redirect(lab_url)
    else:
        return HttpResponse(
            "Lab not available. Please ensure the lab is running with: "
            "docker-compose --profile business-logic up", 
            status=503
        )

def security_headers_lab(request):
    """Redirect to Security Headers lab via Nginx"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    lab_url = get_lab_url('security_headers')
    if lab_url:
        return redirect(lab_url)
    else:
        return HttpResponse(
            "Lab not available. Please ensure the lab is running with: "
            "docker-compose --profile security-headers up", 
            status=503
        )
'''

# ============================================================================
# MAIN EXECUTION
# ============================================================================
print("🚀 RECOVERING ALL FILES...")
print("=" * 60)

create_file("nginx/nginx.conf", nginx_conf)
create_file("docker-compose.yml", docker_compose_main)
create_file("docker-compose.labs.yml", docker_compose_labs)
create_file("challenge/lab_registry.py", lab_registry)

print("\n" + "=" * 60)
print("📝 NOTE: challenge/views.py needs manual update")
print("Replace the three lab functions with the code above")
print("=" * 60)

print("\n✅ RECOVERY COMPLETE!")
print("\nNext steps:")
print("1. Review the files created")
print("2. Update challenge/views.py with the new lab functions")
print("3. Update Flask apps with static_url_path (see pattern below)")
print("4. Commit: git add . && git commit -m 'Fix: Remove hardcoded ports'")
print("5. Test: docker-compose -f docker-compose.yml -f docker-compose.labs.yml --profile labs up")

print("\n" + "=" * 60)
print("Flask app pattern (apply to each lab):")
print("=" * 60)
print("app = Flask(__name__, static_url_path='/labs/<lab-name>/static')")