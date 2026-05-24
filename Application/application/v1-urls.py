from django.urls import path

from application.views import *

app_name = "application"

urlpatterns = [
    path("applications/", ApplicationList.as_view(), name="applications"),
    path("cvs/", CvList.as_view(), name="cvs"),
    path("internal/cvs/", InternalCVList.as_view(), name="internal_cv_list"),
]
