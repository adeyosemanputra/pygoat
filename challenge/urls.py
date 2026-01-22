from django.urls import path,include
from .views import *

urlpatterns = [
    path('<str:challenge>', DoItFast.as_view(), name='do-it-fast'),
    path('bopla_lab/', bopla_lab, name='bopla'),
    path('business_logic_lab/', business_logic_lab, name='business_logic'),
    path('security_headers_lab/', security_headers_lab, name='security_headers'),
    path('start-lab/<str:lab_image_name>/', start_lab, name='start_lab'),
]