from django.urls import path

from .views import *

app_name = "employer_admin"

urlpatterns = [
    path("admin/jobs/", JobList.as_view(), name="admin_job_create"),
    path("admin/jobs/", JobList.as_view(), name="admin_job_list"),
    path("admin/jobs/<str:job_id>/", JobDetail.as_view(), name="employer_admin_detail"),
    path("admin/locations/", LocationList.as_view(), name="Locations"),
    path("admin/categories/", CategoryList.as_view(), name="categories"),
]
