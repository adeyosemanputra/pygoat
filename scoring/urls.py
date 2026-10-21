from django.urls import path
from . import views

app_name = 'scoring'

urlpatterns = [
    path('scores/', views.user_scores, name='user_scores'),
    path('achievements/', views.user_achievements, name='user_achievements'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
