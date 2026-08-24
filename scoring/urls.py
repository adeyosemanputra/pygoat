from django.urls import path
from . import views

app_name = 'scoring'

urlpatterns = [
    path('start/<str:content_type>/<int:content_id>/',
         views.start_tracking, name='start_tracking'),
    path('complete/<str:content_type>/<int:content_id>/',
         views.complete_tracking, name='complete_tracking'),
    path('scores/', views.user_scores, name='user_scores'),
    path('achievements/', views.user_achievements, name='user_achievements'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
