from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    
    # API endpoints demonstrating insecure data exposure (for educational purposes)
    path('api/user-data/', views.api_data_view, name='api_data'),
    path('api/all-users/', views.all_users_data_view, name='all_users_data'),
    
    path('logout/', views.logout_view, name='logout'),
    path('lesson/', views.sensitive_data_exposure_lesson, name='lesson'),
    
    # TODO - additional URLs to implement:
    # path('api/v2/user-data/', views.api_data_view_v2, name='api_data_v2'), # secure version
    # path('settings/', views.user_settings, name='settings'),
    # path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]

# This lab intentionally contains insecure endpoints to demonstrate 
# sensitive data exposure vulnerabilities. In a real application,
# these endpoints would require proper authorization checks.

# Note: we should probably organize these better and use routers
# but this is fine for now
