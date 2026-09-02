from rest_framework import serializers

from .models import *


class ApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Application
        fields = "__all__"


class UserCVSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserCV
        fields = ("user_id", "full_name", "cv_file")
        read_only_fields = ("user_id", "full_name")


class InternalCVListSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserCV
        fields = ("user_id", "extracted_text")
