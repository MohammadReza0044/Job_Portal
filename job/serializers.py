from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = "__all__"
