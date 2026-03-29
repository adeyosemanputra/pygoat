from django.urls import path
from . import views

urlpatterns = [
    
    path('auth-check/', views.check_auth, name='auth_check'),
    
    
    path('start-lab/<slug:lab_image_name>/', views.start_lab, name='start_lab'),
    path('stop-labs/', views.stop_user_labs, name='stop_labs'),
    path('list-labs/', views.list_user_labs, name='list_labs'),
    path('stop-lab/<slug:lab_image_name>/', views.stop_lab, name='stop_lab'),
    
    path('<str:challenge>/', views.DoItFast.as_view(), name='do-it-fast'),
]