from django.urls import path

from matching.views import *

app_name = "matching"

urlpatterns = [
    path("internal/trigger-matching/", InternalMatchTrigger.as_view()),
]
