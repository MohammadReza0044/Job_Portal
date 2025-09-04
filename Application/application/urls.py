from django.urls import path

from application.views import *

app_name = "application"

urlpatterns = [
    path("create/", ApplicationList.as_view(), name="app_create"),
    path("list/", ApplicationList.as_view(), name="app_list"),
    path("profile/create/", ProfileList.as_view(), name="profile_create"),
    path("profile/list", ProfileList.as_view(), name="profile_list"),
    path("internal/cvs/", InternalCVList.as_view(), name="internal_cv_list"),
]
