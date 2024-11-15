from django.urls import path

from account.views import *

app_name = "product"

urlpatterns = [
    path("register/", Register.as_view(), name="register"),
    # path('profile/', ProfileApi.as_view(),name="profile"),
]
