from django.urls import path

from jobb.views import *

app_name = "job"

urlpatterns = [
    path("create/", JobList.as_view(), name="job_create"),
    path("list/", JobList.as_view(), name="job_list"),
    path("<int:job_id>/", JobDetail.as_view(), name="job_detail"),
]
