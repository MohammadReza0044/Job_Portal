from django.urls import path

from job.views import *

app_name = "job"

urlpatterns = [
    path("jobs/", JobList.as_view(), name="job_list"),
    path("jobs/<str:job_id>/", JobDetail.as_view(), name="job_detail"),
    path("internal/jobs/", InternalJobList.as_view(), name="internal_job_list"),
    path(
        "internal/jobs/<str:job_id>/",
        InternalJobDetail.as_view(),
        name="internal_job_detail",
    ),
]
