from rest_framework import serializers

from .models import *


class InternalMatchingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobMatch
        fields = "__all__"
