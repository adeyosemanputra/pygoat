from django.urls import path, include
from .views import *

urlpatterns = [
    path("<str:challenge>", DoItFast.as_view(), name="do-it-fast"),
    path("start-lab/<slug:lab_image_name>/", start_lab, name="start_lab"),
    path("stop-labs/", stop_user_labs, name="stop_labs"),
    path("list-labs/", list_user_labs, name="list_labs"),
    path("stop-lab/<slug:lab_image_name>/", stop_lab, name="stop_lab"),
]
