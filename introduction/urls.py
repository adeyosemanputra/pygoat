from django.urls import include, path

from introduction.playground.A9.api import log_function_target

from . import apis, mitre, views

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
    path(
        "broken_access_lab_1", views.a1_broken_access_lab_1, name="broken_access_lab_1"
    ),
    path(
        "broken_access_lab_2", views.a1_broken_access_lab_2, name="broken_access_lab_2"
    ),
    path(
        "broken_access_lab_3", views.a1_broken_access_lab_3, name="broken_access_lab_3"
    ),
    path(
        "broken_access_controle/secret",
        views.a1_broken_access_lab3_secret,
        name="broken_access_controle_secret",
    ),
    path("ssrf", views.ssrf, name="SSRF"),
    path("injection", views.injection, name="injection"),
    path("injection_sql_lab", views.injection_sql_lab, name="injection"),
    path("api/ssrf", apis.ssrf_code_checker, name="api/ssrf"),
    path("ssti", views.ssti, name="SSTI"),
    path("ssti/lab", views.ssti_lab, name="SSTI Lab"),
    path("ssti/blog/<str:blog_id>", views.ssti_view_blog, name="SSTI Blog"),
    path("cryptographic_failure", views.crypto_failure, name="cryptographic_failure"),
    path(
        "cryptographic_failure/lab",
        views.crypto_failure_lab,
        name="cryptographic_failure_lab",
    ),
    path("A03", views.supply_chain_failures, name="supply_chain_failures"),
    path(
        "dependency_attack_lab",
        views.dependency_attack_lab_page,
        name="dependency_attack_lab",
    ),
    path(
        "package_injection_lab",
        views.package_injection_lab_page,
        name="package_injection_lab",
    ),
    path(
        "open_source_library_attack_lab",
        views.open_source_library_lab_page,
        name="open_source_library_attack_lab",
    ),
    path(
        "cryptographic_failure/lab2",
        views.crypto_failure_lab2,
        name="cryptographic_failure_lab2",
    ),
    path(
        "cryptographic_failure/lab3",
        views.crypto_failure_lab3,
        name="cryptographic_failure_lab3",
    ),
    path("auth_failure", views.auth_failure, name="auth_failure"),
    path(
        "auth_failure/lab2/admin12983gfugef81e8yeryepanel",
        views.auth_failure_lab2,
        name="auth_failure_lab2",
    ),
    path("auth_failure/lab3", views.auth_failure_lab3, name="auth_failure_lab2"),
    path("2021/A8", views.software_and_data_integrity_failure, name="A8"),
    path("2021/A8/lab2", views.software_and_data_integrity_failure_lab2, name="A8"),
    path("2021/A8/lab3", views.software_and_data_integrity_failure_lab3, name="A8"),
    path("2021/discussion/A9/api", apis.log_function_checker, name="A10 discussion"),
    path("2021/discussion/A9/target", log_function_target, name="A9 discussion"),
    path("2021/discussion/A7", views.A7_discussion, name="A7 discussion"),
    path("2021/discussion/A7/api", apis.A7_disscussion_api, name="A7 discussion api"),
    path("2021/discussion/A6", views.A6_discussion, name="A6 discussion"),
    path("2021/discussion/A6/api", apis.A6_disscussion_api, name="A6 discussion api"),
    path(
        "2021/discussion/A6/api2", apis.A6_disscussion_api_2, name="A6 discussion api2"
    ),
    ##------------------- mitre endpoints --------------------------------------------------------------|
    path("mitre/1", mitre.mitre_top1, name="mitre_top1"),
    path("mitre/2", mitre.mitre_top2, name="mitre_top2"),
    path("mitre/3", mitre.mitre_top3, name="mitre_top3"),
    path("mitre/4", mitre.mitre_top4, name="mitre_top4"),
    path("mitre/5", mitre.mitre_top5, name="mitre_top5"),
    path("mitre/6", mitre.mitre_top6, name="mitre_top6"),
    path("mitre/7", mitre.mitre_top7, name="mitre_top7"),
    path("mitre/8", mitre.mitre_top8, name="mitre_top8"),
    path("mitre/9", mitre.mitre_top9, name="mitre_top9"),
    path("mitre/10", mitre.mitre_top10, name="mitre_top10"),
    path("mitre/11", mitre.mitre_top11, name="mitre_top11"),
    path("mitre/12", mitre.mitre_top12, name="mitre_top12"),
    path("mitre/13", mitre.mitre_top13, name="mitre_top13"),
    path("mitre/14", mitre.mitre_top14, name="mitre_top14"),
    path("mitre/15", mitre.mitre_top15, name="mitre_top15"),
    path("mitre/16", mitre.mitre_top16, name="mitre_top16"),
    path("mitre/17", mitre.mitre_top17, name="mitre_top17"),
    path("mitre/18", mitre.mitre_top18, name="mitre_top18"),
    path("mitre/19", mitre.mitre_top19, name="mitre_top19"),
    path("mitre/20", mitre.mitre_top20, name="mitre_top20"),
    path("mitre/21", mitre.mitre_top21, name="mitre_top21"),
    path("mitre/22", mitre.mitre_top22, name="mitre_top22"),
    path("mitre/23", mitre.mitre_top23, name="mitre_top23"),
    path("mitre/24", mitre.mitre_top24, name="mitre_top24"),
    path("mitre/25", mitre.mitre_top25, name="mitre_top25"),
    path("mitre/9/lab/login", mitre.csrf_lab_login, name="csrf_lab_login"),
    path(
        "mitre/9/lab/transaction", mitre.csrf_transfer_monei, name="csrf_lab_login_api"
    ),
    path(
        "mitre/9/lab/api/<str:recipent>/<int:amount>",
        mitre.csrf_transfer_monei_api,
        name="csrf_lab_login_api",
    ),
    path("mitre/25/lab/api", mitre.mitre_lab_25_api, name="mitre_lab_25_api"),
    path("mitre/25/lab", mitre.mitre_lab_25, name="mitre_lab_25"),
    path("mitre/17/lab", mitre.mitre_lab_17, name="mitre_lab_17"),
    path("mitre/17/lab/api", mitre.mitre_lab_17_api, name="mitre_lab_17_api"),
]
