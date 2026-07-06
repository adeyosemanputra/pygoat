from django.urls import include, path

from . import views

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("", views.home, name="homepage"),
    path("xss", views.xss, name="xss"),
    path("sql", views.sql, name="sql"),
    path("insec_des", views.insec_des, name="insec_des"),
    path("xxe", views.xxe, name="xxe"),
    path("auth", views.auth_home, name="auth_home"),
    path("ba", views.ba, name="Broken Access Control"),
    path("data_exp", views.data_exp, name="data_exp"),
    path("robots.txt", views.robots, name="robots.txt"),
    path("500error", views.error, name="500error"),
    path("cmd", views.cmd, name="Command Injection"),
    path("bau", views.bau, name="Broken Authe"),
    path("sec_mis", views.sec_mis, name="Security Misconfiguration"),
    path("a9", views.a9, name="A9"),
    path("a10", views.a10, name="A10"),
    path("insecure-design", views.insec_desgine, name="insecure-design"),
    path("broken_access_control", views.a1_broken_access, name="broken_access"),
    path("ssrf", views.ssrf, name="SSRF"),
    path("injection", views.injection, name="injection"),
    path("ssti", views.ssti, name="SSTI"),
    path("cryptographic_failure", views.crypto_failure, name="cryptographic_failure"),
    path("A03", views.supply_chain_failures, name="supply_chain_failures"),
    path("auth_failure", views.auth_failure, name="auth_failure"),
    path("2021/A8", views.software_and_data_integrity_failure, name="A8"),
]
