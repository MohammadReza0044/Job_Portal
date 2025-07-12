from django.urls import path

from matching.views import *

app_name = "matching"

urlpatterns = [
    path(
        "internal/trigger-matching-new-job-to-cvs/",
        InternalMatchNewJobToAllCvsTrigger.as_view(),
        name="trigger_matching_new_job_to_cvs",
    ),
    path(
        "internal/trigger-matching-new-cv-to-jobs/",
        InternalMatchNewCvToAllJobsTrigger.as_view(),
        name="trigger_matching_new_cv_to_jobs",
    ),
    path("internal/match/list/", InternalMatchList.as_view(), name="match_list"),
]
