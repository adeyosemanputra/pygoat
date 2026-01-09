from django.urls import path
from . import views

urlpatterns = [
    path('', views.xxe_home, name='xxe_home'),
    path('lab/', views.xxe_lab, name='xxe_lab'),
    path('see/', views.xxe_see, name='xxe_see'),
    path('parse/', views.xxe_parse, name='xxe_parse'),
] 