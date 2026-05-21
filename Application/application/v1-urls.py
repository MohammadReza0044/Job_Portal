from django.urls import path

from application.views import *

app_name = "application"

urlpatterns = [
    path("applications/", ApplicationList.as_view(), name="app_create"),
    path("applications/", ApplicationList.as_view(), name="app_list"),
    path("profiles/", ProfileList.as_view(), name="profile_create"),
    path("profiles/", ProfileList.as_view(), name="profile_list"),
    path("internal/cvs/", InternalCVList.as_view(), name="internal_cv_list"),
]
