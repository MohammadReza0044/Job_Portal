from django.urls import path

from job.views import *

app_name = "job"

urlpatterns = [
    path("job/create/", JobList.as_view(), name="job_create"),
    path("job/list/", JobList.as_view(), name="job_list"),
    path("job/<int:job_id>/", JobDetail.as_view(), name="job_detail"),
    path("location/create/", LocationList.as_view(), name="Location_create"),
    path("location/list/", LocationList.as_view(), name="location_list"),
    path("category/create/", CategoryList.as_view(), name="category_create"),
    path("category/list/", CategoryList.as_view(), name="category_list"),
]
