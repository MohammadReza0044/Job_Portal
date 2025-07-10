from django.urls import path

from matching.views import *

app_name = "matching"

urlpatterns = [
    path(
        "internal/trigger-matching-new-job-to-cvs/",
        InternalMatchNewJobToAllCvsTrigger.as_view(),
    ),
    path(
        "internal/trigger-matching-new-cv-to-jobs/",
        InternalMatchNewCvToAllJobsTrigger.as_view(),
    ),
]
