from django.urls import path

from application.views import *

app_name = "application"

urlpatterns = [
    path("create/", ApplicationList.as_view(), name="job_create"),
    path("list/", ApplicationList.as_view(), name="job_list"),
    path("profile/create/", ProfileList.as_view(), name="profile_create"),
    path("profile/list", ProfileList.as_view(), name="profile_list"),
]
