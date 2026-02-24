from django.urls import path
from . import views

urlpatterns = [
    path("api/solve/", views.submit_solve, name="api_solve"),
    path("v1/<str:challenge>/", views.DoItFast.as_view(), name="do_it_fast"),
    
    # These names must match what is in your HTML templates (likely 'bopla', etc.)
    path("bopla/", views.bopla_lab, name="bopla"),
    path("business-logic/", views.business_logic_lab, name="business_logic"),
    path("security-headers/", views.security_headers_lab, name="security_headers"),
]
