from django.urls import path

from account.views import *

app_name = "account"

urlpatterns = [
    path("register/", Register.as_view(), name="register"),
    path("profile/", Profile.as_view(), name="profile"),
]
