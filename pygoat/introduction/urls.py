from django.urls import path

from .import views

urlpatterns = [
    path('', views.home, name='homepage'),
    path('xss', views.xss,name="xss"),
    path('xssL',views.xss_lab,name='xss_lab'),
    path('xssL1',views.xss_lab,name='xss_lab'),
]