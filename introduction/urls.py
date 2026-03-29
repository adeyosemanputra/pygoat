from django.urls import include, path
from . import views

urlpatterns = [
    # Core
    path("accounts/", include("allauth.urls")),
    path("", views.home, name="homepage"),
    path("register/", views.register, name="register"),

    # Traefik Bouncer
    path("auth-check/", views.check_auth, name="auth_check"),

    # Lab Theory Pages
    path("xss", views.xss, name="xss"),
    path("sql", views.sql, name="sql"),
    path("insec_des", views.insec_des, name="insec_des"),
    path("xxe", views.xxe, name="xxe"),
    path("cmd", views.cmd, name="cmd"),
    path("bau", views.bau, name="bau"),
    path("healthz", views.healthz, name="healthz"),
    path("supply-chain-failures", views.supply_chain_failures, name="supply_chain_failures"),
    path("sec_mis", views.sec_mis, name="sec_mis"),
]
