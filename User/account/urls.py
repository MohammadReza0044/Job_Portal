from account.views import *
from django.urls import path

app_name = "account"

urlpatterns = [
    path("register/", Register.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="token_obtain_pair"),
    path("profile/", Profile.as_view(), name="profile"),
]
