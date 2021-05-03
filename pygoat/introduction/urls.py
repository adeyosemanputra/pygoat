from django.urls import path

from .import views

urlpatterns = [
    path('', views.home, name='homepage'),
    path('xss', views.xss,name="xss"),
    path('xssL',views.xss_lab,name='xss_lab'),
    path('xssL1',views.xss_lab,name='xss_lab'),
    path("sql",views.sql,name='sql'),
    path("sql_lab",views.sql_lab,name="sql_lab"),
    path("sql_lab1",views.sql_lab,name="sql_lab"),
    path("insec_des",views.insec_des,name="insec_des"),
    path("insec_des_lab",views.insec_des_lab,name="insec_des_lab"),
    path("xxe",views.xxe,name="xxe"),
    path("xxe_lab",views.xxe_lab,name="xxe_lab"),
    path("xxe_see",views.xxe_see,name="xxe_see"),
    path("xxe_parse",views.xxe_parse,name="xxe_parse"),
    path("ba",views.ba,name="Broken Access Control"),
    path("ba_lab",views.ba_lab,name="Broken Access Control Lab"),
    path("data_exp",views.data_exp,name="data_exp"),
    path("data_exp_lab",views.data_exp_lab,name="data_exp_lab"),
    path("robots.txt",views.robots,name="robots.txt"),
    path("500error",views.error,name="500error"),
    path("cmd",views.cmd,name="Command Injection"),
    path("cmd_lab",views.cmd_lab,name="Command Injection Lab"),
    path("bau", views.bau, name="Broken Authe"),
    path("bau_lab", views.bau_lab, name="LAB"),
    path("login_otp", views.login_otp, name="OTP Login"),
    path("otp", views.Otp, name="OTP Verification"),
    path("sec_mis", views.sec_mis, name="Security Misconfiguration"),
    path("sec_mis_lab", views.sec_mis_lab, name="Security Misconfiguration Lab"),
    path("secret", views.secret, name="Secret key for A6"),
    path("a9",views.a9,name="A9"),
    path("a9_lab",views.a9_lab,name="A9 LAb"),
    path("get_version",views.get_version,name="Get Version")




]