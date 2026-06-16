from django.urls import path, include
from .views import *

urlpatterns = [
    path("<str:challenge>", DoItFast.as_view(), name="do-it-fast"),
    path("start-lab/<slug:lab_image_name>/", start_lab, name="start_lab"),
    path("stop-labs/", stop_user_labs, name="stop_labs"),
    path("list-labs/", list_user_labs, name="list_labs"),
    path("stop-lab/<slug:lab_image_name>/", stop_lab, name="stop_lab"),
    path("custom-labs/list/", list_custom_labs, name="list_custom_labs"),
    path("custom-labs/create/", create_custom_lab, name="create_custom_lab"),
    path("custom-labs/update/<int:lab_id>/", update_custom_lab, name="update_custom_lab"),
    path("custom-labs/delete/<int:lab_id>/", delete_custom_lab, name="delete_custom_lab"),
]
