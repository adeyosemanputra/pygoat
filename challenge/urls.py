from django.urls import path,include
from .views import *

urlpatterns = [
    path('auth-check/', check_auth, name='auth_check'),
    path('<str:challenge>', DoItFast.as_view(), name='do-it-fast'),
]