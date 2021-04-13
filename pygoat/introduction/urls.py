from django.urls import path

from .import views

urlpatterns = [
    path('', views.home, name='homepage'),
    path('xss', views.xss,name="xss"),
    path('xssL',views.xssL,name='xssL'),
    path('xssL1',views.xssL,name='xssL'),
]