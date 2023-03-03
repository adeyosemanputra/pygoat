from django.urls import path,include
from .views import *

urlpatterns = [
    path('<str:challenge>', DoItFast.as_view(), name='do-it-fast'),
]