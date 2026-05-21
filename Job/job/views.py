from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView


from utils.internal_permission import IsInternalService
from utils.messages import result_message

from .models import *
from .permissions import *
from .serializers import *


class JobList(ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filterset_fields = ["category_id__title", "location_id__title", "job_type"]
    ordering_fields = ["salary", "created_at"]


class JobDetail(APIView):

    def get(self, request, job_id):

        try:
            job = get_object_or_404(Job, id=job_id)
            serializer = JobSerializer(job)
            result = result_message("OK", status.HTTP_200_OK, serializer.data)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            result = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class InternalJobList(APIView):
    permission_classes = [IsInternalService]

    def get(self, request):

        try:
            jobs = Job.objects.all()
            serializer = InternalJobListSerializer(jobs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            resul = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(resul, status=status.HTTP_400_BAD_REQUEST)


class InternalJobDetail(APIView):
    permission_classes = [IsInternalService]

    def get(self, request, job_id):

        try:
            job = get_object_or_404(Job, id=job_id)
            serializer = InternalJobListSerializer(job)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            resul = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(resul, status=status.HTTP_400_BAD_REQUEST)
