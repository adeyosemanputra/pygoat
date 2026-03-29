from django.urls import include, path
from . import views

urlpatterns = [
    # Core Authentication & Home
    path("accounts/", include("allauth.urls")),
    path("", views.home, name="homepage"),
    path("register/", views.register, name="register"),

    # Traefik ForwardAuth Bouncer (The heart of your POC)
    path("auth-check/", views.check_auth, name="auth_check"),

    # Theory/Description Pages (Aligned with v3 Architecture)
    path("xss", views.xss, name="xss"),
    path("sql", views.sql, name="sql"),
    path("insec_des", views.insec_des, name="insec_des"),
    path("xxe", views.xxe, name="xxe"),
    path("cmd", views.cmd, name="Command Injection"),
    path("bau", views.bau, name="Broken Authe"),
    path("sec_mis", views.sec_mis, name="Security Misconfiguration"),
]
]
