from django.urls import path

from .views import *

app_name = "employer_admin"

urlpatterns = [
    path("jobs/", JobList.as_view(), name="admin_job_create"),
    path("jobs/", JobList.as_view(), name="admin_job_list"),
    path("jobs/<str:job_id>/", JobDetail.as_view(), name="employer_admin_detail"),
    path("locations/", LocationList.as_view(), name="Locations"),
    path("categories/", CategoryList.as_view(), name="categories"),
]
