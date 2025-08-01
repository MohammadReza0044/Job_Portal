from rest_framework import serializers

from .models import *


class ApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Application
        fields = "__all__"


class JobSeekerProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobSeekerProfile
        fields = "__all__"


class InternalCVListSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobSeekerProfile
        fields = ("user_id", "extracted_text")
