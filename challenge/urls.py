from django.urls import path,include
from .views import *
from dockerized_labs.sensitive_data_exposure.dataexposure.views import profile_view

urlpatterns = [
    path('profile-test/', profile_view, name='profile_test'),
    path('<str:challenge>', DoItFast.as_view(), name='do-it-fast'),
]