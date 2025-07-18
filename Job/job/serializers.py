from rest_framework import serializers

from .models import *


class JobSerializer(serializers.ModelSerializer):
    employer_id = serializers.UUIDField()

    class Meta:
        model = Job
        fields = "__all__"


class JobUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255, required=False)
    location = serializers.CharField(max_length=255, required=False)
    job_type = serializers.ChoiceField(choices=Job.JOB_TYPE, required=False)
    salary = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(max_length=None, required=False)
    is_active = serializers.BooleanField(required=False)

    class Meta:
        model = Job
        fields = ("title", "location", "job_type", "salary", "description", "is_active")


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"


class InternalJobListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = ("id", "description", "status")
